"""create deployments table

Revision ID: 2026_08_14_0003
Revises: 2026_08_14_0002
Create Date: 2026-08-14 08:11:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '2026_08_14_0003'
down_revision: Union[str, None] = '2026_08_14_0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'deployments',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('project_id', sa.String(length=64), nullable=False),
        sa.Column('service_id', sa.String(length=64), nullable=False),
        sa.Column('version', sa.String(length=64), nullable=False),
        sa.Column('commit_hash', sa.String(length=64), nullable=True),
        sa.Column('author', sa.String(length=128), nullable=False, server_default='CI/CD Pipeline'),
        sa.Column('deployed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('environment', sa.String(length=32), nullable=True, server_default='Production'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='Success'),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('config_changes', sa.JSON(), nullable=True),
        sa.Column('diff_summary', sa.Text(), nullable=True),
        sa.Column('pr_url', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deployments_project_id'), 'deployments', ['project_id'], unique=False)
    op.create_index(op.f('ix_deployments_service_id'), 'deployments', ['service_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_deployments_service_id'), table_name='deployments')
    op.drop_index(op.f('ix_deployments_project_id'), table_name='deployments')
    op.drop_table('deployments')
