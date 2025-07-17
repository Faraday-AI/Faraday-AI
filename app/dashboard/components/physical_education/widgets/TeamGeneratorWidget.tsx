import React, { useState, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Slider,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Tooltip,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Group as GroupIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Download as DownloadIcon,
  Sports as SportsIcon,
  Balance as BalanceIcon,
} from '@mui/icons-material';

interface Player {
  id: string;
  name: string;
  skillLevel: number;
  preferredPosition?: string;
}

interface Team {
  id: string;
  name: string;
  players: Player[];
  averageSkill: number;
}

const POSITIONS = ['Forward', 'Midfielder', 'Defender', 'Goalkeeper'];
const SKILL_LEVELS = ['Beginner', 'Intermediate', 'Advanced', 'Expert'];

export const TeamGeneratorWidget: React.FC = () => {
  const [players, setPlayers] = useState<Player[]>([]);
  const [newPlayerName, setNewPlayerName] = useState('');
  const [teams, setTeams] = useState<Team[]>([]);
  const [numTeams, setNumTeams] = useState(2);
  const [editingPlayer, setEditingPlayer] = useState<Player | null>(null);
  const [showPlayerDialog, setShowPlayerDialog] = useState(false);
  const [balanceBySkill, setBalanceBySkill] = useState(true);
  const [balanceByPosition, setBalanceByPosition] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addPlayer = () => {
    if (newPlayerName.trim() && !players.some(p => p.name.toLowerCase() === newPlayerName.toLowerCase())) {
      setEditingPlayer({
        id: Date.now().toString(),
        name: newPlayerName.trim(),
        skillLevel: 2, // Default to Intermediate
      });
      setShowPlayerDialog(true);
      setNewPlayerName('');
    }
  };

  const savePlayer = (player: Player) => {
    if (editingPlayer) {
      setPlayers(players.map(p => p.id === player.id ? player : p));
    } else {
      setPlayers([...players, player]);
    }
    setEditingPlayer(null);
    setShowPlayerDialog(false);
  };

  const removePlayer = (playerId: string) => {
    setPlayers(players.filter(p => p.id !== playerId));
  };

  const calculateTeamSkill = (teamPlayers: Player[]) => {
    return teamPlayers.reduce((sum, player) => sum + player.skillLevel, 0) / teamPlayers.length;
  };

  const generateTeams = () => {
    if (players.length < numTeams) {
      setError('Not enough players for the selected number of teams');
      return;
    }

    // Sort players by skill level
    const sortedPlayers = [...players].sort((a, b) => b.skillLevel - a.skillLevel);
    
    // Create teams
    const newTeams: Team[] = Array.from({ length: numTeams }, (_, i) => ({
      id: (i + 1).toString(),
      name: `Team ${i + 1}`,
      players: [],
      averageSkill: 0,
    }));

    // Distribute players
    sortedPlayers.forEach((player, index) => {
      const teamIndex = index % numTeams;
      newTeams[teamIndex].players.push(player);
    });

    // Calculate average skill for each team
    newTeams.forEach(team => {
      team.averageSkill = calculateTeamSkill(team.players);
    });

    setTeams(newTeams);
    setError(null);
  };

  const clearTeams = () => {
    setTeams([]);
  };

  const exportTeams = () => {
    const data = {
      teams,
      generatedAt: new Date().toISOString(),
      totalPlayers: players.length,
      settings: {
        balanceBySkill,
        balanceByPosition,
      },
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `teams-${new Date().toISOString()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          <Typography variant="h6">Team Generator</Typography>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Player Input */}
          <Box display="flex" gap={1}>
            <TextField
              fullWidth
              size="small"
              label="Player Name"
              value={newPlayerName}
              onChange={(e) => setNewPlayerName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addPlayer()}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={addPlayer}
              disabled={!newPlayerName.trim()}
            >
              <AddIcon />
            </Button>
          </Box>

          {/* Balance Options */}
          <Box display="flex" gap={2}>
            <Tooltip title="Balance teams by skill level">
              <Chip
                icon={<BalanceIcon />}
                label="Balance by Skill"
                color={balanceBySkill ? "primary" : "default"}
                onClick={() => setBalanceBySkill(!balanceBySkill)}
              />
            </Tooltip>
            <Tooltip title="Balance teams by position">
              <Chip
                icon={<SportsIcon />}
                label="Balance by Position"
                color={balanceByPosition ? "primary" : "default"}
                onClick={() => setBalanceByPosition(!balanceByPosition)}
              />
            </Tooltip>
          </Box>

          {/* Number of Teams Slider */}
          <Box>
            <Typography gutterBottom>Number of Teams: {numTeams}</Typography>
            <Slider
              value={numTeams}
              onChange={(_, value) => setNumTeams(value as number)}
              min={2}
              max={4}
              step={1}
              marks
            />
          </Box>

          {/* Player List */}
          {players.length > 0 && (
            <Box>
              <Typography variant="subtitle1">Players ({players.length})</Typography>
              <List dense>
                {players.map((player) => (
                  <ListItem key={player.id}>
                    <ListItemText
                      primary={player.name}
                      secondary={`Skill: ${SKILL_LEVELS[player.skillLevel - 1]}${player.preferredPosition ? ` | Position: ${player.preferredPosition}` : ''}`}
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        size="small"
                        onClick={() => {
                          setEditingPlayer(player);
                          setShowPlayerDialog(true);
                        }}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        edge="end"
                        size="small"
                        onClick={() => removePlayer(player.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {/* Team Generation Controls */}
          <Box display="flex" gap={1}>
            <Button
              fullWidth
              variant="contained"
              color="primary"
              startIcon={<GroupIcon />}
              onClick={generateTeams}
              disabled={players.length < numTeams}
            >
              Generate Teams
            </Button>
            <Button
              fullWidth
              variant="outlined"
              color="secondary"
              onClick={clearTeams}
              disabled={teams.length === 0}
            >
              Clear Teams
            </Button>
          </Box>

          {/* Generated Teams */}
          {teams.length > 0 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="subtitle1">Generated Teams</Typography>
                <Button
                  startIcon={<DownloadIcon />}
                  onClick={exportTeams}
                >
                  Export
                </Button>
              </Box>
              {teams.map((team) => (
                <Box key={team.id} mt={2}>
                  <Typography variant="subtitle2" color="primary">
                    {team.name} ({team.players.length} players) - Avg Skill: {team.averageSkill.toFixed(1)}
                  </Typography>
                  <List dense>
                    {team.players.map((player) => (
                      <ListItem key={player.id}>
                        <ListItemText
                          primary={player.name}
                          secondary={`Skill: ${SKILL_LEVELS[player.skillLevel - 1]}${player.preferredPosition ? ` | Position: ${player.preferredPosition}` : ''}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              ))}
            </Box>
          )}
        </Box>
      </CardContent>

      {/* Player Dialog */}
      <Dialog open={showPlayerDialog} onClose={() => setShowPlayerDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingPlayer ? 'Edit Player' : 'Add Player'}</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Name"
              value={editingPlayer?.name || ''}
              onChange={(e) => setEditingPlayer({ ...editingPlayer!, name: e.target.value })}
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>Skill Level</InputLabel>
              <Select
                value={editingPlayer?.skillLevel || 2}
                onChange={(e) => setEditingPlayer({ ...editingPlayer!, skillLevel: e.target.value as number })}
                label="Skill Level"
              >
                {SKILL_LEVELS.map((level, index) => (
                  <MenuItem key={level} value={index + 1}>{level}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Preferred Position</InputLabel>
              <Select
                value={editingPlayer?.preferredPosition || ''}
                onChange={(e) => setEditingPlayer({ ...editingPlayer!, preferredPosition: e.target.value as string })}
                label="Preferred Position"
              >
                <MenuItem value="">None</MenuItem>
                {POSITIONS.map((position) => (
                  <MenuItem key={position} value={position}>{position}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPlayerDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => savePlayer(editingPlayer!)}
            disabled={!editingPlayer?.name}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}; 