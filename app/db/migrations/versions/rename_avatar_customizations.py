"""rename avatar customizations table

Revision ID: rename_avatar_customizations
Revises: 
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'rename_avatar_customizations'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Rename the table
    op.rename_table('avatar_customizations', 'student_avatar_customizations')

def downgrade():
    # Rename the table back
    op.rename_table('student_avatar_customizations', 'avatar_customizations') 