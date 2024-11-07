import enum
import sqlalchemy as sa
import geoalchemy2 as gal
from sqlalchemy.orm import relationship

from api.core.base.base_model import BaseTableModel


class EventType(enum.Enum):
    NATURAL = 'Natural'
    FIRE = 'Fire'
    MEDICAL = 'Medical'
    CRIME = 'Crime'
    ACCIDENT = 'Accident'

class EventStatus(enum.Enum):
    PENDING = 'Pending'
    IN_PROGRESS = 'In Progress'
    RESOLVED = 'Resolved'

class SeverityLevel(enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    SEVERE = 5


class Emergency(BaseTableModel):
    __tablename__ = 'emergencies'

    description = sa.Column(sa.String, nullable=True)
    location = sa.Column(gal.Geometry('POINT'), nullable=False)  # Spatial data (latitude, longitude)
    event_type = sa.Column(sa.String, server_default=EventType.ACCIDENT.value) 
    status = sa.Column(sa.String, server_default=EventStatus.PENDING.value)
    severity = sa.Column(sa.String, default=SeverityLevel.LOW.value) 
    attachments = sa.Column(sa.String, nullable=True)
    
    reported_by_id = sa.Column(sa.String, sa.ForeignKey('users.id'))
    
    reported_by = relationship('User', back_populates='reported_emergencies')
    notifications = relationship('Notification', back_populates='emergency')
    responder_emergencies = relationship('ResponderEmergency', back_populates='emergency')
    resources_used = relationship('ResourceAllocation', back_populates='emergency')
    final_report = relationship('FinalReport', back_populates='emergency', uselist=False)
