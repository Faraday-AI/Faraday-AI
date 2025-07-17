"""
Nutrition Models

This module defines nutrition models for physical education.
"""

from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text, Table
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.base import Base, BaseModel as SQLBaseModel
from app.models.mixins import TimestampedMixin

# Re-export for backward compatibility
BaseModelMixin = SQLBaseModel
TimestampMixin = TimestampedMixin

from app.models.physical_education.pe_enums.pe_types import (
    MealType,
    NutritionGoal,
    NutritionCategory
)

class NutritionPlan(BaseModelMixin, TimestampMixin):
    """Model for nutrition plans."""
    
    __tablename__ = "nutrition_plans"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    plan_name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    daily_calories = Column(Integer)
    protein_goal = Column(Float)
    carbs_goal = Column(Float)
    fat_goal = Column(Float)
    plan_notes = Column(Text)
    plan_metadata = Column(JSON)
    
    # Relationships
    student = relationship("Student")
    meals = relationship("Meal", back_populates="nutrition_plan")

class NutritionPlanCreate(BaseModel):
    """Pydantic model for creating nutrition plans."""
    
    student_id: int
    plan_name: str
    start_date: datetime
    end_date: Optional[datetime] = None
    daily_calories: Optional[int] = None
    protein_goal: Optional[float] = None
    carbs_goal: Optional[float] = None
    fat_goal: Optional[float] = None
    plan_notes: Optional[str] = None
    plan_metadata: Optional[dict] = None

class NutritionPlanUpdate(BaseModel):
    """Pydantic model for updating nutrition plans."""
    
    plan_name: Optional[str] = None
    end_date: Optional[datetime] = None
    daily_calories: Optional[int] = None
    protein_goal: Optional[float] = None
    carbs_goal: Optional[float] = None
    fat_goal: Optional[float] = None
    plan_notes: Optional[str] = None
    plan_metadata: Optional[dict] = None

class NutritionPlanResponse(BaseModel):
    """Pydantic model for nutrition plan responses."""
    
    id: int
    student_id: int
    plan_name: str
    start_date: datetime
    end_date: Optional[datetime] = None
    daily_calories: Optional[int] = None
    protein_goal: Optional[float] = None
    carbs_goal: Optional[float] = None
    fat_goal: Optional[float] = None
    plan_notes: Optional[str] = None
    plan_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Meal(BaseModelMixin, TimestampMixin):
    """Model for meals."""
    
    __tablename__ = "meals"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    nutrition_plan_id = Column(Integer, ForeignKey("nutrition_plans.id"), nullable=False)
    meal_type = Column(String(50), nullable=False)
    meal_time = Column(DateTime, nullable=False)
    calories = Column(Integer)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    meal_notes = Column(Text)
    meal_metadata = Column(JSON)
    
    # Relationships
    nutrition_plan = relationship("NutritionPlan", back_populates="meals")
    foods = relationship("MealFood", back_populates="meal")

class MealCreate(BaseModel):
    """Pydantic model for creating meals."""
    
    name: str
    description: Optional[str] = None
    type: MealType
    calories: int
    protein_grams: int
    carbs_grams: int
    fat_grams: int
    nutrition_plan_id: int

class MealUpdate(BaseModel):
    """Pydantic model for updating meals."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[MealType] = None
    calories: Optional[int] = None
    protein_grams: Optional[int] = None
    carbs_grams: Optional[int] = None
    fat_grams: Optional[int] = None

class MealResponse(BaseModel):
    """Pydantic model for meal responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    type: MealType
    calories: int
    protein_grams: int
    carbs_grams: int
    fat_grams: int
    nutrition_plan_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MealFood(BaseModelMixin, TimestampMixin):
    """Model for foods in meals."""
    
    __tablename__ = "meal_foods"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False)
    food_name = Column(String(100), nullable=False)
    quantity = Column(Float)
    unit = Column(String(20))
    calories = Column(Integer)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    food_notes = Column(Text)
    food_metadata = Column(JSON)
    
    # Relationships
    meal = relationship("Meal", back_populates="foods")

class Food(BaseModelMixin, TimestampMixin):
    """Model for foods."""
    __tablename__ = "foods"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False)
    name = Column(String(100), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    food_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    meal = relationship("Meal", back_populates="foods")

class FoodCreate(BaseModel):
    """Pydantic model for creating foods."""
    
    name: str
    description: Optional[str] = None
    serving_size: str
    calories: int
    protein_grams: int
    carbs_grams: int
    fat_grams: int
    fiber_grams: int
    sugar_grams: int
    sodium_mg: int

class FoodUpdate(BaseModel):
    """Pydantic model for updating foods."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    serving_size: Optional[str] = None
    calories: Optional[int] = None
    protein_grams: Optional[int] = None
    carbs_grams: Optional[int] = None
    fat_grams: Optional[int] = None
    fiber_grams: Optional[int] = None
    sugar_grams: Optional[int] = None
    sodium_mg: Optional[int] = None

class FoodResponse(BaseModel):
    """Pydantic model for food responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    serving_size: str
    calories: int
    protein_grams: int
    carbs_grams: int
    fat_grams: int
    fiber_grams: int
    sugar_grams: int
    sodium_mg: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NutritionGoal(BaseModelMixin, TimestampMixin):
    """Model for nutrition goals."""
    __tablename__ = "nutrition_goals"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    goal_type = Column(String(50), nullable=False)
    target_value = Column(Float, nullable=False)
    current_value = Column(Float)
    goal_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    student = relationship("Student", back_populates="nutrition_goals")

class PhysicalEducationNutritionLog(BaseModelMixin, TimestampMixin):
    """Model for nutrition logs."""
    __tablename__ = "physical_education_nutrition_logs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    meal_type = Column(String(50), nullable=False)
    log_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    calories = Column(Integer)
    protein = Column(Float)
    carbohydrates = Column(Float)
    fats = Column(Float)
    hydration = Column(Float)
    notes = Column(Text)
    log_metadata = Column(JSON)
    
    # Relationships
    # student = relationship("app.models.physical_education.student.models.Student", back_populates="physical_education_nutrition_logs")

class PhysicalEducationNutritionLogCreate(BaseModel):
    """Pydantic model for creating nutrition logs."""
    
    student_id: int
    meal_type: MealType
    foods_consumed: List[Dict]
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    fats: Optional[float] = None
    hydration: Optional[float] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None

class PhysicalEducationNutritionLogUpdate(BaseModel):
    """Pydantic model for updating nutrition logs."""
    
    meal_type: Optional[MealType] = None
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    fats: Optional[float] = None
    hydration: Optional[float] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None

class PhysicalEducationNutritionLogResponse(BaseModel):
    """Pydantic model for nutrition log responses."""
    
    id: int
    student_id: int
    meal_type: MealType
    log_date: datetime
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    fats: Optional[float] = None
    hydration: Optional[float] = None
    notes: Optional[str] = None
    log_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PhysicalEducationNutritionRecommendation(BaseModelMixin, TimestampMixin):
    """Model for nutrition recommendations."""
    __tablename__ = "physical_education_nutrition_recommendations"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    category = Column(String(50), nullable=False)
    meal_type = Column(String(50), nullable=False)
    description = Column(Text)
    reasoning = Column(Text)
    suggested_foods = Column(JSON)
    nutrient_targets = Column(JSON)
    recommendation_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    # student = relationship("Student", back_populates="physical_education_nutrition_recommendations")

class PhysicalEducationNutritionRecommendationCreate(BaseModel):
    """Pydantic model for creating nutrition recommendations."""
    
    student_id: int
    category: str
    meal_type: MealType
    description: str
    reasoning: str
    suggested_foods: List[str]
    nutrient_targets: Dict[str, float]
    recommendation_metadata: Optional[Dict] = None  # Renamed from metadata

class PhysicalEducationNutritionRecommendationUpdate(BaseModel):
    """Pydantic model for updating nutrition recommendations."""
    
    category: Optional[str] = None
    meal_type: Optional[MealType] = None
    description: Optional[str] = None
    reasoning: Optional[str] = None
    suggested_foods: Optional[List[str]] = None
    nutrient_targets: Optional[Dict[str, float]] = None
    recommendation_metadata: Optional[Dict] = None  # Renamed from metadata

class PhysicalEducationNutritionRecommendationResponse(BaseModel):
    """Pydantic model for nutrition recommendation responses."""
    
    id: int
    student_id: int
    category: str
    meal_type: MealType
    description: str
    reasoning: str
    suggested_foods: List[str]
    nutrient_targets: Dict[str, float]
    recommendation_metadata: Optional[Dict] = None  # Renamed from metadata
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NutritionEducation(BaseModelMixin, TimestampMixin):
    """Model for nutrition education materials."""
    __tablename__ = "nutrition_education"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    content = Column(JSON, nullable=False)
    age_group = Column(String(50), nullable=False)
    learning_objectives = Column(JSON)
    activities = Column(JSON)
    resources = Column(JSON)
    education_metadata = Column(JSON)  # Using education_metadata to avoid reserved name

class NutritionEducationCreate(BaseModel):
    """Pydantic model for creating nutrition education materials."""
    
    title: str
    category: NutritionCategory
    content: Dict
    age_group: str
    learning_objectives: List[str]
    activities: Optional[List[Dict]] = None
    resources: Optional[List[Dict]] = None
    education_metadata: Optional[Dict] = None

class NutritionEducationUpdate(BaseModel):
    """Pydantic model for updating nutrition education materials."""
    
    title: Optional[str] = None
    category: Optional[NutritionCategory] = None
    content: Optional[Dict] = None
    age_group: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    activities: Optional[List[Dict]] = None
    resources: Optional[List[Dict]] = None
    education_metadata: Optional[Dict] = None

class NutritionEducationResponse(BaseModel):
    """Pydantic model for nutrition education responses."""
    
    id: int
    title: str
    category: NutritionCategory
    content: Dict
    age_group: str
    learning_objectives: List[str]
    activities: Optional[List[Dict]] = None
    resources: Optional[List[Dict]] = None
    education_metadata: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MealFoodCreate(BaseModel):
    """Pydantic model for creating meal foods."""
    
    meal_id: int
    food_name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    food_notes: Optional[str] = None
    food_metadata: Optional[dict] = None

class MealFoodUpdate(BaseModel):
    """Pydantic model for updating meal foods."""
    
    food_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    food_notes: Optional[str] = None
    food_metadata: Optional[dict] = None

class MealFoodResponse(BaseModel):
    """Pydantic model for meal food responses."""
    
    id: int
    meal_id: int
    food_name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    food_notes: Optional[str] = None
    food_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 