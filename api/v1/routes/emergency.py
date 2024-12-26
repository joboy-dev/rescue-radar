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
from api.v1.models.emergency import EventType, SeverityLevel
from api.v1.services.auth import AuthService


emergency_router = APIRouter(prefix='/emergencies')

@emergency_router.api_route('/report', methods=["GET", "POST"])
@add_template_context('pages/emergency/report-emergency.html')
async def report_emergency(
    request: Request,
    pictures: Optional[List[UploadFile]] = None, 
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
                'placeholder': 'e.g. An accident occured on my way to work.',
                'required': True,
            },
            {
                'type': 'select',
                'label': 'Event Type',
                'name': 'event',
                'options': [
                    {'label': 'Natural', 'value': EventType.NATURAL},
                    {'label': 'Fire', 'value': EventType.FIRE},
                    {'label': 'Medical', 'value': EventType.MEDICAL},
                    {'label': 'Crime', 'value': EventType.CRIME},
                    {'label': 'Accident', 'value': EventType.ACCIDENT},
                ],
                'required': True,
            },
            {
                'type': 'select',
                'label': 'Severity Level',
                'name': 'severity',
                'options': [
                    {'label': 'High', 'value': SeverityLevel.HIGH},
                    {'label': 'Medium', 'value': SeverityLevel.MEDIUM},
                    {'label': 'Low', 'value': SeverityLevel.LOW},
                    {'label': 'Critical', 'value': SeverityLevel.CRITICAL},
                    {'label': 'Severe', 'value': SeverityLevel.SEVERE},
                ],
                'required': True,
            },
            {
                'type': 'text',
                'label': 'Location',
                'name': 'location',
                'placeholder': 'e.g. Ikeja, Lagos',
                'required': True,
            }
        ],
        button_text='Report Emergency',
        action='/emergencies/report'
    )
    
    context = {
        'background_url': 'https://img.freepik.com/free-photo/medium-shot-firefighter-trying-put-out-wildfire_23-2151099514.jpg?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid',
        'form': form,
        'user': current_user
    }
    
    if request.method == 'POST':
        pass
    
    return context