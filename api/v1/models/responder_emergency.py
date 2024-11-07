import enum
import sqlalchemy as sa
import geoalchemy2 as gal
from sqlalchemy.orm import relationship

from api.core.base.base_model import BaseTableModel


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
    