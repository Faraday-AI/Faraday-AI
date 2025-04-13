# Button and Path Context Documentation

## Issue Description
The "Learn More" button in the Curriculum Alignment card was not working despite having the correct path. This was happening because:

1. The JavaScript in `services.js` was interfering with the navigation
2. The CSS was making the entire card clickable with `cursor: pointer`
3. The file structure had duplicate files in different locations
4. There were unnecessary index.html files causing path confusion
5. Files were duplicated in both main and subdirectories

## Attempted Solutions (What Didn't Work)

1. **Path Updates**:
   - Tried using `../curriculum-alignment/curriculum-alignment.html`
   - Tried using `curriculum-alignment/curriculum-alignment.html`
   - Tried using absolute paths
   - Tried using index.html in paths
   - Result: Path changes alone didn't fix the issue

2. **CSS Modifications**:
   - Removed `cursor: pointer` from feature cards
   - Added specific styles for `.feature-link`
   - Added hover effects
   - Result: CSS changes alone didn't fix the issue

3. **JavaScript Cleanup**:
   - Tried removing all unnecessary code from `services.js`
   - Attempted to clean up event listeners
   - Result: Simple cleanup didn't fix the issue

4. **File Structure Changes**:
   - Initially tried moving files between directories
   - Attempted to create new directories
   - Tried using index.html files
   - Result: File moving alone didn't fix the issue

## What Finally Worked

1. **Adding data-href Attribute**:
```html
<div class="feature-card" data-href="curriculum-alignment/curriculum-alignment.html">
```

2. **Updating JavaScript to Handle data-href**:
```javascript
document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('click', function(e) {
        if (e.target.tagName === 'A') {
            return;
        }
        const href = this.getAttribute('data-href');
        if (href) {
            window.location.href = href;
        }
    });
});
```

3. **Cleaning Up File Structure**:
   - Removed duplicate `curriculum-alignment.html` from `/lesson-planning/curriculum-alignment/`
   - Kept only the main file in `/curriculum-alignment/`
   - Verified correct file locations
   - Removed all unnecessary index.html files
   - Cleaned up duplicate directories

## Key Learnings

1. **JavaScript is Critical**:
   - The issue was primarily JavaScript-related
   - The `data-href` attribute was the key to making it work
   - Event handling needed to be properly managed

2. **File Structure Matters**:
   - Duplicate files can cause confusion
   - Correct file location is essential
   - Directory structure affects path resolution
   - Avoid using index.html unless absolutely necessary
   - Keep files in their proper directories without duplication

3. **Combination Approach**:
   - Single changes (just CSS, just paths) weren't enough
   - Needed combination of:
     - Correct file structure
     - Proper JavaScript handling
     - Appropriate HTML attributes
     - Clean directory structure
     - No duplicate files

## Common Pitfalls to Watch For

1. **Duplicate Files and Directories**: Always check for:
   - Duplicate files in different locations
   - Unnecessary index.html files
   - Files in both main and subdirectories
   - Parallel directories with same content

2. **JavaScript Interference**: The `services.js` file might have multiple event listeners that interfere with navigation. Look for:
   - Global click handlers
   - Event propagation issues
   - Multiple navigation handlers

3. **CSS Issues**: Check for CSS properties that might affect click behavior:
   - `cursor: pointer` on parent elements
   - `position: relative/absolute` affecting click areas
   - Z-index issues

4. **Path Structure**: Verify the correct path structure:
   - Use relative paths (`../`) when going up directories
   - Use direct paths when in the same directory
   - Avoid using index.html in paths
   - Check for trailing slashes

## Best Practices

1. **File Organization**:
   - Keep files in their proper directories
   - Avoid duplicating files
   - Use consistent naming conventions
   - Don't use index.html unless necessary
   - Keep directory structure clean and simple

2. **JavaScript**:
   - Use `data-href` for navigation
   - Handle click events properly
   - Check for event propagation

3. **CSS**:
   - Only make clickable elements have `cursor: pointer`
   - Use proper z-indexing
   - Avoid overlapping click areas

4. **Testing**:
   - Test both the card and the link separately
   - Verify the path structure
   - Check for JavaScript console errors
   - Verify no duplicate files
   - Check directory structure

## Troubleshooting Steps

1. **First Check**:
   - Verify file exists in correct location
   - Check path in browser dev tools
   - Look for JavaScript errors
   - Check for duplicate files
   - Verify no unnecessary index.html files

2. **If Path is Correct**:
   - Check JavaScript event handlers
   - Verify no conflicting CSS
   - Test with `data-href` attribute
   - Check directory structure

3. **If Still Not Working**:
   - Check for duplicate files
   - Verify directory structure
   - Test with simplified code
   - Remove any index.html references
   - Clean up duplicate directories 