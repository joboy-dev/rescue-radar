from api.utils.location import get_ip_info
from api.v1.models.emergency import Emergency
from api.v1.models.location import EmergencyLocation
from api.v1.services.location import LocationService


class EmergencyService:
    
    @classmethod
    def get_emergency_locations(cls, db):
        emergency_locations = EmergencyLocation.all(db=db, per_page=1000000)        
        # Convert each object to a dictionary (assuming the object has these attributes)
        serialized_locations = [
            {
                "id": loc.id,
                "name": loc.name,
                "city": loc.city,
                "state": loc.state,
                "geo_location": [loc.latitude, loc.longitude],
            }
            for loc in emergency_locations
        ]
        
        return serialized_locations

    @classmethod
    def get_nearby_incidents(cls, db, request):
        
        location_info = get_ip_info(request)
        
        nearby_locations = LocationService.get_nearby_locations(
            city=location_info['city'], 
            state=location_info['region'], 
            km_within=3, 
            db=db
        )
        
        nearby_incidents = []
        
        if nearby_locations:
            for loc in nearby_locations:
                emergency = Emergency.fetch_one_by_field(
                    db=db,
                    location_str=f"{loc['city']}, {loc['state']}",
                )
                if not emergency:
                    continue
                
                nearby_incidents.append(emergency.to_dict(excludes=['location']))
            
        return nearby_incidents
