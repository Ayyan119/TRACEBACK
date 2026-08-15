"""create_log_records_table

Revision ID: 2026_08_14_0007
Revises: 2026_08_14_0006
Create Date: 2026-08-14 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_08_14_0007'
down_revision = '2026_08_14_0006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'log_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('incident_id', sa.String(length=36), nullable=True),
        sa.Column('file_id', sa.String(length=255), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('time', sa.Time(), nullable=False),
        sa.Column('day', sa.String(length=20), nullable=False),
        sa.Column('log_type', sa.String(length=50), nullable=False),
        sa.Column('level', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=True),
        sa.Column('service', sa.String(length=255), nullable=True),
        sa.Column('raw_line', sa.Text(), nullable=False),
        sa.Column('parse_status', sa.String(length=20), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_log_records_date'), 'log_records', ['date'], unique=False)
    op.create_index(op.f('ix_log_records_day'), 'log_records', ['day'], unique=False)
    op.create_index(op.f('ix_log_records_file_id'), 'log_records', ['file_id'], unique=False)
    op.create_index(op.f('ix_log_records_id'), 'log_records', ['id'], unique=False)
    op.create_index(op.f('ix_log_records_incident_id'), 'log_records', ['incident_id'], unique=False)
    op.create_index(op.f('ix_log_records_level'), 'log_records', ['level'], unique=False)
    op.create_index(op.f('ix_log_records_log_type'), 'log_records', ['log_type'], unique=False)
    op.create_index(op.f('ix_log_records_project_id'), 'log_records', ['project_id'], unique=False)
    op.create_index(op.f('ix_log_records_service'), 'log_records', ['service'], unique=False)
    op.create_index(op.f('ix_log_records_source'), 'log_records', ['source'], unique=False)
    op.create_index(op.f('ix_log_records_timestamp'), 'log_records', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_log_records_timestamp'), table_name='log_records')
    op.drop_index(op.f('ix_log_records_source'), table_name='log_records')
    op.drop_index(op.f('ix_log_records_service'), table_name='log_records')
    op.drop_index(op.f('ix_log_records_project_id'), table_name='log_records')
    op.drop_index(op.f('ix_log_records_log_type'), table_name='log_records')
    op.drop_index(op.f('ix_log_records_level'), table_name='log_records')
    op.drop_index(op.f('ix_log_records_incident_id'), table_name='log_records')
    op.drop_index(op.f('ix_log_records_id'), table_name='log_records')
    op.drop_index(op.f('ix_log_records_file_id'), table_name='log_records')
    op.drop_index(op.f('ix_log_records_day'), table_name='log_records')
    op.drop_index(op.f('ix_log_records_date'), table_name='log_records')
    op.drop_table('log_records')
