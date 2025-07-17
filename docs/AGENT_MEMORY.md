# Agent Memory Documentation

## Project Overview
- Project Name: Faraday-AI
- Working Directory: `/Users/joemartucci/Projects/New Faraday Cursor/Faraday-AI`
- Environment: macOS (darwin 24.3.0)
- Deployment: Local Server, Docker, and Render

## Recent Actions
1. Physical Education related files were deleted:
   - Models: routine.py, assessment.py, safety.py, exercise.py
   - Services: routine_service.py, assessment_system.py, safety_manager.py, workout_planner.py, activity_manager.py
   - API Routes: routine_routes.py, assessment.py, safety.py, exercise.py
   - Other: Various PE-related service files and scripts

## Current State
- Base models are intact in `app/models/base.py`
- Project structure includes:
  - app/ (main application code)
  - tests/ (test files)
  - docs/ (documentation)
  - docker/ (Docker configuration)
  - migrations/ (database migrations)
  - models/ (model definitions)
  - scripts/ (utility scripts)

## Important Rules
1. All files must be in Faraday-AI directory
2. No files should be created without explicit approval
3. No files should be moved without explicit approval
4. No files should be edited in wrong locations
5. No nested files should be created
6. No packages/dependencies should be removed without approval
7. No large code sections should be replaced without approval
8. No files should be created/edited in workspace or root directory
9. No duplicate files should be created
10. No files should be moved between directories without approval

## Testing Status
- Tests were previously running successfully
- Current testing issues need investigation
- Test configuration files present:
  - pytest.ini
  - requirements-test.txt
  - TESTING.md
  - COMPREHENSIVE_TESTING.md

## Next Steps
1. Investigate current test failures
2. Review test configuration
3. Check test dependencies
4. Verify test environment setup

## Important Notes
- Always check current working directory first
- Use absolute paths from workspace root
- Verify file existence before creating new files
- Double-check directory structures before making changes
- Take one action at a time and wait for explicit approval
- Preserve existing services and dependencies
- Be cautious with file operations 