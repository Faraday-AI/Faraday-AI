# Subservice Pages Restructuring - Context Note

## Current Status
- Paused restructuring to prioritize Docker setup
- Service is currently deployed on Render
- Frontend changes are planned but not implemented

## Completed Analysis
1. Identified duplicate service pages:
   - `math/` and `math-teacher/`
   - `phys-ed/` and `phys-ed-teacher/`
   - `admin/` and `admin-assistant/`

2. Verified current structure:
   - Teacher-specific directories contain the active, deployed content
   - General directories contain older/unused versions
   - All paths are referenced as `/static/services/services_subpages/[service]/`

3. CSS/JS Structure:
   - Using `/static/css/services.css` for main service pages
   - Using `/static/css/features.css` for feature pages
   - Using `/static/js/services.js` for service functionality
   - Using `/static/js/auth.js` for authentication

## Planned Consolidation
1. Move content FROM general directories INTO teacher-specific directories:
   - `math/` → `math-teacher/`
   - `phys-ed/` → `phys-ed-teacher/`
   - `admin/` → `admin-assistant/`

2. Maintain exact structure:
   - Keep same HTML layout
   - Preserve all CSS classes
   - Maintain navigation paths
   - Use correct CSS files (services.css/features.css)

## Next Steps After Docker Setup
1. Create new subdirectories in teacher-specific folders:
   - `core-math/` (for algebra, calculus, statistics)
   - `teaching-tools/` (for lesson planning, assessment)
   - `student-support/` (for problem solving, feedback)
   - `teacher-features/` (for analytics, customization)

2. Move files while maintaining:
   - Exact HTML structure
   - CSS/JS dependencies
   - Navigation paths
   - Deployment structure

3. Verify changes in Docker environment before deployment

## Important Notes
- All paths must remain exactly as they are for current deployment
- CSS and JavaScript must be maintained exactly as is
- Template structure must be preserved
- Changes should be tested in Docker before deployment

## Files to Consolidate
### Math Service
- From `math/`:
  - algebra.html
  - calculus.html
  - statistics.html
  - problem-solver.html
  - step-by-step.html
  - learning-feedback.html
  - math-tutor.html

- Into `math-teacher/`:
  - Keep existing structure
  - Add new subdirectories
  - Maintain all paths

### Physical Education Service
- From `phys-ed/`:
  - All content files
  - Maintain structure

- Into `phys-ed-teacher/`:
  - Keep existing structure
  - Add new subdirectories
  - Maintain all paths

### Admin Service
- From `admin/`:
  - All content files
  - Maintain structure

- Into `admin-assistant/`:
  - Keep existing structure
  - Add new subdirectories
  - Maintain all paths

## Deployment Considerations
- Changes must be tested in Docker first
- All paths must remain consistent
- CSS/JS must be preserved exactly
- Template structure must be maintained
- Changes should be verified before deployment to Render 