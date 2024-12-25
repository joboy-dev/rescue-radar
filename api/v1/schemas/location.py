from pydantic import BaseModel


class LocationBase(BaseModel):
    
    id: str
    city: str
    state: str
    country: str
    latitude: float
    longitude: float
