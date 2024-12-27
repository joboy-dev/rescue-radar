from typing import List, Optional
from fastapi import APIRouter, File, HTTPException, Request, UploadFile, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from api.core.dependencies.context import add_template_context
from api.core.dependencies.form_builder import build_form
from api.core.dependencies.flash_messages import flash, MessageCategory
from api.db.database import get_db
from api.utils.firebase_service import FirebaseService
from api.v1.models.emergency import Emergency
from api.v1.models.location import Location
from api.v1.models.agency import Agency
from api.v1.models.responder import Responder
from api.v1.models.responder_emergency import ResponderEmergency
from api.v1.services.agency import AgencyService


agency_router = APIRouter(prefix='/agency')


@agency_router.get('/details')
@add_template_context('pages/user/agency/agency-base.html')
async def get_agency_details(
    request: Request,
    db: Session=Depends(get_db)
):
    '''Endpoint to get agency details'''
    
    current_user = request.state.current_user
    
    data = AgencyService.get_agency_full_details(db, current_user)
    
    return data


@agency_router.get('/dashboard')
@add_template_context('pages/user/agency/agency-dashboard.html')
async def agency_dashboard(
    request: Request,
    db: Session=Depends(get_db)
):
    '''Endpoint to get agency details'''
        
    return {'user': request.state.current_user}


@agency_router.get('/responders')
@add_template_context('pages/user/agency/agency-responders.html')
async def agency_responders(
    request: Request,
    db: Session=Depends(get_db)
):
    '''Endpoint to get agency details'''
    
    return {'user': request.state.current_user}
