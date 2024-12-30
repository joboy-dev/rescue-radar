from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from api.core.dependencies.context import add_template_context
from api.core.dependencies.form_builder import build_form
from api.core.dependencies.flash_messages import flash, MessageCategory
from api.db.database import get_db
from api.utils.location import get_ip_info
from api.v1.models.agency import Agency
from api.v1.models.location import Location
from api.v1.models.profile import Profile
from api.v1.models.responder import Responder
from api.v1.models.user import User
from api.v1.services.auth import AuthService


auth_router = APIRouter()

@auth_router.api_route('/login', methods=["GET", "POST"])
@add_template_context('pages/auth/login.html')
async def login(request: Request, db: Session = Depends(get_db)):
    '''Endpoint to log in a user'''
    
    form = build_form(
        title='Login',
        subtitle='Log In to Stay Protected, Anytime, Anywhere.',
        fields=[
            {
                'type': 'email',
                'label': 'Email',
                'name': 'email',
                'placeholder': 'e.g. john.doe@example.com',
                'required': True
            },
            {
                'type': 'password',
                'label': 'Password',
                'name': 'password',
                'placeholder': 'e.g. Password123',
                'required': True
            }
        ],
        button_text='Login',
        action='/login'
    )
    
    context = {
        'background_url': 'https://img.freepik.com/premium-photo/dedicated-emergency-paramedic-ready-urgent-response_100209-13194.jpg?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid',
        'form': form
    }
    
    if request.method == 'POST':
        # Process the form submission
        form_data = await request.form()
        
        # Collect form fields for re-rendering
        context['form_data'] = form_data
        
        # Example validation or processing of form_data
        email = form_data.get('email')
        password = form_data.get('password')
        
        try:
            user = AuthService.authenticate_user(db=db, email=email, password=password)
            
            access_token = AuthService.create_access_token(db=db,user_id=user.id)
            refresh_token = AuthService.create_refresh_token(db=db, user_id=user.id)

            response = RedirectResponse(url="/dashboard", status_code=303)
            
            if not user.role:
                flash(request, 'Select a role', MessageCategory.INFO)
                response =  RedirectResponse(url="/select-role", status_code=303)
            
            if user.role == 'Agency admin':
                # Get user agency
                agency = Agency.fetch_one_by_field(db, creator_id=user.id)
                
                if not agency.location_str:
                    flash(request, 'Update your location details', MessageCategory.INFO)
                    response =  RedirectResponse(url="/agency/add-location", status_code=303)
                else:
                    response =  RedirectResponse(url="/agency/dashboard", status_code=303)
            
            elif user.role == 'Responder':
                response =  RedirectResponse(url="/responders/dashboard", status_code=303)
                
            response.set_cookie(key="access_token", value=access_token, httponly=True)
            response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
            
            flash(request, 'Logged in successfully', MessageCategory.SUCCESS)
            return response
            
        except HTTPException as e:
            flash(request, e.detail, MessageCategory.ERROR)
            return context
    
    return context


@auth_router.api_route('/signup', methods=["GET", "POST"])
@add_template_context('pages/auth/signup.html')
async def signup(request: Request, db: Session = Depends(get_db)):   
    '''Endpoint to sign up a user'''
     
    form = build_form(
        title='Sign Up',
        subtitle='Empowering You with Instant Access to Safety Resources',
        fields=[
            {
                'type': 'email',
                'label': 'Email',
                'name': 'email',
                'placeholder': 'e.g. john.doe@example.com',
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
        button_text='Sign Up',
        action='/signup'
    )
    
    context = {
        'background_url': 'https://img.freepik.com/free-photo/medium-shot-firefighter-trying-put-out-wildfire_23-2151099514.jpg?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid',
        'form': form
    }
    
    if request.method == 'POST':
        # Process the form submission
        form_data = await request.form()
        
        # Collect form fields for re-rendering
        context['form_data'] = form_data
        
        # Example validation or processing of form_data
        email = form_data.get('email')
        password = form_data.get('password')
        confirm_password = form_data.get('confirm-password')
        
        if password != confirm_password:
            flash(request, 'Passwords do not match', MessageCategory.ERROR)
            return context

        # Check if user amready exists
        existing_user = User.fetch_one_by_field(db=db, email=email)
        if existing_user:
            flash(request, 'Email address already in use. Try another email', MessageCategory.ERROR)
            return context

        # Hash the password
        hashed_password = AuthService.hash_password(password)
        
        # Create user
        new_user = User.create(
            db=db,
            email=email,
            password=hashed_password,
            role=None
        )
        
        # Create profile for user
        Profile.create(db=db, user_id=new_user.id)
        
        # Create access token and store in cookies
        access_token = AuthService.create_access_token(db=db, user_id=new_user.id)
        refresh_token = AuthService.create_refresh_token(db=db, user_id=new_user.id)
        
        response = RedirectResponse(url="/select-role", status_code=303)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        
        flash(request, 'Account created successfully', MessageCategory.SUCCESS)
        # Redirect after successful signup
        return response
    
    return context


@auth_router.api_route('/select-role', methods=["GET", "POST"])
@add_template_context('pages/auth/select-role.html')
async def select_role(request: Request, db: Session = Depends(get_db)):
    '''Endpoint for a user to seect thie role in the system'''
    
    form = build_form(
        title='Select Role',
        subtitle=f'Welcome {request.state.current_user.email}. Who will you be signing up as?',
        fields=[],
        button_text='Proceed',
        action='/select-role'
    )
    
    roles = [
        {
            'icon': 'https://cdn-icons-png.freepik.com/256/7977/7977760.png?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid',
            'name': 'User',
            'value': 'Public'
        },
        {
            'icon': 'https://cdn-icons-png.freepik.com/256/979/979993.png?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid',
            'name': 'Responder',
            'value': 'Responder'
        },
        {
            'icon': 'https://cdn-icons-png.freepik.com/256/16321/16321194.png?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid',
            'name': 'Agency',
            'value': 'Agency admin'
        },
    ]
    
    context = {
        'background_url': 'https://img.freepik.com/premium-photo/portrait-african-male-paramedic-front-ambulance_629685-27281.jpg?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid',
        'form': form,
        'roles': roles,
        'user': request.state.current_user
    }
    
    if request.method == 'POST':
        # Process the form submission
        form_data = await request.form()
        
        role = form_data.get('role')
        
        user = User.update(db, request.state.current_user.id, role=role)
        
        flash(request, f'Role set to {user.role}', MessageCategory.SUCCESS) 
               
        # Create profiles based in roles
        if user.role == 'Responder':
            # Get ip info
            location = get_ip_info(request)
            Responder.create(
                db=db,
                user_id=user.id,
                latitude=location['latitude'],
                longitude=location['longitude'],
                location=from_shape(Point(location['latitude'], location['longitude']))
            )
            return RedirectResponse(url="/responders/dashboard", status_code=303)
        elif user.role == 'Agency admin':
            Agency.create(
                db=db,
                creator_id=user.id
            )
            return RedirectResponse(url="/agency/add-location", status_code=303)
        
        return RedirectResponse(url="/dashboard", status_code=303)
    
    return context


@auth_router.api_route('/agency/add-location', methods=["GET", "POST"])
@add_template_context('pages/auth/set-agency-location.html')
async def set_agency_location(request: Request, db: Session = Depends(get_db)):
    '''Endpoint for a user to seect thie role in the system'''
    
    current_user = request.state.current_user
    
    form = build_form(
        title='Set Agency Location',
        subtitle=f'Welcome {current_user.email}. Set agency location before proceeding',
        fields=[],
        button_text='Save',
        action='/agency/add-location'
    )
    
    context = {
        'background_url': 'https://img.freepik.com/premium-photo/portrait-african-male-paramedic-front-ambulance_629685-27281.jpg?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid',
        'form': form,
        'user': current_user
    }
    
    if request.method == 'POST':
        # Process the form submission
        form_data = await request.form()
        
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
            return context
        
        agency = Agency.fetch_one_by_field(db, creator_id=current_user.id)
        
        Agency.update(
            db, 
            id=agency.id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            location_str=location,
            location=location_data.geo_location
        )
        
        flash(request, f'Agency location updated', MessageCategory.SUCCESS)
        return RedirectResponse(url=f"/agency/dashboard", status_code=303)
        
    return context


@auth_router.api_route('/logout', methods=["GET", "POST"])
async def logout(request: Request):
    '''Endpoint to logout the user'''
    
    # access_token = request.cookies.get("access_token")
    # if access_token:
    #     # Revoke the access token
    #     AuthService.revoke_token(access_token, current_user.id)
    
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response
