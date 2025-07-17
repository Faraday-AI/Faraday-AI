from app.services.physical_education.config.model_paths import get_model_path, ensure_model_directories 
import logging
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.monitoring import track_metrics
from app.core.database import get_db
from app.models.physical_education.nutrition import (
    NutritionPlan,
    Meal,
    MealFood,
    Food,
    PhysicalEducationNutritionLog,
    PhysicalEducationNutritionRecommendation,
    NutritionEducation,
)
from app.models.physical_education.pe_enums.pe_types import (
    MealType,
    NutritionCategory,
    DietaryRestriction
)

class NutritionPlanner:
    """Manager for handling nutrition plans and dietary tracking."""

    def __init__(self):
        self.logger = logging.getLogger("nutrition_planner")
        
        # Nutrition recommendation templates
        self.meal_templates = {
            MealType.BREAKFAST: {
                "standard": {
                    "name": "Balanced Breakfast",
                    "description": "A balanced breakfast with protein, carbs, and healthy fats",
                    "serving_size": "1 plate",
                    "calories": 400,
                    "protein": 20,
                    "carbohydrates": 45,
                    "fats": 15,
                    "preparation_time": 15,
                    "ingredients": [
                        "Whole grain bread",
                        "Eggs",
                        "Avocado",
                        "Fresh fruit"
                    ],
                    "instructions": {
                        "1": "Toast bread",
                        "2": "Prepare eggs",
                        "3": "Slice avocado",
                        "4": "Serve with fruit"
                    }
                }
            },
            MealType.PRE_WORKOUT: {
                "standard": {
                    "name": "Pre-Workout Snack",
                    "description": "Light, energizing snack before exercise",
                    "serving_size": "1 portion",
                    "calories": 200,
                    "protein": 10,
                    "carbohydrates": 30,
                    "fats": 5,
                    "preparation_time": 5,
                    "ingredients": [
                        "Banana",
                        "Greek yogurt",
                        "Honey"
                    ],
                    "instructions": {
                        "1": "Mix yogurt with honey",
                        "2": "Serve with banana"
                    }
                }
            }
            # Add more meal templates...
        }

    @track_metrics
    async def create_nutrition_plan(
        self,
        db: Session,
        student_id: int,
        category: NutritionCategory,
        name: str,
        description: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        dietary_restrictions: Optional[List[str]] = None,
        caloric_target: Optional[int] = None,
        macronutrient_targets: Optional[Dict] = None,
        hydration_target: Optional[float] = None,
        special_instructions: Optional[str] = None,
        medical_considerations: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> NutritionPlan:
        """Create a new nutrition plan."""
        try:
            plan = NutritionPlan(
                student_id=student_id,
                plan_name=name,
                start_date=start_date,
                end_date=end_date,
                daily_calories=caloric_target,
                protein_goal=macronutrient_targets.get('protein') if macronutrient_targets else None,
                carbs_goal=macronutrient_targets.get('carbohydrates') if macronutrient_targets else None,
                fat_goal=macronutrient_targets.get('fats') if macronutrient_targets else None,
                plan_notes=special_instructions,
                plan_metadata={
                    'category': category,
                    'description': description,
                    'dietary_restrictions': dietary_restrictions,
                    'hydration_target': hydration_target,
                    'medical_considerations': medical_considerations,
                    **(metadata or {})
                }
            )
            
            db.add(plan)
            db.commit()
            db.refresh(plan)
            
            return plan
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error creating nutrition plan: {str(e)}")
            raise

    @track_metrics
    async def add_meal_to_plan(
        self,
        db: Session,
        plan_id: int,
        meal_type: MealType,
        name: str,
        description: str,
        serving_size: str,
        calories: Optional[int] = None,
        protein: Optional[float] = None,
        carbohydrates: Optional[float] = None,
        fats: Optional[float] = None,
        preparation_time: Optional[int] = None,
        ingredients: List[str] = None,
        instructions: Dict[str, str] = None,
        alternatives: Optional[Dict] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Meal:
        """Add a meal to a nutrition plan."""
        try:
            meal = Meal(
                nutrition_plan_id=plan_id,
                meal_type=meal_type.value,
                meal_time=datetime.utcnow(),
                calories=calories,
                protein=protein,
                carbs=carbohydrates,
                fat=fats,
                meal_notes=notes,
                meal_metadata={
                    'name': name,
                    'description': description,
                    'serving_size': serving_size,
                    'preparation_time': preparation_time,
                    'ingredients': ingredients or [],
                    'instructions': instructions or {},
                    'alternatives': alternatives,
                    **(metadata or {})
                }
            )
            
            db.add(meal)
            db.commit()
            db.refresh(meal)
            
            return meal
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error adding meal to plan: {str(e)}")
            raise

    @track_metrics
    async def log_nutrition(
        self,
        db: Session,
        student_id: int,
        meal_type: MealType,
        foods_consumed: List[Dict],
        calories: Optional[int] = None,
        protein: Optional[float] = None,
        carbohydrates: Optional[float] = None,
        fats: Optional[float] = None,
        hydration: Optional[float] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> PhysicalEducationNutritionLog:
        """Log nutrition intake."""
        try:
            log = PhysicalEducationNutritionLog(
                student_id=student_id,
                date=datetime.utcnow(),
                meal_type=meal_type,
                foods_consumed=foods_consumed,
                calories=calories,
                protein=protein,
                carbohydrates=carbohydrates,
                fats=fats,
                hydration=hydration,
                notes=notes,
                metadata=metadata or {}
            )
            
            db.add(log)
            db.commit()
            db.refresh(log)
            
            return log
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error logging nutrition: {str(e)}")
            raise

    @track_metrics
    async def generate_recommendations(
        self,
        db: Session,
        student_id: int,
        activity_level: str = "moderate",
        dietary_restrictions: Optional[List[DietaryRestriction]] = None
    ) -> List[PhysicalEducationNutritionRecommendation]:
        """Generate nutrition recommendations."""
        try:
            recommendations = []
            
            # Generate meal-specific recommendations
            for meal_type in MealType:
                if meal_type in self.meal_templates:
                    template = self.meal_templates[meal_type]["standard"]
                    
                    # Adjust for dietary restrictions
                    if dietary_restrictions:
                        template = self._adjust_for_restrictions(template, dietary_restrictions)
                    
                    recommendation = PhysicalEducationNutritionRecommendation(
                        student_id=student_id,
                        category=NutritionCategory.GENERAL,
                        meal_type=meal_type,
                        description=f"Recommended {meal_type.value} meal plan",
                        reasoning=f"Based on {activity_level} activity level",
                        suggested_foods=template["ingredients"],
                        nutrient_targets={
                            "calories": template["calories"],
                            "protein": template["protein"],
                            "carbohydrates": template["carbohydrates"],
                            "fats": template["fats"]
                        },
                        recommendation_metadata={
                            "preparation_time": template["preparation_time"],
                            "instructions": template["instructions"]
                        }
                    )
                    
                    recommendations.append(recommendation)
            
            db.add_all(recommendations)
            db.commit()
            for rec in recommendations:
                db.refresh(rec)
            
            return recommendations
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error generating recommendations: {str(e)}")
            raise

    @track_metrics
    async def get_nutrition_history(
        self,
        db: Session,
        student_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        meal_type: Optional[MealType] = None
    ) -> List[PhysicalEducationNutritionLog]:
        """Get nutrition history for a student."""
        try:
            query = db.query(PhysicalEducationNutritionLog).filter(PhysicalEducationNutritionLog.student_id == student_id)
            
            if start_date:
                query = query.filter(PhysicalEducationNutritionLog.date >= start_date)
            if end_date:
                query = query.filter(PhysicalEducationNutritionLog.date <= end_date)
            if meal_type:
                query = query.filter(PhysicalEducationNutritionLog.meal_type == meal_type)
                
            return query.order_by(PhysicalEducationNutritionLog.date.desc()).all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving nutrition history: {str(e)}")
            raise

    @track_metrics
    async def create_education_material(
        self,
        db: Session,
        title: str,
        category: NutritionCategory,
        content: Dict,
        age_group: str,
        learning_objectives: List[str],
        activities: Optional[List[Dict]] = None,
        resources: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> NutritionEducation:
        """Create nutrition education material."""
        try:
            material = NutritionEducation(
                title=title,
                category=category,
                content=content,
                age_group=age_group,
                learning_objectives=learning_objectives,
                activities=activities,
                resources=resources,
                metadata=metadata or {}
            )
            
            db.add(material)
            db.commit()
            db.refresh(material)
            
            return material
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error creating education material: {str(e)}")
            raise

    def _adjust_for_restrictions(
        self,
        template: Dict,
        restrictions: List[DietaryRestriction]
    ) -> Dict:
        """Adjust meal template for dietary restrictions."""
        adjusted = template.copy()
        
        # Implement restriction-based adjustments here
        # For now, return unmodified template
        return adjusted

# Initialize global nutrition planner
nutrition_planner = NutritionPlanner() 