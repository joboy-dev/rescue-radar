import enum
import sqlalchemy as sa
import geoalchemy2 as gal
from sqlalchemy.orm import relationship

from api.core.base.base_model import BaseTableModel


class ResourceType(enum.Enum):
    AMBULANCE = 'ambulance'
    FIRETRUCK = 'firetruck'
    POLICE_CAR = 'police_car'
    WATER_TANKER = 'water_tanker'
    RESCUE_BOAT = 'rescue_boat'
    HELICOPTER = 'helicopter'
    MEDICAL_KIT = 'medical_kit'
    GENERATOR = 'generator'
    CRANE = 'crane'
    LADDER_TRUCK = 'ladder_truck'
    SEARCH_DRONE = 'search_drone'
    BULLDOZER = 'bulldozer'
    

class Resource(BaseTableModel):
    __tablename__ ='resources'
    
    resource_type = sa.Column(sa.String, nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False, default=0)
    
    agency_id = sa.Column(sa.String, sa.ForeignKey('agencies.id'))
    agency = relationship('Agency', back_populates='resources')
    

class ResourceAllocation(BaseTableModel):
    __tablename__ = 'resource_allocations'

    resource_type = sa.Column(sa.String, nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False, default=1)

    emergency_id = sa.Column(sa.String, sa.ForeignKey('emergencies.id'))
    emergency = relationship('Emergency', back_populates='resources_used')
