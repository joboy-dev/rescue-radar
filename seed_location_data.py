import os, json
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from api.v1.models.location import Location


directory = 'api/core/dependencies/data/nigerian_cities'
city_files = os.listdir(directory)

for file in city_files:
    file_path = os.path.join(directory, file)
    print(f'Opening {file_path}')
    
    with open(file_path, 'r') as f:
        cities = json.load(f)
        
        for city in cities:
            point = from_shape(Point(city["lat"], city["long"]))  # Latitude, Longitude
            location = Location.create(
                city=city['name'],
                state=city['region'],
                country=city['country'],
                latitude=city['lat'],
                longitude=city['long'],
                geo_location=point,  # Use PostgreSQL's GEOMETRY data type for storing latitude and longitude
            )
            print(f'New location added: {location.to_dict()}')

    # for city in cities:
    #     city['country'] = 'Nigeria'