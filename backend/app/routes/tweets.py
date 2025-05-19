from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import TweetsModel, UserModel
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
    query = db.query(TweetsModel, UserModel.username.label("username"))\
        .join(UserModel, TweetsModel.owner_id == UserModel.id)\
        .offset(skip).limit(limit)
        
    tweets_db = query.all() 

    tweets = []
    for tweet, username in tweets_db: 
        tweet_dict = {
            "id": tweet.id,
            "content": tweet.content,
            "owner_id": tweet.owner_id,
            "created_at": tweet.created_at,
            "tags": tweet.tags,
            "username": username
        }
        tweets.append(tweet_dict)
    return tweets

# searching for tweets
@router.get("/search", response_model=List[TweetResponse])
def search_tweets(query: str, db: Session = Depends(get_db)):
    search_query = db.query(TweetsModel, UserModel.username.label("username"))\
        .join(UserModel, TweetsModel.owner_id == UserModel.id)\
        .filter(TweetsModel.content.ilike(f"%{query}%"))
        
    tweets_db = search_query.all()
    
    # format like in GET tweets
    tweets = []
    for tweet, username in tweets_db:
        tweet_dict = {
            "id": tweet.id,
            "content": tweet.content,
            "owner_id": tweet.owner_id,
            "created_at": tweet.created_at,
            "tags": tweet.tags,
            "username": username
        }
        tweets.append(tweet_dict)
    return tweets

# searching for tags
@router.get("/search/tags")
def search_tweets_by_tags(tag: str, db: Session = Depends(get_db)):
    search_tag = tag if tag.startswith("#") else f"#{tag}"
    tweets_db = db.query(TweetsModel, UserModel.username.label("username"))\
        .join(UserModel, TweetsModel.owner_id == UserModel.id)\
        .filter(
            or_(
                TweetsModel.tags.ilike(f"%{search_tag}%") , 
                TweetsModel.tags == search_tag , #exact match 
                TweetsModel.content.ilike(f"%{search_tag}%") #content match
            )
        ).all()
    # format like in GET tweets
    tweets = []
    for tweet, username in tweets_db:
        tweet_dict = {
            "id": tweet.id,
            "content": tweet.content,
            "owner_id": tweet.owner_id,
            "created_at": tweet.created_at,
            "tags": tweet.tags,
            "username": username
        }
        tweets.append(tweet_dict)
    return tweets

# get all tweets by user id
# not used
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
    #regex finds words that start with a hashtag
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
    
    #After creating a tweet, clear the database cache
    from database import clear_db_cache
    clear_db_cache()
    
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
    
    #After updating a tweet, clear the database cache
    from database import clear_db_cache
    clear_db_cache()
    
    return {"message": "Tweet updated successfully"}


# delete a tweet
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
    
    # After deleting a tweet, clear the database cache
    from database import clear_db_cache
    clear_db_cache()
    
    return {"message": "Tweet deleted successfully"}


