from typing import List, Optional
from fastapi import APIRouter, File, HTTPException, Request, UploadFile, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from api.core.dependencies.context import add_template_context
from api.core.dependencies.form_builder import build_form
from api.core.dependencies.flash_messages import flash, MessageCategory
from api.db.database import get_db
from api.utils.firebase_service import FirebaseService
from api.v1.models.notification import Notification
from api.v1.models.emergency import EVENT_TYPE_EMOJIS


notification_router = APIRouter(prefix='/notifications')

@notification_router.get('/')
@add_template_context('pages/user/general/notifications.html')
async def notifications(
    request: Request,
    db: Session = Depends(get_db),
):
    '''Endpoint to get all notifications for the authenticated user'''
    
    current_user = request.state.current_user
    
    # Fetch notifications for the current user
    notifications = Notification.fetch_by_field(
        db=db,
        target_user_id=current_user.id,
        is_read=False,
    )
    
    return {
        'user': current_user,
        'notifications': notifications,
        'emojis': EVENT_TYPE_EMOJIS,  # Emoji for event types
    }
    

@notification_router.post('/{notification_id}/mark-as-read')
async def mark_notification_as_read(
    request: Request,
    notification_id: str,
    db: Session = Depends(get_db)
):
    '''Endpoint to mark a notification as read'''
    
    current_user = request.state.current_user
    
    # Fetch the notification to be marked as read
    notification = Notification.update(db=db, id=notification_id, is_read=True)
    
    if not notification:
        flash(request, 'Notification not found.', MessageCategory.ERROR)
    
    if notification.target_user_id != current_user.id:
        flash(request, 'You do not have permission to mark this notification as read.', MessageCategory.ERROR)
    
    flash(request, 'Notification marked as read.', MessageCategory.SUCCESS)
    return RedirectResponse(url='/notifications', status_code=303)


@notification_router.post('/mark-all-as-read')
async def mark_all_notifications_as_read(
    request: Request,
    db: Session = Depends(get_db)
):
    '''Endpoint to mark all notifications as read'''
    
    current_user = request.state.current_user
    
    # Fetch all notifications for the current user
    notifications = Notification.fetch_by_field(
        db=db,
        target_user_id=current_user.id,
        is_read=False,
    )
    
    if not notifications:
        flash(request, 'No unread notifications found.', MessageCategory.INFO)
        return RedirectResponse(url='/notifications', status_code=303)
    
    for notification in notifications:
        Notification.update(db=db, id=notification.id, is_read=True)
    
    flash(request, 'All notifications have been marked as read.', MessageCategory.SUCCESS)
    return RedirectResponse(url='/notifications', status_code=303)
    
