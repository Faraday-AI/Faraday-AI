# Admin Widget Access - Complete Guide

## Overview

Admin users (`role = 'admin'` or `is_superuser = True`) can query **ALL widgets for ANY teacher** across all 545 tables.

## How It Works

### 1. Admin Detection

The `AIWidgetService` automatically detects admin status when initialized:

```python
from app.dashboard.services.ai_widget_service import AIWidgetService
from app.models.core.user import User
from app.models.teacher_registration import TeacherRegistration

# Initialize with admin context
service = AIWidgetService(
    db=db,
    current_user=current_user,  # User model
    current_teacher=current_teacher  # TeacherRegistration model
)

# Admin status is automatically detected and cached
```

### 2. Admin-Aware Query Helpers

The service provides helper methods for admin-aware queries:

#### `_resolve_teacher_id_for_query()`

Resolves teacher_id with admin support:

```python
# Admin can query any teacher
teacher_id = service._resolve_teacher_id_for_query(
    requested_teacher_id=1,  # Admin can specify any teacher ID
    requested_teacher_name="John Doe",  # Or by name
    requested_teacher_email="john@example.com"  # Or by email
)

# Regular users: always returns their own teacher_id (requested params ignored)
```

#### `_build_admin_aware_query()`

Builds queries that respect admin access:

```python
base_query = db.query(PhysicalEducationClass)
query = service._build_admin_aware_query(
    base_query,
    PhysicalEducationClass.teacher_id,
    requested_teacher_id=1,  # Admin can query any teacher
    requested_teacher_name="John Doe",
    requested_teacher_email="john@example.com"
)

# Admin: returns all classes for teacher_id=1
# Regular user: returns only their own classes (requested params ignored)
```

### 3. Widget Method Updates

All widget methods now support admin queries:

```python
# Example: Get class roster for any teacher (admin only)
roster = await service.get_class_roster(
    period="Period 2",
    teacher_id=1,  # Admin can query teacher ID 1
    teacher_name="John Doe",  # Or by name
    teacher_email="john@example.com"  # Or by email
)

# Regular users: teacher_id/name/email params are ignored, returns their own data
```

## Supported Widget Methods

All widget methods support admin access via these parameters:
- `teacher_id` (Optional[int]): Teacher ID to query (admin only)
- `teacher_name` (Optional[str]): Teacher name to query (admin only)
- `teacher_email` (Optional[str]): Teacher email to query (admin only)

### Key Widget Methods

1. **Attendance Widgets**
   - `predict_attendance_patterns()` - Predict attendance for any teacher's classes
   - `mark_attendance()` - Mark attendance for any teacher's classes
   - `get_class_roster()` - Get roster for any teacher's classes

2. **Lesson Plan Widgets**
   - `generate_lesson_plan()` - Generate lesson plans for any teacher

3. **Student Widgets**
   - `get_student_dashboard_data()` - Get student data for any teacher's students
   - `predict_student_performance()` - Predict performance for any teacher's students

4. **Class Management Widgets**
   - `get_class_roster()` - Get class roster for any teacher
   - `_find_class_by_period()` - Find classes by period for any teacher

## Usage Examples

### Example 1: Admin Querying Attendance for Teacher ID 1, Period 2

```python
# Admin user asks: "Show me attendance for teacher ID 1, period 2"

# Backend resolves teacher
teacher_id = service._resolve_teacher_id_for_query(requested_teacher_id=1)

# Find class by period
pe_class = service._find_class_by_period("Period 2", teacher_id=teacher_id)

# Get attendance
attendance = await service.predict_attendance_patterns(
    class_id=pe_class.id,
    days_ahead=7
)
```

### Example 2: Admin Querying by Teacher Name

```python
# Admin user asks: "Show me John Doe's class roster for period 3"

roster = await service.get_class_roster(
    period="Period 3",
    teacher_name="John Doe"  # Admin can query by name
)
```

### Example 3: Regular User (No Admin Access)

```python
# Regular user asks: "Show me my class roster for period 2"

roster = await service.get_class_roster(
    period="Period 2"
    # teacher_id/name/email params are ignored for regular users
    # Returns only their own classes
)
```

## AI Assistant Integration

The AI assistant (Jasper) can understand queries like:

- "Show me attendance for teacher ID 1, period 2"
- "Get class roster for John Doe, period 3"
- "What are the attendance patterns for teacher email john@example.com, period 1?"

The backend automatically:
1. Detects admin status
2. Resolves teacher_id from name/email if needed
3. Queries the appropriate data
4. Returns results in widget format

## Security

- **Admin users**: Can query any teacher's data
- **Regular users**: Can only query their own data (admin params ignored)
- **Validation**: All queries validate teacher exists before returning data
- **Logging**: Admin queries are logged for audit purposes

## Migration Status

✅ **Completed:**
- Admin detection in `AIWidgetService`
- `_resolve_teacher_id_for_query()` helper
- `_build_admin_aware_query()` helper
- `_find_class_by_period()` with admin support
- `get_class_roster()` with admin support
- `GPTFunctionService` updated to pass admin context

🔄 **In Progress:**
- Updating remaining widget methods to use admin-aware queries
- Adding admin params to all widget function schemas

## Testing

To test admin widget access:

1. **As Admin:**
   ```python
   # Should return data for teacher_id=1
   roster = await service.get_class_roster(period="Period 2", teacher_id=1)
   ```

2. **As Regular User:**
   ```python
   # Should return only their own data (teacher_id ignored)
   roster = await service.get_class_roster(period="Period 2", teacher_id=1)
   ```

## Next Steps

1. Update all widget methods to accept `teacher_id`, `teacher_name`, `teacher_email` params
2. Update widget function schemas to include admin params
3. Update AI assistant prompts to understand teacher queries
4. Add comprehensive logging for admin queries

