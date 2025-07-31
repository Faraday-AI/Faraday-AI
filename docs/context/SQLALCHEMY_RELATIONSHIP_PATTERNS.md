# SQLAlchemy Relationship Patterns for Faraday AI

## Overview

This document outlines the working patterns and best practices for SQLAlchemy relationships in the Faraday AI project, based on our successful resolution of 48+ relationship errors in the physical education suite.

## Core Principles

### 1. Never Remove, Always Fix
- **Rule**: Never remove or comment out relationships during development
- **Action**: Always create, rename, or fix relationships to make them work
- **Reason**: Maintains data integrity and prevents loss of functionality

### 2. Use Fully Qualified Paths
- **Pattern**: `app.models.module.submodule.ClassName`
- **Example**: `"app.models.physical_education.equipment.models.Equipment"`
- **Reason**: Resolves naming conflicts when multiple classes share the same name

### 3. Maintain Bidirectional Relationships
- **Pattern**: Always use `back_populates` for bidirectional relationships
- **Example**: 
  ```python
  # Parent model
  children = relationship("Child", back_populates="parent")
  
  # Child model  
  parent = relationship("Parent", back_populates="children")
  ```

## Relationship Patterns by Type

### 1. One-to-Many Relationships

#### Standard Pattern
```python
# Parent model
class Parent(BaseModelMixin, TimestampMixin):
    __tablename__ = "parents"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    # Relationship to children
    children = relationship("app.models.module.child.Child", back_populates="parent")

# Child model
class Child(BaseModelMixin, TimestampMixin):
    __tablename__ = "children"
    
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    name = Column(String, nullable=False)
    
    # Relationship to parent
    parent = relationship("app.models.module.parent.Parent", back_populates="children")
```

#### Multiple Relationships to Same Model
When you have multiple relationships pointing to the same model, use distinct names:

```python
# Student model with multiple health relationships
class Student(BaseModelMixin, TimestampMixin):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True)
    
    # Physical education health metrics
    pe_health_metrics = relationship("app.models.physical_education.health.models.HealthMetric", back_populates="student")
    
    # Health fitness metrics  
    fitness_health_metrics = relationship("app.models.health_fitness.metrics.health_metrics.HealthMetric", back_populates="student")
    
    # Skill assessment health metrics
    skill_assessment_health_metrics = relationship("app.models.skill_assessment.health.HealthMetric", back_populates="student")
```

### 2. Many-to-Many Relationships

#### Standard Pattern
```python
# Association table
association_table = Table(
    'parent_child_association',
    Base.metadata,
    Column('parent_id', Integer, ForeignKey('parents.id'), primary_key=True),
    Column('child_id', Integer, ForeignKey('children.id'), primary_key=True)
)

# Parent model
class Parent(BaseModelMixin, TimestampMixin):
    __tablename__ = "parents"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    # Many-to-many relationship
    children = relationship("app.models.module.child.Child", secondary=association_table, back_populates="parents")

# Child model
class Child(BaseModelMixin, TimestampMixin):
    __tablename__ = "children"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    # Many-to-many relationship
    parents = relationship("app.models.module.parent.Parent", secondary=association_table, back_populates="children")
```

### 3. Self-Referential Relationships

#### Pattern for Self-Referential
```python
class Category(BaseModelMixin, TimestampMixin):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Self-referential relationships
    parent = relationship("app.models.module.category.Category", remote_side=[id], back_populates="children")
    children = relationship("app.models.module.category.Category", back_populates="parent")
```

## Conflict Resolution Patterns

### 1. Naming Conflicts Between Modules

When multiple modules have classes with the same name:

#### Solution: Use Fully Qualified Paths
```python
# Instead of:
equipment = relationship("Equipment", back_populates="maintenance_records")

# Use:
equipment = relationship("app.models.physical_education.equipment.models.Equipment", back_populates="maintenance_records")
```

#### Solution: Rename Classes
```python
# Rename conflicting class
class MovementAnalysisRecord(BaseModelMixin, TimestampMixin):  # Was MovementAnalysis
    __tablename__ = "movement_analysis_records"
    # ... rest of model
```

### 2. Foreign Key Conflicts

When multiple relationships point to the same foreign key:

#### Solution: Use Overlaps Parameter
```python
# Add overlaps parameter to suppress warnings
health_metrics = relationship("HealthMetric", back_populates="student", overlaps="fitness_health_metrics")
fitness_health_metrics = relationship("HealthMetric", back_populates="student", overlaps="health_metrics")
```

#### Solution: Use Distinct Foreign Keys
```python
# Use different foreign key columns
pe_health_metric_id = Column(Integer, ForeignKey("pe_health_metrics.id"), nullable=True)
fitness_health_metric_id = Column(Integer, ForeignKey("fitness_health_metrics.id"), nullable=True)
```

### 3. Circular Import Issues

#### Solution: Use String References
```python
# Always use string references in relationships
student = relationship("app.models.physical_education.student.models.Student", back_populates="activities")
```

#### Solution: Import in __init__.py
```python
# In __init__.py file
from . import models
from .models import *

__all__ = ['Model1', 'Model2', 'Model3']
```

## Base Class Alignment

### Pattern: Use Consistent Base Classes
```python
# All models should use the same base
from app.models.shared_base import SharedBase
from app.models.mixins import TimestampMixin, StatusMixin, MetadataMixin

class MyModel(SharedBase, TimestampMixin, StatusMixin, MetadataMixin):
    __tablename__ = "my_models"
    # ... model definition
```

## Error Resolution Checklist

When encountering SQLAlchemy relationship errors:

### 1. InvalidRequestError: Multiple classes found for path
- **Action**: Use fully qualified path in relationship
- **Example**: `"app.models.module.submodule.ClassName"`

### 2. ArgumentError: reverse_property references non-existent relationship
- **Action**: Check both sides of bidirectional relationship
- **Action**: Ensure `back_populates` references correct relationship name

### 3. NoForeignKeysError: Can't find any foreign key relationships
- **Action**: Add missing foreign key column
- **Action**: Ensure foreign key points to correct table

### 4. KeyError: Mapper has no property
- **Action**: Add missing relationship to the referenced model
- **Action**: Check for typos in relationship names

## Testing Patterns

### 1. Model Import Testing
```python
# Test that models can be imported without errors
from app.models.physical_education.activity.models import Activity
from app.models.core.user import User
print("✅ All models imported successfully")
```

### 2. Instance Creation Testing
```python
# Test that instances can be created
activity = Activity(name="Test", type="fitness", difficulty_level="intermediate")
print("✅ Instance created successfully")
```

### 3. Relationship Testing
```python
# Test that relationships are accessible
print("Activity relationships:", [attr for attr in dir(Activity) if hasattr(getattr(Activity, attr), 'property')])
```

## Common Pitfalls to Avoid

### 1. Don't Remove Relationships
```python
# ❌ Wrong - Don't do this
# relationships = relationship("Model", back_populates="parent")

# ✅ Correct - Fix the relationship instead
relationships = relationship("app.models.module.model.Model", back_populates="parent")
```

### 2. Don't Use Ambiguous References
```python
# ❌ Wrong - Ambiguous
equipment = relationship("Equipment", back_populates="maintenance")

# ✅ Correct - Fully qualified
equipment = relationship("app.models.physical_education.equipment.models.Equipment", back_populates="maintenance")
```

### 3. Don't Forget Foreign Keys
```python
# ❌ Wrong - Missing foreign key
class Child(BaseModelMixin, TimestampMixin):
    __tablename__ = "children"
    id = Column(Integer, primary_key=True)
    # Missing: parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    parent = relationship("Parent", back_populates="children")

# ✅ Correct - With foreign key
class Child(BaseModelMixin, TimestampMixin):
    __tablename__ = "children"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    parent = relationship("Parent", back_populates="children")
```

## Migration Considerations

### 1. Table Name Conflicts
When renaming tables to avoid conflicts:
```python
# Use descriptive table names
__tablename__ = "physical_education_curriculum_units"  # Instead of "curriculum_units"
```

### 2. Foreign Key Updates
When renaming tables, update all foreign key references:
```python
# Update foreign key to match new table name
unit_id = Column(Integer, ForeignKey("physical_education_curriculum_units.id"), nullable=False)
```

## Summary

These patterns ensure:
- ✅ Consistent relationship definitions across the project
- ✅ Resolution of naming conflicts between modules
- ✅ Proper bidirectional relationships
- ✅ No data loss during development
- ✅ Maintainable and scalable codebase

Follow these patterns to maintain the robust database architecture we've established in the physical education suite. 