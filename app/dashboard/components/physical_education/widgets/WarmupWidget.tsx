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
  ListItemIcon,
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
  Chip,
  LinearProgress,
  Alert,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Replay as ReplayIcon,
  Timer as TimerIcon,
  FitnessCenter as ExerciseIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

interface Exercise {
  id: string;
  name: string;
  duration: number;
  description: string;
  category: 'warmup' | 'cooldown';
  muscleGroup: string;
}

interface Routine {
  id: string;
  name: string;
  type: 'warmup' | 'cooldown';
  exercises: Exercise[];
  totalDuration: number;
}

const DEFAULT_EXERCISES: Exercise[] = [
  {
    id: '1',
    name: 'Arm Circles',
    duration: 30,
    description: 'Stand with feet shoulder-width apart and rotate arms in circular motions',
    category: 'warmup',
    muscleGroup: 'Upper Body',
  },
  {
    id: '2',
    name: 'Leg Swings',
    duration: 30,
    description: 'Stand on one leg and swing the other leg forward and backward',
    category: 'warmup',
    muscleGroup: 'Lower Body',
  },
  {
    id: '3',
    name: 'Neck Stretch',
    duration: 20,
    description: 'Gently tilt head from side to side and forward and backward',
    category: 'warmup',
    muscleGroup: 'Neck',
  },
  {
    id: '4',
    name: 'Static Stretch',
    duration: 30,
    description: 'Hold each stretch for 30 seconds',
    category: 'cooldown',
    muscleGroup: 'Full Body',
  },
  {
    id: '5',
    name: 'Deep Breathing',
    duration: 60,
    description: 'Focus on deep, controlled breathing',
    category: 'cooldown',
    muscleGroup: 'Core',
  },
];

const DEFAULT_ROUTINES: Routine[] = [
  {
    id: '1',
    name: 'Quick Warm-up',
    type: 'warmup',
    exercises: DEFAULT_EXERCISES.filter(e => e.category === 'warmup'),
    totalDuration: 80,
  },
  {
    id: '2',
    name: 'Basic Cool-down',
    type: 'cooldown',
    exercises: DEFAULT_EXERCISES.filter(e => e.category === 'cooldown'),
    totalDuration: 90,
  },
];

export const WarmupWidget: React.FC = () => {
  const [routines, setRoutines] = useState<Routine[]>(DEFAULT_ROUTINES);
  const [selectedRoutine, setSelectedRoutine] = useState<Routine | null>(null);
  const [currentExercise, setCurrentExercise] = useState<Exercise | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [showRoutineDialog, setShowRoutineDialog] = useState(false);
  const [newRoutine, setNewRoutine] = useState<Partial<Routine>>({
    type: 'warmup',
    exercises: [],
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isRunning && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(prev => prev - 1);
      }, 1000);
    } else if (timeRemaining === 0 && currentExercise) {
      const currentIndex = selectedRoutine?.exercises.findIndex(e => e.id === currentExercise.id) || -1;
      if (currentIndex >= 0 && selectedRoutine && currentIndex < selectedRoutine.exercises.length - 1) {
        const nextExercise = selectedRoutine.exercises[currentIndex + 1];
        setCurrentExercise(nextExercise);
        setTimeRemaining(nextExercise.duration);
      } else {
        setIsRunning(false);
        setCurrentExercise(null);
      }
    }

    return () => clearInterval(interval);
  }, [isRunning, timeRemaining, currentExercise, selectedRoutine]);

  const startRoutine = (routine: Routine) => {
    setSelectedRoutine(routine);
    setCurrentExercise(routine.exercises[0]);
    setTimeRemaining(routine.exercises[0].duration);
    setIsRunning(true);
  };

  const pauseRoutine = () => {
    setIsRunning(false);
  };

  const resumeRoutine = () => {
    setIsRunning(true);
  };

  const resetRoutine = () => {
    if (selectedRoutine) {
      setCurrentExercise(selectedRoutine.exercises[0]);
      setTimeRemaining(selectedRoutine.exercises[0].duration);
      setIsRunning(false);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const addRoutine = (routine: Routine) => {
    setRoutines([...routines, routine]);
    setShowRoutineDialog(false);
    setNewRoutine({ type: 'warmup', exercises: [] });
  };

  const getProgress = (): number => {
    if (!selectedRoutine || !currentExercise) return 0;
    const currentIndex = selectedRoutine.exercises.findIndex(e => e.id === currentExercise.id);
    const totalExercises = selectedRoutine.exercises.length;
    return (currentIndex / totalExercises) * 100;
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Warm-up/Cool-down</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setShowRoutineDialog(true)}
            >
              New Routine
            </Button>
          </Box>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Current Exercise Display */}
          {currentExercise && (
            <Box textAlign="center" py={2}>
              <Typography variant="h4">{currentExercise.name}</Typography>
              <Typography variant="h2" color="primary">
                {formatTime(timeRemaining)}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {currentExercise.description}
              </Typography>
              <Box display="flex" justifyContent="center" gap={1} mt={2}>
                {isRunning ? (
                  <Button
                    variant="contained"
                    startIcon={<PauseIcon />}
                    onClick={pauseRoutine}
                  >
                    Pause
                  </Button>
                ) : (
                  <Button
                    variant="contained"
                    startIcon={<PlayIcon />}
                    onClick={resumeRoutine}
                  >
                    Resume
                  </Button>
                )}
                <Button
                  variant="outlined"
                  startIcon={<ReplayIcon />}
                  onClick={resetRoutine}
                >
                  Reset
                </Button>
              </Box>
              <LinearProgress
                variant="determinate"
                value={getProgress()}
                sx={{ mt: 2 }}
              />
            </Box>
          )}

          {/* Routines List */}
          <List>
            {routines.map(routine => (
              <ListItem
                key={routine.id}
                sx={{
                  mb: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1,
                }}
              >
                <ListItemIcon>
                  <ExerciseIcon />
                </ListItemIcon>
                <ListItemText
                  primary={routine.name}
                  secondary={
                    <Box>
                      <Typography variant="body2">
                        {routine.type === 'warmup' ? 'Warm-up' : 'Cool-down'} - {routine.exercises.length} exercises
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Total Duration: {formatTime(routine.totalDuration)}
                      </Typography>
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <Button
                    variant="contained"
                    onClick={() => startRoutine(routine)}
                    disabled={!!currentExercise}
                  >
                    Start
                  </Button>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Box>
      </CardContent>

      {/* New Routine Dialog */}
      <Dialog open={showRoutineDialog} onClose={() => setShowRoutineDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Routine</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Routine Name"
              fullWidth
              onChange={(e) => setNewRoutine({ ...newRoutine, name: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Routine Type</InputLabel>
              <Select
                label="Routine Type"
                value={newRoutine.type}
                onChange={(e) => setNewRoutine({ ...newRoutine, type: e.target.value as Routine['type'] })}
              >
                <MenuItem value="warmup">Warm-up</MenuItem>
                <MenuItem value="cooldown">Cool-down</MenuItem>
              </Select>
            </FormControl>
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Select Exercises
              </Typography>
              <List>
                {DEFAULT_EXERCISES
                  .filter(e => e.category === newRoutine.type)
                  .map(exercise => (
                    <ListItem key={exercise.id}>
                      <ListItemText
                        primary={exercise.name}
                        secondary={`${exercise.duration}s - ${exercise.muscleGroup}`}
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          onClick={() => {
                            const exercises = newRoutine.exercises || [];
                            if (exercises.some(e => e.id === exercise.id)) {
                              setNewRoutine({
                                ...newRoutine,
                                exercises: exercises.filter(e => e.id !== exercise.id),
                              });
                            } else {
                              setNewRoutine({
                                ...newRoutine,
                                exercises: [...exercises, exercise],
                              });
                            }
                          }}
                        >
                          <Chip
                            label={newRoutine.exercises?.some(e => e.id === exercise.id) ? 'Selected' : 'Select'}
                            color={newRoutine.exercises?.some(e => e.id === exercise.id) ? 'primary' : 'default'}
                          />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
              </List>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowRoutineDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (newRoutine.name && newRoutine.exercises && newRoutine.exercises.length > 0) {
                addRoutine({
                  ...newRoutine as Routine,
                  id: Date.now().toString(),
                  totalDuration: newRoutine.exercises.reduce((sum, e) => sum + e.duration, 0),
                });
              } else {
                setError('Please provide a name and select at least one exercise');
              }
            }}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}; 