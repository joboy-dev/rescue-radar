from typing import List, Optional
from fastapi import APIRouter, File, HTTPException, Request, UploadFile, Depends

from sqlalchemy.orm import Session
from sqlalchemy import and_, select

from api.core.dependencies.context import add_template_context
from api.core.dependencies.form_builder import build_form
from api.core.dependencies.flash_messages import flash, MessageCategory
from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.location import Location
from api.v1.schemas.location import LocationBase
from api.v1.services.location import LocationService
from api.v1.services.auth import AuthService


location_router = APIRouter(prefix='/locations')

@location_router.get('/search', response_model=List[LocationBase])
# @add_template_context('pages/location/search-locations.html')
async def search_locations(request: Request, city: str, state: str, db: Session=Depends(get_db)):
    '''Endpoint to search for locations'''
    
    locations = Location.search(
        db=db,
        search_fields= {
            'city': city,
            'state': state
        },
        per_page=100000
    )
    
    return locations


@location_router.get('/nearby')
# @add_template_context('pages/location/search-locations.html')
async def get_nearby_locations(
    request: Request, 
    city: str, 
    state: str, 
    km_within: int=3, 
    db: Session=Depends(get_db)
):
    '''Endpoint to get nearby locations'''
    
    nearby_cities = LocationService.get_nearby_locations(city, state, km_within, db=db)
    return nearby_cities
