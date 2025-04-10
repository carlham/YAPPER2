from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
import os

#Creating SQLAlchemy engine using the config.py URL
#SQLAlchemy needs it to execute SQL queries and interact with the DB
engine = create_engine(DATABASE_URL)

#Creating a session factory s
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Creating a base class for declarative class definitions
Base=declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()