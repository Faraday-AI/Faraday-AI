"""Nutrition-related models for physical education."""
import enum
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase

class MealType(str, enum.Enum):
    """Types of meals."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    PRE_WORKOUT = "pre_workout"
    POST_WORKOUT = "post_workout"
    RECOVERY = "recovery"

class DietaryRestriction(str, enum.Enum):
    """Types of dietary restrictions."""
    NONE = "none"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"
    HALAL = "halal"
    KOSHER = "kosher"
    OTHER = "other"

class NutritionCategory(str, enum.Enum):
    """Categories of nutrition education and plans."""
    GENERAL = "general"
    SPORTS = "sports"
    WEIGHT_MANAGEMENT = "weight_management"
    HEALTH_CONDITION = "health_condition"
    PERFORMANCE = "performance"
    RECOVERY = "recovery"

class NutritionEducation(SharedBase):
    """Model for nutrition education materials."""
    __tablename__ = "nutrition_education"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(Enum(NutritionCategory), nullable=False)
    content = Column(JSON, nullable=False)  # Educational content
    learning_objectives = Column(JSON, nullable=False)
    resources = Column(JSON, nullable=True)  # Additional resources
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<NutritionEducation {self.title}>"

class NutritionPlan(SharedBase):
    """Model for student nutrition plans."""
    __tablename__ = "nutrition_plans"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    dietary_restrictions = Column(JSON, nullable=True)  # List of DietaryRestriction
    calorie_target = Column(Integer, nullable=True)
    macronutrient_targets = Column(JSON, nullable=True)  # Protein, carbs, fats
    hydration_target = Column(Float, nullable=True)  # Liters per day
    special_instructions = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student")  # , back_populates="nutrition_plans")
    meals = relationship("MealPlan", back_populates="nutrition_plan")
    goals = relationship("NutritionGoal", back_populates="nutrition_plan")

    def __repr__(self):
        return f"<NutritionPlan {self.title} - {self.student_id}>"

class NutritionGoal(SharedBase):
    """Model for nutrition-related goals."""
    __tablename__ = "nutrition_goals"

    id = Column(Integer, primary_key=True, index=True)
    nutrition_plan_id = Column(Integer, ForeignKey("nutrition_plans.id"), nullable=False)
    description = Column(String, nullable=False)
    target_value = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    deadline = Column(DateTime, nullable=True)
    progress = Column(Float, default=0)  # Percentage
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    nutrition_plan = relationship("NutritionPlan", back_populates="goals")

    def __repr__(self):
        return f"<NutritionGoal {self.description}>"

class MealPlan(SharedBase):
    """Model for planned meals within a nutrition plan."""
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    nutrition_plan_id = Column(Integer, ForeignKey("nutrition_plans.id"), nullable=False)
    meal_type = Column(Enum(MealType), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    serving_size = Column(String, nullable=False)
    calories = Column(Integer, nullable=True)
    protein = Column(Float, nullable=True)
    carbohydrates = Column(Float, nullable=True)
    fats = Column(Float, nullable=True)
    preparation_time = Column(Integer, nullable=True)  # minutes
    ingredients = Column(JSON, nullable=False)
    instructions = Column(JSON, nullable=False)
    alternatives = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    nutrition_plan = relationship("NutritionPlan", back_populates="meals")

    def __repr__(self):
        return f"<MealPlan {self.name} - {self.meal_type}>"

class NutritionLog(SharedBase):
    """Model for tracking student nutrition logs."""
    __tablename__ = "nutrition_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    meal_type = Column(Enum(MealType), nullable=False)
    foods_consumed = Column(JSON, nullable=False)
    calories = Column(Integer, nullable=True)
    protein = Column(Float, nullable=True)
    carbohydrates = Column(Float, nullable=True)
    fats = Column(Float, nullable=True)
    hydration = Column(Float, nullable=True)  # Liters
    notes = Column(String, nullable=True)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="nutrition_logs")

    def __repr__(self):
        return f"<NutritionLog {self.student_id} - {self.date}>"

class NutritionRecommendation(SharedBase):
    """Model for AI-generated nutrition recommendations."""
    __tablename__ = "nutrition_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    category = Column(Enum(NutritionCategory), nullable=False)
    meal_type = Column(Enum(MealType), nullable=True)
    description = Column(String, nullable=False)
    reasoning = Column(String, nullable=False)
    suggested_foods = Column(JSON, nullable=True)
    nutrient_targets = Column(JSON, nullable=True)
    priority = Column(Integer, default=2)
    is_implemented = Column(Boolean, default=False)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="nutrition_recommendations")

    def __repr__(self):
        return f"<NutritionRecommendation {self.student_id} - {self.category}>"

class Meal(SharedBase):
    """Model for individual meals."""
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    meal_type = Column(Enum(MealType), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    date = Column(DateTime, nullable=False)
    time = Column(DateTime, nullable=False)
    
    # Nutritional information
    total_calories = Column(Integer, nullable=True)
    total_protein = Column(Float, nullable=True)
    total_carbohydrates = Column(Float, nullable=True)
    total_fats = Column(Float, nullable=True)
    total_fiber = Column(Float, nullable=True)
    total_sugar = Column(Float, nullable=True)
    total_sodium = Column(Float, nullable=True)
    
    # Meal details
    preparation_time = Column(Integer, nullable=True)  # minutes
    cooking_method = Column(String, nullable=True)
    serving_size = Column(String, nullable=True)
    temperature = Column(String, nullable=True)  # hot, cold, room temperature
    
    # Tracking
    was_consumed = Column(Boolean, default=True)
    consumption_notes = Column(String, nullable=True)
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5 scale
    hunger_level_before = Column(Integer, nullable=True)  # 1-10 scale
    hunger_level_after = Column(Integer, nullable=True)  # 1-10 scale
    
    # Additional data
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="meals")
    food_items = relationship("MealFoodItem", back_populates="meal", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Meal {self.name} - {self.meal_type}>"

class FoodItem(SharedBase):
    """Model for individual food items."""
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)  # fruits, vegetables, grains, etc.
    
    # Nutritional information per 100g
    calories_per_100g = Column(Float, nullable=True)
    protein_per_100g = Column(Float, nullable=True)
    carbohydrates_per_100g = Column(Float, nullable=True)
    fats_per_100g = Column(Float, nullable=True)
    fiber_per_100g = Column(Float, nullable=True)
    sugar_per_100g = Column(Float, nullable=True)
    sodium_per_100g = Column(Float, nullable=True)
    
    # Allergen information
    allergens = Column(JSON, nullable=True)  # List of allergens
    dietary_restrictions = Column(JSON, nullable=True)  # List of dietary restrictions
    
    # Food properties
    is_organic = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    is_dairy_free = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_vegetarian = Column(Boolean, default=False)
    
    # Storage and preparation
    storage_instructions = Column(String, nullable=True)
    shelf_life_days = Column(Integer, nullable=True)
    preparation_notes = Column(String, nullable=True)
    
    # Additional data
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    meal_items = relationship("MealFoodItem", back_populates="food_item")

    def __repr__(self):
        return f"<FoodItem {self.name}>"

class MealFoodItem(SharedBase):
    """Model for associating food items with meals."""
    __tablename__ = "meal_food_items"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=False)
    quantity = Column(Float, nullable=False)  # Amount in grams or units
    unit = Column(String, nullable=False)  # g, oz, cup, piece, etc.
    
    # Calculated nutritional values for this specific quantity
    calories = Column(Integer, nullable=True)
    protein = Column(Float, nullable=True)
    carbohydrates = Column(Float, nullable=True)
    fats = Column(Float, nullable=True)
    fiber = Column(Float, nullable=True)
    sugar = Column(Float, nullable=True)
    sodium = Column(Float, nullable=True)
    
    # Preparation details
    preparation_method = Column(String, nullable=True)
    cooking_time = Column(Integer, nullable=True)  # minutes
    temperature = Column(String, nullable=True)
    
    # Notes
    notes = Column(String, nullable=True)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    meal = relationship("Meal", back_populates="food_items")
    food_item = relationship("FoodItem", back_populates="meal_items")

    def __repr__(self):
        return f"<MealFoodItem {self.food_item_id} - {self.quantity}{self.unit}>" 