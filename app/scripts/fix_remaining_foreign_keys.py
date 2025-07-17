#!/usr/bin/env python3
"""
Fix Remaining Foreign Key References Script

This script fixes the remaining foreign key references that are causing
table creation failures.
"""

import os
import re
from pathlib import Path

# Define the remaining foreign key reference fixes
REMAINING_FOREIGN_KEY_FIXES = {
    # Dashboard notification fixes
    'dashboard_notifications.id': 'dashboard_notification_models.id',
    
    # Goal-related fixes
    'fitness_goals.id': 'health_fitness_goals.id',
    
    # Competition-related fixes
    'competition_events.id': 'competition_base_events.id',
    'competition_participants.id': 'competition_base_participants.id',
    
    # Movement analysis fixes
    'movement_analyses.id': 'movement_analysis_analyses.id',
}

def fix_remaining_foreign_key_references():
    """Fix remaining foreign key references in model files."""
    
    # Get the app directory
    app_dir = Path(__file__).parent.parent
    
    # Find all Python files in the models directory
    model_files = []
    for root, dirs, files in os.walk(app_dir):
        for file in files:
            if file.endswith('.py'):
                model_files.append(Path(root) / file)
    
    print(f"Found {len(model_files)} Python files to check")
    
    fixed_files = []
    
    for file_path in model_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_modified = False
            
            # Fix foreign key references
            for old_ref, new_ref in REMAINING_FOREIGN_KEY_FIXES.items():
                if old_ref in content:
                    # Use regex to match ForeignKey patterns
                    pattern = rf'ForeignKey\s*\(\s*["\']{re.escape(old_ref)}["\']\s*\)'
                    replacement = f'ForeignKey("{new_ref}")'
                    
                    if re.search(pattern, content):
                        content = re.sub(pattern, replacement, content)
                        file_modified = True
                        print(f"  Fixed {old_ref} -> {new_ref} in {file_path.name}")
            
            # Write back if modified
            if file_modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(file_path)
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"\nFixed foreign key references in {len(fixed_files)} files:")
    for file_path in fixed_files:
        print(f"  - {file_path}")

if __name__ == "__main__":
    print("Fixing remaining foreign key references...")
    fix_remaining_foreign_key_references()
    print("Done!") 