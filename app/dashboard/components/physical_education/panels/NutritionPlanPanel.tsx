import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Alert,
  CircularProgress,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Restaurant as MealIcon,
} from '@mui/icons-material';

interface NutritionPlan {
  id: number;
  category: string;
  name: string;
  description: string;
  startDate: string;
  endDate?: string;
  dietaryRestrictions: string[];
  caloricTarget?: number;
  macronutrientTargets: {
    protein: number;
    carbohydrates: number;
    fats: number;
  };
  hydrationTarget?: number;
  specialInstructions?: string;
  medicalConsiderations?: Record<string, any>;
  status: string;
}

interface NutritionLog {
  id: number;
  planId: number;
  mealType: string;
  foodsConsumed: Array<{
    name: string;
    portion: string;
    calories?: number;
  }>;
  calories?: number;
  protein?: number;
  carbohydrates?: number;
  fats?: number;
  hydration?: number;
  timestamp: string;
}

interface MealPlan {
  id: number;
  planId: number;
  day: string;
  meals: Array<{
    type: string;
    time: string;
    foods: Array<{
      name: string;
      portion: string;
      calories: number;
      protein: number;
      carbohydrates: number;
      fats: number;
    }>;
    totalCalories: number;
    totalProtein: number;
    totalCarbs: number;
    totalFats: number;
  }>;
}

interface NutrientAnalysis {
  planId: number;
  date: string;
  totalCalories: number;
  macronutrients: {
    protein: {
      total: number;
      percentage: number;
      target: number;
    };
    carbohydrates: {
      total: number;
      percentage: number;
      target: number;
    };
    fats: {
      total: number;
      percentage: number;
      target: number;
    };
  };
  micronutrients: {
    vitamins: Record<string, number>;
    minerals: Record<string, number>;
  };
  hydration: {
    total: number;
    target: number;
    percentage: number;
  };
}

interface DietaryRecommendation {
  planId: number;
  type: 'MEAL' | 'SNACK' | 'SUPPLEMENT';
  name: string;
  description: string;
  nutritionalValue: {
    calories: number;
    protein: number;
    carbohydrates: number;
    fats: number;
  };
  timing: string;
  reason: string;
}

interface Recipe {
  id: number;
  name: string;
  ingredients: Array<{
    name: string;
    amount: string;
    unit: string;
    nutritionalInfo: {
      calories: number;
      protein: number;
      carbohydrates: number;
      fats: number;
    };
  }>;
  instructions: string[];
  prepTime: number;
  cookTime: number;
  servings: number;
  dietaryTags: string[];
  allergens: string[];
}

interface GroceryList {
  id: number;
  planId: number;
  items: Array<{
    name: string;
    amount: string;
    unit: string;
    category: string;
    priority: 'HIGH' | 'MEDIUM' | 'LOW';
  }>;
  totalItems: number;
  estimatedCost: number;
}

interface NutrientBalance {
  planId: number;
  date: string;
  macronutrientRatio: {
    protein: number;
    carbohydrates: number;
    fats: number;
  };
  micronutrientStatus: {
    vitamins: Record<string, { current: number; target: number; status: 'DEFICIENT' | 'ADEQUATE' | 'EXCESS' }>;
    minerals: Record<string, { current: number; target: number; status: 'DEFICIENT' | 'ADEQUATE' | 'EXCESS' }>;
  };
  fiber: {
    current: number;
    target: number;
    status: 'DEFICIENT' | 'ADEQUATE' | 'EXCESS';
  };
}

interface WorkoutNutritionSync {
  planId: number;
  workoutId: number;
  preWorkout: {
    timing: string;
    recommendations: string[];
    nutrients: {
      carbohydrates: number;
      protein: number;
      hydration: number;
    };
  };
  postWorkout: {
    timing: string;
    recommendations: string[];
    nutrients: {
      carbohydrates: number;
      protein: number;
      hydration: number;
    };
  };
}

interface DietaryProfile {
  planId: number;
  allergies: Array<{
    name: string;
    severity: 'MILD' | 'MODERATE' | 'SEVERE';
    symptoms: string[];
    lastReaction?: string;
  }>;
  intolerances: Array<{
    name: string;
    severity: 'MILD' | 'MODERATE' | 'SEVERE';
    symptoms: string[];
    threshold?: number;
  }>;
  preferences: {
    dietaryStyle: 'OMNIVORE' | 'VEGETARIAN' | 'VEGAN' | 'PESCATARIAN' | 'KETO' | 'PALEO';
    mealTiming: {
      breakfast: string;
      lunch: string;
      dinner: string;
      snacks: string[];
    };
    foodPreferences: string[];
    dislikes: string[];
  };
}

interface NutritionProgress {
  planId: number;
  period: {
    start: string;
    end: string;
  };
  trends: {
    calories: {
      daily: number[];
      weekly: number[];
      monthly: number[];
    };
    macronutrients: {
      protein: {
        daily: number[];
        weekly: number[];
        monthly: number[];
      };
      carbohydrates: {
        daily: number[];
        weekly: number[];
        monthly: number[];
      };
      fats: {
        daily: number[];
        weekly: number[];
        monthly: number[];
      };
    };
    hydration: {
      daily: number[];
      weekly: number[];
      monthly: number[];
    };
  };
  goals: {
    calories: {
      target: number;
      current: number;
      progress: number;
    };
    macronutrients: {
      protein: {
        target: number;
        current: number;
        progress: number;
      };
      carbohydrates: {
        target: number;
        current: number;
        progress: number;
      };
      fats: {
        target: number;
        current: number;
        progress: number;
      };
    };
    hydration: {
      target: number;
      current: number;
      progress: number;
    };
  };
  workoutCorrelation: {
    performance: {
      strength: number;
      endurance: number;
      recovery: number;
    };
    nutrition: {
      preWorkout: number;
      postWorkout: number;
      recovery: number;
    };
  };
}

interface SmartRecommendation {
  planId: number;
  type: 'MEAL' | 'SNACK' | 'SUPPLEMENT' | 'TIMING' | 'PORTION';
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  description: string;
  rationale: string;
  implementation: string[];
  expectedBenefits: string[];
  constraints: {
    budget?: number;
    time?: number;
    availability?: string[];
  };
  alternatives: Array<{
    name: string;
    description: string;
    benefits: string[];
    constraints: {
      budget?: number;
      time?: number;
      availability?: string[];
    };
  }>;
}

interface MealPrepSchedule {
  planId: number;
  week: {
    start: string;
    end: string;
  };
  prepSessions: Array<{
    day: string;
    time: string;
    duration: number;
    meals: Array<{
      name: string;
      servings: number;
      prepTime: number;
      cookTime: number;
      ingredients: Array<{
        name: string;
        amount: string;
        unit: string;
      }>;
    }>;
    totalPrepTime: number;
    totalCookTime: number;
    efficiency: number;
  }>;
  batchCooking: {
    recipes: Array<{
      name: string;
      servings: number;
      storage: string;
      shelfLife: string;
    }>;
    totalServings: number;
    storageSpace: string;
  };
}

interface NutritionalAnalytics {
  planId: number;
  period: {
    start: string;
    end: string;
  };
  patterns: {
    mealTiming: {
      consistency: number;
      optimalTiming: number;
      recommendations: string[];
    };
    nutrientDistribution: {
      daily: Record<string, number>;
      weekly: Record<string, number>;
      monthly: Record<string, number>;
    };
    costEffectiveness: {
      costPerMeal: number;
      costPerNutrient: Record<string, number>;
      savings: number;
    };
    timeManagement: {
      prepEfficiency: number;
      cookEfficiency: number;
      timeSavings: number;
    };
    sustainability: {
      carbonFootprint: number;
      foodWaste: number;
      localIngredients: number;
    };
  };
}

interface SmartIntegration {
  planId: number;
  shopping: {
    optimizedList: Array<{
      item: string;
      amount: string;
      unit: string;
      priority: 'HIGH' | 'MEDIUM' | 'LOW';
      stores: string[];
      bestPrice: number;
    }>;
    totalCost: number;
    savings: number;
    timeEstimate: number;
  };
  timing: {
    optimalMealTimes: {
      breakfast: string;
      lunch: string;
      dinner: string;
      snacks: string[];
    };
    workoutAlignment: {
      preWorkout: string;
      postWorkout: string;
      recovery: string;
    };
    sleepOptimization: {
      lastMeal: string;
      fastingWindow: string;
    };
  };
  recipeAdaptation: {
    modifications: Array<{
      original: string;
      adapted: string;
      reason: string;
      benefits: string[];
    }>;
    successRate: number;
    userPreference: number;
  };
  progressPrediction: {
    shortTerm: {
      calories: number;
      weight: number;
      performance: number;
    };
    longTerm: {
      calories: number;
      weight: number;
      performance: number;
    };
    confidence: number;
  };
}

export const NutritionPlanPanel: React.FC = (): JSX.Element => {
  const [plans, setPlans] = useState<NutritionPlan[]>([]);
  const [logs, setLogs] = useState<NutritionLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [logDialogOpen, setLogDialogOpen] = useState(false);
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null);
  const [newLogData, setNewLogData] = useState({
    mealType: 'BREAKFAST',
    foodsConsumed: [],
    calories: '',
    protein: '',
    carbohydrates: '',
    fats: '',
    hydration: '',
  });
  const [newPlanData, setNewPlanData] = useState({
    category: 'GENERAL',
    name: '',
    description: '',
    dietaryRestrictions: [],
    caloricTarget: '',
    macronutrientTargets: {
      protein: 0,
      carbohydrates: 0,
      fats: 0,
    },
    hydrationTarget: '',
  });
  const [mealPlans, setMealPlans] = useState<MealPlan[]>([]);
  const [nutrientAnalysis, setNutrientAnalysis] = useState<NutrientAnalysis | null>(null);
  const [dietaryRecommendations, setDietaryRecommendations] = useState<DietaryRecommendation[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [groceryList, setGroceryList] = useState<GroceryList | null>(null);
  const [nutrientBalance, setNutrientBalance] = useState<NutrientBalance | null>(null);
  const [workoutSync, setWorkoutSync] = useState<WorkoutNutritionSync | null>(null);
  const [dietaryProfile, setDietaryProfile] = useState<DietaryProfile | null>(null);
  const [nutritionProgress, setNutritionProgress] = useState<NutritionProgress | null>(null);
  const [smartRecommendations, setSmartRecommendations] = useState<SmartRecommendation[]>([]);
  const [mealPrepSchedule, setMealPrepSchedule] = useState<MealPrepSchedule | null>(null);
  const [nutritionalAnalytics, setNutritionalAnalytics] = useState<NutritionalAnalytics | null>(null);
  const [smartIntegration, setSmartIntegration] = useState<SmartIntegration | null>(null);

  const categories = [
    { value: 'GENERAL', label: 'General' },
    { value: 'PERFORMANCE', label: 'Performance' },
    { value: 'WEIGHT_MANAGEMENT', label: 'Weight Management' },
    { value: 'SPECIAL_NEEDS', label: 'Special Needs' },
  ];

  const mealTypes = [
    { value: 'BREAKFAST', label: 'Breakfast' },
    { value: 'LUNCH', label: 'Lunch' },
    { value: 'DINNER', label: 'Dinner' },
    { value: 'SNACK', label: 'Snack' },
  ];

  useEffect(() => {
    fetchPlans();
    fetchLogs();
    fetchMealPlans();
    if (selectedPlanId) {
      fetchMealPrepSchedule(selectedPlanId);
      fetchNutritionalAnalytics(selectedPlanId);
      fetchSmartIntegration(selectedPlanId);
    }
  }, [selectedPlanId]);

  const fetchPlans = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        '/api/v1/physical-education/health-fitness/students/1/nutrition-plans'
      );
      if (!response.ok) throw new Error('Failed to fetch plans');
      const data = await response.json();
      setPlans(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await fetch(
        '/api/v1/physical-education/health-fitness/students/1/nutrition-logs'
      );
      if (!response.ok) throw new Error('Failed to fetch logs');
      const data = await response.json();
      setLogs(data);
    } catch (err) {
      console.error('Error fetching logs:', err);
    }
  };

  const fetchMealPlans = async () => {
    try {
      const response = await fetch(
        '/api/v1/physical-education/health-fitness/students/1/meal-plans'
      );
      if (!response.ok) throw new Error('Failed to fetch meal plans');
      const data = await response.json();
      setMealPlans(data);
    } catch (err) {
      console.error('Error fetching meal plans:', err);
    }
  };

  const fetchMealPrepSchedule = async (planId: number) => {
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/nutrition-plans/${planId}/meal-prep-schedule`
      );
      if (!response.ok) throw new Error('Failed to fetch meal prep schedule');
      const data = await response.json();
      setMealPrepSchedule(data);
    } catch (err) {
      console.error('Error fetching meal prep schedule:', err);
    }
  };

  const fetchNutritionalAnalytics = async (planId: number) => {
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/nutrition-plans/${planId}/analytics`
      );
      if (!response.ok) throw new Error('Failed to fetch nutritional analytics');
      const data = await response.json();
      setNutritionalAnalytics(data);
    } catch (err) {
      console.error('Error fetching nutritional analytics:', err);
    }
  };

  const fetchSmartIntegration = async (planId: number) => {
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/nutrition-plans/${planId}/smart-integration`
      );
      if (!response.ok) throw new Error('Failed to fetch smart integration');
      const data = await response.json();
      setSmartIntegration(data);
    } catch (err) {
      console.error('Error fetching smart integration:', err);
    }
  };

  const analyzeNutrients = async (planId: number) => {
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/nutrition-plans/${planId}/analysis`
      );
      if (!response.ok) throw new Error('Failed to analyze nutrients');
      const data = await response.json();
      setNutrientAnalysis(data);
    } catch (err) {
      console.error('Error analyzing nutrients:', err);
    }
  };

  const getDietaryRecommendations = async (planId: number) => {
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/nutrition-plans/${planId}/recommendations`
      );
      if (!response.ok) throw new Error('Failed to get recommendations');
      const data = await response.json();
      setDietaryRecommendations(data);
    } catch (err) {
      console.error('Error getting recommendations:', err);
    }
  };

  const handleAddPlan = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        '/api/v1/physical-education/health-fitness/students/1/nutrition-plans',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(newPlanData),
        }
      );
      if (!response.ok) throw new Error('Failed to add plan');
      setNewPlanData({
        category: 'GENERAL',
        name: '',
        description: '',
        dietaryRestrictions: [],
        caloricTarget: '',
        macronutrientTargets: {
          protein: 0,
          carbohydrates: 0,
          fats: 0,
        },
        hydrationTarget: '',
      });
      fetchPlans();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleAddLog = async () => {
    if (!selectedPlanId) return;
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/nutrition-plans/${selectedPlanId}/logs`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            meal_type: newLogData.mealType,
            foods_consumed: newLogData.foodsConsumed,
            calories: newLogData.calories ? parseInt(newLogData.calories) : undefined,
            protein: newLogData.protein ? parseFloat(newLogData.protein) : undefined,
            carbohydrates: newLogData.carbohydrates ? parseFloat(newLogData.carbohydrates) : undefined,
            fats: newLogData.fats ? parseFloat(newLogData.fats) : undefined,
            hydration: newLogData.hydration ? parseFloat(newLogData.hydration) : undefined,
          }),
        }
      );
      if (!response.ok) throw new Error('Failed to add log');
      setLogDialogOpen(false);
      setNewLogData({
        mealType: 'BREAKFAST',
        foodsConsumed: [],
        calories: '',
        protein: '',
        carbohydrates: '',
        fats: '',
        hydration: '',
      });
      fetchLogs();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const fetchRecipes = async (planId: number) => {
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/nutrition-plans/${planId}/recipes`
      );
      if (!response.ok) throw new Error('Failed to fetch recipes');
      const data = await response.json();
      setRecipes(data);
    } catch (err) {
      console.error('Error fetching recipes:', err);
    }
  };

  const generateGroceryList = async (planId: number) => {
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/nutrition-plans/${planId}/grocery-list`
      );
      if (!response.ok) throw new Error('Failed to generate grocery list');
      const data = await response.json();
      setGroceryList(data);
    } catch (err) {
      console.error('Error generating grocery list:', err);
    }
  };

  const analyzeNutrientBalance = async (planId: number) => {
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/nutrition-plans/${planId}/nutrient-balance`
      );
      if (!response.ok) throw new Error('Failed to analyze nutrient balance');
      const data = await response.json();
      setNutrientBalance(data);
    } catch (err) {
      console.error('Error analyzing nutrient balance:', err);
    }
  };

  const syncWithWorkout = async (planId: number, workoutId: number) => {
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/nutrition-plans/${planId}/workout-sync/${workoutId}`
      );
      if (!response.ok) throw new Error('Failed to sync with workout');
      const data = await response.json();
      setWorkoutSync(data);
    } catch (err) {
      console.error('Error syncing with workout:', err);
    }
  };

  const fetchDietaryProfile = async (planId: number) => {
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/nutrition-plans/${planId}/dietary-profile`
      );
      if (!response.ok) throw new Error('Failed to fetch dietary profile');
      const data = await response.json();
      setDietaryProfile(data);
    } catch (err) {
      console.error('Error fetching dietary profile:', err);
    }
  };

  const fetchNutritionProgress = async (planId: number) => {
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/nutrition-plans/${planId}/progress`
      );
      if (!response.ok) throw new Error('Failed to fetch nutrition progress');
      const data = await response.json();
      setNutritionProgress(data);
    } catch (err) {
      console.error('Error fetching nutrition progress:', err);
    }
  };

  const fetchSmartRecommendations = async (planId: number) => {
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/nutrition-plans/${planId}/smart-recommendations`
      );
      if (!response.ok) throw new Error('Failed to fetch smart recommendations');
      const data = await response.json();
      setSmartRecommendations(data);
    } catch (err) {
      console.error('Error fetching smart recommendations:', err);
    }
  };

  const handlePlanSelect = (planId: number) => {
    setSelectedPlanId(planId);
  };

  const NutrientAnalysisCard: React.FC<{ analysis: NutrientAnalysis }> = ({ analysis }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Nutrient Analysis
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="subtitle1">
              Total Calories: {analysis.totalCalories}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Macronutrients
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Typography variant="body2" color="text.secondary">
                  Protein
                </Typography>
                <Typography variant="body1">
                  {analysis.macronutrients.protein.total}g ({analysis.macronutrients.protein.percentage}%)
                </Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="body2" color="text.secondary">
                  Carbs
                </Typography>
                <Typography variant="body1">
                  {analysis.macronutrients.carbohydrates.total}g ({analysis.macronutrients.carbohydrates.percentage}%)
                </Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="body2" color="text.secondary">
                  Fats
                </Typography>
                <Typography variant="body1">
                  {analysis.macronutrients.fats.total}g ({analysis.macronutrients.fats.percentage}%)
                </Typography>
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Hydration
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body1">
                {analysis.hydration.total} / {analysis.hydration.target} ml
              </Typography>
              <Chip
                label={`${analysis.hydration.percentage}%`}
                color={analysis.hydration.percentage >= 100 ? 'success' : 'warning'}
              />
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const DietaryRecommendationCard: React.FC<{ recommendations: DietaryRecommendation[] }> = ({ recommendations }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Dietary Recommendations
        </Typography>
        <List>
          {recommendations.map((recommendation, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={recommendation.name}
                secondary={
                  <Box>
                    <Typography variant="body2">
                      {recommendation.description}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Timing: {recommendation.timing}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Reason: {recommendation.reason}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );

  const MealPlanCard: React.FC<{ mealPlan: MealPlan }> = ({ mealPlan }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Meal Plan for {new Date(mealPlan.day).toLocaleDateString()}
        </Typography>
        <List>
          {mealPlan.meals.map((meal, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={`${meal.type} (${meal.time})`}
                secondary={
                  <Box>
                    <Typography variant="body2">
                      Total: {meal.totalCalories} kcal
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      P: {meal.totalProtein}g | C: {meal.totalCarbs}g | F: {meal.totalFats}g
                    </Typography>
                    <List dense>
                      {meal.foods.map((food, foodIndex) => (
                        <ListItem key={foodIndex}>
                          <ListItemText
                            primary={food.name}
                            secondary={`${food.portion} - ${food.calories} kcal`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );

  const RecipeCard: React.FC<{ recipe: Recipe }> = ({ recipe }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {recipe.name}
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Chip label={`${recipe.prepTime} min prep`} size="small" />
          <Chip label={`${recipe.cookTime} min cook`} size="small" />
          <Chip label={`${recipe.servings} servings`} size="small" />
        </Box>
        <Typography variant="subtitle2" gutterBottom>
          Ingredients
        </Typography>
        <List dense>
          {recipe.ingredients.map((ingredient, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={ingredient.name}
                secondary={`${ingredient.amount} ${ingredient.unit}`}
              />
            </ListItem>
          ))}
        </List>
        <Typography variant="subtitle2" gutterBottom>
          Instructions
        </Typography>
        <List dense>
          {recipe.instructions.map((instruction, index) => (
            <ListItem key={index}>
              <ListItemText primary={`${index + 1}. ${instruction}`} />
            </ListItem>
          ))}
        </List>
        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
          {recipe.dietaryTags.map((tag, index) => (
            <Chip key={index} label={tag} size="small" color="primary" />
          ))}
        </Box>
      </CardContent>
    </Card>
  );

  const GroceryListCard: React.FC<{ list: GroceryList }> = ({ list }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Grocery List
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Total Items: {list.totalItems} | Estimated Cost: ${list.estimatedCost.toFixed(2)}
        </Typography>
        <List>
          {list.items.map((item, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={item.name}
                secondary={
                  <Box>
                    <Typography variant="body2">
                      {item.amount} {item.unit}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Category: {item.category}
                    </Typography>
                  </Box>
                }
              />
              <Chip
                label={item.priority}
                size="small"
                color={
                  item.priority === 'HIGH'
                    ? 'error'
                    : item.priority === 'MEDIUM'
                    ? 'warning'
                    : 'success'
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );

  const NutrientBalanceCard: React.FC<{ balance: NutrientBalance }> = ({ balance }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Nutrient Balance
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Macronutrient Ratio
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Typography variant="body2">
                Protein: {balance.macronutrientRatio.protein}%
              </Typography>
              <Typography variant="body2">
                Carbs: {balance.macronutrientRatio.carbohydrates}%
              </Typography>
              <Typography variant="body2">
                Fats: {balance.macronutrientRatio.fats}%
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Micronutrient Status
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(balance.micronutrientStatus.vitamins).map(([vitamin, status]) => (
                <Grid item xs={6} key={vitamin}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2">{vitamin}:</Typography>
                    <Chip
                      label={status.status}
                      size="small"
                      color={
                        status.status === 'DEFICIENT'
                          ? 'error'
                          : status.status === 'EXCESS'
                          ? 'warning'
                          : 'success'
                      }
                    />
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Fiber Status
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2">
                {balance.fiber.current}g / {balance.fiber.target}g
              </Typography>
              <Chip
                label={balance.fiber.status}
                size="small"
                color={
                  balance.fiber.status === 'DEFICIENT'
                    ? 'error'
                    : balance.fiber.status === 'EXCESS'
                    ? 'warning'
                    : 'success'
                }
              />
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const WorkoutSyncCard: React.FC<{ sync: WorkoutNutritionSync }> = ({ sync }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Workout Nutrition Sync
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Pre-Workout
            </Typography>
            <Box sx={{ pl: 2 }}>
              <Typography variant="body2">
                Timing: {sync.preWorkout.timing}
              </Typography>
              <Typography variant="body2">
                Nutrients:
              </Typography>
              <Box sx={{ pl: 2 }}>
                <Typography variant="body2">
                  Carbs: {sync.preWorkout.nutrients.carbohydrates}g
                </Typography>
                <Typography variant="body2">
                  Protein: {sync.preWorkout.nutrients.protein}g
                </Typography>
                <Typography variant="body2">
                  Hydration: {sync.preWorkout.nutrients.hydration}ml
                </Typography>
              </Box>
              <Typography variant="body2">
                Recommendations:
              </Typography>
              <List dense>
                {sync.preWorkout.recommendations.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Post-Workout
            </Typography>
            <Box sx={{ pl: 2 }}>
              <Typography variant="body2">
                Timing: {sync.postWorkout.timing}
              </Typography>
              <Typography variant="body2">
                Nutrients:
              </Typography>
              <Box sx={{ pl: 2 }}>
                <Typography variant="body2">
                  Carbs: {sync.postWorkout.nutrients.carbohydrates}g
                </Typography>
                <Typography variant="body2">
                  Protein: {sync.postWorkout.nutrients.protein}g
                </Typography>
                <Typography variant="body2">
                  Hydration: {sync.postWorkout.nutrients.hydration}ml
                </Typography>
              </Box>
              <Typography variant="body2">
                Recommendations:
              </Typography>
              <List dense>
                {sync.postWorkout.recommendations.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const DietaryProfileCard: React.FC<{ profile: DietaryProfile }> = ({ profile }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Dietary Profile
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Allergies
            </Typography>
            <List dense>
              {profile.allergies.map((allergy, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={allergy.name}
                    secondary={
                      <Box>
                        <Typography variant="body2">
                          Severity: {allergy.severity}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Symptoms: {allergy.symptoms.join(', ')}
                        </Typography>
                        {allergy.lastReaction && (
                          <Typography variant="body2" color="error">
                            Last Reaction: {allergy.lastReaction}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Intolerances
            </Typography>
            <List dense>
              {profile.intolerances.map((intolerance, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={intolerance.name}
                    secondary={
                      <Box>
                        <Typography variant="body2">
                          Severity: {intolerance.severity}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Symptoms: {intolerance.symptoms.join(', ')}
                        </Typography>
                        {intolerance.threshold && (
                          <Typography variant="body2">
                            Threshold: {intolerance.threshold}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Preferences
            </Typography>
            <Box sx={{ pl: 2 }}>
              <Typography variant="body2">
                Dietary Style: {profile.preferences.dietaryStyle}
              </Typography>
              <Typography variant="body2">
                Meal Timing:
              </Typography>
              <Box sx={{ pl: 2 }}>
                <Typography variant="body2">
                  Breakfast: {profile.preferences.mealTiming.breakfast}
                </Typography>
                <Typography variant="body2">
                  Lunch: {profile.preferences.mealTiming.lunch}
                </Typography>
                <Typography variant="body2">
                  Dinner: {profile.preferences.mealTiming.dinner}
                </Typography>
                <Typography variant="body2">
                  Snacks: {profile.preferences.mealTiming.snacks.join(', ')}
                </Typography>
              </Box>
              <Typography variant="body2">
                Food Preferences: {profile.preferences.foodPreferences.join(', ')}
              </Typography>
              <Typography variant="body2">
                Dislikes: {profile.preferences.dislikes.join(', ')}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const NutritionProgressCard: React.FC<{ progress: NutritionProgress }> = ({ progress }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Nutrition Progress
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Goals Progress
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2">
                  Calories: {progress.goals.calories.current} / {progress.goals.calories.target}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={(progress.goals.calories.current / progress.goals.calories.target) * 100}
                />
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">
                  Hydration: {progress.goals.hydration.current} / {progress.goals.hydration.target}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={(progress.goals.hydration.current / progress.goals.hydration.target) * 100}
                />
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Macronutrient Progress
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Typography variant="body2">
                  Protein: {progress.goals.macronutrients.protein.current}g / {progress.goals.macronutrients.protein.target}g
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={(progress.goals.macronutrients.protein.current / progress.goals.macronutrients.protein.target) * 100}
                />
              </Grid>
              <Grid item xs={4}>
                <Typography variant="body2">
                  Carbs: {progress.goals.macronutrients.carbohydrates.current}g / {progress.goals.macronutrients.carbohydrates.target}g
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={(progress.goals.macronutrients.carbohydrates.current / progress.goals.macronutrients.carbohydrates.target) * 100}
                />
              </Grid>
              <Grid item xs={4}>
                <Typography variant="body2">
                  Fats: {progress.goals.macronutrients.fats.current}g / {progress.goals.macronutrients.fats.target}g
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={(progress.goals.macronutrients.fats.current / progress.goals.macronutrients.fats.target) * 100}
                />
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Workout Correlation
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Typography variant="body2">
                  Strength: {progress.workoutCorrelation.performance.strength}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={progress.workoutCorrelation.performance.strength}
                />
              </Grid>
              <Grid item xs={4}>
                <Typography variant="body2">
                  Endurance: {progress.workoutCorrelation.performance.endurance}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={progress.workoutCorrelation.performance.endurance}
                />
              </Grid>
              <Grid item xs={4}>
                <Typography variant="body2">
                  Recovery: {progress.workoutCorrelation.performance.recovery}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={progress.workoutCorrelation.performance.recovery}
                />
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const SmartRecommendationCard: React.FC<{ recommendation: SmartRecommendation }> = ({ recommendation }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            {recommendation.title}
          </Typography>
          <Chip
            label={recommendation.priority}
            color={
              recommendation.priority === 'HIGH'
                ? 'error'
                : recommendation.priority === 'MEDIUM'
                ? 'warning'
                : 'success'
            }
          />
        </Box>
        <Typography variant="body1" gutterBottom>
          {recommendation.description}
        </Typography>
        <Typography variant="subtitle2" gutterBottom>
          Rationale
        </Typography>
        <Typography variant="body2" paragraph>
          {recommendation.rationale}
        </Typography>
        <Typography variant="subtitle2" gutterBottom>
          Implementation
        </Typography>
        <List dense>
          {recommendation.implementation.map((step, index) => (
            <ListItem key={index}>
              <ListItemText primary={step} />
            </ListItem>
          ))}
        </List>
        <Typography variant="subtitle2" gutterBottom>
          Expected Benefits
        </Typography>
        <List dense>
          {recommendation.expectedBenefits.map((benefit, index) => (
            <ListItem key={index}>
              <ListItemText primary={benefit} />
            </ListItem>
          ))}
        </List>
        {recommendation.constraints && (
          <>
            <Typography variant="subtitle2" gutterBottom>
              Constraints
            </Typography>
            <List dense>
              {Object.entries(recommendation.constraints).map(([key, value]) => (
                <ListItem key={key}>
                  <ListItemText
                    primary={key.charAt(0).toUpperCase() + key.slice(1)}
                    secondary={value}
                  />
                </ListItem>
              ))}
            </List>
          </>
        )}
        {recommendation.alternatives.length > 0 && (
          <>
            <Typography variant="subtitle2" gutterBottom>
              Alternatives
            </Typography>
            <List dense>
              {recommendation.alternatives.map((alternative, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={alternative.name}
                    secondary={
                      <Box>
                        <Typography variant="body2">
                          {alternative.description}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Benefits: {alternative.benefits.join(', ')}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </>
        )}
      </CardContent>
    </Card>
  );

  const MealPrepScheduleCard: React.FC<{ schedule: MealPrepSchedule }> = ({ schedule }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Meal Prep Schedule
        </Typography>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Week of {new Date(schedule.week.start).toLocaleDateString()} - {new Date(schedule.week.end).toLocaleDateString()}
        </Typography>
        <List>
          {schedule.prepSessions.map((session, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={`${session.day} at ${session.time}`}
                secondary={
                  <Box>
                    <Typography variant="body2">
                      Duration: {session.duration} minutes
                    </Typography>
                    <Typography variant="body2">
                      Efficiency: {session.efficiency}%
                    </Typography>
                    <List dense>
                      {session.meals.map((meal, mealIndex) => (
                        <ListItem key={mealIndex}>
                          <ListItemText
                            primary={meal.name}
                            secondary={
                              <Box>
                                <Typography variant="body2">
                                  Servings: {meal.servings}
                                </Typography>
                                <Typography variant="body2">
                                  Prep: {meal.prepTime} min | Cook: {meal.cookTime} min
                                </Typography>
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
        <Typography variant="subtitle2" gutterBottom>
          Batch Cooking
        </Typography>
        <List dense>
          {schedule.batchCooking.recipes.map((recipe, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={recipe.name}
                secondary={
                  <Box>
                    <Typography variant="body2">
                      Servings: {recipe.servings}
                    </Typography>
                    <Typography variant="body2">
                      Storage: {recipe.storage} | Shelf Life: {recipe.shelfLife}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );

  const NutritionalAnalyticsCard: React.FC<{ analytics: NutritionalAnalytics }> = ({ analytics }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Nutritional Analytics
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Meal Timing
            </Typography>
            <Box sx={{ pl: 2 }}>
              <Typography variant="body2">
                Consistency: {analytics.patterns.mealTiming.consistency}%
              </Typography>
              <Typography variant="body2">
                Optimal Timing: {analytics.patterns.mealTiming.optimalTiming}%
              </Typography>
              <List dense>
                {analytics.patterns.mealTiming.recommendations.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Cost Effectiveness
            </Typography>
            <Box sx={{ pl: 2 }}>
              <Typography variant="body2">
                Cost per Meal: ${analytics.patterns.costEffectiveness.costPerMeal.toFixed(2)}
              </Typography>
              <Typography variant="body2">
                Total Savings: ${analytics.patterns.costEffectiveness.savings.toFixed(2)}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Time Management
            </Typography>
            <Box sx={{ pl: 2 }}>
              <Typography variant="body2">
                Prep Efficiency: {analytics.patterns.timeManagement.prepEfficiency}%
              </Typography>
              <Typography variant="body2">
                Cook Efficiency: {analytics.patterns.timeManagement.cookEfficiency}%
              </Typography>
              <Typography variant="body2">
                Time Savings: {analytics.patterns.timeManagement.timeSavings} minutes
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Sustainability
            </Typography>
            <Box sx={{ pl: 2 }}>
              <Typography variant="body2">
                Carbon Footprint: {analytics.patterns.sustainability.carbonFootprint} kg CO2
              </Typography>
              <Typography variant="body2">
                Food Waste: {analytics.patterns.sustainability.foodWaste}%
              </Typography>
              <Typography variant="body2">
                Local Ingredients: {analytics.patterns.sustainability.localIngredients}%
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const SmartIntegrationCard: React.FC<{ integration: SmartIntegration }> = ({ integration }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Smart Integration
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Optimized Shopping
            </Typography>
            <List dense>
              {integration.shopping.optimizedList.map((item, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={item.item}
                    secondary={
                      <Box>
                        <Typography variant="body2">
                          {item.amount} {item.unit}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Best Price: ${item.bestPrice.toFixed(2)} at {item.stores.join(', ')}
                        </Typography>
                      </Box>
                    }
                  />
                  <Chip
                    label={item.priority}
                    size="small"
                    color={
                      item.priority === 'HIGH'
                        ? 'error'
                        : item.priority === 'MEDIUM'
                        ? 'warning'
                        : 'success'
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Optimal Timing
            </Typography>
            <Box sx={{ pl: 2 }}>
              <Typography variant="body2">
                Breakfast: {integration.timing.optimalMealTimes.breakfast}
              </Typography>
              <Typography variant="body2">
                Lunch: {integration.timing.optimalMealTimes.lunch}
              </Typography>
              <Typography variant="body2">
                Dinner: {integration.timing.optimalMealTimes.dinner}
              </Typography>
              <Typography variant="body2">
                Snacks: {integration.timing.optimalMealTimes.snacks.join(', ')}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Progress Prediction
            </Typography>
            <Box sx={{ pl: 2 }}>
              <Typography variant="body2">
                Short Term:
              </Typography>
              <Box sx={{ pl: 2 }}>
                <Typography variant="body2">
                  Calories: {integration.progressPrediction.shortTerm.calories}
                </Typography>
                <Typography variant="body2">
                  Weight: {integration.progressPrediction.shortTerm.weight} kg
                </Typography>
                <Typography variant="body2">
                  Performance: {integration.progressPrediction.shortTerm.performance}%
                </Typography>
              </Box>
              <Typography variant="body2">
                Long Term:
              </Typography>
              <Box sx={{ pl: 2 }}>
                <Typography variant="body2">
                  Calories: {integration.progressPrediction.longTerm.calories}
                </Typography>
                <Typography variant="body2">
                  Weight: {integration.progressPrediction.longTerm.weight} kg
                </Typography>
                <Typography variant="body2">
                  Performance: {integration.progressPrediction.longTerm.performance}%
                </Typography>
              </Box>
              <Typography variant="body2">
                Confidence: {integration.progressPrediction.confidence}%
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <Typography variant="h6">Nutrition Plans</Typography>
          <IconButton onClick={fetchPlans} color="primary">
            <RefreshIcon />
          </IconButton>
        </Box>
      </Grid>

      {error && (
        <Grid item xs={12}>
          <Alert severity="error">{error}</Alert>
        </Grid>
      )}

      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Current Plans
            </Typography>
            {loading ? (
              <CircularProgress />
            ) : (
              <List>
                {plans.map((plan) => (
                  <React.Fragment key={plan.id}>
                    <ListItem>
                      <ListItemText
                        primary={plan.name}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              {plan.description}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                              <Chip
                                label={plan.category}
                                size="small"
                                color="primary"
                                variant="outlined"
                              />
                              {plan.caloricTarget && (
                                <Chip
                                  label={`${plan.caloricTarget} cal`}
                                  size="small"
                                  variant="outlined"
                                />
                              )}
                              <Chip
                                label={plan.status}
                                size="small"
                                color={plan.status === 'ACTIVE' ? 'success' : 'default'}
                                variant="outlined"
                              />
                            </Box>
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          onClick={() => {
                            setSelectedPlanId(plan.id);
                            setLogDialogOpen(true);
                          }}
                          color="primary"
                        >
                          <MealIcon />
                        </IconButton>
                        <IconButton edge="end">
                          <EditIcon />
                        </IconButton>
                        <IconButton edge="end" color="error">
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Add New Plan
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={newPlanData.category}
                  label="Category"
                  onChange={(e) => setNewPlanData({ ...newPlanData, category: e.target.value })}
                >
                  {categories.map((category) => (
                    <MenuItem key={category.value} value={category.value}>
                      {category.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                label="Name"
                value={newPlanData.name}
                onChange={(e) => setNewPlanData({ ...newPlanData, name: e.target.value })}
                fullWidth
              />
              <TextField
                label="Description"
                value={newPlanData.description}
                onChange={(e) => setNewPlanData({ ...newPlanData, description: e.target.value })}
                multiline
                rows={3}
                fullWidth
              />
              <TextField
                label="Caloric Target"
                type="number"
                value={newPlanData.caloricTarget}
                onChange={(e) => setNewPlanData({ ...newPlanData, caloricTarget: e.target.value })}
                fullWidth
              />
              <TextField
                label="Hydration Target (L)"
                type="number"
                value={newPlanData.hydrationTarget}
                onChange={(e) => setNewPlanData({ ...newPlanData, hydrationTarget: e.target.value })}
                fullWidth
              />
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleAddPlan}
                disabled={loading || !newPlanData.name || !newPlanData.description}
              >
                Add Plan
              </Button>
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Logs
            </Typography>
            <List>
              {logs.slice(0, 5).map((log) => (
                <ListItem key={log.id}>
                  <ListItemText
                    primary={`${log.mealType} - ${new Date(log.timestamp).toLocaleDateString()}`}
                    secondary={
                      <Box>
                        {log.calories && (
                          <Typography variant="body2" color="textSecondary">
                            Calories: {log.calories}
                          </Typography>
                        )}
                        {log.foodsConsumed.length > 0 && (
                          <Typography variant="body2" color="textSecondary">
                            Foods: {log.foodsConsumed.map(f => f.name).join(', ')}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>

      <Dialog open={logDialogOpen} onClose={() => setLogDialogOpen(false)}>
        <DialogTitle>Add Nutrition Log</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Meal Type</InputLabel>
              <Select
                value={newLogData.mealType}
                label="Meal Type"
                onChange={(e) => setNewLogData({ ...newLogData, mealType: e.target.value })}
              >
                {mealTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Calories"
              type="number"
              value={newLogData.calories}
              onChange={(e) => setNewLogData({ ...newLogData, calories: e.target.value })}
              fullWidth
            />
            <TextField
              label="Protein (g)"
              type="number"
              value={newLogData.protein}
              onChange={(e) => setNewLogData({ ...newLogData, protein: e.target.value })}
              fullWidth
            />
            <TextField
              label="Carbohydrates (g)"
              type="number"
              value={newLogData.carbohydrates}
              onChange={(e) => setNewLogData({ ...newLogData, carbohydrates: e.target.value })}
              fullWidth
            />
            <TextField
              label="Fats (g)"
              type="number"
              value={newLogData.fats}
              onChange={(e) => setNewLogData({ ...newLogData, fats: e.target.value })}
              fullWidth
            />
            <TextField
              label="Hydration (L)"
              type="number"
              value={newLogData.hydration}
              onChange={(e) => setNewLogData({ ...newLogData, hydration: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLogDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAddLog} variant="contained" color="primary">
            Add Log
          </Button>
        </DialogActions>
      </Dialog>

      {selectedPlanId && mealPrepSchedule && (
        <Grid item xs={12}>
          <MealPrepScheduleCard schedule={mealPrepSchedule} />
        </Grid>
      )}

      {selectedPlanId && nutritionalAnalytics && (
        <Grid item xs={12}>
          <NutritionalAnalyticsCard analytics={nutritionalAnalytics} />
        </Grid>
      )}

      {selectedPlanId && smartIntegration && (
        <Grid item xs={12}>
          <SmartIntegrationCard integration={smartIntegration} />
        </Grid>
      )}
    </Grid>
  );
}; 