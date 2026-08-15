"""create investigations table

Revision ID: 2026_08_15_0009
Revises: 2026_08_15_0008
Create Date: 2026-08-15 18:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '2026_08_15_0009'
down_revision: Union[str, None] = '2026_08_15_0008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'investigations',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('incident_id', sa.String(length=64), nullable=False),
        sa.Column('project_id', sa.String(length=64), nullable=False),
        sa.Column('investigation_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='CREATED'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_ms', sa.Float(), nullable=True),
        sa.Column('incident_description', sa.Text(), nullable=True),
        sa.Column('final_summary', sa.Text(), nullable=True),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('final_report_json', sa.JSON(), nullable=True),
        sa.Column('selected_hypothesis_json', sa.JSON(), nullable=True),
        sa.Column('hypotheses_json', sa.JSON(), nullable=True),
        sa.Column('accepted_evidence_json', sa.JSON(), nullable=True),
        sa.Column('rejected_evidence_json', sa.JSON(), nullable=True),
        sa.Column('execution_trace_json', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_investigations_incident_id'), 'investigations', ['incident_id'], unique=False)
    op.create_index(op.f('ix_investigations_project_id'), 'investigations', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_investigations_project_id'), table_name='investigations')
    op.drop_index(op.f('ix_investigations_incident_id'), table_name='investigations')
    op.drop_table('investigations')
