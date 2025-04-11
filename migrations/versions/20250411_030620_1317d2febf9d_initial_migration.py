"""Initial migration

Revision ID: 1317d2febf9d
Revises: 
Create Date: 2025-04-11 03:06:20.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1317d2febf9d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create new tables
    op.create_table('activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('activity_type', sa.Enum('warm_up', 'skill_development', 'fitness_training', 'game', 'cool_down', name='activitytype'), nullable=False),
        sa.Column('difficulty', sa.Enum('beginner', 'intermediate', 'advanced', name='difficultylevel'), nullable=False),
        sa.Column('equipment_required', sa.Enum('none', 'minimal', 'moderate', 'extensive', name='equipmentrequirement'), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('classes',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('grade_level', sa.String(), nullable=False),
    sa.Column('max_students', sa.Integer(), nullable=False),
    sa.Column('schedule', sa.JSON(), nullable=False),
    sa.Column('location', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('environmental_checks',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('class_id', sa.String(), nullable=False),
    sa.Column('check_date', sa.DateTime(), nullable=True),
    sa.Column('temperature', sa.Float(), nullable=True),
    sa.Column('humidity', sa.Float(), nullable=True),
    sa.Column('air_quality', sa.Float(), nullable=True),
    sa.Column('surface_conditions', sa.JSON(), nullable=True),
    sa.Column('lighting', sa.Float(), nullable=True),
    sa.Column('equipment_condition', sa.JSON(), nullable=True),
    sa.Column('environmental_metadata', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('equipment_checks',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('class_id', sa.String(), nullable=False),
    sa.Column('equipment_id', sa.String(), nullable=False),
    sa.Column('check_date', sa.DateTime(), nullable=True),
    sa.Column('maintenance_status', sa.Boolean(), nullable=False),
    sa.Column('damage_status', sa.Boolean(), nullable=False),
    sa.Column('age_status', sa.Boolean(), nullable=False),
    sa.Column('last_maintenance', sa.DateTime(), nullable=True),
    sa.Column('purchase_date', sa.DateTime(), nullable=True),
    sa.Column('max_age_years', sa.Float(), nullable=True),
    sa.Column('equipment_metadata', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('safety_checks',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('class_id', sa.String(), nullable=False),
    sa.Column('check_type', sa.String(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('results', sa.JSON(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('check_metadata', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('students',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('grade', sa.String(), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('medical_conditions', sa.JSON(), nullable=True),
    sa.Column('fitness_level', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('activity_category_association',
        sa.Column('activity_id', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], )
    )
    op.create_table('activity_plans',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('student_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('activity_progressions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.String(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('current_level', sa.Enum('BEGINNER', 'INTERMEDIATE', 'ADVANCED', name='difficultylevel'), nullable=False),
        sa.Column('improvement_rate', sa.Float(), nullable=False),
        sa.Column('last_assessment_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('class_students',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('class_id', sa.String(), nullable=False),
    sa.Column('student_id', sa.String(), nullable=False),
    sa.Column('enrollment_date', sa.DateTime(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('exercises',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('sets', sa.Integer(), nullable=False),
        sa.Column('reps', sa.Integer(), nullable=False),
        sa.Column('rest_time_seconds', sa.Integer(), nullable=False),
        sa.Column('technique_notes', sa.String(), nullable=False),
        sa.Column('progression_steps', sa.JSON(), nullable=True),
        sa.Column('regression_steps', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('risk_assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(), nullable=False),
        sa.Column('hazards', sa.JSON(), nullable=True),
        sa.Column('control_measures', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('routines',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('class_id', sa.String(), nullable=False),
    sa.Column('duration_minutes', sa.Integer(), nullable=False),
    sa.Column('focus_areas', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('safety_incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.String(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('incident_type', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('action_taken', sa.String(), nullable=False),
        sa.Column('incident_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('student_activity_performances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.String(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('student_activity_preferences',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('student_id', sa.String(), nullable=False),
    sa.Column('activity_type', sa.Enum('WARM_UP', 'SKILL_DEVELOPMENT', 'FITNESS_TRAINING', 'GAME', 'COOL_DOWN', name='activitytype'), nullable=False),
    sa.Column('preference_score', sa.Float(), nullable=False),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('activity_plan_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.String(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ),
        sa.ForeignKeyConstraint(['plan_id'], ['activity_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('routine_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('routine_id', sa.String(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ),
        sa.ForeignKeyConstraint(['routine_id'], ['routines.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # Drop new tables first
    op.drop_table('routine_activities')
    op.drop_table('activity_plan_activities')
    op.drop_table('student_activity_preferences')
    op.drop_table('student_activity_performances')
    op.drop_table('safety_incidents')
    op.drop_table('routines')
    op.drop_table('risk_assessments')
    op.drop_table('exercises')
    op.drop_table('class_students')
    op.drop_table('activity_progressions')
    op.drop_table('activity_plans')
    op.drop_table('activity_category_association')
    op.drop_table('students')
    op.drop_table('safety_checks')
    op.drop_table('equipment_checks')
    op.drop_table('environmental_checks')
    op.drop_table('classes')
    op.drop_table('activities')

    # Recreate old tables
    op.create_table('assistant_capabilities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
