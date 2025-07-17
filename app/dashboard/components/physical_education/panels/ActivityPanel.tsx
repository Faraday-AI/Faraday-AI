import React, { useState, useEffect } from 'react';
import {
  Box,
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
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  FormHelperText,
  Alert,
  CircularProgress,
  Tooltip as MuiTooltip,
  InputAdornment,
  Menu,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  DirectionsRun as RunIcon,
  FitnessCenter as FitnessCenterIcon,
  Pool as SwimIcon,
  SportsSoccer as SportsIcon,
  Search as SearchIcon,
  Sort as SortIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { format, isValid, parseISO } from 'date-fns';
import { Line, Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  ChartType,
} from 'chart.js';
import zoomPlugin from 'chartjs-plugin-zoom';
import * as XLSX from 'xlsx';
import { ChartOptions } from 'chart.js';

// Add type declaration for zoom plugin
declare module 'chart.js' {
  interface PluginOptionsByType<TType extends ChartType> {
    zoom: {
      zoom: {
        wheel: {
          enabled: boolean;
        };
        pinch: {
          enabled: boolean;
        };
        mode: string;
      };
      pan: {
        enabled: boolean;
        mode: string;
      };
    };
  }
}

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  ChartTooltip,
  Legend,
  zoomPlugin
);

interface Activity {
  id: number;
  type: 'RUNNING' | 'SWIMMING' | 'GYM' | 'SPORTS' | 'OTHER';
  duration: number; // in minutes
  intensity: 'LOW' | 'MODERATE' | 'HIGH';
  caloriesBurned: number;
  date: string;
  notes?: string;
  performanceMetrics: {
    // Common metrics
    heartRate?: number;
    // Running specific
    distance?: number;
    pace?: number;
    elevationGain?: number;
    cadence?: number;
    strideLength?: number;
    terrain?: 'FLAT' | 'HILLY' | 'MOUNTAIN' | 'TRAIL';
    // Swimming specific
    laps?: number;
    poolLength?: number;
    strokeType?: 'FREESTYLE' | 'BACKSTROKE' | 'BREASTSTROKE' | 'BUTTERFLY';
    strokeCount?: number;
    poolType?: 'INDOOR' | 'OUTDOOR';
    waterTemp?: number;
    // Gym specific
    sets?: number;
    reps?: number;
    weight?: number;
    exerciseType?: 'STRENGTH' | 'CARDIO' | 'FLEXIBILITY';
    equipment?: string;
    restTime?: number;
    targetMuscle?: string;
    // Sports specific
    sportType?: 'BASKETBALL' | 'SOCCER' | 'TENNIS' | 'VOLLEYBALL';
    score?: string;
    opponent?: string;
    position?: string;
    gameDuration?: number;
    pointsScored?: number;
    assists?: number;
    rebounds?: number;
  };
}

interface ActivityMetrics {
  totalDuration: number;
  totalCalories: number;
  activitiesByType: Record<string, number>;
  weeklyAverage: number;
  monthlyTrend: number[];
}

const API_BASE_URL = '/api/activities';

// Define a type for the zoom plugin configuration
type ZoomConfig = {
  zoom: {
    wheel: { enabled: boolean };
    pinch: { enabled: boolean };
    mode: string;
  };
  pan: {
    enabled: boolean;
    mode: string;
  };
};

// Define a type for export formats
type ExportFormat = 'CSV' | 'JSON' | 'EXCEL';

interface ChartData {
  lineData: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      borderColor: string;
      backgroundColor: string;
      tension: number;
      pointRadius: number;
      pointHoverRadius: number;
    }>;
  };
  barData: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      backgroundColor: string[];
      borderColor: string[];
      borderWidth: number;
    }>;
  };
  caloriesData: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      backgroundColor: string[];
      borderColor: string[];
      borderWidth: number;
    }>;
  };
  intensityData: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      backgroundColor: string[];
      borderColor: string[];
      borderWidth: number;
    }>;
  };
}

const ActivityTypeSpecificFields: React.FC<{
  type: Activity['type'];
  editingItem: Activity | null;
}> = ({ type, editingItem }) => {
  switch (type) {
    case 'RUNNING':
      return (
        <>
          <TextField
            fullWidth
            name="distance"
            label="Distance (km)"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.distance}
            margin="normal"
          />
          <TextField
            fullWidth
            name="pace"
            label="Pace (min/km)"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.pace}
            margin="normal"
          />
          <TextField
            fullWidth
            name="elevationGain"
            label="Elevation Gain (m)"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.elevationGain}
            margin="normal"
          />
          <TextField
            fullWidth
            name="cadence"
            label="Cadence (steps/min)"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.cadence}
            margin="normal"
          />
          <TextField
            fullWidth
            name="strideLength"
            label="Stride Length (m)"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.strideLength}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Terrain</InputLabel>
            <Select
              name="terrain"
              defaultValue={editingItem?.performanceMetrics?.terrain || ''}
            >
              <MenuItem value="FLAT">Flat</MenuItem>
              <MenuItem value="HILLY">Hilly</MenuItem>
              <MenuItem value="MOUNTAIN">Mountain</MenuItem>
              <MenuItem value="TRAIL">Trail</MenuItem>
            </Select>
          </FormControl>
        </>
      );
    case 'SWIMMING':
      return (
        <>
          <TextField
            fullWidth
            name="laps"
            label="Laps"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.laps}
            margin="normal"
          />
          <TextField
            fullWidth
            name="poolLength"
            label="Pool Length (m)"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.poolLength}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Stroke Type</InputLabel>
            <Select
              name="strokeType"
              defaultValue={editingItem?.performanceMetrics?.strokeType || ''}
            >
              <MenuItem value="FREESTYLE">Freestyle</MenuItem>
              <MenuItem value="BACKSTROKE">Backstroke</MenuItem>
              <MenuItem value="BREASTSTROKE">Breaststroke</MenuItem>
              <MenuItem value="BUTTERFLY">Butterfly</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            name="strokeCount"
            label="Stroke Count"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.strokeCount}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Pool Type</InputLabel>
            <Select
              name="poolType"
              defaultValue={editingItem?.performanceMetrics?.poolType || ''}
            >
              <MenuItem value="INDOOR">Indoor</MenuItem>
              <MenuItem value="OUTDOOR">Outdoor</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            name="waterTemp"
            label="Water Temperature (°C)"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.waterTemp}
            margin="normal"
          />
        </>
      );
    case 'GYM':
      return (
        <>
          <TextField
            fullWidth
            name="sets"
            label="Sets"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.sets}
            margin="normal"
          />
          <TextField
            fullWidth
            name="reps"
            label="Reps"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.reps}
            margin="normal"
          />
          <TextField
            fullWidth
            name="weight"
            label="Weight (kg)"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.weight}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Exercise Type</InputLabel>
            <Select
              name="exerciseType"
              defaultValue={editingItem?.performanceMetrics?.exerciseType || ''}
            >
              <MenuItem value="STRENGTH">Strength</MenuItem>
              <MenuItem value="CARDIO">Cardio</MenuItem>
              <MenuItem value="FLEXIBILITY">Flexibility</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            name="equipment"
            label="Equipment Used"
            defaultValue={editingItem?.performanceMetrics?.equipment}
            margin="normal"
          />
          <TextField
            fullWidth
            name="restTime"
            label="Rest Time (seconds)"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.restTime}
            margin="normal"
          />
          <TextField
            fullWidth
            name="targetMuscle"
            label="Target Muscle Group"
            defaultValue={editingItem?.performanceMetrics?.targetMuscle}
            margin="normal"
          />
        </>
      );
    case 'SPORTS':
      return (
        <>
          <FormControl fullWidth margin="normal">
            <InputLabel>Sport Type</InputLabel>
            <Select
              name="sportType"
              defaultValue={editingItem?.performanceMetrics?.sportType || ''}
            >
              <MenuItem value="BASKETBALL">Basketball</MenuItem>
              <MenuItem value="SOCCER">Soccer</MenuItem>
              <MenuItem value="TENNIS">Tennis</MenuItem>
              <MenuItem value="VOLLEYBALL">Volleyball</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            name="score"
            label="Score"
            defaultValue={editingItem?.performanceMetrics?.score}
            margin="normal"
          />
          <TextField
            fullWidth
            name="opponent"
            label="Opponent"
            defaultValue={editingItem?.performanceMetrics?.opponent}
            margin="normal"
          />
          <TextField
            fullWidth
            name="position"
            label="Position"
            defaultValue={editingItem?.performanceMetrics?.position}
            margin="normal"
          />
          <TextField
            fullWidth
            name="gameDuration"
            label="Game Duration (minutes)"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.gameDuration}
            margin="normal"
          />
          <TextField
            fullWidth
            name="pointsScored"
            label="Points Scored"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.pointsScored}
            margin="normal"
          />
          <TextField
            fullWidth
            name="assists"
            label="Assists"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.assists}
            margin="normal"
          />
          <TextField
            fullWidth
            name="rebounds"
            label="Rebounds"
            type="number"
            defaultValue={editingItem?.performanceMetrics?.rebounds}
            margin="normal"
          />
        </>
      );
    default:
      return null;
  }
};

const getChartData = (metrics: ActivityMetrics, activities: Activity[]): ChartData => {
  const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  
  // Calculate calories burned by activity type
  const caloriesByType = activities.reduce((acc, activity) => {
    acc[activity.type] = (acc[activity.type] || 0) + activity.caloriesBurned;
    return acc;
  }, {} as Record<string, number>);

  // Calculate intensity distribution
  const intensityDistribution = activities.reduce((acc, activity) => {
    acc[activity.intensity] = (acc[activity.intensity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Calculate daily durations
  const dailyDurations = activities.reduce((acc, activity) => {
    const day = new Date(activity.date).getDay();
    acc[day] = (acc[day] || 0) + activity.duration;
    return acc;
  }, {} as Record<number, number>);

  return {
    lineData: {
      labels,
      datasets: [
        {
          label: 'Duration (minutes)',
          data: labels.map((_, i) => dailyDurations[i] || 0),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.5)',
          tension: 0.1,
          pointRadius: 5,
          pointHoverRadius: 8,
        },
      ],
    },
    barData: {
      labels: Object.keys(caloriesByType),
      datasets: [
        {
          label: 'Calories Burned',
          data: Object.values(caloriesByType),
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
          ],
          borderWidth: 1,
        },
      ],
    },
    caloriesData: {
      labels: Object.keys(caloriesByType),
      datasets: [
        {
          label: 'Calories Burned',
          data: Object.values(caloriesByType),
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
          ],
          borderWidth: 1,
        },
      ],
    },
    intensityData: {
      labels: Object.keys(intensityDistribution),
      datasets: [
        {
          label: 'Intensity Distribution',
          data: Object.values(intensityDistribution),
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
          ],
          borderWidth: 1,
        },
      ],
    },
  };
};

const exportActivities = (activities: Activity[], format: ExportFormat): void => {
  const headers = [
    'Type',
    'Date',
    'Duration (minutes)',
    'Calories Burned',
    'Intensity',
    'Notes',
  ];

  const rows = activities.map(activity => [
    activity.type,
    activity.date,
    activity.duration,
    activity.caloriesBurned,
    activity.intensity,
    activity.notes || '',
  ]);

  switch (format) {
    case 'CSV': {
      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
      ].join('\n');
      downloadFile(csvContent, 'text/csv', 'activities.csv');
      break;
    }
    case 'JSON': {
      const jsonContent = JSON.stringify(activities, null, 2);
      downloadFile(jsonContent, 'application/json', 'activities.json');
      break;
    }
    case 'EXCEL': {
      const worksheet = XLSX.utils.aoa_to_sheet([headers, ...rows]);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Activities');
      XLSX.writeFile(workbook, 'activities.xlsx');
      break;
    }
  }
};

const downloadFile = (content: string, mimeType: string, filename: string) => {
  const blob = new Blob([content], { type: `${mimeType};charset=utf-8;` });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const ActivityPanel: React.FC = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [metrics, setMetrics] = useState<ActivityMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState<Activity | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'duration' | 'calories'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [filterType, setFilterType] = useState<Activity['type'] | 'ALL'>('ALL');
  const [exportMenuAnchor, setExportMenuAnchor] = useState<null | HTMLElement>(null);

  const filteredAndSortedActivities = activities
    .filter(activity => {
      const matchesSearch = activity.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        activity.notes?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesType = filterType === 'ALL' || activity.type === filterType;
      return matchesSearch && matchesType;
    })
    .sort((a, b) => {
      const multiplier = sortOrder === 'asc' ? 1 : -1;
      switch (sortBy) {
        case 'date':
          return multiplier * (new Date(a.date).getTime() - new Date(b.date).getTime());
        case 'duration':
          return multiplier * (a.duration - b.duration);
        case 'calories':
          return multiplier * (a.caloriesBurned - b.caloriesBurned);
        default:
          return 0;
      }
    });

  const fetchActivities = async () => {
    setLoading(true);
    try {
      const [activitiesRes, metricsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/activities`),
        fetch(`${API_BASE_URL}/metrics`)
      ]);

      if (!activitiesRes.ok || !metricsRes.ok) {
        throw new Error('Failed to fetch activity data');
      }

      const [activitiesData, metricsData] = await Promise.all([
        activitiesRes.json(),
        metricsRes.json()
      ]);

      setActivities(activitiesData);
      setMetrics(metricsData);
    } catch (err) {
      setError('Failed to fetch activity data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddActivity = async (activity: Activity) => {
    try {
      const response = await fetch(`${API_BASE_URL}/activities`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(activity),
      });

      if (!response.ok) {
        throw new Error('Failed to add activity');
      }

      await fetchActivities();
    } catch (err) {
      setError('Failed to add activity');
    }
  };

  const handleUpdateActivity = async (activity: Activity) => {
    try {
      const response = await fetch(`${API_BASE_URL}/activities/${activity.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(activity),
      });

      if (!response.ok) {
        throw new Error('Failed to update activity');
      }

      await fetchActivities();
    } catch (err) {
      setError('Failed to update activity');
    }
  };

  const handleDeleteActivity = async (activityId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/activities/${activityId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete activity');
      }

      await fetchActivities();
    } catch (err) {
      setError('Failed to delete activity');
    }
  };

  const handleOpenDialog = (activity?: Activity) => {
    setEditingItem(activity || null);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingItem(null);
    setFormErrors({});
  };

  const validateActivity = (activity: Activity): boolean => {
    const errors: Record<string, string> = {};
    
    if (!activity.type) errors.type = 'Activity type is required';
    if (!activity.duration || activity.duration <= 0) errors.duration = 'Duration must be greater than 0';
    if (!activity.intensity) errors.intensity = 'Intensity is required';
    if (!activity.caloriesBurned || activity.caloriesBurned <= 0) errors.caloriesBurned = 'Calories burned must be greater than 0';
    if (!activity.date) errors.date = 'Date is required';
    if (!isValid(parseISO(activity.date))) errors.date = 'Invalid date format';

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmitActivity = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    
    const activity: Activity = {
      id: editingItem?.id || 0,
      type: formData.get('type') as Activity['type'],
      duration: Number(formData.get('duration')),
      intensity: formData.get('intensity') as Activity['intensity'],
      caloriesBurned: Number(formData.get('caloriesBurned')),
      date: formData.get('date') as string,
      notes: formData.get('notes') as string,
      performanceMetrics: {
        distance: formData.get('distance') ? Number(formData.get('distance')) : undefined,
        laps: formData.get('laps') ? Number(formData.get('laps')) : undefined,
        sets: formData.get('sets') ? Number(formData.get('sets')) : undefined,
        reps: formData.get('reps') ? Number(formData.get('reps')) : undefined,
        heartRate: formData.get('heartRate') ? Number(formData.get('heartRate')) : undefined,
        pace: formData.get('pace') ? Number(formData.get('pace')) : undefined,
        elevationGain: formData.get('elevationGain') ? Number(formData.get('elevationGain')) : undefined,
        poolLength: formData.get('poolLength') ? Number(formData.get('poolLength')) : undefined,
        strokeType: formData.get('strokeType') as Activity['performanceMetrics']['strokeType'],
        weight: formData.get('weight') ? Number(formData.get('weight')) : undefined,
        exerciseType: formData.get('exerciseType') as Activity['performanceMetrics']['exerciseType'],
        sportType: formData.get('sportType') as Activity['performanceMetrics']['sportType'],
        score: formData.get('score') as string,
        opponent: formData.get('opponent') as string,
      },
    };

    if (!validateActivity(activity)) return;

    try {
      if (editingItem) {
        await handleUpdateActivity(activity);
      } else {
        await handleAddActivity(activity);
      }
      handleCloseDialog();
    } catch (err) {
      setError('Failed to save activity');
    }
  };

  const getActivitySpecificMetrics = (activity: Activity) => {
    switch (activity.type) {
      case 'RUNNING':
        return [
          { label: 'Distance', value: `${activity.performanceMetrics.distance} km` },
          { label: 'Pace', value: `${activity.performanceMetrics.pace} min/km` },
          { label: 'Elevation', value: `${activity.performanceMetrics.elevationGain} m` },
        ];
      case 'SWIMMING':
        return [
          { label: 'Laps', value: activity.performanceMetrics.laps },
          { label: 'Pool Length', value: `${activity.performanceMetrics.poolLength} m` },
          { label: 'Stroke', value: activity.performanceMetrics.strokeType },
        ];
      case 'GYM':
        return [
          { label: 'Sets', value: activity.performanceMetrics.sets },
          { label: 'Reps', value: activity.performanceMetrics.reps },
          { label: 'Weight', value: `${activity.performanceMetrics.weight} kg` },
          { label: 'Type', value: activity.performanceMetrics.exerciseType },
        ];
      case 'SPORTS':
        return [
          { label: 'Sport', value: activity.performanceMetrics.sportType },
          { label: 'Score', value: activity.performanceMetrics.score },
          { label: 'Opponent', value: activity.performanceMetrics.opponent },
        ];
      default:
        return [];
    }
  };

  const handleExportClick = (event: React.MouseEvent<HTMLElement>) => {
    setExportMenuAnchor(event.currentTarget);
  };

  const handleExportClose = () => {
    setExportMenuAnchor(null);
  };

  const handleExport = (format: ExportFormat): void => {
    exportActivities(activities, format);
    handleExportClose();
  };

  useEffect(() => {
    fetchActivities();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert 
        severity="error" 
        sx={{ mt: 2 }}
        action={
          <Button 
            color="inherit" 
            size="small"
            onClick={() => {
              setError(null);
              fetchActivities();
            }}
          >
            Retry
          </Button>
        }
      >
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={selectedTab} onChange={(_, newValue) => setSelectedTab(newValue)}>
          <Tab label="Activities" icon={<RunIcon />} />
          <Tab label="Metrics" icon={<FitnessCenterIcon />} />
        </Tabs>
      </Box>

      <Box sx={{ p: 3 }}>
        {selectedTab === 0 && (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">Activities</Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        variant="outlined"
                        startIcon={<DownloadIcon />}
                        onClick={handleExportClick}
                        id="export-button"
                      >
                        Export
                      </Button>
                      <Menu
                        anchorEl={exportMenuAnchor}
                        open={Boolean(exportMenuAnchor)}
                        onClose={handleExportClose}
                      >
                        <MenuItem onClick={() => handleExport('CSV')}>Export as CSV</MenuItem>
                        <MenuItem onClick={() => handleExport('JSON')}>Export as JSON</MenuItem>
                        <MenuItem onClick={() => handleExport('EXCEL')}>Export as Excel</MenuItem>
                      </Menu>
                      <Button
                        variant="contained"
                        startIcon={<AddIcon />}
                        onClick={() => handleOpenDialog()}
                      >
                        Add Activity
                      </Button>
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                    <TextField
                      placeholder="Search activities..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <SearchIcon />
                          </InputAdornment>
                        ),
                      }}
                      sx={{ flex: 1 }}
                    />
                    
                    <FormControl sx={{ minWidth: 120 }}>
                      <InputLabel>Filter by Type</InputLabel>
                      <Select
                        value={filterType}
                        onChange={(e) => setFilterType(e.target.value as Activity['type'] | 'ALL')}
                        label="Filter by Type"
                      >
                        <MenuItem value="ALL">All Types</MenuItem>
                        <MenuItem value="RUNNING">Running</MenuItem>
                        <MenuItem value="SWIMMING">Swimming</MenuItem>
                        <MenuItem value="GYM">Gym</MenuItem>
                        <MenuItem value="SPORTS">Sports</MenuItem>
                        <MenuItem value="OTHER">Other</MenuItem>
                      </Select>
                    </FormControl>

                    <FormControl sx={{ minWidth: 120 }}>
                      <InputLabel>Sort by</InputLabel>
                      <Select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value as 'date' | 'duration' | 'calories')}
                        label="Sort by"
                      >
                        <MenuItem value="date">Date</MenuItem>
                        <MenuItem value="duration">Duration</MenuItem>
                        <MenuItem value="calories">Calories</MenuItem>
                      </Select>
                    </FormControl>

                    <IconButton
                      onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                      color="primary"
                    >
                      <SortIcon />
                    </IconButton>
                  </Box>

                  <List>
                    {filteredAndSortedActivities.map((activity) => (
                      <React.Fragment key={activity.id}>
                        <ListItem>
                          <ListItemText
                            primary={activity.type}
                            secondary={
                              <Box>
                                <Typography variant="body2">
                                  {format(parseISO(activity.date), 'PPP')} - {activity.duration} minutes
                                </Typography>
                                {getActivitySpecificMetrics(activity).map((metric, index) => (
                                  <Typography key={index} variant="body2" color="text.secondary">
                                    {metric.label}: {metric.value}
                                  </Typography>
                                ))}
                              </Box>
                            }
                          />
                          <ListItemSecondaryAction>
                            <MuiTooltip title="Edit activity">
                              <IconButton edge="end" onClick={() => handleOpenDialog(activity)}>
                                <EditIcon />
                              </IconButton>
                            </MuiTooltip>
                            <MuiTooltip title="Delete activity">
                              <IconButton edge="end" onClick={() => handleDeleteActivity(activity.id)}>
                                <DeleteIcon />
                              </IconButton>
                            </MuiTooltip>
                          </ListItemSecondaryAction>
                        </ListItem>
                        <Divider />
                      </React.Fragment>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {selectedTab === 1 && metrics && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Activity Summary</Typography>
                  <Typography>Total Duration: {metrics.totalDuration} minutes</Typography>
                  <Typography>Total Calories: {metrics.totalCalories} kcal</Typography>
                  <Typography>Weekly Average: {metrics.weeklyAverage} minutes</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Activity Distribution</Typography>
                  <Box sx={{ height: 300 }}>
                    <Pie
                      data={getChartData(metrics, activities).barData}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          tooltip: {
                            callbacks: {
                              label: (context) => {
                                const label = context.label || '';
                                const value = context.raw as number;
                                const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} activities (${percentage}%)`;
                              },
                            },
                          },
                        },
                        onClick: (event, elements) => {
                          if (elements.length > 0) {
                            const index = elements[0].index;
                            const type = Object.keys(metrics.activitiesByType)[index];
                            setFilterType(type as Activity['type']);
                            setSelectedTab(0);
                          }
                        },
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Calories Burned by Activity Type</Typography>
                  <Box sx={{ height: 300 }}>
                    <Bar
                      data={getChartData(metrics, activities).caloriesData}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                          y: {
                            beginAtZero: true,
                            title: {
                              display: true,
                              text: 'Calories Burned',
                            },
                          },
                        },
                        plugins: {
                          tooltip: {
                            callbacks: {
                              label: (context) => {
                                const label = context.dataset.label || '';
                                const value = context.raw as number;
                                return `${label}: ${value} kcal`;
                              },
                            },
                          },
                        },
                        onClick: (event, elements) => {
                          if (elements.length > 0) {
                            const index = elements[0].index;
                            const type = Object.keys(caloriesByType)[index];
                            setFilterType(type as Activity['type']);
                            setSelectedTab(0);
                          }
                        },
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Activity Intensity Distribution</Typography>
                  <Box sx={{ height: 300 }}>
                    <Pie
                      data={getChartData(metrics, activities).intensityData}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          tooltip: {
                            callbacks: {
                              label: (context) => {
                                const label = context.label || '';
                                const value = context.raw as number;
                                const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} activities (${percentage}%)`;
                              },
                            },
                          },
                        },
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Weekly Activity Trend</Typography>
                  <Box sx={{ height: 300 }}>
                    <Line
                      data={getChartData(metrics, activities).lineData}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                          y: {
                            beginAtZero: true,
                            title: {
                              display: true,
                              text: 'Duration (minutes)',
                            },
                          },
                        },
                        plugins: {
                          tooltip: {
                            callbacks: {
                              label: (context) => {
                                const label = context.dataset.label || '';
                                const value = context.raw as number;
                                return `${label}: ${value} minutes`;
                              },
                            },
                          },
                          // @ts-ignore - Type mismatch between Chart.js v4 and type definitions
                          zoom: {
                            zoom: {
                              wheel: { enabled: true },
                              pinch: { enabled: true },
                              mode: 'xy',
                            },
                            pan: {
                              enabled: true,
                              mode: 'xy',
                            },
                          },
                        },
                      } as ChartOptions<'line'>}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </Box>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmitActivity}>
          <DialogTitle>
            {editingItem ? 'Edit Activity' : 'Add Activity'}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              <FormControl fullWidth margin="normal" required error={!!formErrors.type}>
                <InputLabel>Activity Type</InputLabel>
                <Select
                  name="type"
                  defaultValue={editingItem?.type || ''}
                >
                  <MenuItem value="RUNNING">Running</MenuItem>
                  <MenuItem value="SWIMMING">Swimming</MenuItem>
                  <MenuItem value="GYM">Gym</MenuItem>
                  <MenuItem value="SPORTS">Sports</MenuItem>
                  <MenuItem value="OTHER">Other</MenuItem>
                </Select>
                {formErrors.type && <FormHelperText>{formErrors.type}</FormHelperText>}
              </FormControl>

              <TextField
                fullWidth
                name="duration"
                label="Duration (minutes)"
                type="number"
                defaultValue={editingItem?.duration}
                margin="normal"
                required
                error={!!formErrors.duration}
                helperText={formErrors.duration}
              />

              <FormControl fullWidth margin="normal" required error={!!formErrors.intensity}>
                <InputLabel>Intensity</InputLabel>
                <Select
                  name="intensity"
                  defaultValue={editingItem?.intensity || ''}
                >
                  <MenuItem value="LOW">Low</MenuItem>
                  <MenuItem value="MODERATE">Moderate</MenuItem>
                  <MenuItem value="HIGH">High</MenuItem>
                </Select>
                {formErrors.intensity && <FormHelperText>{formErrors.intensity}</FormHelperText>}
              </FormControl>

              <TextField
                fullWidth
                name="caloriesBurned"
                label="Calories Burned"
                type="number"
                defaultValue={editingItem?.caloriesBurned}
                margin="normal"
                required
                error={!!formErrors.caloriesBurned}
                helperText={formErrors.caloriesBurned}
              />

              <TextField
                fullWidth
                name="date"
                label="Date"
                type="date"
                defaultValue={editingItem?.date ? format(parseISO(editingItem.date), 'yyyy-MM-dd') : ''}
                margin="normal"
                required
                error={!!formErrors.date}
                helperText={formErrors.date}
                InputLabelProps={{ shrink: true }}
              />

              <TextField
                fullWidth
                name="notes"
                label="Notes"
                multiline
                rows={3}
                defaultValue={editingItem?.notes}
                margin="normal"
              />

              <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>Performance Metrics</Typography>

              <ActivityTypeSpecificFields
                type={editingItem?.type || 'RUNNING'}
                editingItem={editingItem}
              />

              <TextField
                fullWidth
                name="heartRate"
                label="Heart Rate (bpm)"
                type="number"
                defaultValue={editingItem?.performanceMetrics?.heartRate}
                margin="normal"
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button type="submit" variant="contained" color="primary">
              {editingItem ? 'Update' : 'Add'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}; 