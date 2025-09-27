# HANDOFF DOCUMENT: Phase 2 Database Seeding Issues

## Project Overview
**Project**: Faraday-AI Physical Education Management System  
**Database**: PostgreSQL running in Docker container  
**Environment**: Development with full data recreation on each run  
**Current Status**: 228/457 tables populated (down from 229, need to reach 238+)

## Database Architecture
- **Database Name**: `faraday_ai` (PostgreSQL)
- **Container**: `faraday-ai-db-1` via Docker Compose
- **Connection**: Via `docker-compose exec app` commands
- **Data Strategy**: Full CASCADE DROP at start, then recreate all data
- **Script Location**: `/app/app/scripts/seed_data/seed_database.py`

## The Core Problem
**Phase 2 Educational System functions work individually but fail silently in the full script context**, causing 5 critical tables to show 0 records:

### Failing Tables (0 records each):
1. `courses` - Should have 25 records
2. `assignments` - Should have 50+ records  
3. `course_enrollments` - Should have 100+ records
4. `grades` - Should have 200+ records
5. `curriculum_standard_association` - Should have 50+ records

### Working Phase 2 Tables (have data):
- `educational_teachers`: 32 records ✅
- `educational_classes`: 192 records ✅
- `educational_class_students`: 4,800 records ✅
- `curriculum`: 300 records ✅
- `curriculum_lessons`: 600 records ✅
- `curriculum_standards`: 50 records ✅

## Technical Context

### Phase Execution Order:
1. **Phase 1**: Foundation (users, schools, activities) - ✅ Working
2. **Phase 2**: Educational System - ⚠️ **PARTIALLY FAILING**
3. **Phase 3**: Health & Fitness - ✅ Working (41/41 tables)
4. **Phase 4**: Safety & Risk Management - ✅ Working (35/35 tables)  
5. **Phase 5**: Advanced Analytics & AI - ✅ Working (36/36 tables)

### Key Files:
- **Main Script**: `Faraday-AI/app/scripts/seed_data/seed_database.py`
- **Phase 2 Logic**: `Faraday-AI/app/scripts/seed_data/seed_phase2_educational_system.py`
- **Functions Failing**: `seed_courses()`, `seed_assignments()`, `seed_course_enrollments()`, `seed_grades()`, `seed_curriculum_standard_associations()`

## What We've Tried (Failed Approaches)

1. **Added debug output** - Functions not even being called or failing before debug output
2. **Fixed "skip if existing" logic** - Changed to always recreate data in development
3. **Added session.commit() calls** - After each Phase 2 function to prevent rollbacks
4. **Made functions flexible** - To work with whatever data Phase 1 creates
5. **Fixed foreign key constraints** - Only use IDs from correct tables
6. **Removed hardcoded fallbacks** - Functions should adapt to existing data

## Current State of Code

### Phase 2 Functions Status:
- **`seed_courses()`**: Has debug output, flexible user lookup, always recreates data
- **`seed_assignments()`**: Similar fixes applied
- **`seed_course_enrollments()`**: Similar fixes applied  
- **`seed_grades()`**: Similar fixes applied
- **`seed_curriculum_standard_associations()`**: Similar fixes applied

### Debug Output Added:
```python
print(f"  🔍 Looking for user data in tables: {possible_user_tables}")
print(f"  📊 {table_name}: {len(user_ids)} records")
```

**Note**: This debug output is NOT appearing in the terminal, suggesting functions are failing before reaching this point.

## Critical Constraints

1. **NO DATA DELETION**: Only the initial CASCADE DROP should remove data
2. **DEVELOPMENT MODE**: Data changes each run, functions must be flexible
3. **HARDCODED TABLE NAMES**: Table names are fixed, only data within changes
4. **TRANSACTION ROLLBACKS**: Later phases may cause rollbacks that undo Phase 2 data

## What the New Agent Needs to Do

### Immediate Goals:
1. **Identify why Phase 2 functions fail in full script** but work individually
2. **Get table count back to 238+** (currently 228, was 229)
3. **Fix the 5 failing Phase 2 tables** without breaking working ones
4. **Prevent further data loss** - stop making changes that reduce table count

### Debugging Strategy:
1. **Run Phase 2 functions individually** to confirm they work
2. **Add comprehensive error logging** to catch silent failures
3. **Check transaction state** during full script execution
4. **Identify rollback source** that's undoing Phase 2 data
5. **Test minimal reproduction** of the full script issue

### Key Questions to Answer:
- Why don't the debug print statements appear in the terminal?
- What's causing the silent failures in the full script context?
- Are there transaction rollbacks happening that undo Phase 2 data?
- Is there a dependency issue between Phase 1 and Phase 2?

## Environment Setup

```bash
# Navigate to project
cd /Users/joemartucci/Projects/New\ Faraday\ Cursor/Faraday-AI

# Activate virtual environment  
source venv/bin/activate

# Run full script
docker-compose exec app python -c "import sys; sys.path.insert(0, '/app'); from app.scripts.seed_data.seed_database import seed_database; result = seed_database(); print(f'Full database seeding completed with {result} total records')"

# Check specific table counts
docker-compose exec db psql -U postgres -d faraday_ai -c "SELECT 'courses' as table_name, COUNT(*) as record_count FROM courses UNION ALL SELECT 'assignments', COUNT(*) FROM assignments UNION ALL SELECT 'course_enrollments', COUNT(*) FROM course_enrollments UNION ALL SELECT 'grades', COUNT(*) FROM grades ORDER BY table_name;"
```

## Success Criteria

- **Table Count**: 238+ populated tables (currently 228)
- **Phase 2 Complete**: All 5 failing tables must have data
- **No Regression**: Don't lose any currently working tables
- **Stable**: Full script run should consistently produce same results

## Files to Focus On

1. **`seed_phase2_educational_system.py`** - Main Phase 2 logic
2. **`seed_database.py`** - Main orchestration script
3. **Terminal output** - Look for missing debug messages and error patterns

## Handoff Notes

The new agent should start by running the full script and carefully analyzing why the Phase 2 debug output doesn't appear, then systematically debug the transaction/execution flow issues. The current agent has made multiple attempts that have resulted in data loss (229 → 228 tables), so a fresh approach is needed.

## Current Working Directory
- **Path**: `/Users/joemartucci/Projects/New Faraday Cursor/Faraday-AI`
- **Virtual Environment**: `venv/bin/activate` (already activated)
- **Docker Services**: Running via `docker-compose`

## Last Known Good State
- **Table Count**: 229/457 (before current regression)
- **Phase 2 Status**: 5 tables failing, rest working
- **Script Status**: Full script runs but Phase 2 functions fail silently

## Critical Missing Information

### User Rules & Constraints:
- **macOS Environment**: User is on macOS 24.4.0
- **Working Directory**: ALL files must be in Faraday-AI directory (`/Users/joemartucci/Projects/New Faraday Cursor/Faraday-AI`)
- **Development Philosophy**: "In development, code should not be removed; if something doesn't work, add, create, or rename code to make it work"
- **Data Strategy**: "The only time that any data should be removed from the database is in the beginning when we drop everything with cascade from that point on nothing else should be dropped ever again"
- **Approval Process**: User prefers to be asked before each action, especially file creation/modification

### Database Connection Details:
- **Host**: localhost (via Docker)
- **Port**: 5432 (default PostgreSQL)
- **Username**: postgres
- **Database**: faraday_ai
- **Connection Method**: `docker-compose exec db psql -U postgres -d faraday_ai`

### Phase 2 Function Execution Order:
```python
# In seed_phase2_educational_system.py around line 3070
print("Seeding courses...")
courses_count = seed_courses(session)
results['courses'] = courses_count
print(f"✅ Created {courses_count} courses")
```

### Known Working Phase 2 Functions:
- `seed_educational_teachers()` - Creates 32 records
- `seed_educational_classes()` - Creates 192 records  
- `seed_educational_class_students()` - Creates 4,800 records
- `seed_curriculum()` - Creates 300 records
- `seed_curriculum_lessons()` - Creates 600 records
- `seed_curriculum_standards()` - Creates 50 records

### Known Failing Phase 2 Functions:
- `seed_courses()` - Should create 25 records, creates 0
- `seed_assignments()` - Should create 50+ records, creates 0
- `seed_course_enrollments()` - Should create 100+ records, creates 0
- `seed_grades()` - Should create 200+ records, creates 0
- `seed_curriculum_standard_associations()` - Should create 50+ records, creates 0

### Error Patterns Observed:
- Functions work individually when tested in isolation
- Debug print statements don't appear in full script output
- No error messages or exceptions visible in terminal
- Silent failures suggest transaction rollbacks or early exits

### Phase 1 Data Available for Phase 2:
- **Users**: 32 records in `users` table
- **Students**: 4,171 records in `students` table
- **Schools**: 6 records in `schools` table
- **Activities**: 1,024 records in `activities` table
- **Curriculum**: 300 records in `curriculum` table
- **Standards**: 50 records in `curriculum_standards` table

### Transaction Management:
- Phase 2 has `session.commit()` calls after each function
- Later phases may cause rollbacks that undo Phase 2 data
- Need to identify which phase is causing the rollback

### Testing Commands:
```bash
# Test individual Phase 2 function
docker-compose exec app python -c "import sys; sys.path.insert(0, '/app'); from app.scripts.seed_data.seed_phase2_educational_system import seed_courses; from app.database import get_db; session = next(get_db()); result = seed_courses(session); print(f'Courses created: {result}')"

# Check Phase 2 table counts specifically
docker-compose exec db psql -U postgres -d faraday_ai -c "SELECT 'courses' as table, COUNT(*) as count FROM courses UNION ALL SELECT 'assignments', COUNT(*) FROM assignments UNION ALL SELECT 'course_enrollments', COUNT(*) FROM course_enrollments UNION ALL SELECT 'grades', COUNT(*) FROM grades UNION ALL SELECT 'curriculum_standard_association', COUNT(*) FROM curriculum_standard_association ORDER BY table;"
```

## Next Steps for New Agent
1. Read this handoff document completely
2. Run the full script to see current state
3. Test Phase 2 functions individually to confirm they work
4. Add comprehensive error logging to identify silent failures
5. Debug transaction rollback issues systematically
6. Focus on getting table count back to 238+ without regression
7. **CRITICAL**: Ask user for approval before making any changes
8. **CRITICAL**: Follow the "add, don't remove" development philosophy
