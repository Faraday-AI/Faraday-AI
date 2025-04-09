# Button and Path Context Documentation

## Issue History and Resolution Attempts

### Curriculum Alignment "Learn More" Button
1. Initial Issue: Button not working
2. Attempted Fixes:
   - Checked file paths and structure
   - Verified JavaScript event handlers
   - Added `data-href` attribute to feature card (WORKED)
   - Modified JavaScript click handler to properly handle feature card clicks (WORKED)

### Back Button Navigation
1. Initial Issue: Back button redirecting to wrong page
2. Attempted Fixes:
   - Checked relative paths in HTML
   - Added specific back button event handler in JavaScript (WORKED)
   - Used capture phase to ensure handler runs first (WORKED)
   - Added `e.stopPropagation()` to prevent interference (WORKED)

### Resource Integration "Learn More" Button
1. Initial Issue: Button not working
2. Attempted Fixes:
   - Checked file structure and paths
   - Added `data-href` attribute to match working cards (WORKED)
   - Ensured consistent structure with other feature cards (WORKED)

### Duplicate Files and Directories
1. Issues Found:
   - Multiple index.html files in different locations
   - Duplicate feature directories
   - Inconsistent file naming
2. Resolution:
   - Standardized on single index.html in root directory
   - Removed duplicate feature directories
   - Enforced consistent naming convention
   - Maintained single source of truth for each feature

### Index.html Navigation
1. Issues:
   - Inconsistent navigation paths
   - Broken links due to duplicate files
2. Fixes:
   - Standardized all paths relative to root index.html
   - Updated navigation links to use consistent paths
   - Removed redundant index.html files
   - Ensured all features link back to main index.html

## Working Structure
All feature cards should follow this structure:
```html
<div class="feature-card" data-href="path/to/page.html">
    <div class="feature-icon">[icon]</div>
    <h3>Feature Title</h3>
    <p>Feature Description</p>
    <a href="path/to/page.html" class="feature-link">Learn More</a>
</div>
```

## Key Fixes Implemented
1. JavaScript click handler in services.js:
   - Added proper event handling for back buttons
   - Fixed feature card click handling
   - Ensured proper navigation paths
   - Used capture phase for back button events
   - Added stopPropagation to prevent interference

2. HTML Structure:
   - All feature cards must have `data-href` attribute
   - Back buttons must point to `../lesson-planning.html`
   - Feature links must match the `data-href` path
   - Consistent structure across all feature cards
   - Single index.html in root directory
   - No duplicate feature directories

## Directory Structure
```
phys-ed-teacher/
├── index.html (single source of truth)
├── lesson-planning.html
├── curriculum-alignment/
│   ├── curriculum-alignment.html
│   └── try-it.html
├── content-sequencing/
│   ├── content-sequencing.html
│   └── try-it.html
└── resource-integration/
    ├── resource-integration.html
    └── try-it.html
```

## Path Resolution
- All paths are relative to the current file location
- Back buttons use `../` to navigate up one level
- Feature links use relative paths within their feature directory
- JavaScript handles navigation for feature card clicks
- Back button navigation takes precedence over other click handlers
- All navigation paths relative to root index.html
- No duplicate paths or files allowed

## Best Practices
1. Always include `data-href` attribute on feature cards
2. Keep feature links consistent with `data-href` paths
3. Use proper relative paths for navigation
4. Maintain consistent directory structure across features
5. Use capture phase for critical event handlers
6. Prevent event propagation when necessary
7. Keep feature card structure consistent across all features
8. Maintain single source of truth for index.html
9. Avoid duplicate files and directories
10. Use consistent naming conventions
11. Keep all navigation paths relative to root 