import sqlalchemy as sa, enum
from sqlalchemy.orm import relationship

from api.core.base.base_model import BaseTableModel


class TokenType(enum.Enum):
    
    ACCESS = 'access'
    REFRESH = 'refresh'
    

class Token(BaseTableModel):
    __tablename__ = 'tokens'
    
    token = sa.Column(sa.String, nullable=False)
    token_type = sa.Column(sa.String, server_default=TokenType.ACCESS.value)
    expiry_time = sa.Column(sa.DateTime, nullable=False)
    
    user_id = sa.Column(sa.String, sa.ForeignKey('users.id'), nullable=True)
    user = relationship('User', back_populates='tokens')
    
    def is_expired(self):
        return self.expiry_time < sa.func.now()


class BlacklistedToken(BaseTableModel):
    __tablename__ = 'blacklisted_tokens'
    
    token = sa.Column(sa.String, nullable=False)
    
    user_id = sa.Column(sa.String, sa.ForeignKey('users.id'), nullable=True)
    user = relationship('User', back_populates='blacklisted_tokens')
