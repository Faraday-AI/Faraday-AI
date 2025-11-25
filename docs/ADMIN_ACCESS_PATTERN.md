# Admin Access Pattern - Production Guide

## Overview

Admin users (`role = 'admin'` or `is_superuser = True`) should have access to **ALL data across all 545 tables**, while regular users only see their own data.

## The Problem

Many endpoints filter data by `teacher_id` or `user_id` without checking admin status first, limiting admin users to only their own data.

## The Solution

Use the **admin-aware dependency injection pattern** in all endpoints.

## Production-Ready Pattern

### Option 1: FastAPI Dependency (RECOMMENDED)

Use `get_admin_context_from_teacher` dependency in endpoints:

```python
from app.core.dependencies_admin import get_admin_context_from_teacher
from app.utils.admin_check import build_filtered_query

@router.get("/students")
async def get_students(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    admin_context: dict = Depends(get_admin_context_from_teacher),
    db: Session = Depends(get_db)
):
    # Build query with automatic admin filtering
    base_query = db.query(BetaStudent)
    query = build_filtered_query(
        base_query,
        BetaStudent.created_by_teacher_id,
        current_teacher.id,
        teacher_registration=current_teacher,
        db=db
    )
    return query.all()
```

### Option 2: Base Service Class

Inherit from `BaseAdminService` in service classes:

```python
from app.services.base_admin_service import BaseAdminService

class MyService(BaseAdminService):
    def __init__(self, db: Session, current_teacher: TeacherRegistration):
        super().__init__(db, current_teacher=current_teacher)
    
    def get_items(self):
        # Automatically handles admin filtering
        query = self.build_admin_query(
            self.db.query(MyModel),
            MyModel.user_id,
            self.current_user_id
        )
        return query.all()
```

## Benefits

✅ **Automatic**: Admin checks happen automatically  
✅ **Consistent**: Same pattern across all endpoints  
✅ **Maintainable**: One place to update logic  
✅ **Production-Ready**: Handles all edge cases  
✅ **Scalable**: Works for all 545 tables  

## Migration Strategy

1. **New endpoints**: Use the pattern from day one
2. **Existing endpoints**: Migrate gradually, starting with most-used endpoints
3. **Services**: Update services to inherit from `BaseAdminService`

## Files Created

- `app/utils/admin_check.py` - Core utility functions
- `app/services/base_admin_service.py` - Base service class
- `app/core/dependencies_admin.py` - FastAPI dependencies

## Testing

Admin users should be able to:
- See all students (not just their own)
- See all classes (not just their own)
- See all lesson plans (not just their own)
- Access all data across all 545 tables

Regular users should only see their own data (unchanged behavior).

