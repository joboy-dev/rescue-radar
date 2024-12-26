from api.v1.models.location import EmergencyLocation


class EmergencyService:
    
    @classmethod
    def get_emergency_locations(cls, db):
        # Emergency locations
        emergency_locations = EmergencyLocation.all(db=db, per_page=1000000)
        # emergency_locations = EmergencyLocation.fetch_by_field(db=db, city='Ikorodu')
        
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
        
        print(len(serialized_locations))
        print(serialized_locations[0])
        
        return serialized_locations