from pydantic import BaseModel
from datetime import datetime

#Base schema for user data
class UserBase(BaseModel):
    username: str
    email: str

#Schema for creating a new user
class UserCreate(UserBase):
    password: str

#This schema represents a user
class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

#Tweet data schema
class TweetBase(BaseModel):
    content: str

#Tweet creation schema, it inherits from tweetbase and doesnt need additional fields
class TweetCreate(TweetBase):
    pass

#This schema represents a tweet 
class Tweet(TweetBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        orm_mode = True