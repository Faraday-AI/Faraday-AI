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
  LinearProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Tooltip,
  Checkbox,
  Rating,
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Timeline as TimelineIcon,
  Notifications as NotificationsIcon,
  TrendingUp as TrendingUpIcon,
  Share as ShareIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  ChartTooltip,
  Legend
);

interface Milestone {
  id: string;
  description: string;
  targetValue: number;
  achieved: boolean;
}

interface FitnessGoal {
  id: number;
  category: string;
  description: string;
  targetValue: number;
  currentValue: number;
  startDate: string;
  targetDate: string;
  status: string;
  timeframe: string;
  priority: number;
  activityType?: string;
  milestones: Milestone[];
  progressHistory: Array<{
    date: string;
    value: number;
  }>;
  notifications: boolean;
  linkedWorkoutPlanId?: number;
  linkedNutritionPlanId?: number;
  healthMetrics: Array<{
    metric: string;
    target: number;
    current: number;
  }>;
}

interface GoalFilter {
  status: string;
  priority: number | null;
  timeframe: string;
}

interface GoalAnalytics {
  averageProgress: number;
  completionRate: number;
  bestPerformingCategory: string;
  timeToCompletion: number;
  consistencyScore: number;
  improvementRate: number;
  categoryBreakdown: {
    category: string;
    progress: number;
    completionRate: number;
    averageTimeToComplete: number;
  }[];
  weeklyProgress: {
    date: string;
    progress: number;
    activities: number;
  }[];
}

interface ActivityHistory {
  type: string;
  count: number;
  lastActivity: string;
  averageDuration: number;
  totalCalories: number;
}

interface UserFeedback {
  id: string;
  goalId: number;
  type: 'difficulty' | 'motivation' | 'suggestion';
  rating: number;
  comment: string;
  date: string;
}

export const FitnessGoalsPanel: React.FC = () => {
  const [goals, setGoals] = useState<FitnessGoal[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('CARDIOVASCULAR');
  const [selectedActivityType, setSelectedActivityType] = useState<string>('');
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState<FitnessGoal | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [sortBy, setSortBy] = useState<'priority' | 'progress' | 'dueDate'>('priority');
  const [filters, setFilters] = useState<GoalFilter>({
    status: 'ALL',
    priority: null,
    timeframe: 'ALL'
  });

  const [newGoalData, setNewGoalData] = useState({
    description: '',
    targetValue: '',
    timeframe: 'SHORT_TERM',
    priority: 1,
    activityType: '',
    milestones: [] as Milestone[],
    healthMetrics: [] as FitnessGoal['healthMetrics'],
  });

  const [analytics, setAnalytics] = useState<GoalAnalytics>({
    averageProgress: 0,
    completionRate: 0,
    bestPerformingCategory: '',
    timeToCompletion: 0,
    consistencyScore: 0,
    improvementRate: 0,
    categoryBreakdown: [],
    weeklyProgress: [],
  });

  const [activityHistory, setActivityHistory] = useState<ActivityHistory[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [userFeedback, setUserFeedback] = useState<UserFeedback[]>([]);
  const [showFeedbackDialog, setShowFeedbackDialog] = useState(false);
  const [selectedGoalForFeedback, setSelectedGoalForFeedback] = useState<FitnessGoal | null>(null);
  const [feedbackType, setFeedbackType] = useState<'difficulty' | 'motivation' | 'suggestion'>('difficulty');
  const [feedbackRating, setFeedbackRating] = useState(0);
  const [feedbackComment, setFeedbackComment] = useState('');

  const categories = [
    { value: 'CARDIOVASCULAR', label: 'Cardiovascular', icon: '🏃' },
    { value: 'STRENGTH', label: 'Strength', icon: '💪' },
    { value: 'FLEXIBILITY', label: 'Flexibility', icon: '🧘' },
    { value: 'ENDURANCE', label: 'Endurance', icon: '🏊' },
    { value: 'SPORTS', label: 'Sports', icon: '⚽' },
    { value: 'WEIGHT', label: 'Weight Management', icon: '⚖️' },
  ];

  const activityTypes = [
    { value: 'RUNNING', label: 'Running', category: 'CARDIOVASCULAR' },
    { value: 'SWIMMING', label: 'Swimming', category: 'CARDIOVASCULAR' },
    { value: 'CYCLING', label: 'Cycling', category: 'CARDIOVASCULAR' },
    { value: 'WEIGHT_LIFTING', label: 'Weight Lifting', category: 'STRENGTH' },
    { value: 'BODYWEIGHT', label: 'Bodyweight Exercises', category: 'STRENGTH' },
    { value: 'YOGA', label: 'Yoga', category: 'FLEXIBILITY' },
    { value: 'STRETCHING', label: 'Stretching', category: 'FLEXIBILITY' },
    { value: 'SPORTS', label: 'Sports', category: 'SPORTS' },
  ];

  const goalTemplates = [
    {
      name: '5K Runner',
      category: 'CARDIOVASCULAR',
      description: 'Complete a 5K run in under 30 minutes',
      milestones: [
        {
          id: 'm1',
          description: 'Run 1 mile without stopping',
          targetValue: 1,
          achieved: false
        },
        {
          id: 'm2',
          description: 'Run 3 miles in under 35 minutes',
          targetValue: 3,
          achieved: false
        },
        {
          id: 'm3',
          description: 'Complete 5K in under 30 minutes',
          targetValue: 5,
          achieved: false
        }
      ]
    },
    {
      name: 'Push-up Challenge',
      category: 'STRENGTH',
      description: 'Complete 50 push-ups in one set',
      milestones: [
        {
          id: 'm1',
          description: 'Complete 10 push-ups in one set',
          targetValue: 10,
          achieved: false
        },
        {
          id: 'm2',
          description: 'Complete 25 push-ups in one set',
          targetValue: 25,
          achieved: false
        },
        {
          id: 'm3',
          description: 'Complete 50 push-ups in one set',
          targetValue: 50,
          achieved: false
        }
      ]
    },
    {
      name: 'Splits Goal',
      category: 'FLEXIBILITY',
      description: 'Achieve full splits',
      milestones: [
        {
          id: 'm1',
          description: 'Touch toes while standing',
          targetValue: 1,
          achieved: false
        },
        {
          id: 'm2',
          description: 'Hold 90-degree split for 30 seconds',
          targetValue: 2,
          achieved: false
        },
        {
          id: 'm3',
          description: 'Achieve full splits',
          targetValue: 3,
          achieved: false
        }
      ]
    },
    {
      name: 'Weight Loss',
      category: 'WEIGHT_MANAGEMENT',
      description: 'Lose 10 pounds in 3 months',
      milestones: [
        {
          id: 'm1',
          description: 'Lose first 3 pounds',
          targetValue: 3,
          achieved: false
        },
        {
          id: 'm2',
          description: 'Lose 7 pounds',
          targetValue: 7,
          achieved: false
        },
        {
          id: 'm3',
          description: 'Lose 10 pounds',
          targetValue: 10,
          achieved: false
        }
      ]
    }
  ];

  const timeframes = [
    { value: 'SHORT_TERM', label: 'Short Term (1-4 weeks)' },
    { value: 'MEDIUM_TERM', label: 'Medium Term (1-3 months)' },
    { value: 'LONG_TERM', label: 'Long Term (3+ months)' },
    { value: 'ACADEMIC_YEAR', label: 'Academic Year' },
  ];

  useEffect(() => {
    fetchGoals();
  }, [selectedCategory]);

  const fetchGoals = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/students/1/fitness-goals?category=${selectedCategory}`
      );
      if (!response.ok) throw new Error('Failed to fetch goals');
      const data = await response.json();
      setGoals(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleAddGoal = async () => {
    setLoading(true);
    setError(null);
    try {
      const template = goalTemplates.find(t => t.name === selectedTemplate);
      const response = await fetch(
        '/api/v1/physical-education/health-fitness/students/1/fitness-goals',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            category: selectedCategory,
            description: template ? template.description : newGoalData.description,
            target_value: parseFloat(newGoalData.targetValue),
            timeframe: newGoalData.timeframe,
            priority: newGoalData.priority,
            activityType: selectedActivityType,
            milestones: template ? template.milestones : newGoalData.milestones,
            healthMetrics: newGoalData.healthMetrics,
          }),
        }
      );
      if (!response.ok) throw new Error('Failed to add goal');
      setNewGoalData({
        description: '',
        targetValue: '',
        timeframe: 'SHORT_TERM',
        priority: 1,
        activityType: '',
        milestones: [],
        healthMetrics: [],
      });
      setSelectedTemplate('');
      setSelectedActivityType('');
      setOpenDialog(false);
      fetchGoals();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProgress = async (goalId: number, newValue: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/fitness-goals/${goalId}/progress`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            value: newValue,
          }),
        }
      );
      if (!response.ok) throw new Error('Failed to update progress');
      fetchGoals();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 100) return 'success';
    if (progress >= 50) return 'primary';
    if (progress >= 25) return 'warning';
    return 'error';
  };

  const calculateProgress = (current: number, target: number) => {
    return Math.min((current / target) * 100, 100);
  };

  const filteredAndSortedGoals = React.useMemo(() => {
    let result = [...goals];
    
    // Apply filters
    if (filters.status !== 'ALL') {
      result = result.filter(goal => goal.status === filters.status);
    }
    if (filters.priority !== null) {
      result = result.filter(goal => goal.priority === filters.priority);
    }
    if (filters.timeframe !== 'ALL') {
      result = result.filter(goal => goal.timeframe === filters.timeframe);
    }
    
    // Apply sorting
    switch (sortBy) {
      case 'priority':
        result.sort((a, b) => a.priority - b.priority);
        break;
      case 'progress':
        result.sort((a, b) => {
          const progressA = calculateProgress(a.currentValue, a.targetValue);
          const progressB = calculateProgress(b.currentValue, b.targetValue);
          return progressB - progressA;
        });
        break;
      case 'dueDate':
        result.sort((a, b) => new Date(a.targetDate).getTime() - new Date(b.targetDate).getTime());
        break;
    }
    
    return result;
  }, [goals, filters, sortBy]);

  const handleShareGoal = async (goal: FitnessGoal) => {
    try {
      const response = await fetch('/api/v1/physical-education/health-fitness/goals/share', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goalId: goal.id })
      });
      if (!response.ok) throw new Error('Failed to share goal');
      // Show success notification
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to share goal');
    }
  };

  const GoalProgressChart: React.FC<{ goal: FitnessGoal }> = ({ goal }) => {
    const chartData = {
      labels: goal.progressHistory.map(item => new Date(item.date).toLocaleDateString()),
      datasets: [
        {
          label: 'Progress',
          data: goal.progressHistory.map(item => item.value),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.5)',
          tension: 0.1,
        },
        {
          label: 'Target',
          data: goal.progressHistory.map(() => goal.targetValue),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
          borderDash: [5, 5],
        },
      ],
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'top' as const,
        },
        title: {
          display: true,
          text: 'Progress Over Time',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    };

    return <Line data={chartData} options={options} />;
  };

  const MilestoneProgress: React.FC<{ milestones: Milestone[] }> = ({ milestones }) => {
    const completed = milestones.filter(m => m.achieved).length;
    const total = milestones.length;

    return (
      <Box sx={{ mt: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Milestones: {completed}/{total}
        </Typography>
        <LinearProgress
          variant="determinate"
          value={(completed / total) * 100}
          sx={{ mt: 1 }}
        />
        <Box sx={{ mt: 1 }}>
          {milestones.map((milestone) => (
            <Box
              key={milestone.id}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                mt: 0.5
              }}
            >
              <Checkbox
                checked={milestone.achieved}
                disabled
                size="small"
              />
              <Typography variant="body2">
                {milestone.description}
              </Typography>
            </Box>
          ))}
        </Box>
      </Box>
    );
  };

  const HealthMetricsDisplay: React.FC<{ metrics: FitnessGoal['healthMetrics'] }> = ({ metrics }) => {
    return (
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Health Metrics
        </Typography>
        <Grid container spacing={2}>
          {metrics.map((metric, index) => (
            <Grid item xs={12} sm={6} key={index}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="body2" gutterBottom>
                    {metric.metric}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={(metric.current / metric.target) * 100}
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="caption">
                    {metric.current} / {metric.target}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  };

  const handleGoalClick = (goal: FitnessGoal) => {
    setSelectedGoal(goal);
    setOpenDialog(true);
  };

  const EnhancedProgressChart: React.FC<{ goal: FitnessGoal }> = ({ goal }) => {
    const chartData = {
      labels: goal.progressHistory.map(item => new Date(item.date).toLocaleDateString()),
      datasets: [
        {
          label: 'Progress',
          data: goal.progressHistory.map(item => item.value),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.5)',
          tension: 0.1,
        },
        {
          label: 'Target',
          data: goal.progressHistory.map(() => goal.targetValue),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
          borderDash: [5, 5],
        },
        {
          label: 'Average Progress',
          data: goal.progressHistory.map((_, index, array) => {
            const slice = array.slice(0, index + 1);
            return slice.reduce((sum, item) => sum + item.value, 0) / slice.length;
          }),
          borderColor: 'rgb(153, 102, 255)',
          backgroundColor: 'rgba(153, 102, 255, 0.5)',
          borderDash: [2, 2],
        }
      ],
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'top' as const,
        },
        title: {
          display: true,
          text: 'Progress Over Time',
        },
        tooltip: {
          callbacks: {
            label: (context: any) => {
              const label = context.dataset.label || '';
              const value = context.parsed.y;
              const percentage = (value / goal.targetValue) * 100;
              return `${label}: ${value} (${percentage.toFixed(1)}%)`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Value'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Date'
          }
        }
      }
    };

    return <Line data={chartData} options={options} />;
  };

  const GoalCompletionCelebration: React.FC<{ goal: FitnessGoal }> = ({ goal }) => {
    const [showCelebration, setShowCelebration] = useState(true);

    if (!showCelebration) return null;

    return (
      <Dialog
        open={showCelebration}
        onClose={() => setShowCelebration(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogContent>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h4" gutterBottom>
              🎉 Congratulations! 🎉
            </Typography>
            <Typography variant="h6" gutterBottom>
              You've completed your goal:
            </Typography>
            <Typography variant="h5" color="primary" gutterBottom>
              {goal.description}
            </Typography>
            <Typography variant="body1" sx={{ mt: 2 }}>
              You achieved {goal.currentValue} out of {goal.targetValue}!
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={() => setShowCelebration(false)}
              sx={{ mt: 3 }}
            >
              Continue
            </Button>
          </Box>
        </DialogContent>
      </Dialog>
    );
  };

  const ProgressNotification: React.FC<{ goal: FitnessGoal }> = ({ goal }) => {
    const progress = calculateProgress(goal.currentValue, goal.targetValue);
    const lastProgress = goal.progressHistory[goal.progressHistory.length - 2]?.value || 0;
    const progressDiff = goal.currentValue - lastProgress;

    if (progressDiff <= 0) return null;

    return (
      <Alert
        severity="info"
        sx={{ mb: 2 }}
        action={
          <IconButton
            aria-label="close"
            color="inherit"
            size="small"
          >
            <CloseIcon />
          </IconButton>
        }
      >
        <Typography variant="body2">
          Great progress! You've increased your {goal.description} by {progressDiff} units.
          {progress >= 50 && progress < 100 && " You're halfway there!"}
          {progress >= 100 && " You've reached your goal!"}
        </Typography>
      </Alert>
    );
  };

  const GoalAnalyticsCard: React.FC<{ analytics: GoalAnalytics }> = ({ analytics }) => {
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
      const timer = setTimeout(() => setIsLoading(false), 500);
      return () => clearTimeout(timer);
    }, [analytics]);

    if (isLoading) {
      return (
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
              <CircularProgress />
            </Box>
          </CardContent>
        </Card>
      );
    }

    return (
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Goal Analytics
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <Tooltip title="Average progress across all your goals">
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">
                    {analytics.averageProgress}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Average Progress
                  </Typography>
                </Box>
              </Tooltip>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Tooltip title="Percentage of goals you've successfully completed">
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    {analytics.completionRate}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Completion Rate
                  </Typography>
                </Box>
              </Tooltip>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Tooltip title="Category where you're making the most progress">
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="info.main">
                    {analytics.bestPerformingCategory}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Best Category
                  </Typography>
                </Box>
              </Tooltip>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Tooltip title="Average number of days to complete a goal">
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">
                    {analytics.timeToCompletion} days
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg. Time to Complete
                  </Typography>
                </Box>
              </Tooltip>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  const QuickProgressUpdate: React.FC<{ goal: FitnessGoal; onUpdate: (value: number) => void }> = ({ 
    goal, 
    onUpdate 
  }) => {
    const [value, setValue] = useState(goal.currentValue);
    const [isUpdating, setIsUpdating] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    const handleUpdate = async () => {
      if (value < 0 || value > goal.targetValue) {
        setError(`Value must be between 0 and ${goal.targetValue}`);
        return;
      }

      setIsUpdating(true);
      setError(null);
      try {
        await onUpdate(value);
        setSuccess(true);
        setTimeout(() => setSuccess(false), 2000);
      } catch (err) {
        setError('Failed to update progress');
      } finally {
        setIsUpdating(false);
      }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
      if (e.key === 'Enter') {
        handleUpdate();
      }
    };

    return (
      <Box sx={{ mt: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TextField
            size="small"
            type="number"
            value={value}
            onChange={(e) => {
              setValue(Number(e.target.value));
              setError(null);
            }}
            onKeyPress={handleKeyPress}
            inputProps={{ 
              min: 0, 
              max: goal.targetValue,
              'aria-label': 'Progress value'
            }}
            error={!!error}
            helperText={error}
            sx={{ width: 100 }}
          />
          <Button
            size="small"
            variant="contained"
            onClick={handleUpdate}
            disabled={isUpdating}
          >
            {isUpdating ? <CircularProgress size={20} /> : 'Update'}
          </Button>
        </Box>
        {success && (
          <Alert severity="success" sx={{ mt: 1 }}>
            Progress updated successfully!
          </Alert>
        )}
      </Box>
    );
  };

  const getPersonalizedRecommendations = (history: ActivityHistory[]) => {
    if (history.length === 0) return [];

    // Sort activities by frequency and recency
    const sortedActivities = [...history].sort((a, b) => {
      const frequencyDiff = b.count - a.count;
      if (frequencyDiff !== 0) return frequencyDiff;
      return new Date(b.lastActivity).getTime() - new Date(a.lastActivity).getTime();
    });

    const recommendations = [];
    const usedCategories = new Set<string>();

    // First, recommend based on most frequent activities
    for (const activity of sortedActivities) {
      const activityType = activityTypes.find(type => type.value === activity.type);
      if (!activityType || usedCategories.has(activityType.category)) continue;

      const categoryTemplates = goalTemplates
        .filter(template => template.category === activityType.category)
        .map(template => ({
          ...template,
          relevance: activity.count * 0.6 + // Frequency weight
            (activity.averageDuration / 60) * 0.2 + // Duration weight
            (activity.totalCalories / 1000) * 0.2 // Calories weight
        }))
        .sort((a, b) => b.relevance - a.relevance);

      if (categoryTemplates.length > 0) {
        recommendations.push(categoryTemplates[0]);
        usedCategories.add(activityType.category);
      }

      if (recommendations.length >= 3) break;
    }

    // If we don't have enough recommendations, add complementary goals
    if (recommendations.length < 3) {
      const complementaryCategories = {
        'CARDIOVASCULAR': 'STRENGTH',
        'STRENGTH': 'FLEXIBILITY',
        'FLEXIBILITY': 'CARDIOVASCULAR',
        'ENDURANCE': 'STRENGTH',
        'SPORTS': 'FLEXIBILITY',
        'WEIGHT_MANAGEMENT': 'CARDIOVASCULAR'
      };

      for (const category of Object.keys(complementaryCategories)) {
        if (usedCategories.has(category)) {
          const complementaryCategory = complementaryCategories[category as keyof typeof complementaryCategories];
          if (!usedCategories.has(complementaryCategory)) {
            const complementaryTemplate = goalTemplates
              .find(template => template.category === complementaryCategory);
            if (complementaryTemplate) {
              recommendations.push(complementaryTemplate);
              usedCategories.add(complementaryCategory);
            }
          }
        }
      }
    }

    return recommendations.slice(0, 3);
  };

  const GoalRecommendations: React.FC = () => {
    const [isLoading, setIsLoading] = useState(true);
    const [recommendations, setRecommendations] = useState<typeof goalTemplates>([]);

    useEffect(() => {
      const fetchRecommendations = async () => {
        setIsLoading(true);
        try {
          const personalizedRecs = getPersonalizedRecommendations(activityHistory);
          setRecommendations(personalizedRecs);
        } finally {
          setIsLoading(false);
        }
      };

      fetchRecommendations();
    }, [activityHistory]);

    if (isLoadingHistory || isLoading) {
      return (
        <Card variant="outlined" sx={{ mt: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
              <CircularProgress />
            </Box>
          </CardContent>
        </Card>
      );
    }

    if (recommendations.length === 0) return null;

    return (
      <Card variant="outlined" sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recommended Goals
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Based on your activity history and fitness patterns
          </Typography>
          <Grid container spacing={2}>
            {recommendations.map((template) => (
              <Grid item xs={12} sm={4} key={template.name}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      {template.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {template.description}
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        Category: {categories.find(c => c.value === template.category)?.label}
                      </Typography>
                    </Box>
                    <Button
                      size="small"
                      variant="outlined"
                      sx={{ mt: 1 }}
                      onClick={() => {
                        setSelectedTemplate(template.name);
                        setOpenDialog(true);
                      }}
                    >
                      Use Template
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    );
  };

  const calculateConsistencyScore = (goals: FitnessGoal[]) => {
    if (goals.length === 0) return 0;
    
    const consistencyScores = goals.map(goal => {
      const progressHistory = goal.progressHistory;
      if (progressHistory.length < 2) return 0;

      const dates = progressHistory.map(p => new Date(p.date));
      const intervals = dates.slice(1).map((date, i) => 
        (date.getTime() - dates[i].getTime()) / (1000 * 60 * 60 * 24)
      );

      const averageInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
      const variance = intervals.reduce((a, b) => a + Math.pow(b - averageInterval, 2), 0) / intervals.length;
      
      return Math.max(0, 100 - (variance * 10));
    });

    return Math.round(consistencyScores.reduce((a, b) => a + b, 0) / consistencyScores.length);
  };

  const calculateImprovementRate = (goals: FitnessGoal[]) => {
    if (goals.length === 0) return 0;

    const rates = goals.map(goal => {
      const progressHistory = goal.progressHistory;
      if (progressHistory.length < 2) return 0;

      const startValue = progressHistory[0].value;
      const endValue = progressHistory[progressHistory.length - 1].value;
      const days = (new Date(progressHistory[progressHistory.length - 1].date).getTime() - 
                   new Date(progressHistory[0].date).getTime()) / (1000 * 60 * 60 * 24);

      return ((endValue - startValue) / startValue) * (30 / days) * 100;
    });

    return Math.round(rates.reduce((a, b) => a + b, 0) / rates.length);
  };

  const calculateCategoryBreakdown = (goals: FitnessGoal[]) => {
    const categoryData = new Map<string, {
      progress: number[];
      completionRate: number[];
      timeToComplete: number[];
    }>();

    goals.forEach(goal => {
      const category = goal.category;
      if (!categoryData.has(category)) {
        categoryData.set(category, { progress: [], completionRate: [], timeToComplete: [] });
      }
      const data = categoryData.get(category)!;
      
      data.progress.push(calculateProgress(goal.currentValue, goal.targetValue));
      data.completionRate.push(goal.status === 'COMPLETED' ? 1 : 0);
      
      if (goal.status === 'COMPLETED') {
        const timeToComplete = (new Date(goal.targetDate).getTime() - 
                              new Date(goal.startDate).getTime()) / (1000 * 60 * 60 * 24);
        data.timeToComplete.push(timeToComplete);
      }
    });

    return Array.from(categoryData.entries()).map(([category, data]) => ({
      category,
      progress: Math.round(data.progress.reduce((a, b) => a + b, 0) / data.progress.length),
      completionRate: Math.round((data.completionRate.reduce((a, b) => a + b, 0) / data.completionRate.length) * 100),
      averageTimeToComplete: Math.round(data.timeToComplete.reduce((a, b) => a + b, 0) / data.timeToComplete.length)
    }));
  };

  const calculateWeeklyProgress = (goals: FitnessGoal[]) => {
    const weeklyData = new Map<string, { progress: number; activities: number }>();

    goals.forEach(goal => {
      goal.progressHistory.forEach(entry => {
        const date = new Date(entry.date);
        const weekStart = new Date(date);
        weekStart.setDate(date.getDate() - date.getDay());
        const weekKey = weekStart.toISOString().split('T')[0];

        if (!weeklyData.has(weekKey)) {
          weeklyData.set(weekKey, { progress: 0, activities: 0 });
        }
        const data = weeklyData.get(weekKey)!;
        data.progress += entry.value;
        data.activities += 1;
      });
    });

    return Array.from(weeklyData.entries())
      .map(([date, data]) => ({
        date,
        progress: Math.round(data.progress / data.activities),
        activities: data.activities
      }))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  };

  useEffect(() => {
    const calculateAnalytics = () => {
      if (goals.length === 0) return;

      const completedGoals = goals.filter(g => g.status === 'COMPLETED');
      const categoryProgress = goals.reduce((acc, goal) => {
        acc[goal.category] = (acc[goal.category] || 0) + 
          calculateProgress(goal.currentValue, goal.targetValue);
        return acc;
      }, {} as Record<string, number>);

      const bestCategory = Object.entries(categoryProgress)
        .sort(([, a], [, b]) => b - a)[0][0];

      setAnalytics({
        averageProgress: Math.round(
          goals.reduce((sum, goal) => 
            sum + calculateProgress(goal.currentValue, goal.targetValue), 0
          ) / goals.length
        ),
        completionRate: Math.round((completedGoals.length / goals.length) * 100),
        bestPerformingCategory: bestCategory,
        timeToCompletion: completedGoals.length > 0
          ? Math.round(completedGoals.reduce((sum, goal) => {
              const start = new Date(goal.startDate);
              const end = new Date(goal.targetDate);
              return sum + (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24);
            }, 0) / completedGoals.length)
          : 0,
        consistencyScore: calculateConsistencyScore(goals),
        improvementRate: calculateImprovementRate(goals),
        categoryBreakdown: calculateCategoryBreakdown(goals),
        weeklyProgress: calculateWeeklyProgress(goals)
      });
    };

    calculateAnalytics();
  }, [goals]);

  useEffect(() => {
    const fetchActivityHistory = async () => {
      setIsLoadingHistory(true);
      try {
        const response = await fetch('/api/v1/physical-education/activities/history');
        if (!response.ok) throw new Error('Failed to fetch activity history');
        const data = await response.json();
        setActivityHistory(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load activity history');
      } finally {
        setIsLoadingHistory(false);
      }
    };

    fetchActivityHistory();
  }, []);

  const handleSubmitFeedback = async () => {
    if (!selectedGoalForFeedback) return;

    try {
      const response = await fetch('/api/v1/physical-education/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goalId: selectedGoalForFeedback.id,
          type: feedbackType,
          rating: feedbackRating,
          comment: feedbackComment
        })
      });

      if (!response.ok) throw new Error('Failed to submit feedback');

      setUserFeedback(prev => [...prev, {
        id: Date.now().toString(),
        goalId: selectedGoalForFeedback.id,
        type: feedbackType,
        rating: feedbackRating,
        comment: feedbackComment,
        date: new Date().toISOString()
      }]);

      setShowFeedbackDialog(false);
      setSelectedGoalForFeedback(null);
      setFeedbackType('difficulty');
      setFeedbackRating(0);
      setFeedbackComment('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit feedback');
    }
  };

  const FeedbackDialog: React.FC = () => {
    if (!selectedGoalForFeedback) return null;

    return (
      <Dialog open={showFeedbackDialog} onClose={() => setShowFeedbackDialog(false)}>
        <DialogTitle>Provide Feedback</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Feedback Type</InputLabel>
              <Select
                value={feedbackType}
                label="Feedback Type"
                onChange={(e) => setFeedbackType(e.target.value as typeof feedbackType)}
              >
                <MenuItem value="difficulty">Difficulty Level</MenuItem>
                <MenuItem value="motivation">Motivation</MenuItem>
                <MenuItem value="suggestion">Suggestion</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ mb: 2 }}>
              <Typography gutterBottom>Rating</Typography>
              <Rating
                value={feedbackRating}
                onChange={(_, value) => setFeedbackRating(value || 0)}
              />
            </Box>

            <TextField
              fullWidth
              multiline
              rows={4}
              label="Comments"
              value={feedbackComment}
              onChange={(e) => setFeedbackComment(e.target.value)}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowFeedbackDialog(false)}>Cancel</Button>
          <Button onClick={handleSubmitFeedback} variant="contained" color="primary">
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  const EnhancedAnalyticsCard: React.FC<{ analytics: GoalAnalytics }> = ({ analytics }) => {
    return (
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Detailed Analytics
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" gutterBottom>
                Overall Performance
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Tooltip title="Average progress across all goals">
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">
                        {analytics.averageProgress}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Average Progress
                      </Typography>
                    </Box>
                  </Tooltip>
                </Grid>
                <Grid item xs={6}>
                  <Tooltip title="How consistently you work on your goals">
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="info.main">
                        {analytics.consistencyScore}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Consistency Score
                      </Typography>
                    </Box>
                  </Tooltip>
                </Grid>
              </Grid>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" gutterBottom>
                Category Performance
              </Typography>
              <Grid container spacing={2}>
                {analytics.categoryBreakdown.map(category => (
                  <Grid item xs={6} key={category.category}>
                    <Tooltip title={`${category.completionRate}% completion rate`}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="success.main">
                          {category.progress}%
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {categories.find(c => c.value === category.category)?.label}
                        </Typography>
                      </Box>
                    </Tooltip>
                  </Grid>
                ))}
              </Grid>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={selectedCategory}
              label="Category"
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                setSelectedActivityType('');
              }}
            >
              {categories.map((category) => (
                <MenuItem key={category.value} value={category.value}>
                  {category.icon} {category.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Activity Type</InputLabel>
            <Select
              value={selectedActivityType}
              label="Activity Type"
              onChange={(e) => setSelectedActivityType(e.target.value)}
              disabled={!selectedCategory}
            >
              {activityTypes
                .filter(type => type.category === selectedCategory)
                .map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Sort By</InputLabel>
            <Select
              value={sortBy}
              label="Sort By"
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            >
              <MenuItem value="priority">Priority</MenuItem>
              <MenuItem value="progress">Progress</MenuItem>
              <MenuItem value="dueDate">Due Date</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.status}
              label="Status"
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            >
              <MenuItem value="ALL">All Statuses</MenuItem>
              <MenuItem value="IN_PROGRESS">In Progress</MenuItem>
              <MenuItem value="COMPLETED">Completed</MenuItem>
              <MenuItem value="NOT_STARTED">Not Started</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Timeframe</InputLabel>
            <Select
              value={filters.timeframe}
              label="Timeframe"
              onChange={(e) => setFilters({ ...filters, timeframe: e.target.value })}
            >
              <MenuItem value="ALL">All Timeframes</MenuItem>
              {timeframes.map((timeframe) => (
                <MenuItem key={timeframe.value} value={timeframe.value}>
                  {timeframe.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              setSelectedGoal(null);
              setOpenDialog(true);
            }}
          >
            Add Goal
          </Button>

          <IconButton onClick={fetchGoals} color="primary">
            <RefreshIcon />
          </IconButton>
        </Box>
      </Grid>

      {error && (
        <Grid item xs={12}>
          <Alert severity="error">{error}</Alert>
        </Grid>
      )}

      <Grid item xs={12}>
        <GoalAnalyticsCard analytics={analytics} />
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
              <Tab label="Goals" icon={<TrendingUpIcon />} />
              <Tab label="Progress" icon={<TimelineIcon />} />
              <Tab label="Notifications" icon={<NotificationsIcon />} />
            </Tabs>

            {activeTab === 0 && (
              <>
                <Grid container spacing={2} sx={{ mt: 2 }}>
                  {filteredAndSortedGoals.map((goal) => (
                    <Grid item xs={12} md={6} key={goal.id}>
                      <Card variant="outlined" onClick={() => handleGoalClick(goal)}>
                        <CardContent>
                          <ProgressNotification goal={goal} />
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="subtitle1">
                              {goal.description}
                            </Typography>
                            <Box>
                              <IconButton size="small" onClick={(e) => {
                                e.stopPropagation();
                                handleShareGoal(goal);
                              }}>
                                <ShareIcon />
                              </IconButton>
                              <IconButton size="small">
                                <EditIcon />
                              </IconButton>
                              <IconButton size="small" color="error">
                                <DeleteIcon />
                              </IconButton>
                            </Box>
                          </Box>
                          <QuickProgressUpdate
                            goal={goal}
                            onUpdate={(value) => handleUpdateProgress(goal.id, value)}
                          />
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={calculateProgress(goal.currentValue, goal.targetValue)}
                              color={getProgressColor(calculateProgress(goal.currentValue, goal.targetValue)) as any}
                              sx={{ flexGrow: 1 }}
                            />
                            <Typography variant="body2">
                              {goal.currentValue} / {goal.targetValue}
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Chip
                              label={goal.timeframe}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                            <Chip
                              label={`Priority ${goal.priority}`}
                              size="small"
                              color="secondary"
                              variant="outlined"
                            />
                            <Chip
                              label={goal.status}
                              size="small"
                              color={goal.status === 'COMPLETED' ? 'success' : 'default'}
                              variant="outlined"
                            />
                          </Box>
                          <MilestoneProgress milestones={goal.milestones} />
                          <HealthMetricsDisplay metrics={goal.healthMetrics} />
                          {goal.status === 'COMPLETED' && (
                            <GoalCompletionCelebration goal={goal} />
                          )}
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
                <GoalRecommendations />
              </>
            )}

            {activeTab === 1 && selectedGoal && (
              <Box sx={{ mt: 2 }}>
                <EnhancedProgressChart goal={selectedGoal} />
              </Box>
            )}

            {activeTab === 2 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Goal Notifications
                </Typography>
                {/* Add notification settings and history here */}
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <EnhancedAnalyticsCard analytics={analytics} />
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedGoal ? 'Edit Goal' : 'Add New Goal'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Goal Template</InputLabel>
              <Select
                value={selectedTemplate}
                label="Goal Template"
                onChange={(e) => {
                  setSelectedTemplate(e.target.value);
                  const template = goalTemplates.find(t => t.name === e.target.value);
                  if (template) {
                    setNewGoalData({
                      ...newGoalData,
                      description: template.description,
                      milestones: template.milestones,
                    });
                  }
                }}
              >
                {goalTemplates
                  .filter(template => template.category === selectedCategory)
                  .map((template) => (
                    <MenuItem key={template.name} value={template.name}>
                      {template.name}
                    </MenuItem>
                  ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Description"
              value={newGoalData.description}
              onChange={(e) => setNewGoalData({ ...newGoalData, description: e.target.value })}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Target Value"
              type="number"
              value={newGoalData.targetValue}
              onChange={(e) => setNewGoalData({ ...newGoalData, targetValue: e.target.value })}
              sx={{ mb: 2 }}
            />

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Timeframe</InputLabel>
              <Select
                value={newGoalData.timeframe}
                label="Timeframe"
                onChange={(e) => setNewGoalData({ ...newGoalData, timeframe: e.target.value })}
              >
                {timeframes.map((timeframe) => (
                  <MenuItem key={timeframe.value} value={timeframe.value}>
                    {timeframe.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Priority"
              type="number"
              value={newGoalData.priority}
              onChange={(e) => setNewGoalData({ ...newGoalData, priority: parseInt(e.target.value) })}
              sx={{ mb: 2 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleAddGoal} variant="contained" color="primary">
            {selectedGoal ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>

      <FeedbackDialog />
    </Grid>
  );
}; 