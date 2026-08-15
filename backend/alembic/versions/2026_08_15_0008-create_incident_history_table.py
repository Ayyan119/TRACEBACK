"""create incident history table

Revision ID: 2026_08_15_0008
Revises: 2026_08_14_0007
Create Date: 2026-08-15 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '2026_08_15_0008'
down_revision: Union[str, None] = '2026_08_14_0007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'incident_history',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('incident_id', sa.String(length=64), nullable=False),
        sa.Column('project_id', sa.String(length=64), nullable=False),
        sa.Column('incident_code', sa.String(length=32), nullable=False),
        sa.Column('historical_payload', sa.JSON(), nullable=False),
        sa.Column('qdrant_point_id', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='indexed'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_history_incident_id'), 'incident_history', ['incident_id'], unique=True)
    op.create_index(op.f('ix_incident_history_project_id'), 'incident_history', ['project_id'], unique=False)
    op.create_index(op.f('ix_incident_history_incident_code'), 'incident_history', ['incident_code'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_incident_history_incident_code'), table_name='incident_history')
    op.drop_index(op.f('ix_incident_history_project_id'), table_name='incident_history')
    op.drop_index(op.f('ix_incident_history_incident_id'), table_name='incident_history')
    op.drop_table('incident_history')
