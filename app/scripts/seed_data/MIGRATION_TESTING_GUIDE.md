# Migration Testing Guide

## Overview

Before running the main seed script, **ALWAYS run the migration SQL validation tests** to catch errors before they occur in the main script.

## Quick Start

### Test Phase 5 and Phase 6 (Most Critical)

```bash
# In Docker container
docker-compose exec app python app/scripts/seed_data/test_all_phase_migrations.py
```

### Test Specific Phase

```bash
# Test Phase 5 only
docker-compose exec app python app/scripts/seed_data/test_all_phase_migrations.py --phase 5

# Test Phase 6 only
docker-compose exec app python app/scripts/seed_data/test_all_phase_migrations.py --phase 6

# Test Phase 1 & 2
docker-compose exec app python app/scripts/seed_data/test_all_phase_migrations.py --phase 1
```

### Test All Phases

```bash
docker-compose exec app python app/scripts/seed_data/test_all_phase_migrations.py --all
```

## What These Tests Catch

### Phase 5 Tests (`test_phase5_migration_sql.py`)

1. **Type Coercion Errors (JSON/JSONB)**
   - ✅ Verifies all `COALESCE` statements have explicit `::jsonb` casts
   - ✅ Tests: `context_data`, `content`, `key_points`, `topics`, `summary_metadata`, `backup_content`, `backup_metadata`, `metric_metadata`, `sharing_permissions`

2. **Missing Column Errors**
   - ✅ Verifies `sharing_metadata` is NOT referenced (column doesn't exist)
   - ✅ Verifies `metadata` column exists (should be used instead)

3. **Table Schema Validation**
   - ✅ Verifies all source tables exist
   - ✅ Verifies all target tables exist
   - ✅ Verifies all required columns exist

4. **Query Syntax Validation**
   - ✅ Tests all migration queries can be parsed
   - ✅ Tests queries execute without syntax errors

### Phase 6 Tests (`test_phase6_migration_sql.py`)

1. **Type Coercion Errors (JSON/JSONB)**
   - ✅ Verifies `core_dashboard_widgets.configuration` has explicit cast
   - ✅ Verifies `beta_widgets.configuration` has explicit cast
   - ✅ Verifies `core_dashboard_widgets.size` has explicit cast

2. **Missing Column Errors**
   - ✅ Verifies `dashboard_notification_preferences` does NOT have `created_at`/`updated_at`
   - ✅ Verifies migration queries don't reference these columns

3. **Type Mismatch Errors (Integer = UUID)**
   - ✅ Verifies `teacher_preferences.teacher_id` type
   - ✅ Verifies `physical_education_teachers.id` type
   - ✅ Tests correct JOIN query (uses `physical_education_teachers`)
   - ✅ Tests incorrect JOIN query fails (if `teacher_registrations` used)

4. **Table Schema Validation**
   - ✅ Verifies all source tables exist
   - ✅ Verifies all target tables exist
   - ✅ Verifies all required columns exist

## Integration with Main Script

### Option 1: Run Tests Before Main Script (Recommended)

```bash
# Step 1: Run validation tests
docker-compose exec app python app/scripts/seed_data/test_all_phase_migrations.py

# Step 2: If tests pass, run main seed script
docker-compose exec app python app/scripts/seed_data/seed_database.py
```

### Option 2: Add to CI/CD Pipeline

Add these tests to your CI/CD pipeline to catch errors automatically:

```yaml
- name: Test Migration SQL
  run: |
    docker-compose exec app python app/scripts/seed_data/test_all_phase_migrations.py --all
```

## Test Output

### Success Output

```
✅ All Phase 5 migration SQL tests passed!
   Migration queries are ready to run.
✅ All Phase 6 migration SQL tests passed!
   Migration queries are ready to run.
✅ All tests PASSED!
   ✅ Migration queries are validated and ready to run.
   ✅ You can now safely run the main migration script.
```

### Error Output

```
❌ Found 3 ERROR(S):
  ❌ gpt_interaction_contexts.context_data: Type coercion error - ...
  ❌ shared_contexts.sharing_metadata: Column does not exist
  ❌ dashboard_notification_preferences: Missing column created_at

⚠️  Migration will FAIL if these errors are not fixed!
```

## Common Errors Caught

### 1. JSON/JSONB Type Coercion

**Error:**
```
COALESCE could not convert type jsonb to json
```

**Fix:**
Add explicit `::jsonb` cast:
```sql
-- ❌ Wrong
COALESCE(gic.context_data, '{}'::jsonb)

-- ✅ Correct
COALESCE(gic.context_data::jsonb, '{}'::jsonb)
```

### 2. Missing Column

**Error:**
```
column "created_at" of relation "dashboard_notification_preferences" does not exist
```

**Fix:**
Remove column from INSERT statement:
```sql
-- ❌ Wrong
INSERT INTO dashboard_notification_preferences (
    user_id, ..., created_at, updated_at
)

-- ✅ Correct
INSERT INTO dashboard_notification_preferences (
    user_id, ...
    -- created_at and updated_at removed
)
```

### 3. Type Mismatch in JOIN

**Error:**
```
operator does not exist: integer = uuid
```

**Fix:**
Use correct table with matching types:
```sql
-- ❌ Wrong
FROM teacher_preferences tp
INNER JOIN teacher_registrations tr ON tp.teacher_id = tr.id

-- ✅ Correct
FROM teacher_preferences tp
INNER JOIN physical_education_teachers pet ON tp.teacher_id = pet.id
INNER JOIN users u ON u.id = pet.user_id
```

## Best Practices

1. **Always run tests before main script** - Catch errors early
2. **Fix all errors before proceeding** - Don't ignore warnings
3. **Run tests after code changes** - Verify fixes worked
4. **Add tests to CI/CD** - Prevent regressions
5. **Document new errors** - Update tests if schema changes

## Test Files

- `test_phase5_migration_sql.py` - Phase 5 SQL validation
- `test_phase6_migration_sql.py` - Phase 6 SQL validation
- `test_phase1_phase2_migration.py` - Phase 1 & 2 migration tests
- `test_all_phase_migrations.py` - Test runner for all phases

## Troubleshooting

### Tests Fail with "Table does not exist"

**Solution:** Run migrations first:
```bash
docker-compose exec app alembic upgrade head
```

### Tests Fail with "Column does not exist"

**Solution:** Check if schema has changed. Update test file or migration file accordingly.

### Tests Pass But Migration Still Fails

**Solution:** 
1. Check for data-specific issues (NULL values, constraints)
2. Verify foreign key constraints
3. Check for duplicate key violations

## Next Steps

After tests pass:
1. ✅ Run main seed script
2. ✅ Verify migration results
3. ✅ Check data integrity
4. ✅ Run integration tests

