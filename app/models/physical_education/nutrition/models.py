"""
Nutrition Models

This module defines nutrition models for physical education.
"""

from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text, Table
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.core.base import CoreBase
from app.models.mixins import TimestampedMixin

# Re-export for backward compatibility
BaseModelMixin = CoreBase
TimestampMixin = TimestampedMixin

from app.models.physical_education.pe_enums.pe_types import (
    MealType,
    NutritionGoal,
    NutritionCategory
)

# Import Student model to ensure it's registered with SQLAlchemy
from app.models.physical_education.student.models import Student

class PhysicalEducationNutritionPlan(BaseModelMixin, TimestampMixin):
    """Model for physical education nutrition plans."""
    
    __tablename__ = "physical_education_nutrition_plans"
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
    meals = relationship("PhysicalEducationMeal", back_populates="nutrition_plan")

class PhysicalEducationNutritionPlanCreate(BaseModel):
    """Pydantic model for creating physical education nutrition plans."""
    
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

class PhysicalEducationNutritionPlanUpdate(BaseModel):
    """Pydantic model for updating physical education nutrition plans."""
    
    plan_name: Optional[str] = None
    end_date: Optional[datetime] = None
    daily_calories: Optional[int] = None
    protein_goal: Optional[float] = None
    carbs_goal: Optional[float] = None
    fat_goal: Optional[float] = None
    plan_notes: Optional[str] = None
    plan_metadata: Optional[dict] = None

class PhysicalEducationNutritionPlanResponse(BaseModel):
    """Pydantic model for physical education nutrition plan responses."""
    
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

class PhysicalEducationMeal(BaseModelMixin, TimestampMixin):
    """Model for physical education meals."""
    
    __tablename__ = "physical_education_meals"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    nutrition_plan_id = Column(Integer, ForeignKey("physical_education_nutrition_plans.id"), nullable=False)
    meal_type = Column(String(50), nullable=False)
    meal_time = Column(DateTime, nullable=False)
    calories = Column(Integer)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    meal_notes = Column(Text)
    meal_metadata = Column(JSON)
    
    # Relationships
    nutrition_plan = relationship("PhysicalEducationNutritionPlan", back_populates="meals")
    foods = relationship("PhysicalEducationMealFood", back_populates="meal")

class PhysicalEducationMealCreate(BaseModel):
    """Pydantic model for creating physical education meals."""
    
    name: str
    description: Optional[str] = None
    type: MealType
    calories: int
    protein_grams: int
    carbs_grams: int
    fat_grams: int
    nutrition_plan_id: int

class PhysicalEducationMealUpdate(BaseModel):
    """Pydantic model for updating physical education meals."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[MealType] = None
    calories: Optional[int] = None
    protein_grams: Optional[int] = None
    carbs_grams: Optional[int] = None
    fat_grams: Optional[int] = None

class PhysicalEducationMealResponse(BaseModel):
    """Pydantic model for physical education meal responses."""
    
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

class PhysicalEducationMealFood(BaseModelMixin, TimestampMixin):
    """Model for foods in physical education meals."""
    
    __tablename__ = "physical_education_meal_foods"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("physical_education_meals.id"), nullable=False)
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
    meal = relationship("PhysicalEducationMeal", back_populates="foods")

# Removed duplicate Food class - using MealFood instead

# Removed duplicate Food Pydantic models - using MealFood models instead

class NutritionGoal(BaseModelMixin, TimestampMixin):
    """Model for nutrition goals."""
    __tablename__ = "physical_education_nutrition_goals"  # Changed to avoid conflicts
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
    __tablename__ = "physical_education_nutrition_education"  # Changed to avoid conflicts
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

class PhysicalEducationMealFoodCreate(BaseModel):
    """Pydantic model for creating physical education meal foods."""
    
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

class PhysicalEducationMealFoodUpdate(BaseModel):
    """Pydantic model for updating physical education meal foods."""
    
    food_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    food_notes: Optional[str] = None
    food_metadata: Optional[dict] = None

class PhysicalEducationMealFoodResponse(BaseModel):
    """Pydantic model for physical education meal food responses."""
    
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

# Food models for backward compatibility
class Food(BaseModelMixin, TimestampMixin):
    """Model for food items."""
    __tablename__ = "foods"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    calories_per_100g = Column(Float)
    protein_per_100g = Column(Float)
    carbs_per_100g = Column(Float)
    fat_per_100g = Column(Float)
    food_category = Column(String(50))
    food_metadata = Column(JSON)
    
    def __repr__(self):
        return f"<Food {self.name} - {self.calories_per_100g} cal/100g>"

class FoodCreate(BaseModel):
    """Pydantic model for creating food items."""
    
    name: str
    description: Optional[str] = None
    calories_per_100g: Optional[float] = None
    protein_per_100g: Optional[float] = None
    carbs_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None
    food_category: Optional[str] = None
    food_metadata: Optional[dict] = None

class FoodUpdate(BaseModel):
    """Pydantic model for updating food items."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    calories_per_100g: Optional[float] = None
    protein_per_100g: Optional[float] = None
    carbs_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None
    food_category: Optional[str] = None
    food_metadata: Optional[dict] = None

class FoodResponse(BaseModel):
    """Pydantic model for food item responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    calories_per_100g: Optional[float] = None
    protein_per_100g: Optional[float] = None
    carbs_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None
    food_category: Optional[str] = None
    food_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 