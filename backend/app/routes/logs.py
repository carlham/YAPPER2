from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database import get_db

# Create a router for the logs endpoint
router = APIRouter(
    prefix="/logs",
    tags=["logs"]
)

# Global variable to store API call logs
# Fix
api_logs = []
db_access_count = 0

# Add a function to log API calls
def log_api_call(method: str, endpoint: str):
    api_logs.append([method, endpoint])

# Add a function to increment database access count
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
        "db_access_count": db_access_count
    }