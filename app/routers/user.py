from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..schemas import PostCreate, Post, UserCreate, UserOut
from ..database import SessionLocal, get_db
from .. import models, schemas, utils
from sqlalchemy.orm import Session


router = APIRouter(
    prefix='/users',
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):    
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f'user with email: {user.email} already exists'
        )
        return

    hashed_password = utils.hash(user.password)
    user.password =  hashed_password 

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get('/{id}', response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()   
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'user with id: {id} does not exist'
        )

    return user