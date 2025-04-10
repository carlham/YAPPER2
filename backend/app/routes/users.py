from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from models import UserModel
from schemas import UserCreate, UserResponse
from utils import get_password_hash

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("", response_model=List[UserResponse])
def read_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return users

# searching for users
@router.get("/search", response_model=List[UserResponse])
def search_users(query: str, db: Session = Depends(get_db)):
    users = db.query(UserModel).filter(UserModel.username.ilike(f"%{query}%")).all() 
    return users

#get a user by id
@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        return {"error": "User not found"}
    return user

#create account
@router.post("", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # check if user exists
    existing_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # hash password with same function used in auth
    hashed_password = get_password_hash(user.password)

    # create new user
    db_user = UserModel(
        username=user.username,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

#not used
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
