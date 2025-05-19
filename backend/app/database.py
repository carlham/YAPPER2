from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
import os
import time
import sys

# Determine if DB caching should be enabled
# Always enabled by default, can be disabled explicitly via environment variable
ENABLE_DB_CACHE = os.environ.get("ENABLE_DB_CACHE", "True").lower() == "true"

#Creating SQLAlchemy engine using the config.py URL
#SQLAlchemy needs it to execute SQL queries and interact with the DB
engine = create_engine(DATABASE_URL)

#Creating a session factory s
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Creating a base class for declarative class definitions
Base = declarative_base()

#Import routes.logs 
from routes.logs import log_db_access, increment_db_access_count

#SQLAlchemy event listener to log database access
@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """
    Log db access
    """
    conn.info.setdefault("query_start_time", []).append(time.time())

    #Log db operation
    statement_lower = statement.lower()
    operation = "UNKNOWN"
    table = "UNKNOWN"

    if "select" in statement_lower: 
        operation = "SELECT"
    elif "insert" in statement_lower: 
        operation = "INSERT"
    elif "update" in statement_lower:
        operation = "UPDATE"
    elif "delete" in statement_lower:
        operation = "DELETE"

    #Basic table extraction
    table_keywords = ["from", "into", "update", "join"]
    for keyword in table_keywords:
        if f" {keyword} " in statement_lower:
            parts = statement_lower.split(f" {keyword} ")[1].strip().split(" ")
            if parts:
                table = parts[0].strip()
                break

    query_details = f"{statement[:100]}..." if len(statement) > 100 else statement
    log_db_access(operation, table, query_details)
    increment_db_access_count()

# Database query caching integration
if ENABLE_DB_CACHE:
    from db_cache import (
        hash_query, 
        is_cacheable_query, 
        get_from_cache, 
        store_in_cache
    )
    
    def cached_query(query):
        """
        Wrapper function to add caching to SQLAlchemy queries
        
        Usage example:
            # Instead of:
            # result = db.query(Model).filter(...).all()
            
            # Use:
            # result = cached_query(db.query(Model).filter(...)).all()
        """
        # Original query execution method
        original_all = query.all
        original_first = query.first
        original_one = query.one
        original_one_or_none = query.one_or_none
        
        # Check if query is cacheable
        if not is_cacheable_query(query):
            return query
        
        # Generate hash for this query
        query_hash = hash_query(query)
        
        # Replace the execute methods with cached versions
        def cached_all():
            found, result = get_from_cache(query_hash + "_all")
            if found:
                return result
            result = original_all()
            store_in_cache(query_hash + "_all", result)
            return result
            
        def cached_first():
            found, result = get_from_cache(query_hash + "_first")
            if found:
                return result
            result = original_first()
            store_in_cache(query_hash + "_first", result)
            return result
            
        def cached_one():
            found, result = get_from_cache(query_hash + "_one")
            if found:
                return result
            result = original_one()
            store_in_cache(query_hash + "_one", result)
            return result
            
        def cached_one_or_none():
            found, result = get_from_cache(query_hash + "_one_or_none")
            if found:
                return result
            result = original_one_or_none()
            store_in_cache(query_hash + "_one_or_none", result)
            return result
        
        # Replace methods with cached versions
        query.all = cached_all
        query.first = cached_first
        query.one = cached_one
        query.one_or_none = cached_one_or_none
        
        return query

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_cached_query(query):
    """Utility function to apply caching if enabled"""
    if ENABLE_DB_CACHE:
        return cached_query(query)
    return query

def get_db_cache_stats():
    """Get database cache statistics for monitoring"""
    if ENABLE_DB_CACHE:
        # Import here to avoid circular import
        from db_cache import get_cache_stats
        stats = get_cache_stats()
        return {
            "hits": stats["hits"],
            "misses": stats["misses"],
            "size": stats["size"],
            "status": "enabled"
        }
    return {"status": "disabled"}
    
def clear_db_cache():
    """Clear the database query cache"""
    try:
        if ENABLE_DB_CACHE:
            # Import here to avoid circular import
            from db_cache import clear_cache
            clear_cache()
            return {"status": "cache cleared"}
        return {"status": "cache disabled"}
    except Exception as e:
        # Handle any exceptions that might occur
        return {"status": "error", "message": str(e)}
