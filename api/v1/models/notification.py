import sqlalchemy as sa
from sqlalchemy.orm import relationship

from api.core.base.base_model import BaseTableModel


class Notification(BaseTableModel):
    __tablename__ = 'notifications'

    message = sa.Column(sa.String, nullable=False)
    is_read = sa.Column(sa.Boolean, default=False)
    target_user_id = sa.Column(sa.String, sa.ForeignKey('users.id'))  # The user who will receive the notification
    emergency_id = sa.Column(sa.String, sa.ForeignKey('emergencies.id'))  # Related emergency

    # Relationships
    target_user = relationship('User', back_populates='notifications')
    emergency = relationship('Emergency', back_populates='notifications')
