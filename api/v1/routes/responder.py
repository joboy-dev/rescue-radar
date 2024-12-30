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
from api.v1.services.responder import ResponderService


responder_router = APIRouter(prefix='/responders')

@responder_router.get('/dashboard')
@add_template_context('pages/user/responder/responder-dashboard.html')
async def responder_dashboard(
    request: Request,
    db: Session=Depends(get_db)
):
    '''Endpoint to get responder details'''
        
    # return {'user': request.state.current_user}
    current_user = request.state.current_user
    
    redirect_dashboard = '/dashboard' if current_user.role == 'Public' else '/agency/dashboard'
    
    if current_user.role != 'Responder':
        flash(request,'Unauthorized action', MessageCategory.ERROR)
        return RedirectResponse(
            url=redirect_dashboard, 
            status_code=303
        )
    
    data = ResponderService.get_responder_full_details(db, current_user)  # current user is in here
    print(data)
    
    return data


# Fetch all responders from db
@responder_router.get('/')
@add_template_context('pages/user/agency/responders.html')
async def get_responders(request: Request, db: Session = Depends(get_db)):
    '''Endpoint to get all responders in db'''
    
    current_user = request.state.current_user
    responders = Responder.all(db)
    
    return {
        'user': current_user,
        'responders': responders
    }
    

@responder_router.get('/agencyless')
@add_template_context('pages/user/agency/responders.html')
async def get_responders_without_agency(request: Request, db: Session = Depends(get_db)):
    '''Endpoint to get all responders in db'''
    
    current_user = request.state.current_user
    # responders = db.query(Responder).filter(Responder.agency_id == None).all()
    responders = Responder.fetch_by_field(db, order='asc', agency_id=None)
    
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
    
    return responders


# Fetch responder by id
