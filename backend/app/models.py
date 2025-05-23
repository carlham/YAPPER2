from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base 

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, server_default=func.now()) #Timestamp

    tweets = relationship("TweetsModel", back_populates="owner") # Relationship with the "Tweet" model

class TweetsModel(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id")) #Foreignkey is referencing users.id
    created_at = Column(DateTime, server_default=func.now())
    tags = Column(String, nullable=True) #Optional field
    likes = Column(Integer, default=0) #Number of likes

    owner = relationship("UserModel", back_populates="tweets") #Relationship with the "User" model
