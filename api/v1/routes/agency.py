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
        
    # return {'user': request.state.current_user}
    current_user = request.state.current_user
    
    if current_user.role != 'Agency admin':
        flash(request,'Unauthorized action', MessageCategory.ERROR)
        return RedirectResponse(url='/dashboard', status_code=303)
    
    data = AgencyService.get_agency_full_details(db, current_user)  # current user is in here
    
    return data


@agency_router.get('/responders')
@add_template_context('pages/user/agency/agency-responders.html')
async def agency_responders(
    request: Request,
    db: Session=Depends(get_db)
):
    '''Endpoint to get agency details'''
    
    # return {'user': request.state.current_user}
    current_user = request.state.current_user
    
    if current_user.role != 'Agency admin':
        flash(request,'Unauthorized action', MessageCategory.ERROR)
        return RedirectResponse(url='/dashboard', status_code=303)
    
    data = AgencyService.get_agency_full_details(db, current_user)
    
    return data


@agency_router.get('/emergencies')
@add_template_context('pages/user/agency/emergencies.html')
async def agency_emergencies(
    request: Request,
    db: Session=Depends(get_db)
):
    '''Endpoint to get agency details'''
    
    current_user = request.state.current_user
    
    if current_user.role != 'Agency admin':
        flash(request,'Unauthorized action', MessageCategory.ERROR)
        return RedirectResponse(url='/dashboard', status_code=303)
    
    data = AgencyService.get_agency_full_details(db, current_user)
    
    return data


@agency_router.get('/settings')
@add_template_context('pages/user/agency/agency-settings.html')
async def agency_settings(
    request: Request,
    db: Session=Depends(get_db)
):
    '''Endpoint to get agency settings'''
    
    # return {'user': request.state.current_user}
    current_user = request.state.current_user
    
    if current_user.role != 'Agency admin':
        flash(request,'Unauthorized action', MessageCategory.ERROR)
        return RedirectResponse(url='/dashboard', status_code=303)
    
    data = AgencyService.get_agency_full_details(db, current_user)
    
    return data


@agency_router.post('/settings/update')
async def update_agency_settings(
    request: Request,
    db: Session=Depends(get_db)
):
    '''Endpoint to update agency settings'''
    
    current_user = request.state.current_user
    
    if current_user.role != 'Agency admin':
        flash(request,'Unauthorized action', MessageCategory.ERROR)
        return RedirectResponse(url='/dashboard', status_code=303)
    
    # Process the form submission
    form_data = await request.form()
    
    # Example validation or processing of form_data
    agency_name = form_data.get('name')
    contact_number = form_data.get('contact-number')
    contact_email = form_data.get('contact-email')
    location = form_data.get('location')
    
    # Get relevant location data
    location_data = Location.fetch_one_by_field(
        db=db,
        city=location.split(',')[-2].strip(),
        state=location.split(',')[-1].strip()
    )
    
    # If location data is not found throw an error  so user selects from suggestion
    if not location_data:
        flash(
            request,
            message='Please select a valid location from the suggestions.',
            category=MessageCategory.ERROR
        )
        return RedirectResponse(url=f"/agency/settings", status_code=303)
    
    agency = Agency.fetch_one_by_field(db, creator_id=current_user.id)
    
    Agency.update(
        db, 
        id=agency.id,
        latitude=location_data.latitude,
        longitude=location_data.longitude,
        location_str=location,
        location=location_data.geo_location,
        name=agency_name,
        contact_number=contact_number,
        contact_email=contact_email,
    )
    
    flash(request, f'Agency details updated', MessageCategory.SUCCESS)
    return RedirectResponse(url=f"/agency/settings", status_code=303)


@agency_router.post('/emergencies/{emergency_id}/assign')
async def assign_emergency_to_responder(
    request: Request,
    emergency_id: str,
    db: Session=Depends(get_db)
):
    '''Endpoint to get agency details'''
    
    current_user = request.state.current_user
    
    if current_user.role != 'Agency admin':
        flash(request,'Unauthorized action', MessageCategory.ERROR)
        return RedirectResponse(url='/agency/responders', status_code=303)
    
    # Process the form submission
    form_data = await request.form()
    
    # Example validation or processing of form_data
    responder_id = form_data.get('responder')
    
    # Fetch emergency and responder
    emergency = Emergency.fetch_by_id(db, id=emergency_id)
    responder = Responder.fetch_by_id(db, id=responder_id)
    
    if not emergency or not responder:
        flash(request,'Invalid request', MessageCategory.ERROR)
        return RedirectResponse(url='/agency/emergencies', status_code=303)
    
    # Check if responder is already engaged
    if responder.status =='engaged':
        flash(request,'Responder is already engaged', MessageCategory.ERROR)
        return RedirectResponse(url='/agency/emergencies')
    
    # Check if responder is already assigned to this emergency
    responder_emergency_assigned = ResponderEmergency.fetch_one_by_field(
        db=db,
        emergency_id=emergency.id,
        responder_id=responder.id,
    )
    
    if responder_emergency_assigned:
        flash(request,'Responder is already assigned to this emergency', MessageCategory.ERROR)
        return RedirectResponse(url='/agency/emergencies')
    
    # Create responder emergency
    ResponderEmergency.create(
        db=db,
        emergency_id=emergency.id,
        responder_id=responder.id,
        status='Assigned',
    )
    
    # Update responder status
    Responder.update(db=db, id=responder.id, status='engaged')
    
    # Update emergency status
    Emergency.update(db=db, id=emergency.id, status='In Progress')
    
    flash(request,'Emergency assigned successfully', MessageCategory.SUCCESS)
    return RedirectResponse(url='/agency/emergencies', status_code=303)


@agency_router.post('/responders/{responder_id}/remove')
async def remove_responder_from_agency(
    request: Request,
    responder_id: str,
    db: Session=Depends(get_db)
):
    '''Endpoint to remove responder from agency'''
    
    current_user = request.state.current_user
    
    if current_user.role != 'Agency admin':
        flash(request,'Unauthorized action', MessageCategory.ERROR)
        return RedirectResponse('/agency/responders', 303)
    
    responder = Responder.fetch_by_id(db, id=responder_id)
    
    if not responder:
        flash(request,'Invalid request', MessageCategory.ERROR)
        return RedirectResponse('/agency/responders', 303)
    
    if responder.status == 'engaged':
        flash(request,'Cannot remove engaged responder', MessageCategory.ERROR)
        return RedirectResponse('/agency/responders', 303)
        
    Responder.update(
        db=db, 
        id=responder_id,
        agency_id=None
    )
    
    flash(request,'Responder removed from agency', MessageCategory.SUCCESS)
    return RedirectResponse('/agency/responders', 303)


@agency_router.post('/responders/{responder_id}/add')
async def add_responder_to_agency(
    request: Request,
    responder_id: str,
    db: Session=Depends(get_db)
):
    '''Endpoint to add responder to agency'''
    
    current_user = request.state.current_user
    
    if current_user.role != 'Agency admin':
        flash(request,'Unauthorized action', MessageCategory.ERROR)
        return RedirectResponse('/agency/responders', 303)
    
    agency = Agency.fetch_one_by_field(db, creator_id=current_user.id)
    
    responder = Responder.update(
        db=db, 
        id=responder_id,
        agency_id=agency.id
    )
    
    if not responder:
        flash(request,'Invalid request', MessageCategory.ERROR)
        return RedirectResponse('/agency/responders', 303)
    
    flash(request,'Responder added to agency', MessageCategory.SUCCESS)
    return RedirectResponse('/agency/responders', 303)
