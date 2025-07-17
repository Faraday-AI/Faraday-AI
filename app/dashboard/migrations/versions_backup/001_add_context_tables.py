"""Add context management tables

This migration adds the tables needed for GPT context management
and coordination in the Faraday AI Dashboard.
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic
revision = '001_add_context_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create context_gpts table (many-to-many relationship)
    op.create_table(
        'context_gpts',
        sa.Column('context_id', sa.String(), sa.ForeignKey('gpt_contexts.id')),
        sa.Column('gpt_definition_id', sa.String(), sa.ForeignKey('gpt_definitions.id')),
        sa.PrimaryKeyConstraint('context_id', 'gpt_definition_id')
    )

    # Create gpt_contexts table
    op.create_table(
        'gpt_contexts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column('primary_gpt_id', sa.String(), sa.ForeignKey('gpt_definitions.id'), nullable=False),
        sa.Column('name', sa.String()),
        sa.Column('description', sa.String()),
        sa.Column('context_data', sa.JSON()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('closed_at', sa.DateTime())
    )

    # Create context_interactions table
    op.create_table(
        'context_interactions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('context_id', sa.String(), sa.ForeignKey('gpt_contexts.id'), nullable=False),
        sa.Column('gpt_id', sa.String(), sa.ForeignKey('gpt_definitions.id'), nullable=False),
        sa.Column('interaction_type', sa.String(), nullable=False),
        sa.Column('content', sa.JSON()),
        sa.Column('metadata', sa.JSON()),
        sa.Column('timestamp', sa.DateTime(), default=datetime.utcnow)
    )

    # Create shared_contexts table
    op.create_table(
        'shared_contexts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('context_id', sa.String(), sa.ForeignKey('gpt_contexts.id'), nullable=False),
        sa.Column('source_gpt_id', sa.String(), sa.ForeignKey('gpt_definitions.id'), nullable=False),
        sa.Column('target_gpt_id', sa.String(), sa.ForeignKey('gpt_definitions.id'), nullable=False),
        sa.Column('shared_data', sa.JSON()),
        sa.Column('metadata', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('expires_at', sa.DateTime())
    )

    # Create context_summaries table
    op.create_table(
        'context_summaries',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('context_id', sa.String(), sa.ForeignKey('gpt_contexts.id'), nullable=False),
        sa.Column('summary_type', sa.String(), nullable=False),
        sa.Column('content', sa.JSON()),
        sa.Column('metadata', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow)
    )

    # Create indexes for better query performance
    op.create_index('idx_gpt_contexts_user_id', 'gpt_contexts', ['user_id'])
    op.create_index('idx_gpt_contexts_primary_gpt', 'gpt_contexts', ['primary_gpt_id'])
    op.create_index('idx_gpt_contexts_active', 'gpt_contexts', ['is_active'])
    op.create_index('idx_context_interactions_context', 'context_interactions', ['context_id'])
    op.create_index('idx_context_interactions_gpt', 'context_interactions', ['gpt_id'])
    op.create_index('idx_shared_contexts_context', 'shared_contexts', ['context_id'])
    op.create_index('idx_context_summaries_context', 'context_summaries', ['context_id'])

def downgrade():
    # Drop indexes
    op.drop_index('idx_context_summaries_context')
    op.drop_index('idx_shared_contexts_context')
    op.drop_index('idx_context_interactions_gpt')
    op.drop_index('idx_context_interactions_context')
    op.drop_index('idx_gpt_contexts_active')
    op.drop_index('idx_gpt_contexts_primary_gpt')
    op.drop_index('idx_gpt_contexts_user_id')

    # Drop tables
    op.drop_table('context_summaries')
    op.drop_table('shared_contexts')
    op.drop_table('context_interactions')
    op.drop_table('gpt_contexts')
    op.drop_table('context_gpts') 