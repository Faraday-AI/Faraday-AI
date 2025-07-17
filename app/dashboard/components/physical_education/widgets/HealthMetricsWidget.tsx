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
  Slider,
  LinearProgress,
} from '@mui/material';
import {
  FitnessCenter as FitnessIcon,
  MonitorHeart as HeartIcon,
  Speed as SpeedIcon,
  Timeline as TrendIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Delete as DeleteIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer } from 'recharts';

interface HealthMetrics {
  id: string;
  date: string;
  weight: number;
  height: number;
  bmi: number;
  heartRate: number;
  bloodPressure: {
    systolic: number;
    diastolic: number;
  };
  bodyFat?: number;
  muscleMass?: number;
}

interface FitnessAssessment {
  id: string;
  date: string;
  type: FitnessTestType;
  score: number;
  level: FitnessLevel;
  notes?: string;
}

interface FitnessGoal {
  id: string;
  metric: string;
  target: number;
  current: number;
  deadline: string;
  status: 'in-progress' | 'completed' | 'overdue';
}

type FitnessTestType = 'cardio' | 'strength' | 'flexibility' | 'endurance';
type FitnessLevel = 'beginner' | 'intermediate' | 'advanced' | 'elite';

const MOCK_HEALTH_METRICS: HealthMetrics = {
  id: '1',
  date: new Date().toISOString(),
  weight: 70,
  height: 175,
  bmi: 22.9,
  heartRate: 72,
  bloodPressure: {
    systolic: 120,
    diastolic: 80,
  },
};

const FITNESS_TEST_TYPES: FitnessTestType[] = ['cardio', 'strength', 'flexibility', 'endurance'];
const FITNESS_LEVELS: FitnessLevel[] = ['beginner', 'intermediate', 'advanced', 'elite'];

const BMI_CATEGORIES = [
  { range: [0, 18.5], label: 'Underweight', color: 'warning' },
  { range: [18.5, 24.9], label: 'Normal', color: 'success' },
  { range: [25, 29.9], label: 'Overweight', color: 'warning' },
  { range: [30, Infinity], label: 'Obese', color: 'error' },
];

export const HealthMetricsWidget: React.FC = () => {
  const [metrics, setMetrics] = useState<HealthMetrics[]>([MOCK_HEALTH_METRICS]);
  const [assessments, setAssessments] = useState<FitnessAssessment[]>([]);
  const [goals, setGoals] = useState<FitnessGoal[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showMetricsDialog, setShowMetricsDialog] = useState(false);
  const [showAssessmentDialog, setShowAssessmentDialog] = useState(false);
  const [showGoalDialog, setShowGoalDialog] = useState(false);
  const [newMetrics, setNewMetrics] = useState<Partial<HealthMetrics>>({
    date: new Date().toISOString().split('T')[0],
  });
  const [newAssessment, setNewAssessment] = useState<Partial<FitnessAssessment>>({
    date: new Date().toISOString().split('T')[0],
    type: 'cardio',
  });
  const [newGoal, setNewGoal] = useState<Partial<FitnessGoal>>({
    status: 'in-progress',
  });

  const calculateBMI = (weight: number, height: number): number => {
    const heightInMeters = height / 100;
    return Number((weight / (heightInMeters * heightInMeters)).toFixed(1));
  };

  const getBMICategory = (bmi: number) => {
    return BMI_CATEGORIES.find(category => bmi >= category.range[0] && bmi < category.range[1]) || BMI_CATEGORIES[0];
  };

  const addHealthMetrics = (metrics: HealthMetrics) => {
    setMetrics(prev => [...prev, metrics]);
    setShowMetricsDialog(false);
    setNewMetrics({
      date: new Date().toISOString().split('T')[0],
    });
  };

  const addFitnessAssessment = (assessment: FitnessAssessment) => {
    setAssessments(prev => [...prev, assessment]);
    setShowAssessmentDialog(false);
    setNewAssessment({
      date: new Date().toISOString().split('T')[0],
      type: 'cardio',
    });
  };

  const addFitnessGoal = (goal: FitnessGoal) => {
    setGoals(prev => [...prev, goal]);
    setShowGoalDialog(false);
    setNewGoal({
      status: 'in-progress',
    });
  };

  const getMetricsProgress = () => {
    return metrics.map(m => ({
      date: m.date,
      bmi: m.bmi,
      weight: m.weight,
      heartRate: m.heartRate,
    }));
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Health Metrics</Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowMetricsDialog(true)}
              >
                Add Metrics
              </Button>
              <Button
                variant="outlined"
                startIcon={<AssessmentIcon />}
                onClick={() => setShowAssessmentDialog(true)}
              >
                Add Assessment
              </Button>
            </Box>
          </Box>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Current Metrics */}
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Latest Measurements
                </Typography>
                {loading ? (
                  <Box display="flex" justifyContent="center" p={2}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box display="flex" flexDirection="column" gap={1}>
                        <Typography variant="body2" color="text.secondary">
                          BMI
                        </Typography>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="h6">
                            {metrics[metrics.length - 1].bmi}
                          </Typography>
                          <Chip
                            label={getBMICategory(metrics[metrics.length - 1].bmi).label}
                            color={getBMICategory(metrics[metrics.length - 1].bmi).color as any}
                            size="small"
                          />
                        </Box>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box display="flex" flexDirection="column" gap={1}>
                        <Typography variant="body2" color="text.secondary">
                          Weight
                        </Typography>
                        <Typography variant="h6">
                          {metrics[metrics.length - 1].weight} kg
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box display="flex" flexDirection="column" gap={1}>
                        <Typography variant="body2" color="text.secondary">
                          Heart Rate
                        </Typography>
                        <Typography variant="h6">
                          {metrics[metrics.length - 1].heartRate} bpm
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box display="flex" flexDirection="column" gap={1}>
                        <Typography variant="body2" color="text.secondary">
                          Blood Pressure
                        </Typography>
                        <Typography variant="h6">
                          {metrics[metrics.length - 1].bloodPressure.systolic}/
                          {metrics[metrics.length - 1].bloodPressure.diastolic}
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                )}
              </Paper>
            </Grid>

            {/* Metrics Trend */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Metrics Trend
                </Typography>
                <Box height={200}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={getMetricsProgress()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="date"
                        tickFormatter={(value) => new Date(value).toLocaleDateString()}
                      />
                      <YAxis domain={['auto', 'auto']} />
                      <ChartTooltip />
                      <Line
                        type="monotone"
                        dataKey="bmi"
                        stroke="#2196F3"
                        name="BMI"
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey="weight"
                        stroke="#4CAF50"
                        name="Weight"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </Paper>
            </Grid>
          </Grid>

          {/* Fitness Assessments */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Recent Assessments
            </Typography>
            <List>
              {assessments.slice(-3).map((assessment, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <FitnessIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={`${assessment.type.charAt(0).toUpperCase() + assessment.type.slice(1)} Assessment`}
                    secondary={
                      <>
                        <Typography variant="body2" component="span">
                          Level: {assessment.level} | Score: {assessment.score}
                        </Typography>
                        <br />
                        <Typography variant="caption" color="text.secondary">
                          {new Date(assessment.date).toLocaleDateString()}
                        </Typography>
                      </>
                    }
                  />
                  <Chip
                    label={assessment.level}
                    color={
                      assessment.level === 'elite'
                        ? 'success'
                        : assessment.level === 'advanced'
                        ? 'primary'
                        : assessment.level === 'intermediate'
                        ? 'warning'
                        : 'default'
                    }
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </Paper>

          {/* Fitness Goals */}
          <Paper sx={{ p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="subtitle1">
                Fitness Goals
              </Typography>
              <Button
                size="small"
                startIcon={<AddIcon />}
                onClick={() => setShowGoalDialog(true)}
              >
                Add Goal
              </Button>
            </Box>
            <List>
              {goals.map((goal, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={goal.metric}
                    secondary={
                      <>
                        <LinearProgress
                          variant="determinate"
                          value={(goal.current / goal.target) * 100}
                          sx={{ my: 1 }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          {goal.current} / {goal.target} | Due: {new Date(goal.deadline).toLocaleDateString()}
                        </Typography>
                      </>
                    }
                  />
                  <Chip
                    label={goal.status}
                    color={
                      goal.status === 'completed'
                        ? 'success'
                        : goal.status === 'overdue'
                        ? 'error'
                        : 'primary'
                    }
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Box>
      </CardContent>

      {/* Add Metrics Dialog */}
      <Dialog open={showMetricsDialog} onClose={() => setShowMetricsDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Health Metrics</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Weight (kg)"
              type="number"
              fullWidth
              onChange={(e) => {
                const weight = parseFloat(e.target.value);
                const height = newMetrics.height || 0;
                setNewMetrics({
                  ...newMetrics,
                  weight,
                  bmi: calculateBMI(weight, height),
                });
              }}
            />
            <TextField
              label="Height (cm)"
              type="number"
              fullWidth
              onChange={(e) => {
                const height = parseFloat(e.target.value);
                const weight = newMetrics.weight || 0;
                setNewMetrics({
                  ...newMetrics,
                  height,
                  bmi: calculateBMI(weight, height),
                });
              }}
            />
            <TextField
              label="Heart Rate (bpm)"
              type="number"
              fullWidth
              onChange={(e) =>
                setNewMetrics({ ...newMetrics, heartRate: parseInt(e.target.value) })
              }
            />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  label="Systolic"
                  type="number"
                  fullWidth
                  onChange={(e) =>
                    setNewMetrics({
                      ...newMetrics,
                      bloodPressure: {
                        ...newMetrics.bloodPressure,
                        systolic: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Diastolic"
                  type="number"
                  fullWidth
                  onChange={(e) =>
                    setNewMetrics({
                      ...newMetrics,
                      bloodPressure: {
                        ...newMetrics.bloodPressure,
                        diastolic: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </Grid>
            </Grid>
            <TextField
              label="Body Fat %"
              type="number"
              fullWidth
              onChange={(e) =>
                setNewMetrics({ ...newMetrics, bodyFat: parseFloat(e.target.value) })
              }
            />
            <TextField
              label="Muscle Mass %"
              type="number"
              fullWidth
              onChange={(e) =>
                setNewMetrics({ ...newMetrics, muscleMass: parseFloat(e.target.value) })
              }
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowMetricsDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (
                newMetrics.weight &&
                newMetrics.height &&
                newMetrics.heartRate &&
                newMetrics.bloodPressure?.systolic &&
                newMetrics.bloodPressure?.diastolic
              ) {
                addHealthMetrics({
                  ...newMetrics as HealthMetrics,
                  id: Date.now().toString(),
                });
              } else {
                setError('Please fill in all required fields');
              }
            }}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Assessment Dialog */}
      <Dialog open={showAssessmentDialog} onClose={() => setShowAssessmentDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Fitness Assessment</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <FormControl fullWidth>
              <InputLabel>Test Type</InputLabel>
              <Select
                value={newAssessment.type}
                label="Test Type"
                onChange={(e) =>
                  setNewAssessment({ ...newAssessment, type: e.target.value as FitnessTestType })
                }
              >
                {FITNESS_TEST_TYPES.map(type => (
                  <MenuItem key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Score"
              type="number"
              fullWidth
              onChange={(e) =>
                setNewAssessment({ ...newAssessment, score: parseInt(e.target.value) })
              }
            />
            <FormControl fullWidth>
              <InputLabel>Level</InputLabel>
              <Select
                value={newAssessment.level}
                label="Level"
                onChange={(e) =>
                  setNewAssessment({ ...newAssessment, level: e.target.value as FitnessLevel })
                }
              >
                {FITNESS_LEVELS.map(level => (
                  <MenuItem key={level} value={level}>
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Notes"
              multiline
              rows={3}
              fullWidth
              onChange={(e) =>
                setNewAssessment({ ...newAssessment, notes: e.target.value })
              }
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAssessmentDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (newAssessment.type && newAssessment.score && newAssessment.level) {
                addFitnessAssessment({
                  ...newAssessment as FitnessAssessment,
                  id: Date.now().toString(),
                });
              } else {
                setError('Please fill in all required fields');
              }
            }}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Goal Dialog */}
      <Dialog open={showGoalDialog} onClose={() => setShowGoalDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Fitness Goal</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Metric"
              fullWidth
              onChange={(e) => setNewGoal({ ...newGoal, metric: e.target.value })}
            />
            <TextField
              label="Target"
              type="number"
              fullWidth
              onChange={(e) => setNewGoal({ ...newGoal, target: parseFloat(e.target.value) })}
            />
            <TextField
              label="Current"
              type="number"
              fullWidth
              onChange={(e) => setNewGoal({ ...newGoal, current: parseFloat(e.target.value) })}
            />
            <TextField
              label="Deadline"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              onChange={(e) => setNewGoal({ ...newGoal, deadline: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowGoalDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (newGoal.metric && newGoal.target && newGoal.current && newGoal.deadline) {
                addFitnessGoal({
                  ...newGoal as FitnessGoal,
                  id: Date.now().toString(),
                });
              } else {
                setError('Please fill in all required fields');
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