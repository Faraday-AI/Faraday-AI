import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Paper,
  useTheme,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TimelineIcon from '@mui/icons-material/Timeline';

interface ProgressData {
  date: string;
  value: number;
  target: number;
  category: string;
}

interface Milestone {
  id: string;
  title: string;
  description: string;
  targetDate: string;
  status: 'completed' | 'in-progress' | 'upcoming';
  progress: number;
  category: string;
}

interface ProgressMetrics {
  currentValue: number;
  targetValue: number;
  progressPercentage: number;
  trend: 'up' | 'down' | 'stable';
  lastUpdated: string;
}

const ProgressPanel: React.FC = () => {
  const theme = useTheme();
  const [progressData, setProgressData] = useState<ProgressData[]>([]);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [timeRange, setTimeRange] = useState<string>('3m');
  const [activeTab, setActiveTab] = useState(0);

  const categories = useMemo(() => ['all', 'fitness', 'nutrition', 'health'], []);

  useEffect(() => {
    const fetchProgressData = async () => {
      try {
        // Simulated data with more comprehensive metrics
        const mockData: ProgressData[] = [
          { date: '2024-01', value: 65, target: 80, category: 'fitness' },
          { date: '2024-02', value: 75, target: 80, category: 'fitness' },
          { date: '2024-03', value: 80, target: 80, category: 'fitness' },
          { date: '2024-04', value: 85, target: 80, category: 'fitness' },
          { date: '2024-01', value: 70, target: 90, category: 'nutrition' },
          { date: '2024-02', value: 80, target: 90, category: 'nutrition' },
          { date: '2024-03', value: 85, target: 90, category: 'nutrition' },
          { date: '2024-04', value: 88, target: 90, category: 'nutrition' },
        ];

        const mockMilestones: Milestone[] = [
          {
            id: '1',
            title: 'First 5K Run',
            description: 'Complete a 5K run without stopping',
            targetDate: '2024-06-01',
            status: 'in-progress',
            progress: 75,
            category: 'fitness',
          },
          {
            id: '2',
            title: 'Weight Loss Goal',
            description: 'Lose 10 pounds',
            targetDate: '2024-07-01',
            status: 'upcoming',
            progress: 30,
            category: 'nutrition',
          },
          {
            id: '3',
            title: 'Flexibility Target',
            description: 'Achieve full range of motion',
            targetDate: '2024-08-01',
            status: 'in-progress',
            progress: 60,
            category: 'health',
          },
        ];

        setProgressData(mockData);
        setMilestones(mockMilestones);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching progress data:', error);
        setLoading(false);
      }
    };

    fetchProgressData();
  }, []);

  const filteredData = useMemo(() => {
    return progressData.filter(
      (item) => selectedCategory === 'all' || item.category === selectedCategory
    );
  }, [progressData, selectedCategory]);

  const filteredMilestones = useMemo(() => {
    return milestones.filter(
      (milestone) => selectedCategory === 'all' || milestone.category === selectedCategory
    );
  }, [milestones, selectedCategory]);

  const calculateMetrics = useMemo(() => {
    if (filteredData.length === 0) return null;

    const latestData = filteredData[filteredData.length - 1];
    const previousData = filteredData[filteredData.length - 2];

    const metrics: ProgressMetrics = {
      currentValue: latestData.value,
      targetValue: latestData.target,
      progressPercentage: (latestData.value / latestData.target) * 100,
      trend: previousData
        ? latestData.value > previousData.value
          ? 'up'
          : latestData.value < previousData.value
          ? 'down'
          : 'stable'
        : 'stable',
      lastUpdated: latestData.date,
    };

    return metrics;
  }, [filteredData]);

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Controls */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Category</InputLabel>
                    <Select
                      value={selectedCategory}
                      onChange={(e) => setSelectedCategory(e.target.value)}
                      label="Category"
                    >
                      {categories.map((category) => (
                        <MenuItem key={category} value={category}>
                          {category.charAt(0).toUpperCase() + category.slice(1)}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Time Range</InputLabel>
                    <Select
                      value={timeRange}
                      onChange={(e) => setTimeRange(e.target.value)}
                      label="Time Range"
                    >
                      <MenuItem value="1m">Last Month</MenuItem>
                      <MenuItem value="3m">Last 3 Months</MenuItem>
                      <MenuItem value="6m">Last 6 Months</MenuItem>
                      <MenuItem value="1y">Last Year</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Progress Overview */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
                  <Tab label="Progress" icon={<TimelineIcon />} />
                  <Tab label="Targets" icon={<TrendingUpIcon />} />
                </Tabs>
              </Box>

              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  {activeTab === 0 ? (
                    <AreaChart data={filteredData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="value"
                        stroke={theme.palette.primary.main}
                        fill={theme.palette.primary.light}
                        fillOpacity={0.3}
                      />
                      <Line
                        type="monotone"
                        dataKey="target"
                        stroke={theme.palette.secondary.main}
                        strokeDasharray="5 5"
                      />
                    </AreaChart>
                  ) : (
                    <LineChart data={filteredData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke={theme.palette.primary.main}
                        activeDot={{ r: 8 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="target"
                        stroke={theme.palette.secondary.main}
                        strokeDasharray="5 5"
                      />
                    </LineChart>
                  )}
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Metrics and Milestones */}
        <Grid item xs={12} md={4}>
          <Grid container spacing={3}>
            {/* Metrics Card */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Current Progress
                  </Typography>
                  {calculateMetrics && (
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Typography variant="h4" sx={{ mr: 1 }}>
                          {calculateMetrics.currentValue}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          / {calculateMetrics.targetValue}
                        </Typography>
                        <Box sx={{ ml: 'auto' }}>
                          {calculateMetrics.trend === 'up' ? (
                            <TrendingUpIcon color="success" />
                          ) : calculateMetrics.trend === 'down' ? (
                            <TrendingDownIcon color="error" />
                          ) : null}
                        </Box>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={calculateMetrics.progressPercentage}
                        sx={{ height: 10, borderRadius: 5 }}
                      />
                      <Typography variant="caption" color="text.secondary">
                        Last updated: {calculateMetrics.lastUpdated}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Milestones Card */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Milestones
                  </Typography>
                  {filteredMilestones.map((milestone) => (
                    <Paper
                      key={milestone.id}
                      sx={{
                        p: 2,
                        mb: 2,
                        backgroundColor:
                          milestone.status === 'completed'
                            ? theme.palette.success.light
                            : milestone.status === 'in-progress'
                            ? theme.palette.warning.light
                            : theme.palette.grey[100],
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                          {milestone.title}
                        </Typography>
                        <Chip
                          label={milestone.status}
                          size="small"
                          color={
                            milestone.status === 'completed'
                              ? 'success'
                              : milestone.status === 'in-progress'
                              ? 'warning'
                              : 'default'
                          }
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {milestone.description}
                      </Typography>
                      <Box sx={{ mb: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={milestone.progress}
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                      <Typography variant="caption" display="block">
                        Target: {new Date(milestone.targetDate).toLocaleDateString()}
                      </Typography>
                    </Paper>
                  ))}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ProgressPanel; 