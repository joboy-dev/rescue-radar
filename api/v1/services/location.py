from fastapi import Depends
from geoalchemy2.functions import ST_DWithin, ST_GeogFromWKB
from sqlalchemy.orm import Session
from sqlalchemy import select

from api.db.database import get_db
from api.v1.models.location import Location
from api.utils.logger import app_logger


class LocationService:
    
    @classmethod    
    def get_nearby_locations(
        cls,
        city: str, 
        state: str, 
        km_within: int=3, 
        db: Session=Depends(get_db)
    ):
        '''Function to get nearby locations'''
        
        # Check if target city exists
        target_city = Location.fetch_one_by_field(
            db=db,
            city=city.capitalize(), 
            state=state.capitalize()
        )
        
        # If the target city is not found, return an error message
        if not target_city:
            app_logger.info(f"City '{city.capitalize()}, {state.capitalize()}' not found.")
            return []
        
        # Extract the geography of the target city
        target_geography = ST_GeogFromWKB(target_city.geo_location)
        
        # Query nearby cities within the specified distance from the target city
        nearby_cities_query = select(Location).where(
            ST_DWithin(Location.geo_location, target_geography, 1000 * km_within)
        )
        result = db.execute(nearby_cities_query)
        
        nearby_cities = [
            city.to_dict(excludes=['geo_location'])
            for city in result.scalars().all()
        ]
        
        return nearby_cities
