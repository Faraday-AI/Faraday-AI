import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Chip,
  LinearProgress,
  Tooltip,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  FitnessCenter as FitnessIcon,
  Timer as TimerIcon,
  TrendingUp as ProgressIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer } from 'recharts';

interface Exercise {
  id: string;
  name: string;
  category: string;
  muscleGroup: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  description: string;
  videoUrl?: string;
}

interface ExerciseSet {
  id: string;
  exerciseId: string;
  date: string;
  weight: number;
  reps: number;
  notes: string;
}

const EXERCISE_CATEGORIES = ['Strength', 'Cardio', 'Flexibility', 'Balance', 'Coordination'];
const MUSCLE_GROUPS = ['Upper Body', 'Lower Body', 'Core', 'Full Body', 'Cardio'];
const DEFAULT_EXERCISES: Exercise[] = [
  {
    id: '1',
    name: 'Push-ups',
    category: 'Strength',
    muscleGroup: 'Upper Body',
    difficulty: 'Beginner',
    description: 'A classic bodyweight exercise that targets the chest, shoulders, and triceps.',
  },
  {
    id: '2',
    name: 'Squats',
    category: 'Strength',
    muscleGroup: 'Lower Body',
    difficulty: 'Beginner',
    description: 'A fundamental lower body exercise that works the quadriceps, hamstrings, and glutes.',
  },
  {
    id: '3',
    name: 'Plank',
    category: 'Strength',
    muscleGroup: 'Core',
    difficulty: 'Beginner',
    description: 'An isometric exercise that strengthens the core muscles.',
  },
];

export const ExerciseTrackerWidget: React.FC = () => {
  const [exercises, setExercises] = useState<Exercise[]>(DEFAULT_EXERCISES);
  const [exerciseSets, setExerciseSets] = useState<ExerciseSet[]>([]);
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);
  const [showExerciseDialog, setShowExerciseDialog] = useState(false);
  const [showSetDialog, setShowSetDialog] = useState(false);
  const [newSet, setNewSet] = useState<Partial<ExerciseSet>>({
    weight: 0,
    reps: 0,
    notes: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');

  const addExercise = (exercise: Exercise) => {
    setExercises([...exercises, exercise]);
    setShowExerciseDialog(false);
  };

  const addSet = (set: ExerciseSet) => {
    if (!selectedExercise) return;
    
    const newExerciseSet: ExerciseSet = {
      ...set,
      id: Date.now().toString(),
      exerciseId: selectedExercise.id,
      date: new Date().toISOString(),
    };
    
    setExerciseSets([...exerciseSets, newExerciseSet]);
    setShowSetDialog(false);
    setNewSet({ weight: 0, reps: 0, notes: '' });
  };

  const removeExercise = (exerciseId: string) => {
    setExercises(exercises.filter(e => e.id !== exerciseId));
    setExerciseSets(exerciseSets.filter(s => s.exerciseId !== exerciseId));
  };

  const getProgressData = (exerciseId: string) => {
    const filteredSets = exerciseSets.filter((s: ExerciseSet) => s.exerciseId === exerciseId);
    return filteredSets.map((set: ExerciseSet) => ({
      date: new Date(set.date).toLocaleDateString(),
      weight: set.weight,
      reps: set.reps,
    }));
  };

  const calculateProgress = (exerciseId: string) => {
    const sets = exerciseSets.filter(s => s.exerciseId === exerciseId);
    if (sets.length < 2) return 0;
    
    const firstSet = sets[0];
    const lastSet = sets[sets.length - 1];
    const weightProgress = ((lastSet.weight - firstSet.weight) / firstSet.weight) * 100;
    const repsProgress = ((lastSet.reps - firstSet.reps) / firstSet.reps) * 100;
    
    return (weightProgress + repsProgress) / 2;
  };

  const filteredExercises = filter === 'all' 
    ? exercises 
    : exercises.filter(e => e.category === filter || e.muscleGroup === filter);

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Exercise Tracker</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setShowExerciseDialog(true)}
            >
              Add Exercise
            </Button>
          </Box>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Filter Controls */}
          <Box display="flex" gap={1} flexWrap="wrap">
            <Chip
              label="All"
              color={filter === 'all' ? 'primary' : 'default'}
              onClick={() => setFilter('all')}
            />
            {EXERCISE_CATEGORIES.map(category => (
              <Chip
                key={category}
                label={category}
                color={filter === category ? 'primary' : 'default'}
                onClick={() => setFilter(category)}
              />
            ))}
            {MUSCLE_GROUPS.map(group => (
              <Chip
                key={group}
                label={group}
                color={filter === group ? 'primary' : 'default'}
                onClick={() => setFilter(group)}
              />
            ))}
          </Box>

          {/* Exercise List */}
          <List>
            {filteredExercises.map(exercise => (
              <React.Fragment key={exercise.id}>
                <ListItem
                  button
                  onClick={() => setSelectedExercise(exercise)}
                  sx={{ mb: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}
                >
                  <ListItemText
                    primary={exercise.name}
                    secondary={
                      <Box component="span">
                        <Chip size="small" label={exercise.category} sx={{ mr: 1 }} />
                        <Chip size="small" label={exercise.muscleGroup} sx={{ mr: 1 }} />
                        <Chip size="small" label={exercise.difficulty} color="secondary" />
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Tooltip title="Add Set">
                      <IconButton
                        edge="end"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedExercise(exercise);
                          setShowSetDialog(true);
                        }}
                      >
                        <AddIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete Exercise">
                      <IconButton
                        edge="end"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeExercise(exercise.id);
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </ListItemSecondaryAction>
                </ListItem>

                {/* Progress Section */}
                {selectedExercise?.id === exercise.id && (
                  <Box p={2}>
                    <Typography variant="subtitle2" gutterBottom>
                      Progress
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={calculateProgress(exercise.id)}
                      sx={{ mb: 2 }}
                    />
                    <Box height={200}>
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={getProgressData(exercise.id)}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <ChartTooltip />
                          <Line type="monotone" dataKey="weight" stroke="#8884d8" />
                          <Line type="monotone" dataKey="reps" stroke="#82ca9d" />
                        </LineChart>
                      </ResponsiveContainer>
                    </Box>
                  </Box>
                )}
              </React.Fragment>
            ))}
          </List>
        </Box>
      </CardContent>

      {/* Add Exercise Dialog */}
      <Dialog open={showExerciseDialog} onClose={() => setShowExerciseDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Exercise</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Exercise Name"
              fullWidth
              onChange={(e) => setSelectedExercise({
                ...selectedExercise!,
                name: e.target.value,
                id: Date.now().toString(),
              } as Exercise)}
            />
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                label="Category"
                onChange={(e) => setSelectedExercise({
                  ...selectedExercise!,
                  category: e.target.value,
                } as Exercise)}
              >
                {EXERCISE_CATEGORIES.map(category => (
                  <MenuItem key={category} value={category}>{category}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Muscle Group</InputLabel>
              <Select
                label="Muscle Group"
                onChange={(e) => setSelectedExercise({
                  ...selectedExercise!,
                  muscleGroup: e.target.value,
                } as Exercise)}
              >
                {MUSCLE_GROUPS.map(group => (
                  <MenuItem key={group} value={group}>{group}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Difficulty</InputLabel>
              <Select
                label="Difficulty"
                onChange={(e) => setSelectedExercise({
                  ...selectedExercise!,
                  difficulty: e.target.value as Exercise['difficulty'],
                } as Exercise)}
              >
                <MenuItem value="Beginner">Beginner</MenuItem>
                <MenuItem value="Intermediate">Intermediate</MenuItem>
                <MenuItem value="Advanced">Advanced</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Description"
              multiline
              rows={4}
              fullWidth
              onChange={(e) => setSelectedExercise({
                ...selectedExercise!,
                description: e.target.value,
              } as Exercise)}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowExerciseDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => addExercise(selectedExercise as Exercise)}
            disabled={!selectedExercise?.name}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Set Dialog */}
      <Dialog open={showSetDialog} onClose={() => setShowSetDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Exercise Set</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Weight (kg)"
              type="number"
              fullWidth
              onChange={(e) => setNewSet({ ...newSet, weight: parseFloat(e.target.value) })}
            />
            <TextField
              label="Repetitions"
              type="number"
              fullWidth
              onChange={(e) => setNewSet({ ...newSet, reps: parseInt(e.target.value) })}
            />
            <TextField
              label="Notes"
              multiline
              rows={2}
              fullWidth
              onChange={(e) => setNewSet({ ...newSet, notes: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSetDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => addSet(newSet as ExerciseSet)}
            disabled={!newSet.weight || !newSet.reps}
          >
            Add Set
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}; 