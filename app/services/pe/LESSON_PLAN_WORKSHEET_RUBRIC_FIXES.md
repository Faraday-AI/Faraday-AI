# Lesson Plan Worksheet and Rubric Extraction Fixes

## Overview
This document describes the fixes implemented for lesson plan worksheet and rubric extraction in `lesson_plan_service.py` and the frontend rendering in `dashboard.js`. These fixes ensure that worksheets display all 10 questions with proper MC options (A-D) and correctly aligned answer keys, and that rubrics are comprehensive with all 4 performance levels.

## Date: December 2024

---

## Worksheet Extraction Fixes

### Problem
- Questions 2-10 were missing MC options (only showing option D)
- Answer keys were misaligned with questions
- Questions with markers like "**Question:**" or "Level 1 (Gathering):" were being included
- Questions with fewer than 3 MC options were being included

### Solution

#### Backend (`lesson_plan_service.py`)

1. **Question-Option Pair Extraction** (`_extract_question_option_pairs_from_text`)
   - **Location**: Lines 278-349
   - **Purpose**: Extracts questions with their MC options together from response text
   - **Key Features**:
     - Skips answer keys that might look like questions
     - Filters out non-worksheet questions (reflection questions, Costa's questions, etc.)
     - Only includes questions with 3+ MC options (worksheets should have 4)
     - Looks ahead up to 10 lines to find MC options for each question
     - Sorts options by letter (A, B, C, D)

2. **Question Filtering** (Lines 317-327, 843-860, 935-951, 967-1000)
   - **Skip Markers**: Filters out questions with:
     - `**Question:**` or `Question:`
     - `Level 1 (Gathering):` or similar Costa's levels
     - `Costa's Level` markers
     - `Reflection Question`
   - **Minimum Options**: Only includes questions with 3+ MC options
   - **Applied in ALL extraction paths**: 
     - `_extract_question_option_pairs_from_text` (primary extraction)
     - `_extract_worksheets_from_field` (line-by-line parsing)
     - `_extract_worksheets_from_field` (fallback text extraction)
     - `_extract_worksheets_from_field` (individual item checking)
   - **Purpose**: Ensures Costa's questioning and reflection questions never appear in worksheets, regardless of extraction method

3. **Worksheet Building** (`_extract_and_enhance_worksheets`, Lines 1316-1350)
   - **Key Logic**: 
     - Extracts question-option pairs directly from `response_text` first
     - If 3+ pairs found, builds worksheet from pairs (more accurate)
     - Ensures exactly 10 questions (not more, not less)
     - Matches answer keys to questions by number if available
     - Creates placeholder answer keys if missing

4. **Answer Key Matching** (Lines 1346-1375)
   - Creates a map of answer keys by question number
   - Matches answer keys to questions by number first
   - Falls back to sequential matching if no numbers found
   - Ensures exactly 10 answer keys (creates placeholders if needed)

#### Frontend (`dashboard.js`)

1. **Markdown Formatting Support** (Lines 1115-1129)
   - Updated regex to handle markdown bold formatting:
     - `**Student Worksheet:**` (markdown bold)
     - `*Student Worksheet:*` (markdown italic/bold)
     - `Student Worksheet:` (plain text)
   - Same fix applied to "Answer Key:" detection

2. **Question Parsing** (`formatWorksheets`, Lines 1098-1377)
   - Looks ahead up to 25 lines for MC options
   - Handles options separated by blank lines
   - Sorts options by letter (A, B, C, D)
   - Properly formats questions with CSS classes
   - **Improved Fallback** (Lines 1274-1374):
     - Detects worksheet content even without "Student Worksheet:" header
     - Re-parses text assuming worksheet mode if questions/MC options detected
     - Ensures CSS classes are always applied
     - Wraps content in proper worksheet sections for styling

---

## Rubric Extraction Fixes

### Problem
- Rubrics were incomplete (only 1-2 criteria rows instead of 3-5)
- Rubrics were missing performance levels (only showing 2 columns instead of 4)
- Duplicate criteria were being added when supplementing
- Default rubric wasn't being created when none found

### Solution

#### Backend (`lesson_plan_service.py`)

1. **Rubric Section Extraction** (Lines 1564-1577)
   - **Improved Patterns**: Multiple patterns to find rubric section:
     - Greedy match to get all rubric content
     - Direct table pattern matching
     - Emoji/header pattern matching
   - **Section Expansion**: If section is too short (< 500 chars), expands to up to 3000 chars

2. **Comprehensive Row Extraction** (Lines 1585-1596)
   - **Always searches full `response_text`** for ALL rubric rows (not just section)
   - Combines rows from both section and full text
   - Better line-by-line parsing fallback

3. **Row Validation** (Lines 1598-1621)
   - **Lenient Validation**: Accepts rows with 2+ columns that have rubric keywords
   - Filters out header rows and separator rows
   - Checks for criteria names (technique, skill, performance, etc.)

4. **Default Criteria Supplementing** (Lines 1646-1676)
   - **When**: Only supplements if 1-2 criteria found (target: 3-5 criteria)
   - **Logic**:
     - Extracts existing criteria names and keywords
     - Tracks which criteria names have been added
     - Only adds default criteria that don't already exist
     - Prevents duplicates by checking both criteria names and keywords
   - **Default Criteria**:
     - Dribbling Technique
     - Passing Accuracy
     - Shooting Form
     - Defensive Positioning
     - Teamwork and Communication

5. **Default Rubric Creation** (`_build_rubric_table`, Lines 1035-1058)
   - **Fixed**: Now creates default rubric when given empty list `[]`
   - **Before**: Returned empty string immediately
   - **After**: Creates default rubric with 5 criteria and all 4 performance levels
   - **Final Fallback**: Always creates default rubric if none found (Line 1830-1834)

6. **Header Row Filtering** (Lines 1668-1684)
   - Filters out header rows before formatting
   - Filters out separator rows (all dashes/colons)
   - Double-checks formatted rows aren't headers
   - Only adds header once at the beginning

7. **Incomplete Rubric Detection and Fallback** (Lines 1521-1525, 2608-2620)
   - **Problem**: JSON rubrics can be truncated (e.g., ends at "| Dribbling" with no data rows)
   - **Detection Logic**:
     - Checks if rubric ends with incomplete row (ends with `|` or pattern like `| Dribbling`)
     - Counts data rows - if fewer than 3, considers incomplete
     - Logs warning when incomplete rubric detected
   - **Fallback Behavior**:
     - If JSON rubric is incomplete, uses regex-extracted rubric from `response_text`
     - Triggers full extraction in `_extract_and_enhance_rubrics` even if incomplete rubric exists
     - Ensures complete rubric is always extracted from AI response
   - **Location**: 
     - Detection: Lines 2608-2620 (JSON rubric check)
     - Extraction trigger: Lines 1521-1525 (`_extract_and_enhance_rubrics` entry point)

---

## Key Functions Reference

### Backend Functions

#### `_extract_question_option_pairs_from_text(text: str) -> List[dict]`
- **Purpose**: Extract questions with their MC options together
- **Returns**: List of `{question, options: [], number}` dictionaries
- **Key Logic**: 
  - Finds numbered or unnumbered questions ending with `?`
  - Looks ahead 10 lines for MC options (A-D)
  - Only includes questions with 3+ options
  - Filters out non-worksheet questions

#### `_combine_worksheets(existing, questions, mc_options, answer_keys) -> str`
- **Purpose**: Combine worksheet components into formatted worksheet
- **Key Logic**:
  - Uses question-option pairs if available (more accurate)
  - Ensures exactly 10 questions
  - Matches answer keys by question number
  - Creates placeholders if answer keys missing

#### `_extract_rubric_rows_from_text(text: str) -> List[str]`
- **Purpose**: Extract rubric table rows from text
- **Key Logic**:
  - Line-by-line extraction (most reliable)
  - Regex pattern fallback
  - Filters separator rows

#### `_build_rubric_table(rows: List[str]) -> str`
- **Purpose**: Build complete rubric table from rows
- **Key Logic**:
  - Creates default rubric if no rows provided
  - Formats each row to have 4 performance levels
  - Deduplicates criteria
  - Adds proper header

#### `_format_rubric_row(row: str) -> str`
- **Purpose**: Format a single rubric row to have 4 performance levels
- **Key Logic**:
  - Handles rows with 2, 3, or 4 columns
  - Fills missing performance levels with defaults
  - Ensures proper table format

### Frontend Functions

#### `formatWorksheets(worksheetsText)`
- **Purpose**: Format worksheet text into HTML with proper CSS classes
- **Key Features**:
  - Detects "Student Worksheet:" and "Answer Key:" sections
  - Handles markdown formatting (`**Student Worksheet:**`)
  - Parses numbered questions
  - Looks ahead for MC options
  - Formats with CSS classes for styling

#### `formatQuestionBlock(question, options)`
- **Purpose**: Generate HTML for a single question and its MC options
- **Returns**: HTML with `.worksheet-question`, `.question-number`, `.question-options` classes

#### `formatRubrics(rubricsText)`
- **Purpose**: Convert markdown rubric tables to HTML tables
- **Key Features**:
  - Parses markdown table format with pipes (`|`)
  - Filters duplicate criteria rows
  - Handles truncated/incomplete rubrics
  - Shows warning when rubric has header but no data rows
  - Renders partial rows when data is truncated
- **Truncation Handling** (Lines 1478-1500):
  - Detects truncated rows (single cell that looks like criteria)
  - Pads incomplete rows with empty cells to maintain table structure
  - Shows warning message if header exists but no data rows found
  - Displays raw data as fallback when rubric is incomplete

---

## Troubleshooting Guide

### Issue: Worksheets missing MC options

**Check:**
1. Backend logs: Look for "Extracted X question-option pairs"
2. Check if `_extract_question_option_pairs_from_text` is finding options
3. Verify questions have 3+ MC options (filter might be too strict)
4. Check if options are being filtered out as invalid

**Fix:**
- Adjust minimum options requirement (currently 3)
- Check option validation logic in `_extract_question_option_pairs_from_text`
- Verify look-ahead distance (currently 10 lines)

### Issue: Answer keys misaligned

**Check:**
1. Backend logs: "Matching X answer keys to Y questions"
2. Check if answer keys have question numbers
3. Verify answer key matching logic (Lines 1346-1375)

**Fix:**
- Ensure answer keys are numbered correctly
- Check answer key extraction patterns
- Verify sequential matching fallback

### Issue: Rubric incomplete (only 1-2 criteria)

**Check:**
1. Backend logs: "Extracted X potential rubric rows"
2. Check if rubric section is being found
3. Verify row validation isn't too strict
4. Check if default supplementing is working

**Fix:**
- Increase section expansion size (currently 3000 chars)
- Adjust validation leniency
- Check default criteria supplementing logic
- Verify `_build_rubric_table` default creation

### Issue: Rubric missing performance levels

**Check:**
1. Verify `_format_rubric_row` is being called
2. Check if rows have enough columns
3. Verify default performance level descriptions

**Fix:**
- Ensure `_format_rubric_row` fills missing levels
- Check default descriptions in function
- Verify header is being added correctly

### Issue: Duplicate criteria in rubric

**Check:**
1. Backend logs: "Added default criteria" (check for duplicates)
2. Verify `added_criteria_names` set is working
3. Check keyword matching logic

**Fix:**
- Ensure criteria name tracking (Lines 1651-1676)
- Verify duplicate prevention in `_build_rubric_table`
- Check keyword extraction logic

### Issue: Frontend not applying CSS classes

**Check:**
1. Verify `formatWorksheets` is being called
2. Check if "Student Worksheet:" section is being detected
3. Verify markdown formatting regex

**Fix:**
- Update regex patterns for section detection
- Check if function is returning HTML (not falling back to plain text)
- Verify CSS classes are in `dashboard.css`
- Check fallback logic (Lines 1274-1374) - should detect worksheet content even without headers

### Issue: Rubric truncated in JSON (only header, no data rows)

**Check:**
1. Backend logs: Look for "⚠️ JSON rubric appears truncated" or "⚠️ Existing rubric appears incomplete"
2. Check if incomplete rubric detection is triggering
3. Verify fallback to regex-extracted rubric is working
4. Check if `_extract_and_enhance_rubrics` is being called even with incomplete rubric

**Fix:**
- Ensure incomplete detection logic is working (Lines 2608-2620)
- Verify `_extract_and_enhance_rubrics` triggers on incomplete rubrics (Lines 1521-1525)
- Check if full `response_text` extraction is finding complete rubric
- Verify frontend is handling truncated rubrics gracefully (Lines 1478-1560)

### Issue: Widget updates breaking autoplay on Safari

**Check:**
1. Console logs: Look for "🔊 Audio fetch started - deferring widget updates"
2. Verify `_audioPlayPromise` is being stored on message div
3. Check if `updateWidgetWithData` is waiting for audio play promise

**Fix:**
- Ensure widget updates wait for audio play() to be called (Lines 2231-2252)
- Verify interaction context is preserved for Safari autoplay
- Check if widgets are being updated before autoplay completes

---

## Testing Checklist

### Worksheets
- [ ] All 10 questions are displayed
- [ ] Each question has 4 MC options (A, B, C, D)
- [ ] Answer keys are numbered 1-10
- [ ] Answer keys match their corresponding questions
- [ ] No reflection/Costa's questions in worksheets
- [ ] CSS classes are applied correctly

### Rubrics
- [ ] Rubric has 3-5 criteria rows
- [ ] Each criteria has 4 performance levels (Excellent, Proficient, Developing, Beginning)
- [ ] No duplicate criteria
- [ ] Header row is present (only once)
- [ ] Default rubric created if none found
- [ ] Table formatting is correct

---

## Key Code Locations

### Backend
- **Worksheet Extraction**: `lesson_plan_service.py` Lines 278-1418
- **Rubric Extraction**: `lesson_plan_service.py` Lines 1440-1834
- **Question-Option Pairs**: `lesson_plan_service.py` Lines 278-349
- **Rubric Table Building**: `lesson_plan_service.py` Lines 1035-1105

### Frontend
- **Worksheet Formatting**: `dashboard.js` Lines 1098-1377
- **Question Block Formatting**: `dashboard.js` Lines 1380-1397
- **Rubric Formatting**: `dashboard.js` Lines 1399-1560
- **Widget Update Deferral**: `dashboard.js` Lines 2231-2252
- **CSS Classes**: `dashboard.css` (search for `.worksheet-*` and `.rubric-*`)

---

## Notes

- **Worksheet extraction is working correctly** - Do not modify unless absolutely necessary
- **Rubric extraction supplements with defaults** - This is intentional to ensure comprehensive rubrics
- **Default rubric has 5 criteria** - This is the standard when none found in response
- **Frontend handles markdown** - Worksheets may have `**Student Worksheet:**` format from AI
- **Costa's questions filtered everywhere** - All extraction paths now filter out "Level 1 (Gathering)" type questions
- **Widget updates deferred for autoplay** - Widgets wait for audio play() to preserve Safari interaction context
- **Incomplete rubric detection** - System automatically detects and fixes truncated rubrics from JSON
- **Frontend rubric resilience** - Frontend handles truncated rubrics gracefully with warnings and fallbacks

---

## Recent Fixes (December 2024 - Latest)

### Costa's Question Filtering Enhancement
- **Issue**: Questions with "Level 1 (Gathering):" were still appearing in worksheets on Render
- **Fix**: Added filtering to ALL extraction paths in `_extract_worksheets_from_field`:
  - Line-by-line parsing (Lines 843-860)
  - Fallback text extraction (Lines 935-951)
  - Individual item checking (Lines 967-1000)
- **Result**: Costa's questions are now filtered regardless of extraction method

### Widget Update Deferral for Autoplay
- **Issue**: Widget updates were breaking Safari's autoplay interaction context
- **Fix**: Added check in `updateWidgetWithData` to wait for audio play promise (Lines 2231-2252)
- **Behavior**: 
  - Checks if `_audioPlayPromise` exists on last AI message
  - Defers widget updates until `play()` is called
  - Preserves user interaction context for Safari autoplay
- **Result**: Autoplay works correctly on Safari even when widgets are updated

### Worksheet CSS Fallback Improvement
- **Issue**: Worksheets weren't getting CSS classes when "Student Worksheet:" header was missing
- **Fix**: Enhanced fallback logic in `formatWorksheets` (Lines 1274-1374)
- **Behavior**:
  - Detects worksheet content by presence of questions/MC options
  - Re-parses text assuming worksheet mode
  - Always wraps content in proper CSS classes
- **Result**: Worksheets always get proper styling even without explicit headers

### Rubric Truncation Detection and Recovery
- **Issue**: JSON rubrics were truncated (ending at "| Dribbling" with no data rows)
- **Fix**: Added incomplete rubric detection and fallback (Lines 1521-1525, 2608-2620)
- **Detection**:
  - Checks if rubric ends with incomplete row
  - Counts data rows - flags as incomplete if < 3 rows
  - Logs warnings for debugging
- **Recovery**:
  - Uses regex-extracted rubric from `response_text` if JSON is incomplete
  - Triggers full extraction even when incomplete rubric exists
- **Result**: Complete rubrics are always extracted, even when JSON is truncated

### Frontend Rubric Truncation Handling
- **Issue**: Frontend couldn't render truncated rubrics (only header, no data)
- **Fix**: Enhanced `formatRubrics` to handle incomplete data (Lines 1478-1560)
- **Features**:
  - Detects and renders truncated rows (single cell that looks like criteria)
  - Pads incomplete rows with empty cells
  - Shows warning message when rubric is incomplete
  - Displays raw data as fallback
- **Result**: Frontend gracefully handles truncated rubrics with user feedback

## Future Improvements

1. **Better AI Prompt**: Request AI to always include complete rubrics with all criteria
2. **Smarter Default Criteria**: Match default criteria to lesson topic (basketball vs. baseball)
3. **Rubric Validation**: Add validation to ensure rubrics have minimum criteria count
4. **Performance**: Optimize row extraction for very long response texts
5. **JSON Parsing**: Investigate why JSON rubrics are being truncated (may be AI response limit)

