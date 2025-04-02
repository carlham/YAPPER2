from pydantic import BaseModel
from datetime import datetime
from typing import Optional

#Base schema for user data
class UserBase(BaseModel):
    username: str

#Schema for creating a new user
class UserCreate(UserBase):
    password: str

#This schema represents a user
class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        orm_mode = True


#Tweet data schema
class TweetBase(BaseModel):
    content: str
    tags: Optional[str] = None

#Tweet creation schema, it inherits from tweetbase and doesnt need additional fields
class TweetCreate(TweetBase):
    owner_id: int

#This schema represents a tweet 
class Tweet(TweetBase):
    id: int
    owner_id: int
    created_at: datetime
    tags : Optional[str]

    class Config:
        orm_mode = True


class TweetResponse(BaseModel):
    id: int
    content: str
    owner_id: int
    tags: Optional[str] = None
    created_at: datetime
    

    class Config:
        orm_mode = True