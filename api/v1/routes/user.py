from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from api.core.dependencies.context import add_template_context
from api.core.dependencies.form_builder import build_form
from api.core.dependencies.flash_messages import flash, MessageCategory
from api.v1.models.profile import Profile
from api.v1.models.user import User
from api.v1.services.auth import AuthService


user_router = APIRouter()

@user_router.get('/dashboard')
@add_template_context('pages/user/dashboards/dashboard.html')
async def dashboard(request: Request):
    return {'user': request.state.current_user}


@user_router.get('/profile')
@add_template_context('pages/user/profile/profile.html')
async def profile(request: Request):
    return {'user': request.state.current_user}


@user_router.api_route('/profile/edit', methods=["GET", "POST"])
@add_template_context('pages/user/profile/edit-profile.html')
async def edit_profile(request: Request):   
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
        existing_profile = Profile.fetch_one_by_field(username=username)
        if existing_profile and existing_profile.id != current_user.profile.id:
            flash(request, 'Username already in use', MessageCategory.ERROR)
            return context
        
        if not current_user.profile:
             Profile.create(
                user_id=current_user.id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number
            )
        
        else:
             Profile.update(
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
async def change_password(request: Request):   
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
        User.update(current_user.id, password=hashed_password)
        flash(request, 'Password changed successfully', MessageCategory.SUCCESS)
        return RedirectResponse(url="/profile", status_code=303)
    
    return context

