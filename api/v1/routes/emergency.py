from typing import List, Optional
from fastapi import APIRouter, File, HTTPException, Request, UploadFile, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from api.core.dependencies.context import add_template_context
from api.core.dependencies.form_builder import build_form
from api.core.dependencies.flash_messages import flash, MessageCategory
from api.db.database import get_db
from api.utils.firebase_service import FirebaseService
from api.utils.paginator import paginate_items
from api.v1.models.location import Location
from api.v1.models.emergency import Emergency, EventType, SeverityLevel, EVENT_TYPE_EMOJIS
from api.v1.models.report import FinalReport
from api.v1.models.responder import Responder
from api.v1.models.responder_emergency import ResponderEmergency
from api.v1.services.emergency import EmergencyService


emergency_router = APIRouter(prefix='/emergencies')

@emergency_router.api_route('/report', methods=["GET", "POST"])
@add_template_context('pages/emergency/report-emergency.html')
async def report_emergency(
    request: Request,
    pictures: Optional[List[UploadFile]]=File(None), 
    db: Session=Depends(get_db)
):
    
    current_user = request.state.current_user
     
    form = build_form(
        title='Report an Emergency',
        fields=[
            {
                'type': 'textarea',
                'label': 'Description',
                'name': 'description',
                # 'placeholder': 'e.g. An accident occured on my way to work.',
                'required': True,
            },
            {
                'type': 'select',
                'label': 'Event Type',
                'name': 'event',
                'options': [
                    {'label': 'Natural', 'value': EventType.NATURAL.value},
                    {'label': 'Fire', 'value': EventType.FIRE.value},
                    {'label': 'Medical', 'value': EventType.MEDICAL.value},
                    {'label': 'Crime', 'value': EventType.CRIME.value},
                    {'label': 'Accident', 'value': EventType.ACCIDENT.value},
                ],
                'required': True,
            },
            {
                'type': 'select',
                'label': 'Severity Level',
                'name': 'severity',
                'options': [
                    {'label': 'High', 'value': SeverityLevel.HIGH.value},
                    {'label': 'Medium', 'value': SeverityLevel.MEDIUM.value},
                    {'label': 'Low', 'value': SeverityLevel.LOW.value},
                    {'label': 'Critical', 'value': SeverityLevel.CRITICAL.value},
                    {'label': 'Severe', 'value': SeverityLevel.SEVERE.value},
                ],
                'required': True,
            }
        ],
        button_text='Report Emergency',
        action='/emergencies/report',
        enctype='multipart/form-data'
    )
    
    context = {
        'background_url': 'https://img.freepik.com/free-photo/medium-shot-firefighter-trying-put-out-wildfire_23-2151099514.jpg?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid',
        'form': form,
        'user': current_user
    }
    
    if request.method == 'POST':
        # Process the form submission
        form_data = await request.form()
        
        # Collect form fields for re-rendering
        context['form_data'] = form_data
        
        description = form_data.get('description').strip()
        event_type = form_data.get('event')
        severity_level = form_data.get('severity')
        location = form_data.get('location')
        
        # Upload pictures to firebase if there are any pictures
        picture_urls = []
        if pictures:
            print(pictures)
            for picture in pictures:
                picture_url = await FirebaseService.upload_file(
                    file=picture,
                    allowed_extensions=['jpg', 'png', 'jpeg', 'gif'],
                    upload_folder='emergencies',
                    model_id=current_user.id
                )
                if not picture_url:
                    flash(request, 'Invalid picture upload Check file extension.', MessageCategory.ERROR)
                    return RedirectResponse(url='/emergencies/report', status_code=303)
                
                picture_urls.append(picture_url)
        
        # Get relevant location data
        location_data = Location.fetch_one_by_field(
            db=db,
            city=location.split(',')[0].strip(),
            state=location.split(',')[1].strip()
        )
        
        # If location data is not found throw an error  so user selects from suggestion
        if not location_data:
            flash(
                request,
                message='Please select a valid location from the suggestions.',
                category=MessageCategory.ERROR
            )
            return context
        
        # location = f'POINT({location_data.longitude} {location_data.latitude})'  # Convert the location data to geospatial data format
        
        # Save the emergency to the database
        Emergency.create(
            db=db,
            description=description,
            event_type=event_type,
            severity=severity_level,
            location=location_data.geo_location,
            location_str=location,
            longitude=location_data.longitude,
            latitude=location_data.latitude,
            reported_by_id=current_user.id if current_user else None,
            attachments=','.join(picture_urls)
        )
        
        # Redirect to the emergency dashboard
        flash(request, 'Emergency reported successfully', MessageCategory.SUCCESS)
    
        return RedirectResponse('/dashboard', 303) if current_user else RedirectResponse('/', 303)
                
    return context


@emergency_router.get('/nearby')
@add_template_context('pages/emergency/view-emergencies.html')
async def get_nearby_incidents(
    request: Request,
    db: Session=Depends(get_db)
):
    '''Endpoint to get all emergencies'''
    
    current_user = request.state.current_user
    
    nearby_incidents = EmergencyService.get_nearby_incidents(db, request)
    
    context = {
        'background_url': 'https://img.freepik.com/free-photo/medium-shot-firefighter-trying-put-out-wildfire_23-2151099514.jpg?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid',
        'user': current_user,
        'emergencies': nearby_incidents
    }
    
    return context
    

@emergency_router.get('/')
@add_template_context('pages/emergency/emergency-list.html')
async def get_all_emergencies(
    request: Request,
    page: int = 1,
    per_page: int = 10,
    db: Session=Depends(get_db)
):
    '''Endpoint to get all emergencies'''
    
    current_user = request.state.current_user
    
    if current_user.role == 'Public':
        emergencies = Emergency.fetch_by_field(db=db, reported_by_id=current_user.id)
    else:
        emergencies = Emergency.all(db)
        
    pagination_data = paginate_items(emergencies, page, per_page)
    
    context = {
        'background_url': 'https://img.freepik.com/free-photo/medium-shot-firefighter-trying-put-out-wildfire_23-2151099514.jpg?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid',
        'user': current_user,
        'pagination_data': pagination_data,
        'emojis': EVENT_TYPE_EMOJIS
    }
    
    return context


@emergency_router.get('/{emergency_id}')
@add_template_context('pages/emergency/emergency-details.html')
async def get_single_emergency(
    request: Request,
    emergency_id: str,
    db: Session=Depends(get_db)
):
    '''Endpoint to get a single emergency by id'''
    
    current_user = request.state.current_user
    
    emergency = Emergency.fetch_by_id(db=db, id=emergency_id)
    
    context = {
        'background_url': 'https://img.freepik.com/free-photo/medium-shot-firefighter-trying-put-out-wildfire_23-2151099514.jpg?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid',
        'user': current_user,
        'emergency': emergency,
        'emojis': EVENT_TYPE_EMOJIS
    }
    
    return context


@emergency_router.post('/{emergency_id}/resolve')
async def mark_emergency_as_resolved(
    request: Request,
    emergency_id: str,
    db: Session=Depends(get_db)
):
    '''Endpoint to update agency settings'''
    
    current_user = request.state.current_user
    
    if current_user.role not in ['Responder', 'Agency admin']:
        flash(request,'Unauthorized action', MessageCategory.ERROR)
        return RedirectResponse(url='/dashboard', status_code=303)
    
    emergency = Emergency.fetch_by_id(db, id=emergency_id)
    
    if not emergency:
        flash(request, 'Emergency not found', MessageCategory.ERROR)
        return RedirectResponse(
            url=f"/responders/emergencies" if current_user.role == 'Responder' else f"/agency/emergencies",             
            status_code=303
        )
    
    emergency = Emergency.update(
        db, 
        id=emergency.id,
        status='Resolved',
    )
    
    for responder_emergency in emergency.responder_emergencies:
        # Update final report
        FinalReport.update(
            db,
            id=responder_emergency.final_report_id,
            outcome='Resolved',
            end_time=datetime.now()
        )
        
        # Update responder status to unavailable
        Responder.update(
            db, 
            id=responder_emergency.responder_id,
            status='available',
        )
        
        ResponderEmergency.update(
            db, 
            id=responder_emergency.id,
            status='Completed',
        )
    
    flash(request, f'Emergency marked as resolved', MessageCategory.SUCCESS)
    return RedirectResponse(
        url=f"/responders/emergencies" if current_user.role == 'Responder' else f"/agency/emergencies", 
        status_code=303
    )
