from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, server_default=func.now()) #Timestamp

    tweets = relationship("Tweet", back_populates="owner") # Relationship with the "Tweet" model

class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey(users.id)) #Foreignkey is referencing users.id
    created_at = Column(DateTime, server_default=func.now())

    owner = relationship("User", back_populates="tweets") #Relationship with the "User" model
