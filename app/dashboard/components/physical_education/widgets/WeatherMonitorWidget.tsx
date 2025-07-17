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
  Switch,
  FormControlLabel,
  CircularProgress,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  WbSunny as SunIcon,
  Opacity as HumidityIcon,
  Air as WindIcon,
  Thermostat as TempIcon,
  Warning as AlertIcon,
  Refresh as RefreshIcon,
  LocationOn as LocationIcon,
  WaterDrop as RainIcon,
  Visibility as VisibilityIcon,
  Check as CheckIcon,
  Block as BlockIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer } from 'recharts';

interface WeatherData {
  temperature: number;
  feelsLike: number;
  humidity: number;
  windSpeed: number;
  visibility: number;
  precipitation: number;
  condition: string;
  icon: string;
  timestamp: string;
}

interface ActivityRecommendation {
  activity: string;
  suitable: boolean;
  reason: string;
  safetyTips: string[];
}

interface WeatherAlert {
  type: 'warning' | 'advisory' | 'watch';
  title: string;
  description: string;
  timestamp: string;
}

const MOCK_WEATHER_DATA: WeatherData[] = [
  {
    temperature: 22,
    feelsLike: 23,
    humidity: 65,
    windSpeed: 10,
    visibility: 10000,
    precipitation: 0,
    condition: 'Clear',
    icon: 'clear_day',
    timestamp: new Date().toISOString(),
  },
];

const OUTDOOR_ACTIVITIES = [
  'Running/Jogging',
  'Team Sports',
  'Field Activities',
  'Track Events',
  'Outdoor Training',
];

const WEATHER_THRESHOLDS = {
  temperature: {
    min: 10,
    max: 35,
  },
  windSpeed: {
    max: 30,
  },
  visibility: {
    min: 5000,
  },
  precipitation: {
    max: 5,
  },
};

export const WeatherMonitorWidget: React.FC = () => {
  const [currentWeather, setCurrentWeather] = useState<WeatherData>(MOCK_WEATHER_DATA[0]);
  const [weatherHistory, setWeatherHistory] = useState<WeatherData[]>(MOCK_WEATHER_DATA);
  const [alerts, setAlerts] = useState<WeatherAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [location, setLocation] = useState<string>('Current Location');

  useEffect(() => {
    fetchWeatherData();
    if (autoRefresh) {
      const interval = setInterval(fetchWeatherData, 300000); // Refresh every 5 minutes
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const fetchWeatherData = async () => {
    setLoading(true);
    try {
      // Simulated API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data update
      const newData: WeatherData = {
        ...MOCK_WEATHER_DATA[0],
        temperature: 20 + Math.random() * 5,
        windSpeed: 5 + Math.random() * 10,
        timestamp: new Date().toISOString(),
      };
      
      setCurrentWeather(newData);
      setWeatherHistory(prev => [...prev, newData].slice(-24)); // Keep last 24 records
      
      // Generate mock alerts based on conditions
      const newAlerts: WeatherAlert[] = [];
      if (newData.temperature > WEATHER_THRESHOLDS.temperature.max) {
        newAlerts.push({
          type: 'warning',
          title: 'High Temperature Alert',
          description: 'Temperature exceeds safe threshold for outdoor activities',
          timestamp: new Date().toISOString(),
        });
      }
      setAlerts(newAlerts);
      
      setError(null);
    } catch (err) {
      setError('Failed to fetch weather data');
    } finally {
      setLoading(false);
    }
  };

  const getActivityRecommendations = (): ActivityRecommendation[] => {
    return OUTDOOR_ACTIVITIES.map(activity => {
      const suitable = 
        currentWeather.temperature >= WEATHER_THRESHOLDS.temperature.min &&
        currentWeather.temperature <= WEATHER_THRESHOLDS.temperature.max &&
        currentWeather.windSpeed <= WEATHER_THRESHOLDS.windSpeed.max &&
        currentWeather.visibility >= WEATHER_THRESHOLDS.visibility.min &&
        currentWeather.precipitation <= WEATHER_THRESHOLDS.precipitation.max;

      let reason = suitable ? 'Weather conditions are favorable' : 'Weather conditions are unfavorable';
      const safetyTips = [];

      if (currentWeather.temperature > 30) {
        safetyTips.push('Ensure proper hydration');
        safetyTips.push('Take regular breaks');
      }
      if (currentWeather.windSpeed > 20) {
        safetyTips.push('Be cautious of strong winds');
      }
      if (currentWeather.precipitation > 0) {
        safetyTips.push('Watch for slippery surfaces');
      }

      return {
        activity,
        suitable,
        reason,
        safetyTips,
      };
    });
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" alignItems="center" gap={1}>
              <Typography variant="h6">Weather Monitor</Typography>
              <Chip
                icon={<LocationIcon />}
                label={location}
                variant="outlined"
                size="small"
              />
            </Box>
            <Box display="flex" alignItems="center" gap={2}>
              <FormControlLabel
                control={
                  <Switch
                    checked={autoRefresh}
                    onChange={(e) => setAutoRefresh(e.target.checked)}
                  />
                }
                label="Auto-refresh"
              />
              <Tooltip title="Refresh">
                <IconButton onClick={fetchWeatherData} disabled={loading}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Current Conditions */}
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Current Conditions
                </Typography>
                {loading ? (
                  <Box display="flex" justifyContent="center" p={2}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box display="flex" alignItems="center" gap={1}>
                        <TempIcon />
                        <Typography>
                          {currentWeather.temperature.toFixed(1)}°C
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box display="flex" alignItems="center" gap={1}>
                        <HumidityIcon />
                        <Typography>{currentWeather.humidity}%</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box display="flex" alignItems="center" gap={1}>
                        <WindIcon />
                        <Typography>{currentWeather.windSpeed} km/h</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box display="flex" alignItems="center" gap={1}>
                        <RainIcon />
                        <Typography>{currentWeather.precipitation} mm</Typography>
                      </Box>
                    </Grid>
                  </Grid>
                )}
              </Paper>
            </Grid>

            {/* Temperature Trend */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Temperature Trend
                </Typography>
                <Box height={200}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={weatherHistory}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timestamp"
                        tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                      />
                      <YAxis domain={['auto', 'auto']} />
                      <ChartTooltip />
                      <Line
                        type="monotone"
                        dataKey="temperature"
                        stroke="#2196F3"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </Paper>
            </Grid>
          </Grid>

          {/* Alerts */}
          {alerts.length > 0 && (
            <Paper sx={{ p: 2, bgcolor: 'error.light' }}>
              <Typography variant="subtitle1" color="error.contrastText" gutterBottom>
                Weather Alerts
              </Typography>
              <List dense>
                {alerts.map((alert, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <AlertIcon color="error" />
                    </ListItemIcon>
                    <ListItemText
                      primary={alert.title}
                      secondary={alert.description}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}

          {/* Activity Recommendations */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Activity Recommendations
            </Typography>
            <List>
              {getActivityRecommendations().map((rec, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    {rec.suitable ? (
                      <CheckIcon color="success" />
                    ) : (
                      <BlockIcon color="error" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={rec.activity}
                    secondary={
                      <>
                        {rec.reason}
                        {rec.safetyTips.length > 0 && (
                          <Typography variant="body2" color="text.secondary">
                            Safety Tips: {rec.safetyTips.join(', ')}
                          </Typography>
                        )}
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Box>
      </CardContent>
    </Card>
  );
}; 