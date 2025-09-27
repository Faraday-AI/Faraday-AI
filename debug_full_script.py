#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')

from app.scripts.seed_data.seed_database import seed_database
import traceback

def test_full_script():
    try:
        print('Running full script with detailed error logging...')
        result = seed_database()
        print(f'Script completed successfully: {result}')
    except Exception as e:
        print(f'Script failed with error: {e}')
        print('Full traceback:')
        traceback.print_exc()

if __name__ == "__main__":
    test_full_script()
