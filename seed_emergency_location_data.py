import os, json
from pprint import pprint
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from api.v1.models.location import EmergencyLocation


directory = 'api/core/dependencies/emergency_locations'


def seed_fire_locations():
    
    with open(f'{directory}/fire.geojson', 'r') as f:
        locations = json.load(f)['features']
        
        for location in locations:
            properties = location['properties']
            
            point = from_shape(Point(properties["latitude"], properties["longitude"]))  # Latitude, Longitude
            emergency_location = EmergencyLocation.create(
                name=properties['poi_file_n'].replace('_', ' '),
                type='Fire Station',
                city=properties['lga_name'],
                state=properties['state_name'],
                country='Nigeria',
                latitude=properties['latitude'],
                longitude=properties['longitude'],
                geo_location=point,  # Use PostgreSQL's GEOMETRY data type for storing latitude and longitude
            )
            print(f'New emergency location added: {emergency_location.to_dict()}')
    

def seed_police_locations():
    
    with open(f'{directory}/police.geojson', 'r') as f:
        locations = json.load(f)['features']
        
        for location in locations:
            coordinates = location['geometry']['coordinates']  # Format: [longitude, latitude]
            properties = location['properties']
            
            point = from_shape(Point(coordinates[1], coordinates[0]))  # Latitude, Longitude
            emergency_location = EmergencyLocation.create(
                name=properties['plc_st_nam'],
                type='Police Station',
                city=properties['lganame'],
                state=properties['statename'],
                country='Nigeria',
                latitude=coordinates[1],
                longitude=coordinates[0],
                geo_location=point,  # Use PostgreSQL's GEOMETRY data type for storing latitude and longitude
            )
            print(f'New emergency location added: {emergency_location.to_dict()}')


def seed_health_locations():
    
    with open(f'{directory}/health.json', 'r') as f:
        locations = json.load(f)['features']
        
        for location in locations:
            coordinates = location['geometry']['coordinates']  # Format: [longitude, latitude]
            properties = location['properties']
        
            point = from_shape(Point(coordinates[1], coordinates[0]))  # Latitude, Longitude
            emergency_location = EmergencyLocation.create(
                name=properties['name'],
                type='Health',
                city=properties['lga_name'],
                state=properties['state_name'],
                country='Nigeria',
                latitude=coordinates[1],
                longitude=coordinates[0],
                geo_location=point,  # Use PostgreSQL's GEOMETRY data type for storing latitude and longitude
            )
            print(f'New emergency location added: {emergency_location.to_dict()}')
    
            
if __name__ == '__main__':
    seed_fire_locations()
    seed_police_locations()
    seed_health_locations()