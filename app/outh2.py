import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from .config import settings
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from . import database, models, schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, settings.algorithm)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        body = jwt.decode(token, settings.secret_key,
                          algorithms=[settings.algorithm])
        u_id: int = body.get("user_id")
        if u_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=u_id)
        return token_data
    except InvalidTokenError:
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}
    )
    token_data = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(
        models.User.id == token_data.id).first()
    if user is None:
        raise credentials_exception
    return user
