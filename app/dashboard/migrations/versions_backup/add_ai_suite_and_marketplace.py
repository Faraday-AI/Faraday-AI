"""add ai suite and marketplace

Revision ID: add_ai_suite_and_marketplace
Revises: add_gpt_manager_features
Create Date: 2024-04-30 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_ai_suite_and_marketplace'
down_revision = 'add_gpt_manager_features'
branch_labels = None
depends_on = None

def upgrade():
    # Create enum types
    op.execute("CREATE TYPE user_type AS ENUM ('student', 'teacher', 'admin', 'developer')")
    op.execute("CREATE TYPE billing_tier AS ENUM ('free', 'basic', 'premium', 'enterprise')")
    op.execute("CREATE TYPE tool_status AS ENUM ('active', 'inactive', 'pending', 'deprecated')")

    # Add new columns to existing tables
    op.add_column('dashboard_users', sa.Column('user_type', sa.Enum('student', 'teacher', 'admin', 'developer', name='user_type'), nullable=False, server_default='student'))
    op.add_column('dashboard_users', sa.Column('billing_tier', sa.Enum('free', 'basic', 'premium', 'enterprise', name='billing_tier'), nullable=False, server_default='free'))
    op.add_column('dashboard_users', sa.Column('organization_id', sa.String()))
    op.add_column('dashboard_users', sa.Column('department_id', sa.String()))
    op.add_column('dashboard_users', sa.Column('credits_balance', sa.Numeric(10, 2), server_default='0'))
    op.add_column('dashboard_users', sa.Column('is_active', sa.Boolean(), server_default='true'))
    op.add_column('dashboard_users', sa.Column('last_login', sa.DateTime()))
    op.add_column('dashboard_users', sa.Column('preferences', postgresql.JSONB(), server_default='{}'))

    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String()),
        sa.Column('subscription_tier', sa.Enum('free', 'basic', 'premium', 'enterprise', name='billing_tier'), nullable=False),
        sa.Column('credits_balance', sa.Numeric(10, 2), server_default='0'),
        sa.Column('settings', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'))
    )

    # Create departments table
    op.create_table(
        'departments',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('settings', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'])
    )

    # Create AI suites table
    op.create_table(
        'ai_suites',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('configuration', postgresql.JSONB(), server_default='{}'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['dashboard_users.id'])
    )

    # Create AI tools table
    op.create_table(
        'ai_tools',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('tool_type', sa.String(), nullable=False),
        sa.Column('version', sa.String()),
        sa.Column('configuration', postgresql.JSONB(), server_default='{}'),
        sa.Column('pricing_tier', sa.Enum('free', 'basic', 'premium', 'enterprise', name='billing_tier'), nullable=False),
        sa.Column('credits_cost', sa.Numeric(10, 2), server_default='0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('requires_approval', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('suite_id', sa.String()),
        sa.ForeignKeyConstraint(['suite_id'], ['ai_suites.id'])
    )

    # Create marketplace listings table
    op.create_table(
        'marketplace_listings',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tool_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('features', postgresql.JSONB(), server_default='[]'),
        sa.Column('pricing_details', postgresql.JSONB(), server_default='{}'),
        sa.Column('category', sa.String()),
        sa.Column('tags', postgresql.JSONB(), server_default='[]'),
        sa.Column('preview_url', sa.String()),
        sa.Column('documentation_url', sa.String()),
        sa.Column('is_featured', sa.Boolean(), server_default='false'),
        sa.Column('is_public', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tool_id'], ['ai_tools.id'])
    )

    # Create tool assignments table
    op.create_table(
        'tool_assignments',
        sa.Column('tool_id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), primary_key=True),
        sa.Column('assigned_by', sa.String()),
        sa.Column('assigned_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime()),
        sa.Column('permissions', postgresql.JSONB(), server_default='{}'),
        sa.ForeignKeyConstraint(['tool_id'], ['ai_tools.id']),
        sa.ForeignKeyConstraint(['user_id'], ['dashboard_users.id']),
        sa.ForeignKeyConstraint(['assigned_by'], ['dashboard_users.id'])
    )

    # Create tool usage logs table
    op.create_table(
        'tool_usage_logs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('tool_id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String()),
        sa.Column('module_id', sa.String()),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('parameters', postgresql.JSONB(), server_default='{}'),
        sa.Column('credits_used', sa.Numeric(10, 2), server_default='0'),
        sa.Column('status', sa.String()),
        sa.Column('error_message', sa.String()),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('duration', sa.Float()),
        sa.ForeignKeyConstraint(['user_id'], ['dashboard_users.id']),
        sa.ForeignKeyConstraint(['tool_id'], ['ai_tools.id'])
    )

    # Add foreign key constraints
    op.create_foreign_key('fk_users_organization', 'dashboard_users', 'organizations', ['organization_id'], ['id'])
    op.create_foreign_key('fk_users_department', 'dashboard_users', 'departments', ['department_id'], ['id'])

def downgrade():
    # Drop foreign key constraints
    op.drop_constraint('fk_users_department', 'dashboard_users', type_='foreignkey')
    op.drop_constraint('fk_users_organization', 'dashboard_users', type_='foreignkey')

    # Drop tables
    op.drop_table('tool_usage_logs')
    op.drop_table('tool_assignments')
    op.drop_table('marketplace_listings')
    op.drop_table('ai_tools')
    op.drop_table('ai_suites')
    op.drop_table('departments')
    op.drop_table('organizations')

    # Drop columns from existing tables
    op.drop_column('dashboard_users', 'preferences')
    op.drop_column('dashboard_users', 'last_login')
    op.drop_column('dashboard_users', 'is_active')
    op.drop_column('dashboard_users', 'credits_balance')
    op.drop_column('dashboard_users', 'department_id')
    op.drop_column('dashboard_users', 'organization_id')
    op.drop_column('dashboard_users', 'billing_tier')
    op.drop_column('dashboard_users', 'user_type')

    # Drop enum types
    op.execute('DROP TYPE tool_status')
    op.execute('DROP TYPE billing_tier')
    op.execute('DROP TYPE user_type') 