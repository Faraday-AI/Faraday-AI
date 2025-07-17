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
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  FitnessCenter as ExerciseIcon,
  Timer as TimerIcon,
  TrendingUp as ProgressIcon,
} from '@mui/icons-material';

interface Exercise {
  id: number;
  name: string;
  description: string;
  category: string;
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
  equipment: string[];
  formTips: string[];
  safetyPrecautions: string[];
  targetMuscles: string[];
  variations: string[];
}

interface WorkoutPlan {
  id: number;
  name: string;
  description: string;
  startDate: string;
  endDate: string;
  frequency: number;
  goals: {
    goalId: number;
    goalName: string;
    targetMetrics: Record<string, number>;
    currentProgress: Record<string, number>;
  }[];
  exercises: Exercise[];
  schedule: {
    day: string;
    exercises: {
      exerciseId: number;
      sets: number;
      reps: number;
      restTime: number;
      notes: string;
    }[];
  }[];
  adaptationsNeeded?: {
    reason: string;
    suggestedChanges: string[];
    priority: 'LOW' | 'MEDIUM' | 'HIGH';
  }[];
  status: string;
}

interface WorkoutSession {
  id: number;
  planId: number;
  startTime: string;
  endTime?: string;
  completed: boolean;
  performanceData: {
    exerciseId: number;
    sets: {
      setNumber: number;
      reps: number;
      weight: number;
      formRating: number;
      notes: string;
    }[];
    totalVolume: number;
    averageFormRating: number;
  }[];
  difficultyRating?: number;
  enjoymentRating?: number;
  notes?: string;
  modificationsUsed?: {
    exerciseId: number;
    modification: string;
    reason: string;
  }[];
}

interface ExercisePerformance {
  exerciseId: number;
  formScore: number;
  powerOutput: number;
  enduranceScore: number;
  techniqueNotes: string[];
  safetyAlerts: string[];
}

interface WorkoutAnalytics {
  totalVolume: number;
  intensityScore: number;
  recoveryStatus: 'READY' | 'NEEDS_REST' | 'OVERLOADED';
  progressTrend: number;
  performanceBenchmarks: {
    strength: number;
    endurance: number;
    flexibility: number;
  };
}

interface SafetyCheck {
  equipmentStatus: 'READY' | 'NEEDS_CHECK' | 'REQUIRES_MAINTENANCE';
  formSafetyScore: number;
  environmentSafety: string[];
  emergencyProcedures: string[];
  safetyAlerts: string[];
}

interface ExerciseAdaptation {
  exerciseId: number;
  currentDifficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
  suggestedDifficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
  variations: string[];
  formImprovements: string[];
  adaptationReason: string;
}

interface ProgressGoal {
  id: number;
  title: string;
  description?: string;
  targetDate: string;
  achievedDate?: string;
  status: string;
  priority: string;
  difficultyLevel: string;
}

interface WorkoutOptimization {
  optimalRestPeriods: Record<number, number>;
  exerciseSequence: number[];
  recoveryTime: number;
  intensityDistribution: {
    warmup: number;
    main: number;
    cooldown: number;
  };
}

interface MuscleGroupRecovery {
  muscleGroup: string;
  lastWorked: string;
  recoveryStatus: 'RECOVERED' | 'RECOVERING' | 'FATIGUED';
  recommendedRest: number;
  nextWorkoutDate: string;
}

interface PerformanceTrend {
  metric: 'STRENGTH' | 'ENDURANCE' | 'FLEXIBILITY' | 'VOLUME';
  currentValue: number;
  trend: 'INCREASING' | 'DECREASING' | 'STABLE';
  rateOfChange: number;
  prediction: {
    nextWeek: number;
    nextMonth: number;
  };
}

interface WorkoutPreferences {
  preferredTime: string;
  availableEquipment: string[];
  maxDuration: number;
  intensityPreference: 'LOW' | 'MEDIUM' | 'HIGH';
  focusAreas: string[];
}

export const WorkoutPlanPanel: React.FC = () => {
  const [plans, setPlans] = useState<WorkoutPlan[]>([]);
  const [sessions, setSessions] = useState<WorkoutSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeSession, setActiveSession] = useState<number | null>(null);
  const [newPlanData, setNewPlanData] = useState({
    name: '',
    description: '',
    frequency: 3,
    goals: {},
    schedule: {},
  });
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [activeExercise, setActiveExercise] = useState<number | null>(null);
  const [restTimer, setRestTimer] = useState<number | null>(null);
  const [formFeedback, setFormFeedback] = useState<Record<number, string>>({});
  const [exercisePerformance, setExercisePerformance] = useState<ExercisePerformance[]>([]);
  const [workoutAnalytics, setWorkoutAnalytics] = useState<WorkoutAnalytics | null>(null);
  const [safetyChecks, setSafetyChecks] = useState<SafetyCheck | null>(null);
  const [exerciseAdaptations, setExerciseAdaptations] = useState<ExerciseAdaptation[]>([]);
  const [progressGoals, setProgressGoals] = useState<ProgressGoal[]>([]);
  const [workoutOptimization, setWorkoutOptimization] = useState<WorkoutOptimization | null>(null);
  const [muscleRecovery, setMuscleRecovery] = useState<MuscleGroupRecovery[]>([]);
  const [performanceTrends, setPerformanceTrends] = useState<PerformanceTrend[]>([]);
  const [workoutPreferences, setWorkoutPreferences] = useState<WorkoutPreferences | null>(null);

  useEffect(() => {
    fetchPlans();
    fetchSessions();
    fetchExercises();
    const interval = setInterval(() => {
      if (restTimer && restTimer > 0) {
        setRestTimer(restTimer - 1);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchPlans = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        '/api/v1/physical-education/health-fitness/students/1/workout-plans'
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

  const fetchSessions = async () => {
    try {
      const response = await fetch(
        '/api/v1/physical-education/health-fitness/students/1/workout-sessions'
      );
      if (!response.ok) throw new Error('Failed to fetch sessions');
      const data = await response.json();
      setSessions(data);
    } catch (err) {
      console.error('Error fetching sessions:', err);
    }
  };

  const fetchExercises = async () => {
    try {
      const response = await fetch('/api/v1/physical-education/exercises');
      if (!response.ok) throw new Error('Failed to fetch exercises');
      const data = await response.json();
      setExercises(data);
    } catch (err) {
      console.error('Error fetching exercises:', err);
    }
  };

  const handleAddPlan = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        '/api/v1/physical-education/health-fitness/students/1/workout-plans',
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
        name: '',
        description: '',
        frequency: 3,
        goals: {},
        schedule: {},
      });
      fetchPlans();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleStartSession = async (planId: number) => {
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/workout-plans/${planId}/sessions`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            start_time: new Date().toISOString(),
          }),
        }
      );
      if (!response.ok) throw new Error('Failed to start session');
      const data = await response.json();
      setActiveSession(data.id);
      fetchSessions();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleEndSession = async (sessionId: number) => {
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/workout-sessions/${sessionId}`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            end_time: new Date().toISOString(),
            completed: true,
          }),
        }
      );
      if (!response.ok) throw new Error('Failed to end session');
      setActiveSession(null);
      fetchSessions();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleStartExercise = (exerciseId: number) => {
    setActiveExercise(exerciseId);
    const exercise = exercises.find(e => e.id === exerciseId);
    if (exercise) {
      setFormFeedback({
        ...formFeedback,
        [exerciseId]: 'Starting exercise...'
      });
    }
  };

  const handleEndExercise = (exerciseId: number, performanceData: any) => {
    setActiveExercise(null);
    // Update session performance data
    const updatedSessions = sessions.map(session => {
      if (session.id === activeSession) {
        return {
          ...session,
          performanceData: [
            ...(session.performanceData || []),
            {
              exerciseId,
              ...performanceData
            }
          ]
        };
      }
      return session;
    });
    setSessions(updatedSessions);
  };

  const analyzeExerciseForm = async (exerciseId: number, videoData: Blob) => {
    try {
      const formData = new FormData();
      formData.append('video', videoData);
      formData.append('exerciseId', exerciseId.toString());

      const response = await fetch('/api/v1/physical-education/exercises/form-analysis', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Failed to analyze form');
      const data = await response.json();
      
      setExercisePerformance(prev => [
        ...prev.filter(p => p.exerciseId !== exerciseId),
        data
      ]);
    } catch (err) {
      console.error('Error analyzing form:', err);
    }
  };

  const calculateWorkoutAnalytics = (session: WorkoutSession) => {
    const totalVolume = session.performanceData.reduce((sum, data) => 
      sum + data.sets.reduce((setSum, set) => setSum + (set.weight * set.reps), 0), 0);

    const intensityScore = session.performanceData.reduce((sum, data) => 
      sum + data.averageFormRating, 0) / session.performanceData.length;

    const recoveryStatus = calculateRecoveryStatus(session);
    const progressTrend = calculateProgressTrend(session);
    const benchmarks = calculatePerformanceBenchmarks(session);

    setWorkoutAnalytics({
      totalVolume,
      intensityScore,
      recoveryStatus,
      progressTrend,
      performanceBenchmarks: benchmarks
    });
  };

  const performSafetyChecks = async (planId: number) => {
    try {
      const response = await fetch(`/api/v1/physical-education/safety/checks/${planId}`);
      if (!response.ok) throw new Error('Failed to perform safety checks');
      const data = await response.json();
      setSafetyChecks(data);
    } catch (err) {
      console.error('Error performing safety checks:', err);
    }
  };

  const calculateRecoveryStatus = (session: WorkoutSession): 'READY' | 'NEEDS_REST' | 'OVERLOADED' => {
    const totalVolume = session.performanceData.reduce((sum, data) => 
      sum + data.sets.reduce((setSum, set) => setSum + (set.weight * set.reps), 0), 0);
    
    const intensityScore = session.performanceData.reduce((sum, data) => 
      sum + data.averageFormRating, 0) / session.performanceData.length;

    if (totalVolume > 1000 && intensityScore > 8) return 'OVERLOADED';
    if (totalVolume > 500 && intensityScore > 6) return 'NEEDS_REST';
    return 'READY';
  };

  const calculateProgressTrend = (session: WorkoutSession): number => {
    const previousSessions = sessions
      .filter(s => s.planId === session.planId && s.id < session.id)
      .sort((a, b) => b.id - a.id)
      .slice(0, 3);

    if (previousSessions.length === 0) return 0;

    const currentVolume = session.performanceData.reduce((sum, data) => 
      sum + data.sets.reduce((setSum, set) => setSum + (set.weight * set.reps), 0), 0);

    const previousVolume = previousSessions.reduce((sum, s) => 
      sum + s.performanceData.reduce((dataSum, data) => 
        dataSum + data.sets.reduce((setSum, set) => setSum + (set.weight * set.reps), 0), 0), 0) / previousSessions.length;

    return ((currentVolume - previousVolume) / previousVolume) * 100;
  };

  const calculatePerformanceBenchmarks = (session: WorkoutSession) => {
    const strength = session.performanceData.reduce((sum, data) => 
      sum + data.sets.reduce((setSum, set) => setSum + set.weight, 0), 0) / session.performanceData.length;

    const endurance = session.performanceData.reduce((sum, data) => 
      sum + data.sets.reduce((setSum, set) => setSum + set.reps, 0), 0) / session.performanceData.length;

    const flexibility = session.performanceData.reduce((sum, data) => 
      sum + data.averageFormRating, 0) / session.performanceData.length;

    return {
      strength: Math.round(strength),
      endurance: Math.round(endurance),
      flexibility: Math.round(flexibility * 10)
    };
  };

  const calculateExerciseAdaptation = (exerciseId: number, performance: ExercisePerformance): ExerciseAdaptation => {
    const exercise = exercises.find(e => e.id === exerciseId);
    if (!exercise) throw new Error('Exercise not found');

    let suggestedDifficulty = exercise.difficulty;
    const formImprovements: string[] = [];
    const variations: string[] = [];

    if (performance.formScore < 7) {
      suggestedDifficulty = 'BEGINNER';
      formImprovements.push('Focus on proper form before increasing difficulty');
    } else if (performance.formScore > 9 && performance.powerOutput > 100) {
      suggestedDifficulty = 'ADVANCED';
      variations.push(...exercise.variations);
    }

    return {
      exerciseId,
      currentDifficulty: exercise.difficulty,
      suggestedDifficulty,
      variations,
      formImprovements,
      adaptationReason: performance.formScore < 7 ? 'Form improvement needed' : 'Ready for progression'
    };
  };

  const updateProgressGoals = (session: WorkoutSession) => {
    const newGoals: ProgressGoal[] = [];
    
    // Volume milestone
    const totalVolume = session.performanceData.reduce((sum, data) => 
      sum + data.sets.reduce((setSum, set) => setSum + (set.weight * set.reps), 0), 0);
    
    newGoals.push({
      id: 1,
      title: 'Volume',
      description: `Reach ${totalVolume} kg of total volume`,
      targetDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      achievedDate: session.completed ? new Date().toISOString() : undefined,
      status: session.completed ? 'Achieved' : 'In Progress',
      priority: 'HIGH',
      difficultyLevel: 'ADVANCED'
    });

    // Strength milestone
    const maxWeight = Math.max(...session.performanceData.flatMap(data => 
      data.sets.map(set => set.weight)));
    
    newGoals.push({
      id: 2,
      title: 'Max Weight',
      description: `Lift ${maxWeight} kg`,
      targetDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      achievedDate: session.completed ? new Date().toISOString() : undefined,
      status: session.completed ? 'Achieved' : 'In Progress',
      priority: 'HIGH',
      difficultyLevel: 'ADVANCED'
    });

    // Endurance milestone
    const totalReps = session.performanceData.reduce((sum, data) => 
      sum + data.sets.reduce((setSum, set) => setSum + set.reps, 0), 0);
    
    newGoals.push({
      id: 3,
      title: 'Total Reps',
      description: `Complete ${totalReps} reps`,
      targetDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      achievedDate: session.completed ? new Date().toISOString() : undefined,
      status: session.completed ? 'Achieved' : 'In Progress',
      priority: 'HIGH',
      difficultyLevel: 'ADVANCED'
    });

    setProgressGoals(newGoals);
  };

  const optimizeWorkout = (plan: WorkoutPlan): WorkoutOptimization => {
    const optimalRestPeriods: Record<number, number> = {};
    const exerciseSequence: number[] = [];
    
    // Calculate optimal rest periods based on exercise intensity
    plan.exercises.forEach(exercise => {
      const intensity = exercise.difficulty === 'BEGINNER' ? 30 :
                       exercise.difficulty === 'INTERMEDIATE' ? 60 : 90;
      optimalRestPeriods[exercise.id] = intensity;
    });

    // Optimize exercise sequence
    const sortedExercises = [...plan.exercises].sort((a, b) => {
      const aIntensity = a.difficulty === 'BEGINNER' ? 1 :
                        a.difficulty === 'INTERMEDIATE' ? 2 : 3;
      const bIntensity = b.difficulty === 'BEGINNER' ? 1 :
                        b.difficulty === 'INTERMEDIATE' ? 2 : 3;
      return aIntensity - bIntensity;
    });

    exerciseSequence.push(...sortedExercises.map(e => e.id));

    // Calculate recovery time
    const totalIntensity = sortedExercises.reduce((sum, e) => 
      sum + (e.difficulty === 'BEGINNER' ? 30 :
             e.difficulty === 'INTERMEDIATE' ? 60 : 90), 0);
    
    const recoveryTime = Math.ceil(totalIntensity / 10) * 24; // Hours

    return {
      optimalRestPeriods,
      exerciseSequence,
      recoveryTime,
      intensityDistribution: {
        warmup: 20,
        main: 60,
        cooldown: 20
      }
    };
  };

  const calculateMuscleRecovery = (session: WorkoutSession): MuscleGroupRecovery[] => {
    const muscleGroups = new Set<string>();
    session.performanceData.forEach(data => {
      const exercise = exercises.find(e => e.id === data.exerciseId);
      if (exercise) {
        exercise.targetMuscles.forEach(muscle => muscleGroups.add(muscle));
      }
    });

    return Array.from(muscleGroups).map(muscleGroup => {
      const lastWorkout = new Date(session.startTime);
      const hoursSinceWorkout = (new Date().getTime() - lastWorkout.getTime()) / (1000 * 60 * 60);
      
      let recoveryStatus: 'RECOVERED' | 'RECOVERING' | 'FATIGUED';
      let recommendedRest: number;
      
      if (hoursSinceWorkout < 24) {
        recoveryStatus = 'FATIGUED';
        recommendedRest = 48 - hoursSinceWorkout;
      } else if (hoursSinceWorkout < 48) {
        recoveryStatus = 'RECOVERING';
        recommendedRest = 48 - hoursSinceWorkout;
      } else {
        recoveryStatus = 'RECOVERED';
        recommendedRest = 0;
      }

      const nextWorkoutDate = new Date(lastWorkout.getTime() + recommendedRest * 60 * 60 * 1000);

      return {
        muscleGroup,
        lastWorked: lastWorkout.toISOString(),
        recoveryStatus,
        recommendedRest,
        nextWorkoutDate: nextWorkoutDate.toISOString()
      };
    });
  };

  const analyzePerformanceTrends = (sessions: WorkoutSession[]): PerformanceTrend[] => {
    const metrics: PerformanceTrend[] = [];

    // Strength trend
    const strengthValues = sessions.map(session => 
      Math.max(...session.performanceData.flatMap(data => 
        data.sets.map(set => set.weight))));
    
    metrics.push(calculateTrend('STRENGTH', strengthValues));

    // Endurance trend
    const enduranceValues = sessions.map(session => 
      session.performanceData.reduce((sum, data) => 
        sum + data.sets.reduce((setSum, set) => setSum + set.reps, 0), 0));
    
    metrics.push(calculateTrend('ENDURANCE', enduranceValues));

    // Volume trend
    const volumeValues = sessions.map(session => 
      session.performanceData.reduce((sum, data) => 
        sum + data.sets.reduce((setSum, set) => setSum + (set.weight * set.reps), 0), 0));
    
    metrics.push(calculateTrend('VOLUME', volumeValues));

    return metrics;
  };

  const calculateTrend = (metric: 'STRENGTH' | 'ENDURANCE' | 'FLEXIBILITY' | 'VOLUME', values: number[]): PerformanceTrend => {
    if (values.length < 2) {
      return {
        metric,
        currentValue: values[0] || 0,
        trend: 'STABLE',
        rateOfChange: 0,
        prediction: {
          nextWeek: values[0] || 0,
          nextMonth: values[0] || 0
        }
      };
    }

    const currentValue = values[values.length - 1];
    const previousValue = values[values.length - 2];
    const rateOfChange = ((currentValue - previousValue) / previousValue) * 100;

    const trend = rateOfChange > 5 ? 'INCREASING' : rateOfChange < -5 ? 'DECREASING' : 'STABLE';

    const prediction = {
      nextWeek: currentValue * (1 + rateOfChange / 100),
      nextMonth: currentValue * Math.pow(1 + rateOfChange / 100, 4)
    };

    return {
      metric,
      currentValue,
      trend,
      rateOfChange,
      prediction
    };
  };

  const personalizeWorkout = (plan: WorkoutPlan, preferences: WorkoutPreferences): WorkoutPlan => {
    const personalizedPlan = { ...plan };

    // Adjust duration based on preferences
    if (preferences.maxDuration) {
      const totalDuration = plan.exercises.reduce((sum, exercise) => 
        sum + (exercise.difficulty === 'BEGINNER' ? 30 :
               exercise.difficulty === 'INTERMEDIATE' ? 45 : 60), 0);
      
      if (totalDuration > preferences.maxDuration) {
        personalizedPlan.exercises = plan.exercises
          .filter(exercise => exercise.difficulty !== 'ADVANCED')
          .slice(0, Math.floor(preferences.maxDuration / 30));
      }
    }

    // Filter exercises based on available equipment
    if (preferences.availableEquipment.length > 0) {
      personalizedPlan.exercises = plan.exercises.filter(exercise =>
        exercise.equipment.every(equip => preferences.availableEquipment.includes(equip))
      );
    }

    // Adjust intensity based on preference
    if (preferences.intensityPreference === 'LOW') {
      personalizedPlan.exercises = plan.exercises
        .filter(exercise => exercise.difficulty === 'BEGINNER');
    } else if (preferences.intensityPreference === 'HIGH') {
      personalizedPlan.exercises = plan.exercises
        .filter(exercise => exercise.difficulty === 'ADVANCED');
    }

    return personalizedPlan;
  };

  const ExerciseFormFeedback: React.FC<{ exerciseId: number }> = ({ exerciseId }) => {
    const exercise = exercises.find(e => e.id === exerciseId);
    if (!exercise) return null;

    return (
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="subtitle1" gutterBottom>
            Form Feedback: {exercise.name}
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              {formFeedback[exerciseId] || 'No feedback available'}
            </Typography>
          </Box>
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Form Tips:
            </Typography>
            <List dense>
              {exercise.formTips.map((tip, index) => (
                <ListItem key={index}>
                  <ListItemText primary={tip} />
                </ListItem>
              ))}
            </List>
          </Box>
        </CardContent>
      </Card>
    );
  };

  const RestTimer = ({ seconds }: { seconds: number }): JSX.Element => {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <TimerIcon color="primary" />
        <Typography variant="h6">
          {Math.floor(seconds / 60)}:{(seconds % 60).toString().padStart(2, '0')}
        </Typography>
      </Box>
    );
  };

  const ProgressTracker: React.FC<{ plan: WorkoutPlan }> = ({ plan }) => {
    return (
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <ProgressIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Goal Progress</Typography>
          </Box>
          {plan.goals.map((goal, index) => (
            <Box key={index} sx={{ mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                {goal.goalName}
              </Typography>
              {Object.entries(goal.targetMetrics).map(([metric, target]) => (
                <Box key={metric} sx={{ mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    {metric}: {goal.currentProgress[metric] || 0} / {target}
                  </Typography>
                  <Box sx={{ width: '100%', height: 8, bgcolor: 'grey.200', borderRadius: 4 }}>
                    <Box
                      sx={{
                        width: `${((goal.currentProgress[metric] || 0) / target) * 100}%`,
                        height: '100%',
                        bgcolor: 'primary.main',
                        borderRadius: 4
                      }}
                    />
                  </Box>
                </Box>
              ))}
            </Box>
          ))}
        </CardContent>
      </Card>
    );
  };

  const ExercisePerformanceCard: React.FC<{ performance: ExercisePerformance }> = ({ performance }) => {
    const exercise = exercises.find(e => e.id === performance.exerciseId);
    if (!exercise) return null;

    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {exercise.name} Performance
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={4}>
              <Typography variant="body2" color="text.secondary">
                Form Score
              </Typography>
              <Typography variant="h6">
                {performance.formScore.toFixed(1)}/10
              </Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="body2" color="text.secondary">
                Power Output
              </Typography>
              <Typography variant="h6">
                {performance.powerOutput} W
              </Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="body2" color="text.secondary">
                Endurance
              </Typography>
              <Typography variant="h6">
                {performance.enduranceScore.toFixed(1)}/10
              </Typography>
            </Grid>
          </Grid>
          {performance.safetyAlerts.length > 0 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              {performance.safetyAlerts.map((alert, index) => (
                <Typography key={index} variant="body2">
                  {alert}
                </Typography>
              ))}
            </Alert>
          )}
        </CardContent>
      </Card>
    );
  };

  const WorkoutAnalyticsCard: React.FC<{ analytics: WorkoutAnalytics }> = ({ analytics }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Workout Analytics
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Total Volume
            </Typography>
            <Typography variant="h6">
              {analytics.totalVolume} kg
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Intensity Score
            </Typography>
            <Typography variant="h6">
              {analytics.intensityScore.toFixed(1)}/10
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary">
              Recovery Status
            </Typography>
            <Chip
              label={analytics.recoveryStatus}
              color={
                analytics.recoveryStatus === 'READY' ? 'success' :
                analytics.recoveryStatus === 'NEEDS_REST' ? 'warning' : 'error'
              }
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const SafetyCheckCard: React.FC<{ checks: SafetyCheck }> = ({ checks }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Safety Status
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Equipment Status
            </Typography>
            <Chip
              label={checks.equipmentStatus}
              color={
                checks.equipmentStatus === 'READY' ? 'success' :
                checks.equipmentStatus === 'NEEDS_CHECK' ? 'warning' : 'error'
              }
            />
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Form Safety Score
            </Typography>
            <Typography variant="h6">
              {checks.formSafetyScore.toFixed(1)}/10
            </Typography>
          </Grid>
          {checks.safetyAlerts.length > 0 && (
            <Grid item xs={12}>
              <Alert severity="warning">
                {checks.safetyAlerts.map((alert, index) => (
                  <Typography key={index} variant="body2">
                    {alert}
                  </Typography>
                ))}
              </Alert>
            </Grid>
          )}
        </Grid>
      </CardContent>
    </Card>
  );

  const ExerciseAdaptationCard: React.FC<{ adaptation: ExerciseAdaptation }> = ({ adaptation }) => {
    const exercise = exercises.find(e => e.id === adaptation.exerciseId);
    if (!exercise) return null;

    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Exercise Adaptation: {exercise.name}
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">
                Current Difficulty
              </Typography>
              <Chip label={adaptation.currentDifficulty} color="primary" />
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">
                Suggested Difficulty
              </Typography>
              <Chip 
                label={adaptation.suggestedDifficulty} 
                color={adaptation.suggestedDifficulty !== adaptation.currentDifficulty ? 'warning' : 'success'} 
              />
            </Grid>
            {adaptation.formImprovements.length > 0 && (
              <Grid item xs={12}>
                <Alert severity="info">
                  {adaptation.formImprovements.map((improvement, index) => (
                    <Typography key={index} variant="body2">
                      {improvement}
                    </Typography>
                  ))}
                </Alert>
              </Grid>
            )}
            {adaptation.variations.length > 0 && (
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Suggested Variations:
                </Typography>
                <List dense>
                  {adaptation.variations.map((variation, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={variation} />
                    </ListItem>
                  ))}
                </List>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>
    );
  };

  const ProgressGoalCard: React.FC<{ goals: ProgressGoal[] }> = ({ goals }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Progress Goals
        </Typography>
        <Grid container spacing={2}>
          {goals.map(goal => (
            <Grid item xs={12} key={goal.id}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    {goal.title}
                  </Typography>
                  <Typography variant="body1">
                    {goal.status}
                  </Typography>
                </Box>
                <Chip
                  label={goal.status === 'Achieved' ? 'Achieved' : 'In Progress'}
                  color={goal.status === 'Achieved' ? 'success' : 'primary'}
                />
              </Box>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );

  const WorkoutOptimizationCard: React.FC<{ optimization: WorkoutOptimization }> = ({ optimization }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Workout Optimization
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Exercise Sequence
            </Typography>
            <List dense>
              {optimization.exerciseSequence.map((exerciseId, index) => {
                const exercise = exercises.find(e => e.id === exerciseId);
                return (
                  <ListItem key={index}>
                    <ListItemText 
                      primary={`${index + 1}. ${exercise?.name}`}
                      secondary={`Rest: ${optimization.optimalRestPeriods[exerciseId]}s`}
                    />
                  </ListItem>
                );
              })}
            </List>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Intensity Distribution
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Chip label={`Warmup: ${optimization.intensityDistribution.warmup}%`} />
              <Chip label={`Main: ${optimization.intensityDistribution.main}%`} />
              <Chip label={`Cooldown: ${optimization.intensityDistribution.cooldown}%`} />
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Recovery Time
            </Typography>
            <Typography variant="body1">
              {optimization.recoveryTime} hours
            </Typography>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const MuscleRecoveryCard: React.FC<{ recovery: MuscleGroupRecovery[] }> = ({ recovery }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Muscle Recovery Status
        </Typography>
        <Grid container spacing={2}>
          {recovery.map((muscle, index) => (
            <Grid item xs={12} key={index}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="subtitle1">
                    {muscle.muscleGroup}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Last worked: {new Date(muscle.lastWorked).toLocaleDateString()}
                  </Typography>
                </Box>
                <Chip
                  label={muscle.recoveryStatus}
                  color={
                    muscle.recoveryStatus === 'RECOVERED' ? 'success' :
                    muscle.recoveryStatus === 'RECOVERING' ? 'warning' : 'error'
                  }
                />
              </Box>
              {muscle.recoveryStatus !== 'RECOVERED' && (
                <Typography variant="body2" color="text.secondary">
                  Recommended rest: {Math.ceil(muscle.recommendedRest)} hours
                </Typography>
              )}
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );

  const PerformanceTrendCard: React.FC<{ trends: PerformanceTrend[] }> = ({ trends }): JSX.Element => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Performance Trends
        </Typography>
        <Grid container spacing={2}>
          {trends.map((trend, index) => (
            <Grid item xs={12} key={index}>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1">
                  {trend.metric}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography variant="body1">
                    Current: {trend.currentValue.toFixed(1)}
                  </Typography>
                  <Chip
                    label={`${trend.trend} (${trend.rateOfChange.toFixed(1)}%)`}
                    color={
                      trend.trend === 'INCREASING' ? 'success' :
                      trend.trend === 'DECREASING' ? 'error' : 'default'
                    }
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Next week: {trend.prediction.nextWeek.toFixed(1)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Next month: {trend.prediction.nextMonth.toFixed(1)}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <Typography variant="h6">Workout Plans</Typography>
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
                                label={`${plan.frequency}x per week`}
                                size="small"
                                color="primary"
                                variant="outlined"
                              />
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
                          onClick={() => handleStartSession(plan.id)}
                          disabled={activeSession !== null}
                          color="primary"
                        >
                          <StartIcon />
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

        {activeSession && (
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6" color="primary">
                  Active Session
                </Typography>
                <Button
                  variant="contained"
                  color="error"
                  startIcon={<StopIcon />}
                  onClick={() => handleEndSession(activeSession)}
                >
                  End Session
                </Button>
              </Box>
            </CardContent>
          </Card>
        )}
      </Grid>

      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Add New Plan
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
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
              <FormControl fullWidth>
                <InputLabel>Weekly Frequency</InputLabel>
                <Select
                  value={newPlanData.frequency}
                  label="Weekly Frequency"
                  onChange={(e) => setNewPlanData({ ...newPlanData, frequency: Number(e.target.value) })}
                >
                  {[1, 2, 3, 4, 5, 6, 7].map((freq) => (
                    <MenuItem key={freq} value={freq}>
                      {freq}x per week
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
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
              Recent Sessions
            </Typography>
            <List>
              {sessions.slice(0, 5).map((session) => (
                <ListItem key={session.id}>
                  <ListItemText
                    primary={new Date(session.startTime).toLocaleDateString()}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          {session.completed ? 'Completed' : 'In Progress'}
                        </Typography>
                        {session.difficultyRating && (
                          <Typography variant="body2" color="textSecondary">
                            Difficulty: {session.difficultyRating}/5
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

      {activeSession && (
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Workout Session
              </Typography>
              {restTimer !== null && <RestTimer seconds={restTimer} />}
              {activeExercise && <ExerciseFormFeedback exerciseId={activeExercise} />}
              {/* ... rest of active session UI ... */}
            </CardContent>
          </Card>
        </Grid>
      )}

      {plans.map(plan => (
        <Grid item xs={12} key={plan.id}>
          <Card>
            <CardContent>
              <ProgressTracker plan={plan} />
              {/* ... rest of plan UI ... */}
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}; 