from fastapi import APIRouter, Depends, Response, status, Request
import time
from typing import Dict, Any
from sqlalchemy.orm import Session
from database import get_db
from routes.logs import increment_db_access_count

# Router for handling likes
router = APIRouter(
    prefix="/likes",
    tags=["likes"]
)
# Implement
# Add new field to yaps, where we just store the number of likes

# Endpoint to add a like to a post
@router.post("/{post_id}")
async def add_like(post_id: str, db: Session = Depends(get_db)):
    
    return {"message": f"Like added to post {post_id}"}