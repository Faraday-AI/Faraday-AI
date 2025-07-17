"""add gpt manager features

Revision ID: add_gpt_manager_features
Revises: 
Create Date: 2024-04-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_gpt_manager_features'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to existing tables
    op.add_column('dashboard_users', sa.Column('role', sa.String(), nullable=False, server_default='user'))
    op.add_column('dashboard_users', sa.Column('api_key', sa.String(), unique=True))
    op.add_column('dashboard_users', sa.Column('last_api_key_rotation', sa.DateTime()))

    op.add_column('gpt_subscriptions', sa.Column('version', sa.String()))
    op.add_column('gpt_subscriptions', sa.Column('rate_limit', sa.Integer(), server_default='100'))
    op.add_column('gpt_subscriptions', sa.Column('usage_count', sa.Integer(), server_default='0'))
    op.add_column('gpt_subscriptions', sa.Column('last_used', sa.DateTime()))

    op.add_column('projects', sa.Column('team_id', sa.String()))
    op.add_column('projects', sa.Column('is_template', sa.Boolean(), server_default='false'))

    op.add_column('gpt_performance', sa.Column('response_time', sa.Float()))
    op.add_column('gpt_performance', sa.Column('error_rate', sa.Float()))
    op.add_column('gpt_performance', sa.Column('usage_count', sa.Integer()))

    op.add_column('feedback', sa.Column('status', sa.String(), server_default='open'))
    op.add_column('feedback', sa.Column('priority', sa.String()))

    op.add_column('dashboard_analytics', sa.Column('gpt_usage', postgresql.JSONB()))
    op.add_column('dashboard_analytics', sa.Column('api_calls', postgresql.JSONB()))
    op.add_column('dashboard_analytics', sa.Column('error_logs', postgresql.JSONB()))

    # Create new tables
    op.create_table(
        'gpt_sharing',
        sa.Column('gpt_id', sa.String(), primary_key=True),
        sa.Column('shared_with_user_id', sa.String(), primary_key=True),
        sa.Column('permissions', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['gpt_id'], ['gpt_subscriptions.id']),
        sa.ForeignKeyConstraint(['shared_with_user_id'], ['dashboard_users.id'])
    )

    op.create_table(
        'categories',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'))
    )

    op.create_table(
        'gpt_categories',
        sa.Column('gpt_id', sa.String(), primary_key=True),
        sa.Column('category_id', sa.String(), primary_key=True),
        sa.ForeignKeyConstraint(['gpt_id'], ['gpt_subscriptions.id']),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'])
    )

    op.create_table(
        'gpt_versions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('subscription_id', sa.String(), nullable=False),
        sa.Column('version_number', sa.String(), nullable=False),
        sa.Column('configuration', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('is_active', sa.Boolean(), server_default='false'),
        sa.ForeignKeyConstraint(['subscription_id'], ['gpt_subscriptions.id'])
    )

    op.create_table(
        'webhooks',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('subscription_id', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('events', postgresql.JSONB()),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['subscription_id'], ['gpt_subscriptions.id'])
    )

    op.create_table(
        'teams',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'))
    )

    op.create_table(
        'team_members',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('team_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.ForeignKeyConstraint(['user_id'], ['dashboard_users.id'])
    )

    op.create_table(
        'comments',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['user_id'], ['dashboard_users.id'])
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('resource_type', sa.String(), nullable=False),
        sa.Column('resource_id', sa.String(), nullable=False),
        sa.Column('details', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['dashboard_users.id'])
    )

def downgrade():
    # Drop new tables
    op.drop_table('audit_logs')
    op.drop_table('comments')
    op.drop_table('team_members')
    op.drop_table('teams')
    op.drop_table('webhooks')
    op.drop_table('gpt_versions')
    op.drop_table('gpt_categories')
    op.drop_table('categories')
    op.drop_table('gpt_sharing')

    # Remove new columns from existing tables
    op.drop_column('dashboard_analytics', 'error_logs')
    op.drop_column('dashboard_analytics', 'api_calls')
    op.drop_column('dashboard_analytics', 'gpt_usage')
    op.drop_column('feedback', 'priority')
    op.drop_column('feedback', 'status')
    op.drop_column('gpt_performance', 'usage_count')
    op.drop_column('gpt_performance', 'error_rate')
    op.drop_column('gpt_performance', 'response_time')
    op.drop_column('projects', 'is_template')
    op.drop_column('projects', 'team_id')
    op.drop_column('gpt_subscriptions', 'last_used')
    op.drop_column('gpt_subscriptions', 'usage_count')
    op.drop_column('gpt_subscriptions', 'rate_limit')
    op.drop_column('gpt_subscriptions', 'version')
    op.drop_column('dashboard_users', 'last_api_key_rotation')
    op.drop_column('dashboard_users', 'api_key')
    op.drop_column('dashboard_users', 'role') 