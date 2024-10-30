from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from api.core.dependencies.context import add_template_context
from api.core.dependencies.form_builder import build_form
from api.v1.schemas import user as user_schemas


auth_router = APIRouter()

@auth_router.api_route('/login', methods=["GET", "POST"])
@add_template_context('pages/auth/login.html')
async def login(request: Request, schema: user_schemas.Login):
    form = build_form(
        title='Login',
        subtitle='Log In to Stay Protected, Anytime, Anywhere.',
        fields=[
            {
                'type': 'email',
                'label': 'Email',
                'name': 'email',
                'required': True
            },
            {
                'type': 'password',
                'label': 'Password',
                'name': 'password',
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
        pass
    
    return context


@auth_router.api_route('/signup', methods=["GET", "POST"])
@add_template_context('pages/auth/signup.html')
async def signup(request: Request):
    form = build_form(
        title='Sign Up',
        subtitle='Empowering You with Instant Access to Safety Resources',
        fields=[
            {
                'type': 'email',
                'label': 'Email',
                'name': 'email',
                'required': True
            },
            {
                'type': 'password',
                'label': 'Password',
                'name': 'password',
                'required': True
            },
            {
                'type': 'password',
                'label': 'Confirm Password',
                'name': 'confirm-password',
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
        
        print(context['form_data'], email, password)
        
        if password != confirm_password:
            context["error"] = "Passwords do not match."
            return context  # Re-render form with error message

        # Redirect after successful signup
        return RedirectResponse(url="/select-role", status_code=303)
    
    return context


@auth_router.api_route('/select-role', methods=["GET", "POST"])
@add_template_context('pages/auth/select-role.html')
async def select_role(request: Request):
    form = build_form(
        title='Select Role',
        subtitle='Who will you be signing up as?',
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
        'roles': roles
    }
    
    if request.method == 'POST':
        # Process the form submission
        form_data = await request.form()
        
        role = form_data.get('role')
        
        print(role)

        # Redirect after successful signup
        return RedirectResponse(url="/login", status_code=303)
    
    return context


# @auth_router.api_route('/logout', methods=["GET", "POST"])
@auth_router.post('/logout')
# @add_template_context('pages/auth/signup.html')
async def logout(request: Request):
    # context = {
    #     'background_url': 'https://img.freepik.com/free-photo/medium-shot-firefighter-trying-put-out-wildfire_23-2151099514.jpg?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid'
    # }
    
    # if request.method == 'POST':
    #     pass
    
    # return context
    
    pass

