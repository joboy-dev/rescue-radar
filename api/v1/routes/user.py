from fastapi import APIRouter, File, HTTPException, Request, UploadFile, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import json

from api.core.dependencies.context import add_template_context
from api.core.dependencies.form_builder import build_form
from api.core.dependencies.flash_messages import flash, MessageCategory
from api.db.database import get_db
from api.utils.firebase_service import FirebaseService
from api.v1.models.emergency import Emergency, EVENT_TYPE_EMOJIS
from api.v1.models.location import EmergencyLocation
from api.v1.models.profile import Profile
from api.v1.models.user import User
from api.v1.services.auth import AuthService
from api.v1.services.emergency import EmergencyService


user_router = APIRouter()

@user_router.get('/dashboard')
@add_template_context('pages/user/dashboards/dashboard.html')
async def dashboard(request: Request, db: Session=Depends(get_db)):
    
    current_user = request.state.current_user
    
    emergency_locations = EmergencyService.get_emergency_locations(db)
    nearby_incidents = EmergencyService.get_nearby_incidents(db, request)
    if current_user.role == 'Public':
        emergencies = Emergency.fetch_by_field(db=db, reported_by_id=current_user.id)
    else:
        emergencies = Emergency.all(db)
        
    with open('api/core/dependencies/data/articles.json', 'r') as f:
        resources = json.load(f)
    
    with open('api/core/dependencies/data/emergency_contacts.json', 'r') as f:
        emergency_contacts = json.load(f)
        
    return {
        'user': current_user,
        'emergency_locations': json.dumps(emergency_locations),
        'nearby_incidents': nearby_incidents,
        'emergencies': emergencies,
        'emojis': EVENT_TYPE_EMOJIS,
        'resources': resources,
        'emergency_contacts': emergency_contacts
    }


@user_router.get('/profile')
@add_template_context('pages/user/profile/profile.html')
async def profile(request: Request):
    return {'user': request.state.current_user}


@user_router.api_route('/profile/edit', methods=["GET", "POST"])
@add_template_context('pages/user/profile/edit-profile.html')
async def edit_profile(request: Request, db: Session=Depends(get_db)):   
    '''Endpoint to edit a user's profile'''
    
    current_user = request.state.current_user
     
    form = build_form(
        title='Edit your Profile',
        fields=[
            {
                'type': 'text',
                'label': 'Username',
                'name': 'username',
                'placeholder': 'e.g. johndoe35',
                'required': False,
                'value': current_user.profile.username if current_user.profile else None
            },
            {
                'type': 'text',
                'label': 'First name',
                'name': 'first-name',
                'placeholder': 'e.g. John',
                'required': False,
                'value': current_user.profile.first_name if current_user.profile else None
            },
            {
                'type': 'text',
                'label': 'Last name',
                'name': 'last-name',
                'placeholder': 'e.g. Doe',
                'required': False,
                'value': current_user.profile.last_name if current_user.profile else None
            },
            {
                'type': 'text',
                'label': 'Phone number',
                'name': 'phone',
                'placeholder': 'e.g. 08012345678',
                'required': False,
                'min_length': 11,
                'value': current_user.profile.phone_number if current_user.profile else None
            }
        ],
        button_text='Save changes',
        action='/profile/edit'
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
        
        # Update user profile with form data
        username = form_data.get('username')
        first_name = form_data.get('first-name')
        last_name = form_data.get('last-name')
        phone_number = form_data.get('phone')
        
        print(username, first_name, last_name, phone_number)
        
        # Check if the username is already taken by another user
        existing_profile = Profile.fetch_one_by_field(db=db, username=username)
        if existing_profile and existing_profile.id != current_user.profile.id:
            flash(request, 'Username already in use', MessageCategory.ERROR)
            return context
        
        if not current_user.profile:
             Profile.create(
                db=db,
                user_id=current_user.id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number
            )
        
        else:
             Profile.update(
                db=db,
                id=current_user.profile.id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number
            )
        
        flash(request, 'Profile updated successfully', MessageCategory.SUCCESS)
        return RedirectResponse('/profile', status_code=303)
    
    return context



@user_router.api_route('/profile/change-password', methods=["GET", "POST"])
@add_template_context('pages/user/profile/change-password.html')
async def change_password(request: Request, db: Session=Depends(get_db)):   
    '''Endpoint to change a user's password'''
    
    current_user = request.state.current_user
     
    form = build_form(
        title='Change Password',
        fields=[
            {
                'type': 'email',
                'label': 'Email',
                'name': 'email',
                'placeholder': 'e.g. john.doe@example.com',
                'required': True,
                'readonly': True,
                'value': current_user.email
            },
            {
                'type': 'password',
                'label': 'Old password',
                'name': 'old-password',
                'placeholder': 'e.g. Password123',
                'required': True
            },
            {
                'type': 'password',
                'label': 'Password',
                'name': 'password',
                'placeholder': 'e.g. Password123',
                'required': True
            },
            {
                'type': 'password',
                'label': 'Confirm Password',
                'name': 'confirm-password',
                'placeholder': 'e.g. Password123',
                'required': True
            }
        ],
        button_text='Save changes',
        action='/profile/change-password'
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
        
        # Example validation or processing of form_data
        email = form_data.get('email')
        old_password = form_data.get('old-password')
        password = form_data.get('password')
        confirm_password = form_data.get('confirm-password')
        
        if password != confirm_password:
            flash(request, 'New passwords do not match', MessageCategory.ERROR)
            return context
        
        if password == old_password:
            flash(request, 'Old and new password cannot be the same', MessageCategory.ERROR)
            return context
        
        # Authenticate user with provided credentials
        try:
            AuthService.authenticate_user(email, old_password)
        except HTTPException as e:
            flash(request, 'Old password is incorrect', MessageCategory.ERROR)
            return context
    
        # Hash the password
        hashed_password = AuthService.hash_password(password)
        
        # Update user password
        User.update(db=db, id=current_user.id, password=hashed_password)
        flash(request, 'Password changed successfully', MessageCategory.SUCCESS)
        return RedirectResponse(url="/profile", status_code=303)
    
    return context



@user_router.api_route('/profile/upload-picture', methods=["POST"])
async def update_profile_picture(
    request: Request, 
    picture: UploadFile, 
    db: Session=Depends(get_db)
):
    '''Endpoint to update user profile picture'''
    
    current_user = request.state.current_user
    profile = Profile.fetch_one_by_field(db=db, user_id=current_user.id)
    
    picture_url = await FirebaseService.upload_file(
        file=picture,
        allowed_extensions=['jpg', 'png', 'jpeg', 'gif'],
        upload_folder='users',
        model_id=current_user.id
    )
    
    if not picture_url:
        flash(request, 'Invalid picture upload. Check file extension.', MessageCategory.ERROR)
        return RedirectResponse(url='/profile', status_code=303)
                
    Profile.update(db=db, id=profile.id, profile_picture=picture_url)
    
    flash(request, 'Picture updated successfully', MessageCategory.SUCCESS)
    
    return RedirectResponse('/profile', 303)
    