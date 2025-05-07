from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
import os
import time


#Creating SQLAlchemy engine using the config.py URL
#SQLAlchemy needs it to execute SQL queries and interact with the DB
engine = create_engine(DATABASE_URL)

#Creating a session factory s
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Creating a base class for declarative class definitions
Base=declarative_base()

#Import routes.logs 
from routes.logs import log_db_access, increment_db_access_count

#SQLAlchemy event listener to log database access
@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """
    Log db access
    """
    conn.info.setdefault('query_start_time', []).append(time.time())

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()