from pydantic import BaseModel, Field, field_validator
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
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


#Tweet data schema
class TweetBase(BaseModel):
    content: str
    tags: Optional[str] = None

#Tweet creation schema, it inherits from tweetbase and doesnt need additional fields
class TweetCreate(TweetBase):
    content: str = Field(..., min_length=1, max_length=250) 
    owner_id: Optional[int] = None
    
    # Validator to ensure content is not empty
    @field_validator('content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v
    

#This schema represents a tweet 
class Tweet(TweetBase):
    id: int
    content: str
    owner_id: int
    created_at: datetime
    tags : Optional[str]
    likes: Optional[int] = 0

    class Config:
        from_attributes = True


class TweetResponse(BaseModel):
    id: int
    content: str
    owner_id: int
    tags: Optional[str] = None
    created_at: datetime
    username: Optional[str] = None
    

    class Config:
        from_attributes = True