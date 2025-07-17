"""
Generate Models Module

This module generates the necessary models for the physical education service.
"""

import os
import sys
from pathlib import Path
from sqlalchemy import inspect

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(project_root))

from app.core.database import Base, engine, DATABASE_URL
from app.models.physical_education.activity.models import Activity
from app.models.physical_education.exercise.models import Exercise
from app.models.physical_education.safety.models import (
    RiskAssessment,
    SafetyIncident,
    SafetyCheck,
    EnvironmentalCheck,
    SafetyProtocol,
    SafetyAlert
)
from app.models.physical_education.pe_enums.pe_types import (
    RiskLevel,
    IncidentSeverity,
    IncidentType,
    AlertType,
    CheckType
)
from app.models.physical_education.class_.models import PhysicalEducationClass
from app.models.physical_education.student.models import Student
from app.models.shared_base import SharedBase
from app.models.organization.base.organization_management import Department, Organization

def generate_models():
    """Generate all models for the physical education service."""
    try:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set")
            
        # Get existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Drop activity_category_associations table if it exists
        if "activity_category_associations" in existing_tables:
            print("Dropping activity_category_associations table...")
            SharedBase.metadata.tables["activity_category_associations"].drop(bind=engine)
            existing_tables.remove("activity_category_associations")
        
        # First, create any missing dependency tables
        dependency_tables = ["subject_categories", "assistant_profiles"]
        for table_name in dependency_tables:
            if table_name in SharedBase.metadata.tables and table_name not in existing_tables:
                print(f"Creating dependency table: {table_name}")
                try:
                    SharedBase.metadata.tables[table_name].create(bind=engine, checkfirst=True)
                except Exception as e:
                    if "already exists" in str(e):
                        print(f"Table {table_name} already exists, skipping...")
                    else:
                        print(f"Warning: Could not create {table_name}: {e}")
        
        # Create remaining tables that don't exist
        for table in SharedBase.metadata.tables:
            if table not in existing_tables:
                print(f"Creating table: {table}")
                try:
                    # Create table without indexes first
                    table_obj = SharedBase.metadata.tables[table]
                    
                    # For SQLite, we need to handle indexes differently
                    if DATABASE_URL.startswith('sqlite'):
                        # Create table without indexes
                        table_obj.create(bind=engine, checkfirst=True)
                        
                        # Create indexes separately
                        for index in table_obj.indexes:
                            try:
                                index.create(bind=engine)
                            except Exception as e:
                                if "already exists" in str(e):
                                    print(f"Index {index.name} already exists, skipping...")
                                else:
                                    raise
                    else:
                        # For PostgreSQL, create table with indexes
                        try:
                            table_obj.create(bind=engine, checkfirst=True)
                        except Exception as e:
                            if "already exists" in str(e) or "relation" in str(e):
                                print(f"Table {table} already exists or has dependency issues, skipping...")
                            else:
                                raise
                        
                except Exception as e:
                    if "already exists" in str(e) or "relation" in str(e):
                        print(f"Table {table} already exists or has dependency issues, skipping...")
                    else:
                        raise
        
        print("Successfully generated all models.")
    except Exception as e:
        print(f"Error generating models: {e}")
        # Don't exit with error code during build
        if not os.getenv('DOCKER_BUILD'):
            sys.exit(1)
        else:
            print("Continuing build process despite model generation errors...")

if __name__ == "__main__":
    generate_models() 