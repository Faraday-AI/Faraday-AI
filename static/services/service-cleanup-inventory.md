# Service/Subservice Cleanup Inventory

## Physical Education Service

### Current Locations:
1. `services/phys-ed-teacher.html` (main service file)
2. `services/services_subpages/phys-ed/` (newer files)
3. `services/services_subpages/phys-ed-teacher/` (additional content)

### Merge Plan:

#### Step 1: Directory Structure
1. Keep main service file:
   - `services/phys-ed-teacher.html` ✓

2. Primary directory:
   - `services/services_subpages/phys-ed/` (main directory)

3. Additional content to merge:
   - `services/services_subpages/phys-ed-teacher/`
     - Subdirectories:
       - `resource-integration/`
       - `content-sequencing/`
       - `activity-design/`
       - `curriculum-alignment/`
     - HTML files:
       - `analytics.html`
       - `differentiated-instruction.html`
       - `drivers-education.html`
       - `health-education.html`
       - `skill-development.html`
       - `resource-generation.html`
       - `ai-customization.html`
       - `curriculum-input.html`
       - `student-progress.html`
       - `skill-evaluation.html`
       - `assessment-tools.html`
       - `game-design.html`

#### Step 2: Merge Process
1. First Phase - Subdirectories:
   - Move `resource-integration/` to `phys-ed/`
   - Move `content-sequencing/` to `phys-ed/`
   - Move `activity-design/` to `phys-ed/`
   - Move `curriculum-alignment/` to `phys-ed/`

2. Second Phase - HTML Files:
   - Compare and merge content with existing files
   - Keep newer versions where applicable
   - Preserve unique content from both directories

3. Third Phase - Cleanup:
   - Remove empty directories
   - Update any internal links
   - Verify all content is accessible

### Progress Tracking:
- [ ] Phase 1: Subdirectories merge
- [ ] Phase 2: HTML files merge
- [ ] Phase 3: Cleanup and verification

## Math Service

### Current Locations:
1. `services/math-teacher/`
   - assets/ (empty)
   - subpages/
     - visual-aids/
     - problem-generation/
     - lesson-planning/
     - Multiple HTML files (25 files)

2. `services/math-teacher.bak/`
   - assets/ (empty)
   - subpages/
     - visual-aids/
     - problem-generation/
     - lesson-planning/
     - Multiple HTML files (28 files)

3. `services/services_subpages/math/` (empty)

### Action Plan for Math:

#### Step 1: Directory Structure ✓
1. Create new structure:
   - `services/math-teacher.html` (main service file) ✓
   - `services/services_subpages/math/` (new directory)

2. Files to keep:
   - Main service file: `math.html` (15KB, 372 lines) ✓
   - Core feature files:
     - `lesson-planning.html`
     - `assessment.html`
     - `visualization.html`
     - `curriculum-aligned.html`
     - `real-time-assessment.html`
     - `adaptive-learning.html`
     - `problem-generation.html`

3. Subdirectories to merge:
   - `visual-aids/`
   - `problem-generation/`
   - `lesson-planning/`

#### Step 2: Merge Process
1. First Phase - Main Service File: ✓
   - Create `math-teacher.html` based on `math.html` ✓
   - Update styling to match new format ✓
   - Ensure all links are updated ✓

2. Second Phase - Core Features:
   - Move and update core feature files to `services_subpages/math/`
   - Update styling and navigation
   - Verify all internal links

3. Third Phase - Subdirectories:
   - Move and merge content from both directories
   - Resolve any conflicts
   - Update file paths and links

4. Fourth Phase - Cleanup:
   - Remove empty directories
   - Verify all content is accessible
   - Update any remaining links

### Progress Tracking:
- [x] Phase 1: Main service file creation
- [ ] Phase 2: Core features migration
- [ ] Phase 3: Subdirectories merge
- [ ] Phase 4: Cleanup and verification

## History Service

### Current Locations:
1. `