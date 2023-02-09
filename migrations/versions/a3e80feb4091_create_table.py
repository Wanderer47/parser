"""create table

Revision ID: a3e80feb4091
Revises: 
Create Date: 2023-02-03 17:37:29.532517

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3e80feb4091'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
            'certified_taxi_drivers',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(50)),
            sa.Column('region', sa.String(50)),
            sa.Column('phone', sa.Integer),
            sa.Column('addres', sa.String(50)),
            )


def downgrade() -> None:
    op.drop_table('certified_taxi_drivers')
