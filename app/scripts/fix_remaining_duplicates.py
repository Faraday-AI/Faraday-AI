#!/usr/bin/env python3
"""
Script to identify and fix remaining duplicate table name conflicts.
"""

import os
import sys
import re
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def find_table_definitions():
    """Find all table name definitions in the codebase."""
    table_definitions = {}
    
    # Search through all Python files
    app_dir = Path(__file__).parent.parent
    for py_file in app_dir.rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find __tablename__ definitions
            matches = re.findall(r'__tablename__\s*=\s*["\']([^"\']+)["\']', content)
            for table_name in matches:
                if table_name not in table_definitions:
                    table_definitions[table_name] = []
                table_definitions[table_name].append(str(py_file))
                
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return table_definitions

def identify_duplicates(table_definitions):
    """Identify tables with multiple definitions."""
    duplicates = {}
    for table_name, files in table_definitions.items():
        if len(files) > 1:
            duplicates[table_name] = files
    return duplicates

def main():
    print("🔍 Finding table definitions...")
    table_definitions = find_table_definitions()
    
    print("🔍 Identifying duplicates...")
    duplicates = identify_duplicates(table_definitions)
    
    if not duplicates:
        print("✅ No duplicate table names found!")
        return
    
    print(f"\n❌ Found {len(duplicates)} duplicate table names:")
    for table_name, files in duplicates.items():
        print(f"\n📋 Table: {table_name}")
        for file_path in files:
            print(f"   📄 {file_path}")
    
    # Focus on the 19 failing tables
    failing_tables = [
        'safety_incidents', 'safety_measures', 'risk_assessments', 'lesson_plans',
        'dashboard_context_gpts', 'gpt_categories', 'dashboard_widgets', 'rate_limits',
        'educational_classes', 'class_attendance', 'class_schedules', 'educational_class_students',
        'progress_notes', 'rate_limit_policies', 'rate_limit_metrics', 'rate_limit_logs',
        'user_preference_template_assignments', 'user_management_preferences', 'circuit_breaker_metrics'
    ]
    
    print(f"\n🎯 Focusing on the 19 failing tables:")
    for table_name in failing_tables:
        if table_name in duplicates:
            print(f"\n📋 Table: {table_name}")
            for file_path in duplicates[table_name]:
                print(f"   📄 {file_path}")
        else:
            print(f"❓ Table {table_name} not found in duplicates - may be a different issue")

if __name__ == "__main__":
    main() 