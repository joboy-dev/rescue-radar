import enum
import sqlalchemy as sa
import geoalchemy2 as gal
from sqlalchemy.orm import relationship, Session
from sqlalchemy import event

from api.core.base.base_model import BaseTableModel
from api.v1.models.notification import Notification
from api.v1.models.responder import Responder
from api.v1.models.report import FinalReport, Outcome


class ResponderStatus(enum.Enum):
    ASSIGNED = 'Assigned'
    ON_SITE = 'On Site'
    COMPLETED = 'Completed'
    RECALLED = 'Recalled'
    

class ResponderEmergency(BaseTableModel):
    __tablename__ = 'responder_emergencies'

    status = sa.Column(sa.String, server_default=ResponderStatus.ASSIGNED.value)
    
    emergency_id = sa.Column(sa.String, sa.ForeignKey('emergencies.id'))
    responder_id = sa.Column(sa.String, sa.ForeignKey('responders.id'))
    final_report_id = sa.Column(sa.String, sa.ForeignKey('final_reports.id'))

    # Relationships
    emergency = relationship('Emergency', back_populates='responder_emergencies')
    responder = relationship('Responder', back_populates='assigned_emergencies')
    final_report = relationship('FinalReport', back_populates='responders')


def after_insert_op(mapper, connection, target):
    try:
        session = Session(bind=connection)
        
        # Get responder
        responder = session.query(Responder).filter_by(id=target.responder_id).first()
        
        # Create notification
        notification = Notification(
            target_user_id=responder.user_id,
            message=f'A new emenrgency has been assigned to you',
            emergency_id=target.emergency_id
        )
        session.add(notification)
        session.commit()
        session.refresh(notification)
        
        # Check if final report for the emergency already exists
        final_report_exists = session.query(FinalReport).filter_by(emergency_id=target.emergency_id).first()
        responder_emergency = session.get(ResponderEmergency, ident=target.id)
        
        if final_report_exists:
            print(f'Final Report already exists for emergency: {target.emergency_id}')
            
            # Update ResponderEmergency with final report id
            responder_emergency.final_report_id = final_report_exists.id
            session.commit()
            session.refresh(responder_emergency)
            
            return  # No need to create a new one
        
        # Create final report
        final_report = FinalReport(
            outcome=Outcome.UNRESOLVED.value,
            description='None',
            emergency_id=target.emergency_id,
            start_time=target.created_at
        )
        session.add(final_report)
        session.commit()
        session.refresh(final_report)
        
        # Update ResponderEmergency with final report id
        responder_emergency.final_report_id = final_report.id
        session.commit()
        session.refresh(responder_emergency)
        
        print(f'Notification and Final Report created for ResponderEmergency: {target.id}')
        
    except Exception as e:
        print(f'An exception occured: {str(e)}')

        
event.listen(ResponderEmergency, 'after_insert', after_insert_op)  
