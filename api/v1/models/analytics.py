import sqlalchemy as sa, enum
from sqlalchemy.orm import relationship

from api.core.base.base_model import BaseTableModel


class DataAnalytics(BaseTableModel):
    __tablename__ = 'data_analytics'
    
    date = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    avg_response_time = sa.Column(sa.Float, nullable=False)
    most_common_emergency_type = sa.Column(sa.String, nullable=False)  # e.g., 'fire', 'medical'
    total_emergencies = sa.Column(sa.Integer, nullable=False)
    total_resources_used = sa.Column(sa.Integer, nullable=False)
    most_used_resource_type = sa.Column(sa.String, nullable=False)
    most_active_responder_id = sa.Column(sa.String, sa.ForeignKey('responders.id'), nullable=True)
