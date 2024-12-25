import sqlalchemy as sa
import geoalchemy2 as gal

from api.core.base.base_model import BaseTableModel


class Location(BaseTableModel):
    __tablename__ = 'locations'
    
    city = sa.Column(sa.String, nullable=False)
    state = sa.Column(sa.String, nullable=False)
    country = sa.Column(sa.String, nullable=False)
    geo_location = sa.Column(gal.Geometry('POINT'), nullable=False)  # Spatial data (latitude, longitude)


class EmergencyLocation(BaseTableModel):
    __tablename__ = 'emergency_locations'
    
    name = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    city = sa.Column(sa.String, nullable=True)
    state = sa.Column(sa.String, nullable=True)
    country = sa.Column(sa.String, nullable=False)
    geo_location = sa.Column(gal.Geometry('POINT'), nullable=False)  # Spatial data (latitude, longitude)
