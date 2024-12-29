import enum
import sqlalchemy as sa
import geoalchemy2 as gal
from sqlalchemy.orm import relationship, Session
from sqlalchemy import event


from api.core.base.base_model import BaseTableModel
from api.v1.models.agency import Agency
from api.v1.models.notification import Notification
from api.v1.models.responder_emergency import ResponderEmergency
from api.v1.services.location import LocationService


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
    
EVENT_TYPE_EMOJIS = {
    EventType.NATURAL.value: "🌪️",  # Tornado or natural disaster
    EventType.FIRE.value: "🔥",     # Fire
    EventType.MEDICAL.value: "🚑",  # Medical emergency
    EventType.CRIME.value: "🚔",    # Crime or law enforcement
    EventType.ACCIDENT.value: "🚗💥",  # Vehicle accident
}


class Emergency(BaseTableModel):
    __tablename__ = 'emergencies'

    description = sa.Column(sa.String, nullable=True)
    latitude = sa.Column(sa.Float, nullable=True)
    longitude = sa.Column(sa.Float, nullable=True)
    location = sa.Column(gal.Geometry('POINT'), nullable=False)  # Spatial data (latitude, longitude)
    location_str = sa.Column(sa.String, nullable=True)
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


def after_insert_op(mapper, connection, target):
    try:
        session = Session(bind=connection)
        
        if target.reported_by_id:
            # Create notification
            notification = Notification(
                target_user_id=target.reported_by_id,
                message=f'You reported emergency of type {target.event_type} at {target.location_str}.',
                emergency_id=target.id
            )
            session.add(notification)
            session.commit()
            session.refresh(notification)
        
        # Send notification to all agencies in the surrounding area
        city, state = target.location_str.split(', ')
        nearby_locations = LocationService.get_nearby_locations(city, state, km_within=5, db=session)
        
        agencies = []
        for location in nearby_locations:
            nearby_agencies = session.query(Agency).filter_by(
                longitude=location['longitude'],
                latitude=location['latitude']
            ).all()
            if nearby_agencies:
                agencies.extend(nearby_agencies)
        
        for agency in agencies:
            # Create notification
            notification = Notification(
                target_user_id=agency.creator_id,
                message=f'New emergency reported of type {target.event_type} at {target.location_str} has been reported. Please review and assign a responder.',
                emergency_id=target.id
            )
            session.add(notification)
        
        session.commit()
            # session.refresh(notification)
        
    except Exception as e:
        print(f'An exception occured: {str(e)}')

        
event.listen(Emergency, 'after_insert', after_insert_op)


def after_update_op(mapper, connection, target):
    try:
        session = Session(bind=connection)
        
        if target.reported_by_id:
            # Create notification
            notification = Notification(
                target_user_id=target.reported_by_id,
                message=f'Emergency reported status for {target.event_type} has been updated to {target.status}',
                emergency_id=target.id
            )
            session.add(notification)
            session.commit()
            session.refresh(notification)
        
    except Exception as e:
        print(f'An exception occured: {str(e)}')

        
event.listen(Emergency, 'after_update', after_update_op)
