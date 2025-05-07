from fastapi import APIRouter, Depends, Response, status, Request
import time
from typing import Dict, Any
from sqlalchemy.orm import Session
from database import get_db
from routes.logs import increment_db_access_count
import threading

# Router for handling likes
router = APIRouter(
    prefix="/likes",
    tags=["likes"]
)

# In-memory storage for batching likes
like_batches = {}

# Lock for thread-safe operations on the like_batches dictionary
batch_lock = threading.Lock()

# Function to check if a batch should be sent to the database
def should_process_batch(tweet_id: str) -> bool:
    if tweet_id not in like_batches:
        return False
    
    batch = like_batches[tweet_id]
    current_time = time.time()
    
    # Process if more than 10 likes accumulated
    if batch["likes"] >= 10:
        return True
    
    # Process if more than 1 minute has passed since the first like
    if current_time - batch["time"] > 60:  # 60 seconds
        return True
    
    return False

# Function to process a batch of likes and update the database
def process_batch(tweet_id: str, db: Session):
    with batch_lock:
        if tweet_id not in like_batches:
            return
        
        # Get the number of likes to add
        likes_to_add = like_batches[tweet_id]["likes"]
        
        # Remove the batch from memory
        del like_batches[tweet_id]
    
    # Update the database with the accumulated likes
    try:
        # Get the tweet from the database
        from models import TweetsModel
        
        # Log database access
        increment_db_access_count()
        
        # Find the tweet and update likes
        tweet = db.query(TweetsModel).filter(TweetsModel.id == int(tweet_id)).first()
        if tweet:
            # Initialize likes to 0 if it's None
            if tweet.likes is None:
                tweet.likes = 0
                
            # Update the likes count in the database
            tweet.likes += likes_to_add
            db.commit()
    except Exception as e:
        print(f"Error processing like batch for tweet {tweet_id}: {str(e)}")

# Background task to periodically check for batches that need processing
def background_batch_processor():
    while True:
        time.sleep(10)  # Check every 10 seconds
        
        # Get a copy of the keys to avoid modifying during iteration
        with batch_lock:
            tweet_ids = list(like_batches.keys())
        
        # Create a session for database operations
        db = next(get_db())
        try:
            for tweet_id in tweet_ids:
                if should_process_batch(tweet_id):
                    process_batch(tweet_id, db)
        finally:
            db.close()

# Start the background processor thread
batch_processor_thread = threading.Thread(target=background_batch_processor, daemon=True)
batch_processor_thread.start()

# Endpoint to add a like to a post
@router.post("/{tweet_id}")
async def add_like(tweet_id: str, db: Session = Depends(get_db)):
    # Add the like to the batch
    with batch_lock:
        current_time = time.time()
        
        if tweet_id not in like_batches:
            # First like for this tweet
            like_batches[tweet_id] = {"likes": 1, "time": current_time}
        else:
            # Increment the like count
            like_batches[tweet_id]["likes"] += 1
        
        # Check if we should process this batch immediately
        should_process = should_process_batch(tweet_id)
    
    # Process the batch if needed
    if should_process:
        process_batch(tweet_id, db)
    
    return {"message": f"Like added to post {tweet_id}"}

# Endpoint to get current like count for a post (includes pending likes)
@router.get("/{tweet_id}")
async def get_likes(tweet_id: str, db: Session = Depends(get_db)):
    from models import TweetsModel
    
    # Log database access
    increment_db_access_count()
    
    # Get current likes from the database
    tweet = db.query(TweetsModel).filter(TweetsModel.id == int(tweet_id)).first()
    db_likes = tweet.likes if tweet else 0
    
    # Add any pending likes from the batch
    pending_likes = 0
    with batch_lock:
        if tweet_id in like_batches:
            pending_likes = like_batches[tweet_id]["likes"]
    
    total_likes = db_likes + pending_likes
    
    return {"tweet_id": tweet_id, "likes": total_likes}