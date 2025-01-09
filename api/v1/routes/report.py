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
from api.v1.services.agency import AgencyService
from api.v1.services.emergency import EmergencyService


report_router = APIRouter(prefix='/reports')


@report_router.get('/')
@add_template_context('pages/report/report-list.html')
async def get_all_reports(
    request: Request,
    page: int = 1,
    per_page: int = 10,
    db: Session=Depends(get_db)
):
    '''Endpoint to get all emergencies'''
    
    current_user = request.state.current_user
    
    if current_user.role not in ['Responder', 'Agency admin']:
        flash(request,'Unauthorized action', MessageCategory.ERROR)
        return RedirectResponse(url='/dashboard', status_code=303)
    
    if current_user.role == 'Responder':
        # Get responder
        responder = Responder.fetch_one_by_field(db=db, user_id=current_user.id)
        
        query = (
            db.query(FinalReport)
            .join(ResponderEmergency, ResponderEmergency.final_report_id == FinalReport.id)
            .filter(ResponderEmergency.responder_id == responder.id)
        )
        reports = query.all()
        
    else:
        agency_details = AgencyService.get_agency_full_details(db, current_user)  
        # Get reports for agency
        reports = agency_details['reports']
    
    pagination_data = paginate_items(reports, page, per_page)
    
    context = {
        'user': current_user,
        'pagination_data': pagination_data,
        'emojis': EVENT_TYPE_EMOJIS
    }
    
    return context


@report_router.get('/{report_id}')
@add_template_context('pages/report/report-details.html')
async def get_report_details(
    request: Request,
    report_id: str,
    db: Session=Depends(get_db)
):
    '''Endpoint to get a single report by id'''
    
    current_user = request.state.current_user
    
    report = FinalReport.fetch_by_id(db=db, id=report_id)
    
    context = {
        'user': current_user,
        'report': report,
        'emojis': EVENT_TYPE_EMOJIS
    }
    
    return context


@report_router.api_route('/{report_id}/update', methods=["GET", "POST"])
@add_template_context('pages/report/update-report.html')
async def update_report(
    request: Request,
    report_id: str,
    db: Session=Depends(get_db)
):
    
    current_user = request.state.current_user
    
    redirect_dashboard = '/dashboard' if current_user.role == 'Public' else '/agency/dashboard'
    
    if current_user.role != 'Responder':
        flash(request,'Unauthorized action', MessageCategory.ERROR)
        return RedirectResponse(
            url=redirect_dashboard, 
            status_code=303
        )
    
    report = FinalReport.fetch_by_id(db=db, id=report_id)
    responder = Responder.fetch_one_by_field(db=db, user_id=current_user.id)
    
    context = {
        'report': report,
        'user': current_user
    }
    
    if request.method == 'POST':
        # Process the form submission
        form_data = await request.form()
        
        # Collect form fields for re-rendering
        context['form_data'] = form_data
        
        description = form_data.get('description').strip()
        comments = form_data.get('comments').strip()
        
        responder_ids = [responder_emergency.responder_id for responder_emergency in report.responders]
        
        if responder.id not in responder_ids:
            # flash error
            flash(request, 'You are not assigned to this report', MessageCategory.ERROR)
            return RedirectResponse(url='/reports', status_code=303)
        
        # Update the report in the database
        FinalReport.update(
            db, 
            id=report_id, 
            description=description, 
            comments=comments
        )
        
        # Redirect to the emergency dashboard
        flash(request, 'Report updated successfully', MessageCategory.SUCCESS)
    
        return RedirectResponse('/reports', 303)
                
    return context
