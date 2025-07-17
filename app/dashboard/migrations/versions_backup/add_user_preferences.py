"""add user preferences

Revision ID: add_user_preferences
Revises: add_ai_suite_and_marketplace
Create Date: 2024-04-30 12:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_user_preferences'
down_revision = 'add_ai_suite_and_marketplace'
branch_labels = None
depends_on = None

def upgrade():
    # Create enum types
    op.execute("CREATE TYPE theme AS ENUM ('light', 'dark', 'system')")
    op.execute("CREATE TYPE font_size AS ENUM ('small', 'medium', 'large')")
    op.execute("CREATE TYPE time_format AS ENUM ('12h', '24h')")
    op.execute("CREATE TYPE backup_frequency AS ENUM ('daily', 'weekly', 'monthly')")
    
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('theme', sa.Enum('light', 'dark', 'system', name='theme'), nullable=False, server_default='light'),
        sa.Column('accent_color', sa.String(), nullable=True),
        sa.Column('font_size', sa.Enum('small', 'medium', 'large', name='font_size'), nullable=False, server_default='medium'),
        sa.Column('font_family', sa.String(), nullable=False, server_default='system'),
        sa.Column('dashboard_layout', postgresql.JSONB(), nullable=True),
        sa.Column('sidebar_position', sa.String(), nullable=False, server_default='left'),
        sa.Column('sidebar_collapsed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('grid_view', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('push_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('in_app_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notification_sound', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notification_types', postgresql.JSONB(), nullable=True),
        sa.Column('quiet_hours', postgresql.JSONB(), nullable=True),
        sa.Column('language', sa.String(), nullable=False, server_default='en'),
        sa.Column('timezone', sa.String(), nullable=False, server_default='UTC'),
        sa.Column('date_format', sa.String(), nullable=False, server_default='YYYY-MM-DD'),
        sa.Column('time_format', sa.Enum('12h', '24h', name='time_format'), nullable=False, server_default='24h'),
        sa.Column('data_sharing', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('analytics_opt_in', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('personalized_ads', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('high_contrast', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reduced_motion', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('screen_reader', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('keyboard_shortcuts', postgresql.JSONB(), nullable=True),
        sa.Column('cache_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('cache_duration', sa.Integer(), nullable=False, server_default='300'),
        sa.Column('auto_refresh', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('refresh_interval', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('connected_services', postgresql.JSONB(), nullable=True),
        sa.Column('webhook_urls', postgresql.JSONB(), nullable=True),
        sa.Column('api_keys', postgresql.JSONB(), nullable=True),
        sa.Column('auto_backup', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('backup_frequency', sa.Enum('daily', 'weekly', 'monthly', name='backup_frequency'), nullable=False, server_default='daily'),
        sa.Column('backup_location', sa.String(), nullable=True),
        sa.Column('custom_settings', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on user_id
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'], unique=True)

def downgrade():
    # Drop the table and indexes
    op.drop_index('ix_user_preferences_user_id', table_name='user_preferences')
    op.drop_table('user_preferences')
    
    # Drop enum types
    op.execute("DROP TYPE theme")
    op.execute("DROP TYPE font_size")
    op.execute("DROP TYPE time_format")
    op.execute("DROP TYPE backup_frequency") 