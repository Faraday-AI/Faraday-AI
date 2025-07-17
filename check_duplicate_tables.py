#!/usr/bin/env python3
"""
Script to identify duplicate table names in the models.
This helps debug table creation failures.
"""

import os
import sys
import re
from collections import defaultdict

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

def find_table_names():
    """Find all table names defined in the models."""
    table_names = defaultdict(list)
    
    # Walk through all Python files in the app/models directory
    models_dir = os.path.join(os.path.dirname(__file__), 'app', 'models')
    
    for root, dirs, files in os.walk(models_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, os.path.dirname(__file__))
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Look for __tablename__ = "table_name" patterns
                    matches = re.findall(r'__tablename__\s*=\s*["\']([^"\']+)["\']', content)
                    
                    for table_name in matches:
                        table_names[table_name].append(relative_path)
                        
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return table_names

def main():
    """Main function to identify duplicate table names."""
    print("Checking for duplicate table names...")
    print("=" * 50)
    
    table_names = find_table_names()
    
    duplicates_found = False
    
    for table_name, files in table_names.items():
        if len(files) > 1:
            duplicates_found = True
            print(f"\nDUPLICATE TABLE: {table_name}")
            print(f"Found in {len(files)} files:")
            for file in files:
                print(f"  - {file}")
    
    if not duplicates_found:
        print("\nNo duplicate table names found!")
    else:
        print(f"\n{'=' * 50}")
        print("DUPLICATE TABLE NAMES DETECTED!")
        print("These are likely causing table creation failures.")
        print("You need to rename one of the duplicate table definitions.")
    
    # Also show all table names for reference
    print(f"\n{'=' * 50}")
    print("ALL TABLE NAMES:")
    for table_name in sorted(table_names.keys()):
        print(f"  {table_name}")

if __name__ == "__main__":
    main() 