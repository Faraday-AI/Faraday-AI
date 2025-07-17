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
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  FitnessCenter as ExerciseIcon,
  Timer as TimerIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  SkipNext as NextIcon,
  Restore as ResetIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Favorite as FavoriteIcon,
} from '@mui/icons-material';

interface Exercise {
  id: string;
  name: string;
  type: ExerciseType;
  duration: number; // in seconds
  description: string;
  targetMuscles: string[];
  intensity: 'low' | 'medium' | 'high';
  notes?: string;
}

interface Routine {
  id: string;
  name: string;
  type: 'warmup' | 'cooldown';
  exercises: Exercise[];
  totalDuration: number;
  favorite: boolean;
}

interface ProgressRecord {
  id: string;
  date: string;
  routineId: string;
  completed: boolean;
  duration: number;
  notes?: string;
}

type ExerciseType = 'stretch' | 'mobility' | 'activation' | 'relaxation';

const EXERCISE_TYPES: ExerciseType[] = ['stretch', 'mobility', 'activation', 'relaxation'];

const DEFAULT_EXERCISES: Exercise[] = [
  {
    id: '1',
    name: 'Arm Circles',
    type: 'mobility',
    duration: 30,
    description: 'Make circular motions with arms',
    targetMuscles: ['shoulders', 'arms'],
    intensity: 'low',
  },
  {
    id: '2',
    name: 'Leg Swings',
    type: 'mobility',
    duration: 45,
    description: 'Swing legs forward and back',
    targetMuscles: ['hips', 'legs'],
    intensity: 'medium',
  },
];

const DEFAULT_ROUTINES: Routine[] = [
  {
    id: '1',
    name: 'Basic Warm-up',
    type: 'warmup',
    exercises: DEFAULT_EXERCISES,
    totalDuration: DEFAULT_EXERCISES.reduce((sum, ex) => sum + ex.duration, 0),
    favorite: false,
  },
];

export const WarmupCooldownWidget: React.FC = () => {
  const [routines, setRoutines] = useState<Routine[]>(DEFAULT_ROUTINES);
  const [exercises, setExercises] = useState<Exercise[]>(DEFAULT_EXERCISES);
  const [progress, setProgress] = useState<ProgressRecord[]>([]);
  const [activeRoutine, setActiveRoutine] = useState<Routine | null>(null);
  const [activeExercise, setActiveExercise] = useState<Exercise | null>(null);
  const [timer, setTimer] = useState<number>(0);
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showRoutineDialog, setShowRoutineDialog] = useState(false);
  const [showExerciseDialog, setShowExerciseDialog] = useState(false);
  const [newRoutine, setNewRoutine] = useState<Partial<Routine>>({
    type: 'warmup',
    exercises: [],
    favorite: false,
  });
  const [newExercise, setNewExercise] = useState<Partial<Exercise>>({
    type: 'stretch',
    duration: 30,
    intensity: 'low',
    targetMuscles: [],
  });

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning && activeExercise) {
      interval = setInterval(() => {
        setTimer(prev => {
          if (prev >= activeExercise.duration) {
            handleExerciseComplete();
            return 0;
          }
          return prev + 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRunning, activeExercise]);

  const handleExerciseComplete = () => {
    if (!activeRoutine || !activeExercise) return;

    const currentIndex = activeRoutine.exercises.findIndex(ex => ex.id === activeExercise.id);
    if (currentIndex < activeRoutine.exercises.length - 1) {
      setActiveExercise(activeRoutine.exercises[currentIndex + 1]);
    } else {
      handleRoutineComplete();
    }
  };

  const handleRoutineComplete = () => {
    if (!activeRoutine) return;

    setProgress(prev => [
      ...prev,
      {
        id: Date.now().toString(),
        date: new Date().toISOString(),
        routineId: activeRoutine.id,
        completed: true,
        duration: activeRoutine.totalDuration,
      },
    ]);
    setIsRunning(false);
    setActiveExercise(null);
    setTimer(0);
  };

  const startRoutine = (routine: Routine) => {
    setActiveRoutine(routine);
    setActiveExercise(routine.exercises[0]);
    setTimer(0);
    setIsRunning(true);
  };

  const toggleTimer = () => {
    setIsRunning(!isRunning);
  };

  const resetTimer = () => {
    setTimer(0);
    setIsRunning(false);
  };

  const skipExercise = () => {
    handleExerciseComplete();
  };

  const addRoutine = (routine: Routine) => {
    setRoutines(prev => [...prev, routine]);
    setShowRoutineDialog(false);
    setNewRoutine({
      type: 'warmup',
      exercises: [],
      favorite: false,
    });
  };

  const addExercise = (exercise: Exercise) => {
    setExercises(prev => [...prev, exercise]);
    if (showRoutineDialog && newRoutine.exercises) {
      setNewRoutine({
        ...newRoutine,
        exercises: [...newRoutine.exercises, exercise],
        totalDuration: (newRoutine.exercises?.reduce((sum, ex) => sum + ex.duration, 0) || 0) + exercise.duration,
      });
    }
    setShowExerciseDialog(false);
    setNewExercise({
      type: 'stretch',
      duration: 30,
      intensity: 'low',
      targetMuscles: [],
    });
  };

  const toggleFavorite = (routineId: string) => {
    setRoutines(prev =>
      prev.map(routine =>
        routine.id === routineId
          ? { ...routine, favorite: !routine.favorite }
          : routine
      )
    );
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Warm-up & Cool-down</Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowRoutineDialog(true)}
              >
                Add Routine
              </Button>
            </Box>
          </Box>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Active Exercise */}
          {activeExercise && (
            <Paper sx={{ p: 2, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
              <Box display="flex" flexDirection="column" gap={2}>
                <Typography variant="h5" align="center">
                  {activeExercise.name}
                </Typography>
                <Typography variant="body1" align="center">
                  {activeExercise.description}
                </Typography>
                <Box display="flex" justifyContent="center" alignItems="center" gap={2}>
                  <Typography variant="h3">
                    {Math.floor(timer / 60)}:{(timer % 60).toString().padStart(2, '0')}
                  </Typography>
                  <Typography variant="body2">
                    / {Math.floor(activeExercise.duration / 60)}:{(activeExercise.duration % 60).toString().padStart(2, '0')}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={(timer / activeExercise.duration) * 100}
                />
                <Box display="flex" justifyContent="center" gap={2}>
                  <IconButton onClick={toggleTimer} color="inherit">
                    {isRunning ? <PauseIcon /> : <PlayIcon />}
                  </IconButton>
                  <IconButton onClick={resetTimer} color="inherit">
                    <ResetIcon />
                  </IconButton>
                  <IconButton onClick={skipExercise} color="inherit">
                    <NextIcon />
                  </IconButton>
                </Box>
              </Box>
            </Paper>
          )}

          {/* Routines List */}
          <Grid container spacing={2}>
            {/* Warm-up Routines */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Warm-up Routines
                </Typography>
                <List>
                  {routines
                    .filter(routine => routine.type === 'warmup')
                    .map(routine => (
                      <ListItem
                        key={routine.id}
                        secondaryAction={
                          <Box display="flex" gap={1}>
                            <IconButton
                              onClick={() => toggleFavorite(routine.id)}
                              color={routine.favorite ? 'primary' : 'default'}
                            >
                              <FavoriteIcon />
                            </IconButton>
                            <Button
                              variant="contained"
                              size="small"
                              onClick={() => startRoutine(routine)}
                              disabled={!!activeRoutine}
                            >
                              Start
                            </Button>
                          </Box>
                        }
                      >
                        <ListItemIcon>
                          <ExerciseIcon />
                        </ListItemIcon>
                        <ListItemText
                          primary={routine.name}
                          secondary={
                            <>
                              <Typography variant="body2" component="span">
                                {routine.exercises.length} exercises
                              </Typography>
                              <br />
                              <Typography variant="caption" color="text.secondary">
                                {Math.floor(routine.totalDuration / 60)} minutes
                              </Typography>
                            </>
                          }
                        />
                      </ListItem>
                    ))}
                </List>
              </Paper>
            </Grid>

            {/* Cool-down Routines */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Cool-down Routines
                </Typography>
                <List>
                  {routines
                    .filter(routine => routine.type === 'cooldown')
                    .map(routine => (
                      <ListItem
                        key={routine.id}
                        secondaryAction={
                          <Box display="flex" gap={1}>
                            <IconButton
                              onClick={() => toggleFavorite(routine.id)}
                              color={routine.favorite ? 'primary' : 'default'}
                            >
                              <FavoriteIcon />
                            </IconButton>
                            <Button
                              variant="contained"
                              size="small"
                              onClick={() => startRoutine(routine)}
                              disabled={!!activeRoutine}
                            >
                              Start
                            </Button>
                          </Box>
                        }
                      >
                        <ListItemIcon>
                          <ExerciseIcon />
                        </ListItemIcon>
                        <ListItemText
                          primary={routine.name}
                          secondary={
                            <>
                              <Typography variant="body2" component="span">
                                {routine.exercises.length} exercises
                              </Typography>
                              <br />
                              <Typography variant="caption" color="text.secondary">
                                {Math.floor(routine.totalDuration / 60)} minutes
                              </Typography>
                            </>
                          }
                        />
                      </ListItem>
                    ))}
                </List>
              </Paper>
            </Grid>
          </Grid>

          {/* Recent Progress */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Recent Progress
            </Typography>
            <List>
              {progress.slice(-5).map((record, index) => {
                const routine = routines.find(r => r.id === record.routineId);
                return (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <TimerIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={routine?.name || 'Unknown Routine'}
                      secondary={
                        <>
                          <Typography variant="body2" component="span">
                            {new Date(record.date).toLocaleDateString()}
                          </Typography>
                          <br />
                          <Typography variant="caption" color="text.secondary">
                            Duration: {Math.floor(record.duration / 60)} minutes
                          </Typography>
                        </>
                      }
                    />
                    <Chip
                      label={record.completed ? 'Completed' : 'Incomplete'}
                      color={record.completed ? 'success' : 'error'}
                      size="small"
                    />
                  </ListItem>
                ))}
            </List>
          </Paper>
        </Box>
      </CardContent>

      {/* Add Routine Dialog */}
      <Dialog open={showRoutineDialog} onClose={() => setShowRoutineDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Routine</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Routine Name"
              fullWidth
              onChange={(e) => setNewRoutine({ ...newRoutine, name: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Type</InputLabel>
              <Select
                value={newRoutine.type}
                label="Type"
                onChange={(e) =>
                  setNewRoutine({ ...newRoutine, type: e.target.value as Routine['type'] })
                }
              >
                <MenuItem value="warmup">Warm-up</MenuItem>
                <MenuItem value="cooldown">Cool-down</MenuItem>
              </Select>
            </FormControl>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="subtitle1">Exercises</Typography>
              <Button
                size="small"
                startIcon={<AddIcon />}
                onClick={() => setShowExerciseDialog(true)}
              >
                Add Exercise
              </Button>
            </Box>
            <List>
              {newRoutine.exercises?.map((exercise, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={exercise.name}
                    secondary={`${exercise.duration} seconds - ${exercise.type}`}
                  />
                </ListItem>
              ))}
            </List>
            <FormControlLabel
              control={
                <Switch
                  checked={newRoutine.favorite}
                  onChange={(e) =>
                    setNewRoutine({ ...newRoutine, favorite: e.target.checked })
                  }
                />
              }
              label="Add to Favorites"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowRoutineDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (newRoutine.name && newRoutine.type && newRoutine.exercises?.length) {
                addRoutine({
                  ...newRoutine as Routine,
                  id: Date.now().toString(),
                  totalDuration: newRoutine.exercises.reduce((sum, ex) => sum + ex.duration, 0),
                });
              } else {
                setError('Please fill in all required fields and add at least one exercise');
              }
            }}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Exercise Dialog */}
      <Dialog open={showExerciseDialog} onClose={() => setShowExerciseDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Exercise</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Exercise Name"
              fullWidth
              onChange={(e) => setNewExercise({ ...newExercise, name: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Type</InputLabel>
              <Select
                value={newExercise.type}
                label="Type"
                onChange={(e) =>
                  setNewExercise({ ...newExercise, type: e.target.value as ExerciseType })
                }
              >
                {EXERCISE_TYPES.map(type => (
                  <MenuItem key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Duration (seconds)"
              type="number"
              fullWidth
              defaultValue={30}
              onChange={(e) =>
                setNewExercise({ ...newExercise, duration: parseInt(e.target.value) })
              }
            />
            <TextField
              label="Description"
              multiline
              rows={2}
              fullWidth
              onChange={(e) =>
                setNewExercise({ ...newExercise, description: e.target.value })
              }
            />
            <TextField
              label="Target Muscles (comma-separated)"
              fullWidth
              onChange={(e) =>
                setNewExercise({
                  ...newExercise,
                  targetMuscles: e.target.value.split(',').map(m => m.trim()),
                })
              }
            />
            <FormControl fullWidth>
              <InputLabel>Intensity</InputLabel>
              <Select
                value={newExercise.intensity}
                label="Intensity"
                onChange={(e) =>
                  setNewExercise({
                    ...newExercise,
                    intensity: e.target.value as Exercise['intensity'],
                  })
                }
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Notes"
              multiline
              rows={2}
              fullWidth
              onChange={(e) => setNewExercise({ ...newExercise, notes: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowExerciseDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (
                newExercise.name &&
                newExercise.type &&
                newExercise.duration &&
                newExercise.description &&
                newExercise.targetMuscles?.length &&
                newExercise.intensity
              ) {
                addExercise({
                  ...newExercise as Exercise,
                  id: Date.now().toString(),
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
    </Card>
  );
}; 