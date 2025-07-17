import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Grid,
  Paper,
  TextField,
  CircularProgress,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Stack,
} from '@mui/material';
import {
  Restaurant as MealIcon,
  Opacity as WaterIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Today as DateIcon,
  Assessment as AssessmentIcon,
  Timeline as TrendIcon,
  CalendarToday as PlanIcon,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';

interface Meal {
  id: string;
  date: string;
  type: MealType;
  name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  notes?: string;
}

interface WaterIntake {
  id: string;
  date: string;
  amount: number; // in ml
  timestamp: string;
}

interface NutritionGoals {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  water: number;
}

interface MealPlan {
  id: string;
  date: string;
  meals: PlannedMeal[];
}

interface PlannedMeal {
  id: string;
  type: MealType;
  name: string;
  calories: number;
  notes?: string;
}

type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack';

const MEAL_TYPES: MealType[] = ['breakfast', 'lunch', 'dinner', 'snack'];

const DEFAULT_GOALS: NutritionGoals = {
  calories: 2000,
  protein: 150,
  carbs: 250,
  fat: 70,
  water: 2500,
};

const MOCK_MEALS: Meal[] = [
  {
    id: '1',
    date: new Date().toISOString().split('T')[0],
    type: 'breakfast',
    name: 'Oatmeal with Fruit',
    calories: 350,
    protein: 12,
    carbs: 60,
    fat: 8,
  },
];

export const NutritionTrackerWidget: React.FC = () => {
  const [meals, setMeals] = useState<Meal[]>(MOCK_MEALS);
  const [waterIntake, setWaterIntake] = useState<WaterIntake[]>([]);
  const [goals, setGoals] = useState<NutritionGoals>(DEFAULT_GOALS);
  const [mealPlans, setMealPlans] = useState<MealPlan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showMealDialog, setShowMealDialog] = useState(false);
  const [showWaterDialog, setShowWaterDialog] = useState(false);
  const [showGoalsDialog, setShowGoalsDialog] = useState(false);
  const [showPlanDialog, setShowPlanDialog] = useState(false);
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [newMeal, setNewMeal] = useState<Partial<Meal>>({
    date: selectedDate,
    type: 'breakfast',
  });
  const [newWaterIntake, setNewWaterIntake] = useState<Partial<WaterIntake>>({
    date: selectedDate,
    amount: 250,
  });
  const [newGoals, setNewGoals] = useState<NutritionGoals>(goals);

  const getDailyTotals = () => {
    const todayMeals = meals.filter(meal => meal.date === selectedDate);
    return {
      calories: todayMeals.reduce((sum, meal) => sum + meal.calories, 0),
      protein: todayMeals.reduce((sum, meal) => sum + meal.protein, 0),
      carbs: todayMeals.reduce((sum, meal) => sum + meal.carbs, 0),
      fat: todayMeals.reduce((sum, meal) => sum + meal.fat, 0),
      water: waterIntake
        .filter(intake => intake.date === selectedDate)
        .reduce((sum, intake) => sum + intake.amount, 0),
    };
  };

  const getNutrientDistribution = () => {
    const totals = getDailyTotals();
    return [
      { name: 'Protein', value: totals.protein * 4, color: '#2196F3' },
      { name: 'Carbs', value: totals.carbs * 4, color: '#4CAF50' },
      { name: 'Fat', value: totals.fat * 9, color: '#FFC107' },
    ];
  };

  const addMeal = (meal: Meal) => {
    setMeals(prev => [...prev, meal]);
    setShowMealDialog(false);
    setNewMeal({
      date: selectedDate,
      type: 'breakfast',
    });
  };

  const addWaterIntake = (intake: WaterIntake) => {
    setWaterIntake(prev => [...prev, intake]);
    setShowWaterDialog(false);
    setNewWaterIntake({
      date: selectedDate,
      amount: 250,
    });
  };

  const updateGoals = (goals: NutritionGoals) => {
    setGoals(goals);
    setShowGoalsDialog(false);
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Nutrition Tracker</Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowMealDialog(true)}
              >
                Add Meal
              </Button>
              <Button
                variant="outlined"
                startIcon={<WaterIcon />}
                onClick={() => setShowWaterDialog(true)}
              >
                Add Water
              </Button>
            </Box>
          </Box>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Date Selection */}
          <TextField
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            fullWidth
            InputLabelProps={{ shrink: true }}
          />

          {/* Daily Summary */}
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Daily Summary
                </Typography>
                {loading ? (
                  <Box display="flex" justifyContent="center" p={2}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Calories
                      </Typography>
                      <Box display="flex" alignItems="center" gap={1}>
                        <LinearProgress
                          variant="determinate"
                          value={(getDailyTotals().calories / goals.calories) * 100}
                          sx={{ flexGrow: 1 }}
                        />
                        <Typography variant="body2">
                          {getDailyTotals().calories} / {goals.calories}
                        </Typography>
                      </Box>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Water Intake
                      </Typography>
                      <Box display="flex" alignItems="center" gap={1}>
                        <LinearProgress
                          variant="determinate"
                          value={(getDailyTotals().water / goals.water) * 100}
                          sx={{ flexGrow: 1 }}
                        />
                        <Typography variant="body2">
                          {(getDailyTotals().water / 1000).toFixed(1)}L / {(goals.water / 1000).toFixed(1)}L
                        </Typography>
                      </Box>
                    </Box>
                    <Grid container spacing={2}>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="text.secondary">
                          Protein
                        </Typography>
                        <Typography>
                          {getDailyTotals().protein}g / {goals.protein}g
                        </Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="text.secondary">
                          Carbs
                        </Typography>
                        <Typography>
                          {getDailyTotals().carbs}g / {goals.carbs}g
                        </Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="text.secondary">
                          Fat
                        </Typography>
                        <Typography>
                          {getDailyTotals().fat}g / {goals.fat}g
                        </Typography>
                      </Grid>
                    </Grid>
                  </Stack>
                )}
              </Paper>
            </Grid>

            {/* Nutrient Distribution */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Calorie Distribution
                </Typography>
                <Box height={200}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={getNutrientDistribution()}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                      >
                        {getNutrientDistribution().map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              </Paper>
            </Grid>
          </Grid>

          {/* Meals List */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Today's Meals
            </Typography>
            <List>
              {meals
                .filter(meal => meal.date === selectedDate)
                .map((meal, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <MealIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={meal.name}
                      secondary={
                        <>
                          <Typography variant="body2" component="span">
                            {meal.type.charAt(0).toUpperCase() + meal.type.slice(1)}
                          </Typography>
                          <br />
                          <Typography variant="caption" color="text.secondary">
                            {meal.calories} kcal | P: {meal.protein}g | C: {meal.carbs}g | F: {meal.fat}g
                          </Typography>
                        </>
                      }
                    />
                    <Chip
                      label={`${meal.calories} kcal`}
                      color="primary"
                      size="small"
                    />
                  </ListItem>
                ))}
            </List>
          </Paper>

          {/* Water Intake */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Water Intake
            </Typography>
            <List>
              {waterIntake
                .filter(intake => intake.date === selectedDate)
                .map((intake, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <WaterIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={`${intake.amount}ml`}
                      secondary={new Date(intake.timestamp).toLocaleTimeString()}
                    />
                  </ListItem>
                ))}
            </List>
          </Paper>
        </Box>
      </CardContent>

      {/* Add Meal Dialog */}
      <Dialog open={showMealDialog} onClose={() => setShowMealDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Meal</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <FormControl fullWidth>
              <InputLabel>Meal Type</InputLabel>
              <Select
                value={newMeal.type}
                label="Meal Type"
                onChange={(e) => setNewMeal({ ...newMeal, type: e.target.value as MealType })}
              >
                {MEAL_TYPES.map(type => (
                  <MenuItem key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Meal Name"
              fullWidth
              onChange={(e) => setNewMeal({ ...newMeal, name: e.target.value })}
            />
            <TextField
              label="Calories"
              type="number"
              fullWidth
              onChange={(e) => setNewMeal({ ...newMeal, calories: parseInt(e.target.value) })}
            />
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <TextField
                  label="Protein (g)"
                  type="number"
                  fullWidth
                  onChange={(e) => setNewMeal({ ...newMeal, protein: parseInt(e.target.value) })}
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="Carbs (g)"
                  type="number"
                  fullWidth
                  onChange={(e) => setNewMeal({ ...newMeal, carbs: parseInt(e.target.value) })}
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="Fat (g)"
                  type="number"
                  fullWidth
                  onChange={(e) => setNewMeal({ ...newMeal, fat: parseInt(e.target.value) })}
                />
              </Grid>
            </Grid>
            <TextField
              label="Notes"
              multiline
              rows={2}
              fullWidth
              onChange={(e) => setNewMeal({ ...newMeal, notes: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowMealDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (
                newMeal.name &&
                newMeal.type &&
                newMeal.calories &&
                newMeal.protein &&
                newMeal.carbs &&
                newMeal.fat
              ) {
                addMeal({
                  ...newMeal as Meal,
                  id: Date.now().toString(),
                  date: selectedDate,
                });
              } else {
                setError('Please fill in all required fields');
              }
            }}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Water Dialog */}
      <Dialog open={showWaterDialog} onClose={() => setShowWaterDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Water Intake</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Amount (ml)"
              type="number"
              fullWidth
              defaultValue={250}
              onChange={(e) =>
                setNewWaterIntake({
                  ...newWaterIntake,
                  amount: parseInt(e.target.value),
                  timestamp: new Date().toISOString(),
                })
              }
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowWaterDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (newWaterIntake.amount) {
                addWaterIntake({
                  ...newWaterIntake as WaterIntake,
                  id: Date.now().toString(),
                  date: selectedDate,
                  timestamp: new Date().toISOString(),
                });
              } else {
                setError('Please enter the amount');
              }
            }}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Goals Dialog */}
      <Dialog open={showGoalsDialog} onClose={() => setShowGoalsDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Update Nutrition Goals</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Daily Calories"
              type="number"
              fullWidth
              value={newGoals.calories}
              onChange={(e) =>
                setNewGoals({ ...newGoals, calories: parseInt(e.target.value) })
              }
            />
            <TextField
              label="Protein Goal (g)"
              type="number"
              fullWidth
              value={newGoals.protein}
              onChange={(e) =>
                setNewGoals({ ...newGoals, protein: parseInt(e.target.value) })
              }
            />
            <TextField
              label="Carbs Goal (g)"
              type="number"
              fullWidth
              value={newGoals.carbs}
              onChange={(e) =>
                setNewGoals({ ...newGoals, carbs: parseInt(e.target.value) })
              }
            />
            <TextField
              label="Fat Goal (g)"
              type="number"
              fullWidth
              value={newGoals.fat}
              onChange={(e) =>
                setNewGoals({ ...newGoals, fat: parseInt(e.target.value) })
              }
            />
            <TextField
              label="Water Goal (ml)"
              type="number"
              fullWidth
              value={newGoals.water}
              onChange={(e) =>
                setNewGoals({ ...newGoals, water: parseInt(e.target.value) })
              }
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowGoalsDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (
                newGoals.calories &&
                newGoals.protein &&
                newGoals.carbs &&
                newGoals.fat &&
                newGoals.water
              ) {
                updateGoals(newGoals);
              } else {
                setError('Please fill in all goals');
              }
            }}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}; 