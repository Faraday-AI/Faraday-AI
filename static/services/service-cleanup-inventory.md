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
   - assets/
   - subpages/

2. `services/math-teacher.bak/`
   - assets/
   - subpages/

3. `services/services_subpages/math/`
   - [Files to be inventoried]

### Action Plan for Math:
[To be completed after Physical Education cleanup]

## History Service

### Current Locations:
1. `services/history-teacher/`
   - assets/
   - subpages/

2. `services/services_subpages/history/`
   - [Files to be inventoried]

### Action Plan for History:
[To be completed after Math cleanup]

## Science Service

### Current Locations:
1. `services/science-teacher/`
   - assets/
   - subpages/

2. `services/services_subpages/science/`
   - [Files to be inventoried]

### Action Plan for Science:
[To be completed after History cleanup]

## Language Arts Service

### Current Locations:
1. `services/language-arts-teacher/`
   - assets/
   - subpages/

2. `services/services_subpages/language-arts/`
   - [Files to be inventoried]

### Action Plan for Language Arts:
[To be completed after Science cleanup]

## Admin Assistant Service

### Current Locations:
1. `services/admin-assistant/`
   - assets/
   - subpages/

2. `services/admin-assistant.bak/`
   - assets/
   - subpages/

3. `services/services_subpages/admin-assistant/`
   - [Files to be inventoried]

### Action Plan for Admin Assistant:
[To be completed after Language Arts cleanup]

## Progress Tracking

- [ ] Physical Education Service cleanup
- [ ] Math Service cleanup
- [ ] History Service cleanup
- [ ] Science Service cleanup
- [ ] Language Arts Service cleanup
- [ ] Admin Assistant Service cleanup 