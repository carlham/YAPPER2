from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from models import TweetsModel
from schemas import TweetCreate, TweetResponse
from utils import get_current_user_id
import re

router = APIRouter(
    prefix="/tweets",
    tags=["tweets"]
)

# endpoints for tweets, get all tweets, create tweet, edit tweet and delete tweet 
@router.get("", response_model=List[TweetResponse])
def read_tweets(db: Session = Depends(get_db), skip: int = None, limit: int = None): # pagination if wanted
    tweets = db.query(TweetsModel).offset(skip).limit(limit).all()
    return tweets

# searching for tweets
@router.get("/search")
def search_tweets(query: str, db: Session = Depends(get_db)):
    tweets = db.query(TweetsModel).filter(TweetsModel.content.ilike(f"%{query}%")).all()
    return tweets

# searching for tags
@router.get("/search/tags")
def search_tweets_by_tags(tag: str, db: Session = Depends(get_db)):
    tweets = db.query(TweetsModel).filter(TweetsModel.tags.ilike(f"%{tag}%")).all()
    return tweets

# get all tweets by user id
# unsure if we need this, but it might be useful for the frontend down the line
@router.get("/user/{user_id}", response_model=List[TweetResponse])
def read_tweets_by_user(user_id: int, db: Session = Depends(get_db)):
    tweets = db.query(TweetsModel).filter(TweetsModel.owner_id == user_id).all()
    if not tweets:
        return {"error": "No tweets found for this user"}
    return tweets


# get a tweet by id
@router.get("/{tweet_id}", response_model=TweetResponse)
def read_tweet(tweet_id: int, db: Session = Depends(get_db)):
    tweet = db.query(TweetsModel).filter(TweetsModel.id == tweet_id).first()
    if tweet is None:
        return {"error": "Tweet not found"}
    return tweet

# modify this to split the tags by hashtag and add them to the tags field
# when creating a tweet

@router.post("", response_model=TweetResponse)
def create_tweet(tweet: TweetCreate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    # Extract hashtags from the content using regex
    # This regex finds words that start with a hashtag
    hashtags = re.findall(r'#(\w+)', tweet.content)

    # Adding hashtags to the tags_string to be stored in the database
    tags_string = " ".join([f"#{tag}" for tag in hashtags])

    tweet = TweetsModel(
        content=tweet.content,
        owner_id=current_user_id, # use id from token
        tags=tags_string,
    )

    db.add(tweet)
    db.commit()
    db.refresh(tweet)
    return tweet

@router.put("/{tweet_id}")
def update_tweet(tweet_id: int, tweet_data: TweetCreate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    # check if tweet exists
    db_tweet = db.query(TweetsModel).filter(TweetsModel.id == tweet_id).first()
    if not db_tweet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tweet not found")
    
    # auth check, only owner can edit own tweets
    if db_tweet.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to edit this tweet")
    # extract hashtags from the content like in create_tweet
    hashtags = re.findall(r'#(\w+)', tweet_data.content)
    tags_string = " ".join([f"#{tag}" for tag in hashtags])

    # get existing tweet from db
    db_tweet = db.query(TweetsModel).filter(TweetsModel.id == tweet_id).first()
    if not db_tweet:
        return {"error": "Tweet not found"}
    

    # update tweet content and tags
    db_tweet.content = tweet_data.content
    db_tweet.tags = tags_string
    db_tweet.owner_id = tweet_data.owner_id

    # commit changes to db
    db.commit()
    db.refresh(db_tweet)
    return {"message": "Tweet updated successfully"}

@router.delete("/{tweet_id}")
def delete_tweet(tweet_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    # check if tweet exists
    db_tweet = db.query(TweetsModel).filter(TweetsModel.id == tweet_id).first()
    if not db_tweet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tweet not found")
    # auth check, only owner can delete own tweets
    if db_tweet.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to delete this tweet")
    # delete tweet from db
    db.delete(db_tweet)
    db.commit()
    return {"message": "Tweet deleted successfully"}


