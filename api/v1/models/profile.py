import sqlalchemy as sa, enum
from sqlalchemy.orm import relationship

from api.core.base.base_model import BaseTableModel


class Profile(BaseTableModel):
    __tablename__ = 'profile'

    username = sa.Column(sa.String, nullable=True, unique=True)
    country_code = sa.Column(sa.String, nullable=True)
    phone_number = sa.Column(sa.String(15), nullable=True)
    first_name = sa.Column(sa.String, nullable=True)
    last_name = sa.Column(sa.String, nullable=True)
    profile_picture = sa.Column(sa.String, nullable=True)
    
    user_id = sa.Column(sa.String, sa.ForeignKey("users.id"), nullable=False)
    user = relationship('User', back_populates='profile')
