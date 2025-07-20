"""create sensor readings table

Revision ID: create_sensor_readings_table
Revises: remove_user_table
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_sensor_readings_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sensor_readings table
    op.create_table('sensor_readings',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('sensor_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_sensor_readings_id'), 'sensor_readings', ['id'], unique=False)
    op.create_index(op.f('ix_sensor_readings_sensor_id'), 'sensor_readings', ['sensor_id'], unique=False)
    op.create_index(op.f('ix_sensor_readings_timestamp'), 'sensor_readings', ['timestamp'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_sensor_readings_timestamp'), table_name='sensor_readings')
    op.drop_index(op.f('ix_sensor_readings_sensor_id'), table_name='sensor_readings')
    op.drop_index(op.f('ix_sensor_readings_id'), table_name='sensor_readings')
    
    # Drop table
    op.drop_table('sensor_readings') 