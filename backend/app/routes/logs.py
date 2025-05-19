from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import time
from datetime import datetime

#Create a router for the logs endpoint
router = APIRouter(
    prefix="/logs",
    tags=["logs"]
)

#Global variable to store API call logs
api_logs = []
db_access_count = 0
db_access_logs = []
MAX_LOGS = 1000 #Maximum number of logs to keep for memory efficiency

#Add a function to log API calls
def log_api_call(method: str, endpoint: str, status_code: int = 200, execution_time: float = 0):
    """
    Log API calls with method and endpoint
    """
    global api_logs
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "execution_time_ms": round(execution_time * 1000, 2)
    }
    api_logs.append(log_entry)
    
    #Keep only the last MAX_LOGS entries for memory efficiency
    if len(api_logs) > MAX_LOGS:
        api_logs = api_logs[:MAX_LOGS]

#Unsure if we want to use this, leaving it here for now (if you want to see the db logs)
def log_db_access(operation: str, table: str, query_details: str = ""):
    """
    Log db operations
    """
    global db_access_logs
    timestamp = datetime.now().isoformat()

    log_entry = {
        "timestamp": timestamp,
        "operation": operation,
        "table": table,
        "query_details": query_details
    }

    db_access_logs.append(log_entry)

    if len(db_access_logs) > MAX_LOGS:
        db_access_logs = db_access_logs[:MAX_LOGS]

    
#Add a function to increment database access count
def increment_db_access_count():
    global db_access_count
    db_access_count += 1

@router.get("", response_model=Dict[str, Any])
def get_logs():
    """
    Get all API call logs and database access count
    """
    return {
        "api_calls": api_logs,
        "total_api_calls": len(api_logs),
        "total_db_calls": db_access_count
    }


#clear logs function
@router.delete("")
def clear_logs():
    """
    Clear all API call logs
    """
    global api_logs, db_access_logs
    api_logs = []
    db_access_logs = []
    return {"message": "Logs cleared"}