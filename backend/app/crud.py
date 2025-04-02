<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

<<<<<<< Updated upstream
#lollol
=======
>>>>>>> Stashed changes
#USER CRUD FUNCTIONS

#Retrieving a user by their id
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.username == username).first()

#Retrieving a user by their username
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()