from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#USER CRUD FUNCTIONS USED IN auth.py

#Retreiving a user by their id
def get_user(db: Session, user_id: int):
    return db.query(models.UserModel).filter(models.UserModel.usernamec == user_id).first()

#Retrieving user by their username
def get_user_by_username(db: Session, username: int):
    return db.query(models.UserModel).filter(models.UserModel.username == username).first()

#Creating a new user
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db.user)
    db.commit()
    db.refresh(db_user)
    return db_user