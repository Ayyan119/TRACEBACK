"""create users table, project user_id column, and performance indexes

Revision ID: 2026_08_17_0010
Revises: 2026_08_15_0009
Create Date: 2026-08-17 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2026_08_17_0010'
down_revision: Union[str, None] = '2026_08_15_0009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('role', sa.String(length=128), nullable=False, server_default='Senior Software Engineer'),
        sa.Column('encrypted_openai_api_key', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=False)

    # 2. Seed initial default user to prevent any data loss on existing projects
    op.execute(
        "INSERT INTO users (id, name, role, created_at, updated_at) "
        "VALUES ('usr_default_ayyan', 'Ayyan Shahid', 'Senior Software Engineer', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) "
        "ON CONFLICT (id) DO NOTHING;"
    )

    # 3. Add user_id column to projects table as nullable first
    op.add_column('projects', sa.Column('user_id', sa.String(length=64), nullable=True))

    # 4. Migrate existing projects to belong to default user
    op.execute("UPDATE projects SET user_id = 'usr_default_ayyan' WHERE user_id IS NULL;")

    # 5. Make user_id NOT NULL & create Foreign Key
    op.alter_column('projects', 'user_id', nullable=False)
    op.create_foreign_key('fk_projects_user_id', 'projects', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_index('idx_projects_user_id', 'projects', ['user_id'], unique=False)

    # 6. Add performance indexes to speed up backend queries
    op.create_index('idx_services_project_id', 'services', ['project_id'], unique=False)
    op.create_index('idx_incidents_project_status', 'incidents', ['project_id', 'status'], unique=False)
    op.create_index('idx_evidence_incident_id', 'evidence', ['incident_id'], unique=False)
    op.create_index('idx_knowledge_project_id', 'knowledge_documents', ['project_id'], unique=False)
    op.create_index('idx_investigations_incident_id', 'investigations', ['incident_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_investigations_incident_id', table_name='investigations')
    op.drop_index('idx_knowledge_project_id', table_name='knowledge_documents')
    op.drop_index('idx_evidence_incident_id', table_name='evidence')
    op.drop_index('idx_incidents_project_status', table_name='incidents')
    op.drop_index('idx_services_project_id', table_name='services')
    op.drop_index('idx_projects_user_id', table_name='projects')
    op.drop_constraint('fk_projects_user_id', 'projects', type_='foreignkey')
    op.drop_column('projects', 'user_id')
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.drop_table('users')
