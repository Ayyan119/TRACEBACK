"""create services table

Revision ID: 2026_08_14_0002
Revises: 2026_08_14_0001
Create Date: 2026-08-14 08:02:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '2026_08_14_0002'
down_revision: Union[str, None] = '2026_08_14_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'services',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('project_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('health', sa.String(length=32), nullable=False, server_default='Healthy'),
        sa.Column('type', sa.String(length=32), nullable=True, server_default='Backend'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('latency_ms', sa.Float(), nullable=False, server_default='15.0'),
        sa.Column('error_rate_percent', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('recent_incidents_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('dependencies', sa.JSON(), nullable=False),
        sa.Column('recent_deployments', sa.JSON(), nullable=False),
        sa.Column('owner_team', sa.String(length=128), nullable=True),
        sa.Column('repository_url', sa.String(length=256), nullable=True),
        sa.Column('environment', sa.String(length=32), nullable=True, server_default='Production'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_services_name'), 'services', ['name'], unique=False)
    op.create_index(op.f('ix_services_project_id'), 'services', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_services_project_id'), table_name='services')
    op.drop_index(op.f('ix_services_name'), table_name='services')
    op.drop_table('services')
