import sqlalchemy as sa
from sqlalchemy.orm import relationship

from api.core.base.base_model import BaseTableModel


class Agency(BaseTableModel):
    __tablename__ = 'agencies'

    name = sa.Column(sa.String, nullable=False)
    contact_email = sa.Column(sa.String, nullable=False)
    contact_number = sa.Column(sa.String, nullable=False)
    
    creator_id = sa.Column(sa.String, sa.ForeignKey('users.id'), nullable=False)
    
    created_by = relationship('User', back_populates='created_agencies')
    responders = relationship('Responder', back_populates='agency')
    resources = relationship('Resource', back_populates='agency')