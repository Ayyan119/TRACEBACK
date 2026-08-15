"""create incidents table

Revision ID: 2026_08_14_0004
Revises: 2026_08_14_0003
Create Date: 2026-08-14 08:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '2026_08_14_0004'
down_revision: Union[str, None] = '2026_08_14_0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'incidents',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('project_id', sa.String(length=64), nullable=False),
        sa.Column('code', sa.String(length=32), nullable=False),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=32), nullable=False, server_default='High'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='Investigating'),
        sa.Column('affected_service', sa.String(length=128), nullable=False),
        sa.Column('affected_services', sa.JSON(), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration', sa.String(length=64), nullable=False, server_default='Active'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='85.0'),
        sa.Column('reporter', sa.String(length=128), nullable=True, server_default='SRE On-Call'),
        sa.Column('environment', sa.String(length=32), nullable=True, server_default='Production'),
        sa.Column('root_cause_summary', sa.Text(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incidents_code'), 'incidents', ['code'], unique=False)
    op.create_index(op.f('ix_incidents_project_id'), 'incidents', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_incidents_project_id'), table_name='incidents')
    op.drop_index(op.f('ix_incidents_code'), table_name='incidents')
    op.drop_table('incidents')
