"""add initial access control data

Revision ID: add_initial_access_control_data
Revises: add_access_control_models
Create Date: 2024-04-30 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
import uuid

# revision identifiers, used by Alembic.
revision = 'add_initial_access_control_data'
down_revision = 'add_access_control_models'
branch_labels = None
depends_on = None

def upgrade():
    # Create system roles
    roles_table = sa.table(
        'roles',
        sa.column('id', sa.String),
        sa.column('name', sa.String),
        sa.column('description', sa.String),
        sa.column('is_system', sa.Boolean),
        sa.column('is_template', sa.Boolean),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime)
    )
    
    system_roles = [
        {
            'id': str(uuid.uuid4()),
            'name': 'system_admin',
            'description': 'System administrator with full access to all resources',
            'is_system': True,
            'is_template': False,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'tool_manager',
            'description': 'Manager with access to manage tools and integrations',
            'is_system': True,
            'is_template': False,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'standard_user',
            'description': 'Standard user with basic access to tools',
            'is_system': True,
            'is_template': False,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    ]
    
    op.bulk_insert(roles_table, system_roles)
    
    # Create system permissions
    permissions_table = sa.table(
        'permissions',
        sa.column('id', sa.String),
        sa.column('name', sa.String),
        sa.column('description', sa.String),
        sa.column('resource_type', sa.String),
        sa.column('action', sa.String),
        sa.column('scope', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime)
    )
    
    system_permissions = [
        # System-wide permissions
        {
            'id': str(uuid.uuid4()),
            'name': 'system_administer',
            'description': 'Full system administration access',
            'resource_type': 'system',
            'action': 'administer',
            'scope': '*',
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        
        # User management permissions
        {
            'id': str(uuid.uuid4()),
            'name': 'user_manage',
            'description': 'Manage user accounts and settings',
            'resource_type': 'user',
            'action': 'manage',
            'scope': '*',
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        
        # Tool management permissions
        {
            'id': str(uuid.uuid4()),
            'name': 'tool_manage',
            'description': 'Manage tools and their configurations',
            'resource_type': 'tool',
            'action': 'manage',
            'scope': '*',
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'tool_execute',
            'description': 'Execute tools and use their features',
            'resource_type': 'tool',
            'action': 'execute',
            'scope': '*',
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        
        # API permissions
        {
            'id': str(uuid.uuid4()),
            'name': 'api_manage',
            'description': 'Manage API integrations and configurations',
            'resource_type': 'api',
            'action': 'manage',
            'scope': '*',
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'api_execute',
            'description': 'Execute API integrations',
            'resource_type': 'api',
            'action': 'execute',
            'scope': '*',
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    ]
    
    op.bulk_insert(permissions_table, system_permissions)
    
    # Create role-permission assignments
    role_permission_table = sa.table(
        'role_permission',
        sa.column('role_id', sa.String),
        sa.column('permission_id', sa.String),
        sa.column('created_at', sa.DateTime)
    )
    
    # Get the IDs of the roles and permissions we just created
    connection = op.get_bind()
    admin_role = connection.execute(
        sa.text("SELECT id FROM roles WHERE name = 'system_admin'")
    ).fetchone()
    manager_role = connection.execute(
        sa.text("SELECT id FROM roles WHERE name = 'tool_manager'")
    ).fetchone()
    user_role = connection.execute(
        sa.text("SELECT id FROM roles WHERE name = 'standard_user'")
    ).fetchone()
    
    system_permission = connection.execute(
        sa.text("SELECT id FROM permissions WHERE name = 'system_administer'")
    ).fetchone()
    user_manage_permission = connection.execute(
        sa.text("SELECT id FROM permissions WHERE name = 'user_manage'")
    ).fetchone()
    tool_manage_permission = connection.execute(
        sa.text("SELECT id FROM permissions WHERE name = 'tool_manage'")
    ).fetchone()
    tool_execute_permission = connection.execute(
        sa.text("SELECT id FROM permissions WHERE name = 'tool_execute'")
    ).fetchone()
    api_manage_permission = connection.execute(
        sa.text("SELECT id FROM permissions WHERE name = 'api_manage'")
    ).fetchone()
    api_execute_permission = connection.execute(
        sa.text("SELECT id FROM permissions WHERE name = 'api_execute'")
    ).fetchone()
    
    role_permissions = [
        # System Admin permissions
        {'role_id': admin_role[0], 'permission_id': system_permission[0], 'created_at': datetime.utcnow()},
        {'role_id': admin_role[0], 'permission_id': user_manage_permission[0], 'created_at': datetime.utcnow()},
        {'role_id': admin_role[0], 'permission_id': tool_manage_permission[0], 'created_at': datetime.utcnow()},
        {'role_id': admin_role[0], 'permission_id': tool_execute_permission[0], 'created_at': datetime.utcnow()},
        {'role_id': admin_role[0], 'permission_id': api_manage_permission[0], 'created_at': datetime.utcnow()},
        {'role_id': admin_role[0], 'permission_id': api_execute_permission[0], 'created_at': datetime.utcnow()},
        
        # Tool Manager permissions
        {'role_id': manager_role[0], 'permission_id': tool_manage_permission[0], 'created_at': datetime.utcnow()},
        {'role_id': manager_role[0], 'permission_id': tool_execute_permission[0], 'created_at': datetime.utcnow()},
        {'role_id': manager_role[0], 'permission_id': api_manage_permission[0], 'created_at': datetime.utcnow()},
        {'role_id': manager_role[0], 'permission_id': api_execute_permission[0], 'created_at': datetime.utcnow()},
        
        # Standard User permissions
        {'role_id': user_role[0], 'permission_id': tool_execute_permission[0], 'created_at': datetime.utcnow()},
        {'role_id': user_role[0], 'permission_id': api_execute_permission[0], 'created_at': datetime.utcnow()}
    ]
    
    op.bulk_insert(role_permission_table, role_permissions)
    
    # Create role hierarchy
    role_hierarchy_table = sa.table(
        'role_hierarchy',
        sa.column('parent_role_id', sa.String),
        sa.column('child_role_id', sa.String),
        sa.column('created_at', sa.DateTime)
    )
    
    role_hierarchy = [
        {'parent_role_id': admin_role[0], 'child_role_id': manager_role[0], 'created_at': datetime.utcnow()},
        {'parent_role_id': manager_role[0], 'child_role_id': user_role[0], 'created_at': datetime.utcnow()}
    ]
    
    op.bulk_insert(role_hierarchy_table, role_hierarchy)

def downgrade():
    # Remove role hierarchy
    op.execute("DELETE FROM role_hierarchy")
    
    # Remove role-permission assignments
    op.execute("DELETE FROM role_permission")
    
    # Remove permissions
    op.execute("DELETE FROM permissions")
    
    # Remove roles
    op.execute("DELETE FROM roles") 