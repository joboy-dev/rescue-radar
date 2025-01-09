import json
import pprint
from typing import Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from api.core.dependencies.context import add_template_context
from api.core.dependencies.flash_messages import MessageCategory, flash
from api.core.dependencies.form_builder import build_form
from api.db.database import get_db
from api.utils.paginator import paginate_items
from api.v1.models.emergency import EVENT_TYPE_EMOJIS
from api.v1.models.location import EmergencyLocation
from api.v1.services.auth import AuthService


external_router = APIRouter()

@external_router.get('/')
@add_template_context('pages/external/index.html')
async def home(
    request: Request,
    # unauthenticated = Depends(AuthService.unauthenticated_only)
):
    # if isinstance(unauthenticated, RedirectResponse):
    #     return unauthenticated 
    
    benefits = [
        {
            "icon": "https://cdn-icons-png.freepik.com/256/6699/6699339.png?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid",
            "title": "Real-Time Emergency Reporting",
            "description": "Easily report incidents from anywhere with location-based reporting. Whether it's a fire, accident, or medical emergency, Rescue Radar ensures help is on the way with just a few taps."
        },
        {
            "icon": "https://cdn-icons-png.freepik.com/256/16267/16267648.png?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid",
            "title": "Live Tracking and Instant Notifications",
            "description": "Stay informed every step of the way. Receive real-time updates and track responder arrival, so you know exactly when help will arrive."
        },
        {
            "icon": "https://cdn-icons-png.freepik.com/256/1055/1055644.png?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid",
            "title": "Transparent Reporting",
            "description": "Receive real-time updates on emergencies, helping you make informed decisions."
        },
        {
            "icon": "https://cdn-icons-png.freepik.com/256/17305/17305214.png?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid",
            "title": "Resource Management at its Best",
            "description": "From ambulances to fire trucks, our system ensures that the right resources are deployed quickly and efficiently for every emergency."
        },
        {
            "icon": "https://cdn-icons-png.freepik.com/256/13632/13632808.png?uid=R65046554&ga=GA1.1.2092350398.1730195801&semt=ais_hybrid",
            "title": "Trusted Responder Network",
            "description": "Connect with verified responders and agencies in your area. We work with local agencies and responders dedicated to your safety."
        },
    ]
    
    how_it_works = [
        {
            "title": "Report",
            "description": "Quickly report an emergency and specify the type of assistance needed."
        },
        {
            "title": "Connect",
            "description": "Our system connects you with the nearest responders and assigns resources for immediate assistance."
        },
        {
            "title": "Track",
            "description": "Stay updated with live location tracking, ETA, and emergency status notifications."
        },
        {
            "title": "Stay Safe",
            "description": "Rescue Radar prioritizes your safety by providing the tools you need to handle emergencies confidently."
        }
    ]

    features = [
        # {
        #     "title": "AI-Driven Emergency Analysis",
        #     "description": "Our AI system analyzes emergency reports for optimal response strategies, ensuring quick and effective solutions."
        # },
        {
            "title": "Secure Real-Time Communication",
            "description": "In-app messaging allows you to communicate securely with responders, giving you peace of mind in emergencies."
        },
        {
            "title": "Location-Based Notifications",
            "description": "Receive automatic alerts if an emergency occurs near you, keeping you and your loved ones informed."
        },
        {
            "title": "Resource and Responder Tracking",
            "description": "From dispatch to arrival, track responders and resources in real-time to know when help will arrive."
        }
    ]
    
    return {
        'benefits': benefits,
        'how_it_works': how_it_works,
        'features': features
    }

@external_router.get('/about')
@add_template_context('pages/external/about.html')
async def about(request: Request):
    return {}


@external_router.get('/contact')
@add_template_context('pages/external/contact.html')
async def contact(request: Request):
    
    form = build_form(
        title='Contact us',
        fields=[
            {
                'type': 'text',
                'label': 'Name',
                'name': 'name',
                'placeholder': 'e.g. John Doe',
                'required': True,
            },
            {
                'type': 'text',
                'label': 'Phone Number',
                'name': 'phone',
                'placeholder': 'e.g. 08012345678',
                'required': False,
            },
            {
                'type': 'email',
                'label': 'Email',
                'name': 'email',
                'placeholder': 'e.g. john.doe@gmail.com',
                'required': True,
            },
            {
                'type': 'textarea',
                'label': 'Message',
                'name': 'message',
                'required': True,
            }
        ],
        button_text='Send Message',
        action='/contact'
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
        
        message = form_data.get('message').strip()
        name = form_data.get('name')
        email = form_data.get('email')
        phone_number = form_data.get('phone')
    
    return context


@external_router.get('/resources')
@add_template_context('pages/external/resources/resources.html')
async def resources(
    request: Request, 
    search: Optional[str] = None,
    page: int = 1,
    per_page: int = 10,
):
    '''Endpoint to load all resources'''
    
    current_user = request.state.current_user
    
    with open('api/core/dependencies/data/articles.json', 'r') as f:
        resources = json.load(f)
    
    if search:
        results = [res for res in resources if search.lower() in res['title'].lower()]
        resources = results
    
    # paginate
    pagination_data = paginate_items(resources, page, per_page)
    
    return {
        'pagination_data': pagination_data,
        'emojis': EVENT_TYPE_EMOJIS,
        'user': current_user
    }


@external_router.get('/resources/search')
# @add_template_context('pages/external/resources.html')
async def search_resources(request: Request, title: str):
    '''Endpoint to load all resources'''
    
    current_user = request.state.current_user
    
    with open('api/core/dependencies/data/articles.json', 'r') as f:
        resources = json.load(f)
    
    results = [res for res in resources if title.lower() in res['title'].lower()]
    
    return results


@external_router.get('/resources/emergency-contacts')
@add_template_context('pages/external/resources/emergency-contacts.html')
async def emergency_contacts(
    request: Request,
    page: int = 1,
    per_page: int = 10,
):
    '''Endpoint to load all emergency contacts'''
    
    current_user = request.state.current_user
    
    with open('api/core/dependencies/data/emergency_contacts.json', 'r') as f:
        emergency_contacts = json.load(f)
    
    pagination_data = paginate_items(emergency_contacts, page, per_page)
        
    return {
        'pagination_data': pagination_data,
        'user': current_user
    }


@external_router.get('/resources/emergency-locations')
@add_template_context('pages/external/resources/emergency-locations.html')
async def emergency_locations(
    request: Request, 
    db: Session=Depends(get_db),
    page: int = 1,
    per_page: int = 10,
):
    '''Endpoint to load all emergency locations'''
    
    current_user = request.state.current_user
    
    emergency_locations = EmergencyLocation.all(db, sort_by='state', order='asc')
    pagination_data = paginate_items(emergency_locations, page, per_page)
        
    return {
        'pagination_data': pagination_data,
        'user': current_user
    }
  
  
@external_router.get('/resources/emergency-locations/{location_id}')
@add_template_context('pages/external/resources/emergency-location-details.html')
async def get_single_emergency_location(
    request: Request, 
    location_id: str, 
    db: Session=Depends(get_db)
):
    '''Endpoint to lget a single location data'''
    
    current_user = request.state.current_user
    
    location = EmergencyLocation.fetch_by_id(db, id=location_id)
    
    if location is None:
        flash(request, 'Location not found', MessageCategory.ERROR)
        return RedirectResponse(url='/resources/emergency-locations')
        
    return {
        'location': location,
        'user': current_user
    }
      

@external_router.get('/resources/{url_slug}')
@add_template_context('pages/external/resources/resource-detail.html')
async def get_single_resource(request: Request, url_slug: str):
    '''Endpoint to load all resources'''
    
    current_user = request.state.current_user
    
    with open('api/core/dependencies/data/articles.json', 'r') as f:
        resources = json.load(f)
    
    res = None
    for resource in resources:
        if resource['url_slug'] == url_slug:
            res = resource
            break
    
    if res is None:
        flash(request, 'Resource not found', MessageCategory.ERROR)
        return RedirectResponse(url='/resources')
        
    return {
        'resource': res,
        'emojis': EVENT_TYPE_EMOJIS,
        'user': current_user
    }
