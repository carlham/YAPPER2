from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schemas, models
from ..database import get_db
from ..utils import create_access_token, verify_password, get_password_hash
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request

router = APIRouter()

@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
     db_user = crud.get_user_by_username(db, username=user.username)
     if db_user:
          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, details="Username already registered")
     
     #Hashing the password using the utility function
     user.password = get_password_hash(user.password)

     #Creating the user in the db
     return crud.create_user(db=db, user=user)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
     #Retrieving user form data from db
     user = crud.get_user_by_username(db, username=form_data.username)

     if not user or not verify_password(form_data.password, user.hashed_password):
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
     
     access_token = create_access_token(data={"sub": user.username})
     
     return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(request: Request):
     return { "message": "Logout successful"}