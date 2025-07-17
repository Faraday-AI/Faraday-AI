"""add activity recommendations

Revision ID: 20240401000000
Revises: 20240331000000
Create Date: 2024-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240401000000'
down_revision = '20240331000000'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'activity_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('class_id', sa.Integer(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('recommendation_score', sa.Float(), nullable=False),
        sa.Column('score_breakdown', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_recommendations_id'), 'activity_recommendations', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_activity_recommendations_id'), table_name='activity_recommendations')
    op.drop_table('activity_recommendations') 