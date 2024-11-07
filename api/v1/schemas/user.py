from fastapi import Form
from pydantic import BaseModel, EmailStr
from typing import Optional


class Signup(BaseModel):
    
    email: EmailStr = Form(...)
    password: str = Form(..., min_length=6)
    confirm_password: str = Form(..., min_length=6)
    

class Login(BaseModel):
    
    email: EmailStr = Form(...)
    password: str = Form(..., min_length=6)


class SelectRole(BaseModel):
    
    role: str = Form(...)
    

class TokenData(BaseModel):

    user_id: Optional[str]
    