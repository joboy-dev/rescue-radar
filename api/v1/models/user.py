import sqlalchemy as sa, enum
from sqlalchemy.orm import relationship

from api.core.base.base_model import BaseTableModel


class UserRole(enum.Enum):
    PUBLIC = 'Public'
    RESPONDER = 'Responder'
    AGENCY_ADMIN = 'Agency admin'
    SUPERADMIN = 'Superadmin'


class User(BaseTableModel):
    __tablename__ = 'users'

    email = sa.Column(sa.String, nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False)
    role = sa.Column(sa.String, nullable=False, server_default=UserRole.PUBLIC.value)
    is_active = sa.Column(sa.Boolean, server_default='true')
    last_login = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    tokens = relationship('Token', back_populates='user')
    blacklisted_tokens = relationship('BlacklistedToken', back_populates='user')
    profile = relationship('Profile', back_populates='user', uselist=False)
    reported_emergencies = relationship('Emergency', back_populates='reported_by')
    notifications = relationship('Notification', back_populates='target_user')
    responder_profile = relationship('Responder', back_populates='user', uselist=False)
    created_agencies = relationship('Agency', back_populates='created_by', uselist=False)
    
    
    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict.pop("password")
        if self.last_login:
            obj_dict["last_login"] = self.last_login.isoformat()
        return obj_dict
        