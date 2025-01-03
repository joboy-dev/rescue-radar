"""empty message

Revision ID: 36ab06de9f55
Revises: d5c8d436b7f4
Create Date: 2025-01-03 05:04:44.206795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36ab06de9f55'
down_revision: Union[str, None] = 'd5c8d436b7f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('final_reports', sa.Column('response_time', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('final_reports', 'response_time')
    # ### end Alembic commands ###
