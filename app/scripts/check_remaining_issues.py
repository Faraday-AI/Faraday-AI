#!/usr/bin/env python3
"""
Check Remaining Issues Script

This script checks for any remaining foreign key or dependency issues
that might be causing table creation failures.
"""

import os
import re
from pathlib import Path

# Define the failing tables to investigate
FAILING_TABLES = [
    'safety_incidents',
    'safety_measures',
    'risk_assessments',
    'lesson_plans',
    'dashboard_context_gpts',
    'gpt_categories',
    'dashboard_widgets',
    'educational_classes',
    'class_attendance',
    'class_schedules',
    'educational_class_students',
    'rate_limits',
    'rate_limit_policies',
    'rate_limit_metrics',
    'rate_limit_logs',
    'user_preference_template_assignments',
    'user_management_preferences',
    'circuit_breaker_metrics'
]

def check_foreign_key_references():
    """Check for foreign key references that might be causing issues."""
    app_dir = Path(__file__).parent.parent
    print("Checking foreign key references for failing tables...")
    for table in FAILING_TABLES:
        print(f"Checking table: {table}")
        # Find all Python files that might reference this table
        for root, dirs, files in os.walk(app_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        # Look for foreign key references to this table
                        fk_pattern = rf'ForeignKey\(["\"]{table}\.id["\"]'
                        matches = re.findall(fk_pattern, content)
                        if matches:
                            print(f"  Found FK reference in {file_path.relative_to(app_dir)}: {matches}")
                        # Look for relationship references
                        rel_pattern = rf'relationship\(["\"][^"\"]*{table}[^"\"]*["\"]'
                        rel_matches = re.findall(rel_pattern, content)
                        if rel_matches:
                            print(f"  Found relationship reference in {file_path.relative_to(app_dir)}: {rel_matches}")
                    except Exception as e:
                        print(f"  Error reading {file_path}: {e}")

def check_table_definitions():
    """Check if the failing tables are properly defined."""
    app_dir = Path(__file__).parent.parent
    print("\nChecking table definitions...")
    for table in FAILING_TABLES:
        print(f"\nLooking for table definition: {table}")
        found = False
        for root, dirs, files in os.walk(app_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        # Look for table definition
                        table_pattern = rf'__tablename__\s*=\s*["\"]{table}["\"]'
                        matches = re.findall(table_pattern, content)
                        if matches:
                            print(f"  Found table definition in {file_path.relative_to(app_dir)}")
                            found = True
                    except Exception as e:
                        print(f"  Error reading {file_path}: {e}")
        if not found:
            print(f"  WARNING: No table definition found for {table}")

def check_imports():
    """Check for import issues that might prevent table creation."""
    app_dir = Path(__file__).parent.parent
    print("\nChecking for import issues...")
    # Check the main models __init__.py
    models_init = app_dir / 'models' / '__init__.py'
    if models_init.exists():
        try:
            with open(models_init, 'r', encoding='utf-8') as f:
                content = f.read()
            # Look for any import errors or missing imports
            print("  Checking models/__init__.py for import issues...")
            # Check for common import patterns that might be missing
            missing_imports = []
            for table in FAILING_TABLES:
                if table not in content:
                    missing_imports.append(table)
            if missing_imports:
                print(f"    Tables not found in imports: {missing_imports}")
        except Exception as e:
            print(f"  Error reading {models_init}: {e}")

if __name__ == "__main__":
    print("Checking remaining issues for failing tables...")
    check_foreign_key_references()
    check_table_definitions()
    check_imports()
    print("\nCheck complete!") 