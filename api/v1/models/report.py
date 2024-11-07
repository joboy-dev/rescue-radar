import sqlalchemy as sa, enum
from sqlalchemy.orm import relationship

from api.core.base.base_model import BaseTableModel


class Outcome(enum.Enum):
    
    RESOLVED = 'resolved'
    FATAL = 'fatal'
    ESCALATED = 'escalated'
    UNRESOLVED = 'unresolved'
    


class FinalReport(BaseTableModel):
    __tablename__ = 'final_reports'

    outcome = sa.Column(sa.String, nullable=False)  # e.g., 'resolved', 'fatal', 'escalated'    
    description = sa.Column(sa.Text, nullable=False)    
    start_time = sa.Column(sa.DateTime, nullable=True)  # When the emergency was reported
    end_time = sa.Column(sa.DateTime, nullable=True)  # When the emergency was resolved
    comments = sa.Column(sa.Text)
    emergency_id = sa.Column(sa.String, sa.ForeignKey('emergencies.id'), nullable=False)
    
    emergency = relationship('Emergency', back_populates='final_report')
    responders = relationship('ResponderEmergency', back_populates='final_report') 
