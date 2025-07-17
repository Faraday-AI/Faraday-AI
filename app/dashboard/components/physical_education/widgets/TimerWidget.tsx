import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  ToggleButtonGroup,
  ToggleButton,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  FormControl,
  InputLabel,
  MenuItem,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Stop,
  RestartAlt,
  Timer,
  TimerOff,
  AddAlarm,
  Delete,
  Settings,
  VolumeUp,
  VolumeOff,
} from '@mui/icons-material';

type TimerMode = 'stopwatch' | 'countdown';
type TimerPreset = { name: string; duration: number };

const DEFAULT_PRESETS: TimerPreset[] = [
  { name: '1 Minute', duration: 60 },
  { name: '2 Minutes', duration: 120 },
  { name: '5 Minutes', duration: 300 },
  { name: '10 Minutes', duration: 600 },
  { name: '15 Minutes', duration: 900 },
  { name: '30 Minutes', duration: 1800 },
];

export const TimerWidget: React.FC = () => {
  const [mode, setMode] = useState<TimerMode>('stopwatch');
  const [time, setTime] = useState(0);
  const [countdownTime, setCountdownTime] = useState(300);
  const [isRunning, setIsRunning] = useState(false);
  const [laps, setLaps] = useState<number[]>([]);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [presets, setPresets] = useState<TimerPreset[]>(DEFAULT_PRESETS);
  const [selectedPreset, setSelectedPreset] = useState<string>('');
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (audioRef.current === null) {
      audioRef.current = new Audio('/sounds/timer-end.mp3');
    }
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  const startTimer = () => {
    if (timerRef.current) return;
    
    timerRef.current = setInterval(() => {
      if (mode === 'stopwatch') {
        setTime(prev => prev + 1);
      } else {
        setTime(prev => {
          if (prev <= 0) {
            stopTimer();
            if (soundEnabled && audioRef.current) {
              audioRef.current.play();
            }
            return 0;
          }
          return prev - 1;
        });
      }
    }, 1000);
    setIsRunning(true);
  };

  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setIsRunning(false);
  };

  const resetTimer = () => {
    stopTimer();
    setTime(mode === 'stopwatch' ? 0 : countdownTime);
    setLaps([]);
  };

  const addLap = () => {
    setLaps([...laps, time]);
  };

  const clearLaps = () => {
    setLaps([]);
  };

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    return [
      hours.toString().padStart(2, '0'),
      minutes.toString().padStart(2, '0'),
      secs.toString().padStart(2, '0')
    ].join(':');
  };

  const handleCountdownChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(event.target.value);
    if (!isNaN(value) && value >= 0) {
      setCountdownTime(value);
      if (!isRunning) {
        setTime(value);
      }
    }
  };

  const handlePresetSelect = (presetName: string) => {
    const preset = presets.find(p => p.name === presetName);
    if (preset) {
      setCountdownTime(preset.duration);
      setTime(preset.duration);
      setSelectedPreset(presetName);
    }
  };

  const addPreset = () => {
    const newPreset: TimerPreset = {
      name: `${countdownTime / 60} Minutes`,
      duration: countdownTime,
    };
    setPresets([...presets, newPreset]);
  };

  const removePreset = (presetName: string) => {
    setPresets(presets.filter(p => p.name !== presetName));
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Timer</Typography>
            <Box display="flex" gap={1}>
              <Tooltip title={soundEnabled ? "Sound On" : "Sound Off"}>
                <IconButton onClick={() => setSoundEnabled(!soundEnabled)}>
                  {soundEnabled ? <VolumeUp /> : <VolumeOff />}
                </IconButton>
              </Tooltip>
              <Tooltip title="Settings">
                <IconButton onClick={() => setShowSettings(true)}>
                  <Settings />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          <ToggleButtonGroup
            value={mode}
            exclusive
            onChange={(_, newMode) => {
              if (newMode) {
                setMode(newMode);
                stopTimer();
                setTime(newMode === 'stopwatch' ? 0 : countdownTime);
              }
            }}
            size="small"
            fullWidth
          >
            <ToggleButton value="stopwatch">Stopwatch</ToggleButton>
            <ToggleButton value="countdown">Countdown</ToggleButton>
          </ToggleButtonGroup>

          {mode === 'countdown' && (
            <Box display="flex" flexDirection="column" gap={1}>
              <FormControl fullWidth>
                <InputLabel>Presets</InputLabel>
                <Select
                  value={selectedPreset}
                  onChange={(e) => handlePresetSelect(e.target.value as string)}
                  label="Presets"
                >
                  {presets.map((preset) => (
                    <MenuItem key={preset.name} value={preset.name}>
                      {preset.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Box display="flex" gap={1}>
                <TextField
                  fullWidth
                  type="number"
                  label="Countdown Time (seconds)"
                  value={countdownTime}
                  onChange={handleCountdownChange}
                  disabled={isRunning}
                />
                <Button
                  variant="contained"
                  onClick={addPreset}
                  disabled={isRunning}
                >
                  <AddAlarm />
                </Button>
              </Box>
            </Box>
          )}

          <Typography variant="h3" textAlign="center" my={2}>
            {formatTime(time)}
          </Typography>

          <Box display="flex" justifyContent="center" gap={1}>
            {!isRunning ? (
              <Button
                variant="contained"
                color="primary"
                startIcon={<PlayArrow />}
                onClick={startTimer}
              >
                Start
              </Button>
            ) : (
              <Button
                variant="contained"
                color="secondary"
                startIcon={<Pause />}
                onClick={stopTimer}
              >
                Pause
              </Button>
            )}
            <Button
              variant="outlined"
              startIcon={<RestartAlt />}
              onClick={resetTimer}
            >
              Reset
            </Button>
            {mode === 'stopwatch' && (
              <Button
                variant="outlined"
                onClick={addLap}
                disabled={!isRunning}
              >
                Lap
              </Button>
            )}
          </Box>

          {laps.length > 0 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="subtitle1">Lap Times</Typography>
                <Button
                  size="small"
                  startIcon={<Delete />}
                  onClick={clearLaps}
                >
                  Clear
                </Button>
              </Box>
              <List dense>
                {laps.map((lap, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={`Lap ${index + 1}`}
                      secondary={formatTime(lap)}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Box>
      </CardContent>

      {/* Settings Dialog */}
      <Dialog open={showSettings} onClose={() => setShowSettings(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Timer Settings</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <Typography variant="subtitle1">Presets</Typography>
            <List dense>
              {presets.map((preset) => (
                <ListItem key={preset.name}>
                  <ListItemText primary={preset.name} secondary={`${preset.duration} seconds`} />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      size="small"
                      onClick={() => removePreset(preset.name)}
                    >
                      <Delete />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}; 