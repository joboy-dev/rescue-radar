import enum
import sqlalchemy as sa
import geoalchemy2 as gal
from sqlalchemy.orm import relationship

from api.core.base.base_model import BaseTableModel


class ResponderStatus(enum.Enum):
    AVAILABLE = 'available'
    ENGAGED = 'engaged'
    OFFLINE = 'offline'
    

class Responder(BaseTableModel):
    __tablename__ = 'responders'

    contact_number = sa.Column(sa.String, nullable=False)
    status = sa.Column(sa.String, default=ResponderStatus.AVAILABLE.value)
    location = sa.Column(gal.Geometry('POINT'))  # Current location of the responder
    
    user_id = sa.Column(sa.String, sa.ForeignKey('users.id'), nullable=False)
    agency_id = sa.Column(sa.String, sa.ForeignKey('agencies.id'))
    
    user = relationship('User', back_populates='responder_profile')    
    agency = relationship('Agency', back_populates='responders')
    assigned_emergencies = relationship('ResponderEmergency', back_populates='responder')
