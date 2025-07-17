import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Slider,
  Grid,
  Chip,
  LinearProgress,
  Alert,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Favorite as HeartIcon,
  Timer as TimerIcon,
  TrendingUp as TrendingIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface HeartRateData {
  timestamp: number;
  bpm: number;
}

interface HeartRateZone {
  name: string;
  min: number;
  max: number;
  color: string;
  description: string;
}

const HEART_RATE_ZONES: HeartRateZone[] = [
  {
    name: 'Resting',
    min: 40,
    max: 60,
    color: '#4CAF50',
    description: 'Resting heart rate zone',
  },
  {
    name: 'Light',
    min: 60,
    max: 70,
    color: '#2196F3',
    description: 'Light exercise zone',
  },
  {
    name: 'Moderate',
    min: 70,
    max: 80,
    color: '#FFC107',
    description: 'Moderate exercise zone',
  },
  {
    name: 'Vigorous',
    min: 80,
    max: 90,
    color: '#FF9800',
    description: 'Vigorous exercise zone',
  },
  {
    name: 'Maximum',
    min: 90,
    max: 100,
    color: '#F44336',
    description: 'Maximum effort zone',
  },
];

export const HeartRateMonitorWidget: React.FC = () => {
  const [heartRate, setHeartRate] = useState<number>(0);
  const [heartRateData, setHeartRateData] = useState<HeartRateData[]>([]);
  const [isMonitoring, setIsMonitoring] = useState<boolean>(false);
  const [targetZone, setTargetZone] = useState<HeartRateZone>(HEART_RATE_ZONES[2]);
  const [error, setError] = useState<string | null>(null);
  const [maxHeartRate, setMaxHeartRate] = useState<number>(220);
  const [age, setAge] = useState<number>(30);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isMonitoring) {
      interval = setInterval(() => {
        // Simulate heart rate data (replace with actual device data)
        const simulatedBPM = Math.floor(
          targetZone.min + Math.random() * (targetZone.max - targetZone.min)
        );
        
        setHeartRate(simulatedBPM);
        setHeartRateData(prev => [
          ...prev,
          { timestamp: Date.now(), bpm: simulatedBPM },
        ].slice(-60)); // Keep last 60 data points
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [isMonitoring, targetZone]);

  useEffect(() => {
    // Calculate max heart rate based on age
    setMaxHeartRate(220 - age);
  }, [age]);

  const getCurrentZone = (bpm: number): HeartRateZone => {
    return HEART_RATE_ZONES.find(zone => bpm >= zone.min && bpm <= zone.max) || HEART_RATE_ZONES[0];
  };

  const getZonePercentage = (bpm: number): number => {
    return (bpm / maxHeartRate) * 100;
  };

  const getRecommendation = (bpm: number): string => {
    const zone = getCurrentZone(bpm);
    if (bpm < targetZone.min) {
      return 'Increase intensity to reach target zone';
    } else if (bpm > targetZone.max) {
      return 'Reduce intensity to stay in target zone';
    }
    return `Maintain current intensity (${zone.name} zone)`;
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          <Typography variant="h6">Heart Rate Monitor</Typography>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Age Input */}
          <Box>
            <Typography gutterBottom>Age: {age}</Typography>
            <Slider
              value={age}
              onChange={(_, value) => setAge(value as number)}
              min={10}
              max={100}
              step={1}
              marks
            />
          </Box>

          {/* Heart Rate Display */}
          <Box textAlign="center" py={2}>
            <Typography variant="h2" color="error">
              {isMonitoring ? heartRate : '--'}
              <Typography variant="caption" color="text.secondary">
                {' '}BPM
              </Typography>
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Max Heart Rate: {maxHeartRate} BPM
            </Typography>
          </Box>

          {/* Progress Bar */}
          <Box>
            <LinearProgress
              variant="determinate"
              value={getZonePercentage(heartRate)}
              sx={{
                height: 20,
                borderRadius: 1,
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getCurrentZone(heartRate).color,
                },
              }}
            />
            <Box display="flex" justifyContent="space-between" mt={1}>
              {HEART_RATE_ZONES.map(zone => (
                <Tooltip key={zone.name} title={zone.description}>
                  <Chip
                    size="small"
                    label={zone.name}
                    sx={{
                      backgroundColor: zone.color,
                      color: 'white',
                      opacity: heartRate >= zone.min && heartRate <= zone.max ? 1 : 0.5,
                    }}
                  />
                </Tooltip>
              ))}
            </Box>
          </Box>

          {/* Target Zone Selection */}
          <Box>
            <Typography gutterBottom>Target Zone</Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {HEART_RATE_ZONES.map(zone => (
                <Chip
                  key={zone.name}
                  label={zone.name}
                  color={targetZone.name === zone.name ? 'primary' : 'default'}
                  onClick={() => setTargetZone(zone)}
                />
              ))}
            </Box>
          </Box>

          {/* Recommendation */}
          {isMonitoring && (
            <Alert
              severity={
                heartRate < targetZone.min
                  ? 'info'
                  : heartRate > targetZone.max
                  ? 'warning'
                  : 'success'
              }
              icon={
                heartRate < targetZone.min
                  ? <TrendingIcon />
                  : heartRate > targetZone.max
                  ? <WarningIcon />
                  : <HeartIcon />
              }
            >
              {getRecommendation(heartRate)}
            </Alert>
          )}

          {/* Heart Rate Chart */}
          {heartRateData.length > 0 && (
            <Box height={200}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={heartRateData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                  />
                  <YAxis domain={[40, maxHeartRate]} />
                  <ChartTooltip
                    labelFormatter={(value) => new Date(value).toLocaleTimeString()}
                    formatter={(value) => [`${value} BPM`, 'Heart Rate']}
                  />
                  <Area
                    type="monotone"
                    dataKey="bpm"
                    stroke="#F44336"
                    fill="#F44336"
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Box>
          )}

          {/* Control Buttons */}
          <Box display="flex" gap={1}>
            <Button
              fullWidth
              variant="contained"
              color={isMonitoring ? 'error' : 'primary'}
              startIcon={isMonitoring ? <TimerIcon /> : <HeartIcon />}
              onClick={() => setIsMonitoring(!isMonitoring)}
            >
              {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}; 