import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  FormControl,
  InputLabel,
  ToggleButtonGroup,
  ToggleButton,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  Edit as EditIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
  ColorLens as ColorLensIcon,
  Timer as TimerIcon,
  RestartAlt as RestartIcon,
} from '@mui/icons-material';
import { SketchPicker } from 'react-color';

interface Team {
  id: string;
  name: string;
  score: number;
  color: string;
  history: { score: number; timestamp: number }[];
}

interface GameSettings {
  maxScore: number;
  scoreIncrement: number;
  autoSave: boolean;
  timerEnabled: boolean;
  timerDuration: number;
}

export const ScoreboardWidget: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([
    { id: '1', name: 'Team A', score: 0, color: '#2196f3', history: [] },
    { id: '2', name: 'Team B', score: 0, color: '#f44336', history: [] },
  ]);
  const [editingTeam, setEditingTeam] = useState<string | null>(null);
  const [newTeamName, setNewTeamName] = useState('');
  const [settings, setSettings] = useState<GameSettings>({
    maxScore: 100,
    scoreIncrement: 1,
    autoSave: true,
    timerEnabled: false,
    timerDuration: 300,
  });
  const [timeLeft, setTimeLeft] = useState(settings.timerDuration);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [colorPickerAnchor, setColorPickerAnchor] = useState<null | HTMLElement>(null);
  const [selectedTeamForColor, setSelectedTeamForColor] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [selectedTeamForHistory, setSelectedTeamForHistory] = useState<string | null>(null);

  // Timer effect
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isTimerRunning && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      setIsTimerRunning(false);
    }
    return () => clearInterval(timer);
  }, [isTimerRunning, timeLeft]);

  const updateScore = (teamId: string, delta: number) => {
    setTeams(teams.map(team => {
      if (team.id === teamId) {
        const newScore = Math.max(0, Math.min(team.score + delta, settings.maxScore));
        return {
          ...team,
          score: newScore,
          history: [...team.history, { score: newScore, timestamp: Date.now() }]
        };
      }
      return team;
    }));
  };

  const startEditing = (teamId: string) => {
    const team = teams.find(t => t.id === teamId);
    if (team) {
      setNewTeamName(team.name);
      setEditingTeam(teamId);
    }
  };

  const saveEdit = (teamId: string) => {
    setTeams(teams.map(team => 
      team.id === teamId ? { ...team, name: newTeamName } : team
    ));
    setEditingTeam(null);
  };

  const addTeam = () => {
    const colors = ['#2196f3', '#f44336', '#4caf50', '#ff9800'];
    const newTeam: Team = {
      id: Date.now().toString(),
      name: `Team ${teams.length + 1}`,
      score: 0,
      color: colors[teams.length % colors.length],
      history: [],
    };
    setTeams([...teams, newTeam]);
  };

  const removeTeam = (teamId: string) => {
    if (teams.length > 2) {
      setTeams(teams.filter(team => team.id !== teamId));
    }
  };

  const resetScores = () => {
    setTeams(teams.map(team => ({
      ...team,
      score: 0,
      history: [...team.history, { score: 0, timestamp: Date.now() }]
    })));
  };

  const handleColorChange = (color: string) => {
    if (selectedTeamForColor) {
      setTeams(teams.map(team => 
        team.id === selectedTeamForColor ? { ...team, color } : team
      ));
    }
    setColorPickerAnchor(null);
    setSelectedTeamForColor(null);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Scoreboard</Typography>
            <Box display="flex" gap={1}>
              <Tooltip title="Game History">
                <IconButton onClick={() => setShowHistory(true)}>
                  <HistoryIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Settings">
                <IconButton onClick={() => setShowHistory(true)}>
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
              <Button
                variant="contained"
                color="primary"
                startIcon={<AddIcon />}
                onClick={addTeam}
                disabled={teams.length >= 4}
              >
                Add Team
              </Button>
            </Box>
          </Box>

          {settings.timerEnabled && (
            <Box display="flex" alignItems="center" justifyContent="center" gap={2}>
              <Typography variant="h5">{formatTime(timeLeft)}</Typography>
              <IconButton
                color={isTimerRunning ? "secondary" : "primary"}
                onClick={() => setIsTimerRunning(!isTimerRunning)}
              >
                <TimerIcon />
              </IconButton>
              <IconButton onClick={() => setTimeLeft(settings.timerDuration)}>
                <RestartIcon />
              </IconButton>
            </Box>
          )}

          <Box display="flex" flexDirection="column" gap={2}>
            {teams.map(team => (
              <Box
                key={team.id}
                display="flex"
                alignItems="center"
                justifyContent="space-between"
                p={2}
                sx={{
                  bgcolor: `${team.color}20`,
                  borderRadius: 1,
                  border: `1px solid ${team.color}`,
                }}
              >
                <Box display="flex" alignItems="center" gap={1}>
                  {editingTeam === team.id ? (
                    <TextField
                      size="small"
                      value={newTeamName}
                      onChange={(e) => setNewTeamName(e.target.value)}
                      onBlur={() => saveEdit(team.id)}
                      onKeyPress={(e) => e.key === 'Enter' && saveEdit(team.id)}
                      autoFocus
                    />
                  ) : (
                    <>
                      <Typography variant="h6">{team.name}</Typography>
                      <IconButton size="small" onClick={() => startEditing(team.id)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          setColorPickerAnchor(e.currentTarget);
                          setSelectedTeamForColor(team.id);
                        }}
                      >
                        <ColorLensIcon fontSize="small" />
                      </IconButton>
                    </>
                  )}
                </Box>

                <Box display="flex" alignItems="center" gap={1}>
                  <IconButton
                    size="small"
                    onClick={() => updateScore(team.id, -settings.scoreIncrement)}
                    disabled={team.score <= 0}
                  >
                    <RemoveIcon />
                  </IconButton>
                  <Typography variant="h5" minWidth={40} textAlign="center">
                    {team.score}
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={() => updateScore(team.id, settings.scoreIncrement)}
                    disabled={team.score >= settings.maxScore}
                  >
                    <AddIcon />
                  </IconButton>
                  {teams.length > 2 && (
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => removeTeam(team.id)}
                    >
                      <RemoveIcon />
                    </IconButton>
                  )}
                </Box>
              </Box>
            ))}
          </Box>

          <Box display="flex" justifyContent="center" gap={1}>
            <Button
              variant="outlined"
              color="secondary"
              onClick={resetScores}
            >
              Reset Scores
            </Button>
          </Box>
        </Box>
      </CardContent>

      {/* Color Picker Menu */}
      <Menu
        anchorEl={colorPickerAnchor}
        open={Boolean(colorPickerAnchor)}
        onClose={() => setColorPickerAnchor(null)}
      >
        <MenuItem>
          <SketchPicker
            color={teams.find(t => t.id === selectedTeamForColor)?.color || '#000'}
            onChangeComplete={(color) => handleColorChange(color.hex)}
          />
        </MenuItem>
      </Menu>

      {/* History Dialog */}
      <Dialog open={showHistory} onClose={() => setShowHistory(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Game History</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Select Team</InputLabel>
            <Select
              value={selectedTeamForHistory || ''}
              onChange={(e) => setSelectedTeamForHistory(e.target.value as string)}
            >
              {teams.map(team => (
                <MenuItem key={team.id} value={team.id}>{team.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          {selectedTeamForHistory && (
            <Box mt={2}>
              {teams
                .find(t => t.id === selectedTeamForHistory)
                ?.history.map((entry, index) => (
                  <Box key={index} display="flex" justifyContent="space-between" py={1}>
                    <Typography>
                      {new Date(entry.timestamp).toLocaleTimeString()}
                    </Typography>
                    <Typography variant="h6">{entry.score}</Typography>
                  </Box>
                ))}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHistory(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog open={false} onClose={() => {}} maxWidth="sm" fullWidth>
        <DialogTitle>Game Settings</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Maximum Score"
              type="number"
              value={settings.maxScore}
              onChange={(e) => setSettings({ ...settings, maxScore: Number(e.target.value) })}
            />
            <TextField
              label="Score Increment"
              type="number"
              value={settings.scoreIncrement}
              onChange={(e) => setSettings({ ...settings, scoreIncrement: Number(e.target.value) })}
            />
            <ToggleButtonGroup
              value={settings.timerEnabled}
              exclusive
              onChange={(_, value) => setSettings({ ...settings, timerEnabled: value })}
            >
              <ToggleButton value={true}>Timer Enabled</ToggleButton>
              <ToggleButton value={false}>Timer Disabled</ToggleButton>
            </ToggleButtonGroup>
            {settings.timerEnabled && (
              <TextField
                label="Timer Duration (seconds)"
                type="number"
                value={settings.timerDuration}
                onChange={(e) => setSettings({ ...settings, timerDuration: Number(e.target.value) })}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {}}>Save</Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}; 