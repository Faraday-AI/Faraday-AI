#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')

from app.scripts.seed_data.seed_phase2_educational_system import seed_phase2_educational_system
from app.core.database import SessionLocal
import traceback

def test_phase2():
    session = SessionLocal()
    try:
        print('Running Phase 2 with detailed logging...')
        result = seed_phase2_educational_system(session)
        print(f'Phase 2 completed: {result}')
        session.commit()
        print('Phase 2 committed successfully')
    except Exception as e:
        print(f'Phase 2 failed: {e}')
        traceback.print_exc()
        session.rollback()
        print('Phase 2 rolled back')
    finally:
        session.close()

if __name__ == "__main__":
    test_phase2()
