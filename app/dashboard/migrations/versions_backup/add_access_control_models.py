"""add access control models

Revision ID: add_access_control_models
Revises: add_user_preferences
Create Date: 2024-04-30 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_access_control_models'
down_revision = 'add_user_preferences'
branch_labels = None
depends_on = None

def upgrade():
    # Create enum types
    op.execute("CREATE TYPE resource_type AS ENUM ('user', 'role', 'permission', 'tool', 'avatar', 'setting', 'api', 'system')")
    op.execute("CREATE TYPE action_type AS ENUM ('create', 'read', 'update', 'delete', 'execute', 'manage', 'administer')")
    
    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('resource_type', postgresql.ENUM('user', 'role', 'permission', 'tool', 'avatar', 'setting', 'api', 'system', name='resource_type'), nullable=False),
        sa.Column('action', postgresql.ENUM('create', 'read', 'update', 'delete', 'execute', 'manage', 'administer', name='action_type'), nullable=False),
        sa.Column('scope', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_template', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create role_permission association table
    op.create_table(
        'role_permission',
        sa.Column('role_id', sa.String(), nullable=False),
        sa.Column('permission_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    
    # Create role_assignments table
    op.create_table(
        'role_assignments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role_id', sa.String(), nullable=False),
        sa.Column('assigned_by', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role_id', name='unique_user_role')
    )
    
    # Create permission_overrides table
    op.create_table(
        'permission_overrides',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('permission_id', sa.String(), nullable=False),
        sa.Column('is_allowed', sa.Boolean(), nullable=False),
        sa.Column('reason', sa.String(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'permission_id', name='unique_user_permission_override')
    )
    
    # Create role_hierarchy table
    op.create_table(
        'role_hierarchy',
        sa.Column('parent_role_id', sa.String(), nullable=False),
        sa.Column('child_role_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['child_role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('parent_role_id', 'child_role_id')
    )
    
    # Create role_templates table
    op.create_table(
        'role_templates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create role_template_permission association table
    op.create_table(
        'role_template_permission',
        sa.Column('template_id', sa.String(), nullable=False),
        sa.Column('permission_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['role_templates.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('template_id', 'permission_id')
    )

def downgrade():
    # Drop tables in reverse order
    op.drop_table('role_template_permission')
    op.drop_table('role_templates')
    op.drop_table('role_hierarchy')
    op.drop_table('permission_overrides')
    op.drop_table('role_assignments')
    op.drop_table('role_permission')
    op.drop_table('roles')
    op.drop_table('permissions')
    
    # Drop enum types
    op.execute('DROP TYPE action_type')
    op.execute('DROP TYPE resource_type') 