from sqlalchemy import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# USER CRUD FUNCTIONS

#Retrieving a user by their id
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

#Retrieving a user by their username
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

#Creating a new user
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# TWEET CRUD FUNCTION

#Retrieving a tweet by id
def get_tweet(db: Session, tweet_id: int):
    return db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()

#Retrieving all tweets with pagination
def get_tweets(db: Session, skip: int=0, limit: int = 100):
    return db.query(models.Tweet).offset(skip).limit(limit).all()

#Creating a new tweet
def create_tweet(db: Session, tweet: schemas.TweetCreate, owner_id: int):
    db_tweet = models.Tweet(content=tweet.content, owner_id=owner_id)
    db.add(db_tweet)
    db.commit()
    db.refresh(db_tweet)
    return db_tweet

#Updating a tweet
def update_tweet(db: Session, tweet_id: int, tweet: schemas.TweetCreate):
    db_tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet.id).first()
    if db_tweet:
        db_tweet.content = tweet.content
        db.commit()
        db.refresh(db_tweet)
        return db_tweet
    return None

#Deleting a tweet
def delete_tweet(db: Session, tweet_id, int):
    db_tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if db_tweet:
        db.delete(db_tweet)
        db.commit()
        return True
    return False

# SEARCH FUNCTIONS

#Searching for tweets that contain specified query
def search_tweets(db: Session, query: str):
    return db.query(models.Tweet).filter(models.Tweet.content.ilike(f"%{query}")).all()

#Searching tweets containtnig specified hashtag
def search_tweets_by_hashtag(db: Session, hashtag: str):
    return db.query(models.Tweet).filter(models.Tweet.content.ilike(f"%{hashtag}")).all()

#Searching for users containing the specified query
def searhc_users(db: Session, query: str)
    return db.query(models.User).filter(models.User.username.ilike(f"%{query}")).all()