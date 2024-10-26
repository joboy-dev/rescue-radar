from typing import Any, Optional, Annotated
import datetime as dt
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from api.utils.settings import settings


bearer_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    
    @classmethod
    def authenticate_user(cls, db: Session, email_or_username: str, password: str):
        pass
    
    @classmethod
    def hash_password(cls, password: str):
        return pwd_context.hash(password)
    
    @classmethod
    def verify_password(cls, password: str, hash: str):
        return pwd_context.verify(password, hash)
    
    @classmethod
    def create_access_token(cls, db: Session, user_id: str):
        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {"user_id": user_id, "exp": expires, "type": "access"}
        encoded_jwt = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt

    @classmethod
    def create_refresh_token(cls, db: Session, user_id: str):
        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {"user_id": user_id, "exp": expires, "type": "refresh"}
        encoded_jwt = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt
    
    
    @classmethod
    def verify_token(cls, token: str):
        pass
    