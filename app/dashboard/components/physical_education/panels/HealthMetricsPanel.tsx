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
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Favorite as HeartIcon,
  DirectionsRun as ActivityIcon,
  Restaurant as NutritionIcon,
  Accessibility as FlexibilityIcon,
  Timer as EnduranceIcon,
  Scale as WeightIcon,
  Height as HeightIcon,
  Straighten as PostureIcon,
  MonitorHeart as VitalsIcon,
  LocalHospital as HealthIcon,
  Notifications as AlertIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  ComposedChart,
  Bar,
} from 'recharts';

interface HealthMetric {
  id: number;
  metricType: string;
  value: number;
  unit: string;
  timestamp: string;
  isAbnormal: boolean;
  notes?: string;
  relatedMetrics?: string[];
  source?: 'MANUAL' | 'DEVICE' | 'CALCULATED';
}

interface HealthAlert {
  id: number;
  metricType: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  message: string;
  timestamp: string;
  recommendation: string;
  isAcknowledged: boolean;
}

interface MetricAnalysis {
  metricType: string;
  currentValue: number;
  previousValue: number;
  trend: 'IMPROVING' | 'DECLINING' | 'STABLE';
  percentageChange: number;
  recommendations: string[];
  relatedMetrics: Array<{
    type: string;
    correlation: number;
  }>;
}

interface VitalSigns {
  bloodPressure: {
    systolic: number;
    diastolic: number;
    timestamp: string;
  };
  heartRate: number;
  respiratoryRate: number;
  temperature: number;
  oxygenSaturation: number;
  timestamp: string;
}

interface BodyComposition {
  weight: number;
  height: number;
  bmi: number;
  bodyFat: number;
  muscleMass: number;
  boneDensity: number;
  hydration: number;
  timestamp: string;
}

export const HealthMetricsPanel: React.FC = () => {
  const [metrics, setMetrics] = useState<HealthMetric[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedMetricType, setSelectedMetricType] = useState('HEART_RATE');
  const [newMetricValue, setNewMetricValue] = useState('');
  const [timeRange, setTimeRange] = useState('1W');

  const metricTypes = [
    { value: 'HEART_RATE', label: 'Heart Rate', unit: 'bpm' },
    { value: 'RESPIRATORY_RATE', label: 'Respiratory Rate', unit: 'breaths/min' },
    { value: 'FLEXIBILITY', label: 'Flexibility', unit: 'cm' },
    { value: 'ENDURANCE', label: 'Endurance', unit: 'minutes' },
  ];

  const timeRanges = [
    { value: '1D', label: 'Last 24 Hours' },
    { value: '1W', label: 'Last Week' },
    { value: '1M', label: 'Last Month' },
    { value: '3M', label: 'Last 3 Months' },
    { value: '6M', label: 'Last 6 Months' },
    { value: '1Y', label: 'Last Year' },
  ];

  useEffect(() => {
    fetchMetrics();
  }, [selectedMetricType, timeRange]);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `/api/v1/physical-education/health-fitness/students/1/health-metrics?` +
        `metric_type=${selectedMetricType}&timeframe=${timeRange}`
      );
      if (!response.ok) throw new Error('Failed to fetch metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleAddMetric = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        '/api/v1/physical-education/health-fitness/students/1/health-metrics',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            metric_type: selectedMetricType,
            value: parseFloat(newMetricValue),
            unit: metricTypes.find(m => m.value === selectedMetricType)?.unit,
          }),
        }
      );
      if (!response.ok) throw new Error('Failed to add metric');
      setNewMetricValue('');
      fetchMetrics();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getMetricStats = () => {
    if (!metrics.length) return { avg: 0, min: 0, max: 0 };
    const values = metrics.map(m => m.value);
    return {
      avg: values.reduce((a, b) => a + b, 0) / values.length,
      min: Math.min(...values),
      max: Math.max(...values),
    };
  };

  const stats = getMetricStats();

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Metric Type</InputLabel>
            <Select
              value={selectedMetricType}
              label="Metric Type"
              onChange={(e) => setSelectedMetricType(e.target.value)}
            >
              {metricTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              {timeRanges.map((range) => (
                <MenuItem key={range.value} value={range.value}>
                  {range.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <IconButton onClick={fetchMetrics} color="primary">
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
              {metricTypes.find(m => m.value === selectedMetricType)?.label} History
            </Typography>
            <Box sx={{ height: 400, position: 'relative' }}>
              {loading ? (
                <Box
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <CircularProgress />
                </Box>
              ) : (
                <ResponsiveContainer>
                  <LineChart data={metrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="timestamp"
                      tickFormatter={(timestamp) => new Date(timestamp).toLocaleDateString()}
                    />
                    <YAxis />
                    <Tooltip
                      labelFormatter={(timestamp) => new Date(timestamp).toLocaleString()}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#8884d8"
                      name={metricTypes.find(m => m.value === selectedMetricType)?.label}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Add New Measurement
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
                  <TextField
                    label="Value"
                    type="number"
                    value={newMetricValue}
                    onChange={(e) => setNewMetricValue(e.target.value)}
                    sx={{ flex: 1 }}
                  />
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleAddMetric}
                    disabled={loading || !newMetricValue}
                  >
                    Add
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Statistics
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Average
                    </Typography>
                    <Typography variant="h6">
                      {stats.avg.toFixed(1)}
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Minimum
                    </Typography>
                    <Typography variant="h6">
                      {stats.min.toFixed(1)}
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Maximum
                    </Typography>
                    <Typography variant="h6">
                      {stats.max.toFixed(1)}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
}; 