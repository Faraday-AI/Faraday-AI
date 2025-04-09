"""add gpt roles

Revision ID: add_gpt_roles
Revises: 
Create Date: 2024-04-07 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_gpt_roles'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create gpt_roles table
    op.create_table(
        'gpt_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('gpt_name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_accessed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('preferences', postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'gpt_name', name='uix_user_gpt')
    )
    
    # Add columns to user_memories
    op.add_column('user_memories', sa.Column('gpt_access', postgresql.JSONB(), server_default='[]', nullable=False))
    op.add_column('user_memories', sa.Column('gpt_source', sa.String(length=255), nullable=True))
    
    # Create gpt_interactions table
    op.create_table(
        'gpt_interactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('gpt_name', sa.String(length=255), nullable=False),
        sa.Column('memory_id', sa.Integer(), nullable=True),
        sa.Column('interaction_type', sa.String(length=50), nullable=True),
        sa.Column('interaction_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['memory_id'], ['user_memories.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_gpt_roles_user_id', 'gpt_roles', ['user_id'])
    op.create_index('ix_gpt_interactions_user_id', 'gpt_interactions', ['user_id'])
    op.create_index('ix_gpt_interactions_memory_id', 'gpt_interactions', ['memory_id'])

def downgrade():
    # Drop indexes
    op.drop_index('ix_gpt_interactions_memory_id')
    op.drop_index('ix_gpt_interactions_user_id')
    op.drop_index('ix_gpt_roles_user_id')
    
    # Drop tables
    op.drop_table('gpt_interactions')
    
    # Drop columns from user_memories
    op.drop_column('user_memories', 'gpt_source')
    op.drop_column('user_memories', 'gpt_access')
    
    # Drop gpt_roles table
    op.drop_table('gpt_roles') 