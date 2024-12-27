from typing import List, Optional
from fastapi import APIRouter, File, HTTPException, Request, UploadFile, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from api.core.dependencies.context import add_template_context
from api.core.dependencies.form_builder import build_form
from api.core.dependencies.flash_messages import flash, MessageCategory
from api.db.database import get_db
from api.utils.firebase_service import FirebaseService
from api.v1.models.profile import Profile
from api.v1.models.user import User
from api.v1.models.responder import Responder
from api.v1.services.emergency import EmergencyService


responder_router = APIRouter(prefix='/responders')

# Fetch all responders from db
@responder_router.get('/')
@add_template_context('pages/user/responder/responders.html')
async def get_responders(request: Request, db: Session = Depends(get_db)):
    '''Endpoint to get all responders in db'''
    
    current_user = request.state.current_user
    responders = Responder.all(db)
    
    return {
        'user': current_user,
        'responders': responders
    }

@responder_router.get('/search')
# @add_template_context('pages/user/responder/responders.html')
async def search_responders(
    request: Request, 
    first_name: str,
    last_name: str,
    email: str,
    db: Session = Depends(get_db)
):
    '''Endpoint to search for all responders in db'''
    
    current_user = request.state.current_user
    responders = (
        db.query(Responder)
        .join(User, User.id == Responder.user_id)
        .join(Profile, Profile.user_id == User.id)
        .filter(
            Profile.first_name.ilike(f'%{first_name}%'),
            Profile.last_name.ilike(f'%{last_name}%'),
            User.email.ilike(f'%{email}%'),
        ).all()
    )
    
    return {
        'user': current_user,
        'responders': responders
    }


# Fetch responder by id
