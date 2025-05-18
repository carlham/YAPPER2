"""
Database query caching module for YAPPER2

This module provides a caching layer for database queries
to reduce the load on the database server.
"""

import time
import hashlib
import json
import sys
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.orm import Query

# Global query cache
# Structure: {query_hash: {"result": result_data, "timestamp": timestamp}}
query_cache = {}

# Cache settings
CACHE_EXPIRATION = 60  # Cache expiration time in seconds
MAX_CACHE_SIZE = 100   # Maximum number of queries to cache

# Track cache statistics
cache_stats = {
    "hits": 0,
    "misses": 0,
    "size": 0
}

def hash_query_str(query_str: str) -> str:
    """Generate a unique hash for a query string."""
    return hashlib.md5(query_str.encode()).hexdigest()

def hash_query(query: Query) -> str:
    """Generate a unique hash for a SQLAlchemy query."""
    if hasattr(query, 'statement'):
        query_str = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
        return hash_query_str(query_str)
    return hash_query_str(str(query))

def is_cacheable_query(query: Query) -> bool:
    """Determine if a query should be cached."""
    try:
        # Only cache SELECT queries (using statement.is_select if available)
        if hasattr(query, 'statement') and hasattr(query.statement, 'is_select'):
            if not query.statement.is_select:
                return False
        
        # Alternative approach for older SQLAlchemy versions
        # Check if the query is for a SELECT operation based on its string representation
        stmt_str = str(query.statement).strip().lower()
        if not stmt_str.startswith('select'):
            return False
            
        # Don't cache queries with specific options that might affect results
        if hasattr(query, '_with_options') and query._with_options:
            return False
            
        if hasattr(query, '_execution_options') and query._execution_options:
            return False
        
        return True
    except Exception:
        # If any error occurs during check, default to not caching
        return False

def get_from_cache(query_hash: str) -> Tuple[bool, Any]:
    """
    Try to get results from cache.
    Returns a tuple: (found, result)
    """
    global cache_stats
    
    # Log cache access attempt
    print(f"Cache access for hash: {query_hash[:8]}...")
    
    if query_hash in query_cache:
        cache_entry = query_cache[query_hash]
        current_time = time.time()
        
        # Check if cache is still valid
        if current_time - cache_entry["timestamp"] < CACHE_EXPIRATION:
            cache_stats["hits"] += 1
            print(f"Cache HIT! Hits now: {cache_stats['hits']}")
            return True, cache_entry["result"]
        else:
            print("Cache entry expired")
    else:
        print("Cache entry not found")
    
    cache_stats["misses"] += 1
    print(f"Cache MISS! Misses now: {cache_stats['misses']}")
    return False, None

def store_in_cache(query_hash: str, result: Any) -> None:
    """Store query results in cache."""
    global cache_stats
    
    print(f"Storing in cache, hash: {query_hash[:8]}")
    
    # Store the result
    query_cache[query_hash] = {
        "result": result,
        "timestamp": time.time()
    }
    
    cache_stats["size"] = len(query_cache)
    print(f"Cache size now: {cache_stats['size']}")
    
    # Clean up if cache exceeds max size
    if len(query_cache) > MAX_CACHE_SIZE:
        print("Cache size exceeds limit, cleaning...")
        clean_cache()

def clean_cache() -> None:
    """Remove expired or oldest items from cache."""
    current_time = time.time()
    
    # First, remove expired entries
    expired_keys = [
        key for key, value in query_cache.items() 
        if current_time - value["timestamp"] > CACHE_EXPIRATION
    ]
    
    for key in expired_keys:
        del query_cache[key]
    
    # If still too large, remove oldest entries
    if len(query_cache) > MAX_CACHE_SIZE:
        sorted_keys = sorted(
            query_cache.keys(), 
            key=lambda k: query_cache[k]["timestamp"]
        )
        
        # Remove oldest entries to get back to 80% of max size
        to_remove = len(query_cache) - int(MAX_CACHE_SIZE * 0.8)
        for i in range(to_remove):
            if i < len(sorted_keys):
                del query_cache[sorted_keys[i]]
    
    cache_stats["size"] = len(query_cache)

def get_cache_stats() -> Dict[str, Any]:
    """Return cache statistics."""
    global cache_stats
    
    hit_rate = 0
    total_requests = cache_stats["hits"] + cache_stats["misses"]
    if total_requests > 0:
        hit_rate = cache_stats["hits"] / total_requests * 100
    
    return {
        "hits": cache_stats["hits"],
        "misses": cache_stats["misses"],
        "size": cache_stats["size"],
        "hit_rate_percent": round(hit_rate, 2)
    }

def clear_cache() -> None:
    """Clear the entire query cache and reset the statistics."""
    global query_cache, cache_stats
    
    print(f"Clearing DB cache. Before clear - Hits: {cache_stats['hits']}, Misses: {cache_stats['misses']}")
    
    # Clear the cache
    query_cache = {}
    
    # Reset all cache statistics to 0
    cache_stats["hits"] = 0
    cache_stats["misses"] = 0 
    cache_stats["size"] = 0
    
    print(f"DB cache cleared. After clear - Hits: {cache_stats['hits']}, Misses: {cache_stats['misses']}")
