from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from models import UserModel
from schemas import UserCreate, UserResponse
import hashlib

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

@router.post("", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_passowrd = hashlib.sha256(user.password.encode()).hexdigest()

    user = UserModel(
        username=user.username,
        hashed_password=hashed_passowrd,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# login and logout routes
@router.post("/login")
def login():
    return {"message": "login successful"}

@router.post("/logout")
def logout():
    return {"message": "logout successful"}

