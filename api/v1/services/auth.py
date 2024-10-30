from typing import Any, Optional, Annotated
import datetime as dt
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from api.db.database import get_db
from api.utils.settings import settings
from api.v1.models.tokens import BlackListedToken
from api.v1.models.user import User
from api.v1.schemas.user import TokenData


bearer_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    
    @classmethod
    def authenticate_user(cls, email: str, password: str):
        
        user = User.fetch_one_by_field(email=email)
        
        if not user:
            raise HTTPException(status_code=400, detail="Invalid user credentials")

        if not cls.verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="Invalid user credentials")

        # Update last_login of user
        User.update(user.id, last_login=dt.datetime.now())
        return user
    
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
    def verify_access_token(cls, access_token: str, credentials_exception):
        """Funtcion to decode and verify access token"""

        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("user_id")
            token_type = payload.get("type")
            
            # Check if token is blackliosted
            blacklisted_token = BlackListedToken.fetch_one_by_field(token=access_token)

            if user_id is None or blacklisted_token is not None:
                raise credentials_exception

            if token_type == "refresh":
                raise HTTPException(detail="Refresh token not allowed", status_code=400)

            token_data = TokenData(id=user_id)

        except JWTError as err:
            print(err)
            raise credentials_exception

        return token_data

    @classmethod
    def verify_refresh_token(cls, refresh_token: str, credentials_exception):
        """Funtcion to decode and verify refresh token"""

        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("user_id")
            token_type = payload.get("type")
            
            blacklisted_token = BlackListedToken.fetch_one_by_field(token=refresh_token)

            if user_id is None or blacklisted_token is not None:
                raise credentials_exception

            if token_type == "access":
                raise HTTPException(detail="Access token not allowed", status_code=400)

            token_data = TokenData(id=user_id)

        except (JWTError, AttributeError):
            raise credentials_exception

        return token_data
    
    @classmethod
    def refresh_access_token(cls, current_refresh_token: str):
        """Function to generate new access token and rotate refresh token"""

        credentials_exception = HTTPException(
            status_code=401, detail="Refresh token expired"
        )

        token = cls.verify_refresh_token(current_refresh_token, credentials_exception)

        if token:
            access = cls.create_access_token(user_id=token.id)
            refresh = cls.create_refresh_token(user_id=token.id)

            return access, refresh
        
    @classmethod
    def get_current_user(
        cls, 
        access_token: str = Depends(bearer_scheme), 
    ) -> User:
        """Function to get current logged in user"""

        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        token = cls.verify_access_token(access_token, credentials_exception)
        user = User.fetch_by_id(token.id)
        
        if not user:
            raise credentials_exception

        return user

    