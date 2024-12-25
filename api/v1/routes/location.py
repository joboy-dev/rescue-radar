from typing import List, Optional
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from geoalchemy2.functions import ST_DWithin, ST_GeogFromWKB

from api.core.dependencies.context import add_template_context
from api.core.dependencies.form_builder import build_form
from api.core.dependencies.flash_messages import flash, MessageCategory
from api.v1.models.location import Location
from api.v1.schemas.location import LocationBase
from api.v1.services.auth import AuthService


location_router = APIRouter(prefix='/locations')

@location_router.get('/search', response_model=List[LocationBase])
# @add_template_context('pages/location/search-locations.html')
async def search_locations(request: Request, city: str, state: str):
    '''Endpoint to search for locations'''
    
    locations = Location.search(
        search_fields= {
            'city': city,
            'state': state
        },
        per_page=100000
    )
    
    return locations


@location_router.get('/nearby', response_model=List[LocationBase])
# @add_template_context('pages/location/search-locations.html')
async def get_nearby_locations(
    request: Request, 
    city: str, 
    state: str, 
    km_within: int=3
):
    '''Endpoint to get nearby locations'''
    
    # Check if target city exists
    target_city = Location.fetch_one_by_field(city=city, state=state)
    
    # If the target city is not found, return an error message
    if not target_city:
        raise HTTPException(
            status=404,
            detail="City with provided details was not found",
        )
    
    # Extract the geography of the target city
    target_geography = ST_GeogFromWKB(target_city.geo_location)
    
    
    
    
