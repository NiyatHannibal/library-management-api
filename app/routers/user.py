from fastapi import HTTPException, Depends, status, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from .. import models, schemas, outh2, utils

router = APIRouter(
    prefix="/users",
    tags=["Users"]

)


def verify_admin(
    current_user: models.User = Depends(outh2.get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    return current_user


@router.post("/register", response_model=schemas.UserResponse)
def register(body=schemas.UserCreate, db: Session = Depends(get_db)):
    body.password = utils.get_password_hash(body.password)
    user = models.User(**body.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=schemas.UserResponse)
def get_profile(current_user: models.User = Depends(outh2.get_current_user)):
    return current_user


@router.get("/", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db), admin: models.User = Depends(verify_admin)):
    users = db.query(models.User).all()
    return users


@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), admin: models.User = Depends(verify_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with Id{user_id} doesn't exist"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def get_user(user_id: int, db: Session = Depends(get_db), admin: models.User = Depends(verify_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with Id{user_id} doesn't exist"
        )
    db.delete(user)
    db.commit()
