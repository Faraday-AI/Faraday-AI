import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
  Avatar,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Badge,
  Tooltip,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  EmojiEvents as TrophyIcon,
  TrendingUp as ProgressIcon,
  Timer as TimerIcon,
  FitnessCenter as ExerciseIcon,
} from '@mui/icons-material';

interface Challenge {
  id: string;
  name: string;
  type: 'steps' | 'distance' | 'time' | 'reps';
  target: number;
  unit: string;
  startDate: string;
  endDate: string;
  participants: Participant[];
}

interface Participant {
  id: string;
  name: string;
  progress: number;
  achievements: Achievement[];
}

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  progress: number;
  completed: boolean;
}

const DEFAULT_CHALLENGES: Challenge[] = [
  {
    id: '1',
    name: '10,000 Steps Challenge',
    type: 'steps',
    target: 10000,
    unit: 'steps',
    startDate: new Date().toISOString(),
    endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    participants: [],
  },
  {
    id: '2',
    name: '5K Run Challenge',
    type: 'distance',
    target: 5,
    unit: 'km',
    startDate: new Date().toISOString(),
    endDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
    participants: [],
  },
];

const ACHIEVEMENTS: Achievement[] = [
  {
    id: '1',
    name: 'First Steps',
    description: 'Complete your first challenge',
    icon: '👣',
    progress: 0,
    completed: false,
  },
  {
    id: '2',
    name: 'Early Bird',
    description: 'Complete a challenge before the deadline',
    icon: '⏰',
    progress: 0,
    completed: false,
  },
  {
    id: '3',
    name: 'Consistency',
    description: 'Complete 3 challenges in a row',
    icon: '📈',
    progress: 0,
    completed: false,
  },
];

export const FitnessChallengeWidget: React.FC = () => {
  const [challenges, setChallenges] = useState<Challenge[]>(DEFAULT_CHALLENGES);
  const [showChallengeDialog, setShowChallengeDialog] = useState(false);
  const [selectedChallenge, setSelectedChallenge] = useState<Challenge | null>(null);
  const [newChallenge, setNewChallenge] = useState<Partial<Challenge>>({
    type: 'steps',
    target: 0,
    unit: '',
  });
  const [error, setError] = useState<string | null>(null);

  const addChallenge = (challenge: Challenge) => {
    setChallenges([...challenges, challenge]);
    setShowChallengeDialog(false);
    setNewChallenge({ type: 'steps', target: 0, unit: '' });
  };

  const joinChallenge = (challengeId: string) => {
    setChallenges(challenges.map(challenge => {
      if (challenge.id === challengeId) {
        return {
          ...challenge,
          participants: [
            ...challenge.participants,
            {
              id: Date.now().toString(),
              name: 'You',
              progress: 0,
              achievements: ACHIEVEMENTS,
            },
          ],
        };
      }
      return challenge;
    }));
  };

  const updateProgress = (challengeId: string, participantId: string, progress: number) => {
    setChallenges(challenges.map(challenge => {
      if (challenge.id === challengeId) {
        return {
          ...challenge,
          participants: challenge.participants.map(participant => {
            if (participant.id === participantId) {
              return {
                ...participant,
                progress,
                achievements: participant.achievements.map(achievement => {
                  if (!achievement.completed) {
                    const newProgress = progress / challenge.target * 100;
                    return {
                      ...achievement,
                      progress: newProgress,
                      completed: newProgress >= 100,
                    };
                  }
                  return achievement;
                }),
              };
            }
            return participant;
          }),
        };
      }
      return challenge;
    }));
  };

  const getChallengeIcon = (type: Challenge['type']) => {
    switch (type) {
      case 'steps':
        return '👣';
      case 'distance':
        return '🏃';
      case 'time':
        return '⏱️';
      case 'reps':
        return '💪';
      default:
        return '🎯';
    }
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Fitness Challenges</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setShowChallengeDialog(true)}
            >
              New Challenge
            </Button>
          </Box>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Challenges List */}
          <List>
            {challenges.map(challenge => (
              <ListItem
                key={challenge.id}
                sx={{
                  mb: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1,
                }}
              >
                <ListItemAvatar>
                  <Avatar>{getChallengeIcon(challenge.type)}</Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={challenge.name}
                  secondary={
                    <Box>
                      <Typography variant="body2">
                        Target: {challenge.target} {challenge.unit}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(challenge.startDate).toLocaleDateString()} -{' '}
                        {new Date(challenge.endDate).toLocaleDateString()}
                      </Typography>
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  {challenge.participants.length > 0 ? (
                    <Box display="flex" flexDirection="column" alignItems="flex-end">
                      <Typography variant="caption" color="text.secondary">
                        {challenge.participants.length} participants
                      </Typography>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => setSelectedChallenge(challenge)}
                      >
                        View Progress
                      </Button>
                    </Box>
                  ) : (
                    <Button
                      variant="contained"
                      onClick={() => joinChallenge(challenge.id)}
                    >
                      Join Challenge
                    </Button>
                  )}
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Box>
      </CardContent>

      {/* New Challenge Dialog */}
      <Dialog open={showChallengeDialog} onClose={() => setShowChallengeDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Challenge</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Challenge Name"
              fullWidth
              onChange={(e) => setNewChallenge({ ...newChallenge, name: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Challenge Type</InputLabel>
              <Select
                label="Challenge Type"
                value={newChallenge.type}
                onChange={(e) => {
                  const type = e.target.value as Challenge['type'];
                  setNewChallenge({
                    ...newChallenge,
                    type,
                    unit: type === 'steps' ? 'steps' : type === 'distance' ? 'km' : type === 'time' ? 'minutes' : 'reps',
                  });
                }}
              >
                <MenuItem value="steps">Steps</MenuItem>
                <MenuItem value="distance">Distance</MenuItem>
                <MenuItem value="time">Time</MenuItem>
                <MenuItem value="reps">Repetitions</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Target"
              type="number"
              fullWidth
              onChange={(e) => setNewChallenge({ ...newChallenge, target: parseInt(e.target.value) })}
            />
            <TextField
              label="Duration (days)"
              type="number"
              fullWidth
              onChange={(e) => {
                const days = parseInt(e.target.value);
                setNewChallenge({
                  ...newChallenge,
                  startDate: new Date().toISOString(),
                  endDate: new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString(),
                });
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowChallengeDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => addChallenge(newChallenge as Challenge)}
            disabled={!newChallenge.name || !newChallenge.target}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Challenge Progress Dialog */}
      <Dialog
        open={!!selectedChallenge}
        onClose={() => setSelectedChallenge(null)}
        maxWidth="md"
        fullWidth
      >
        {selectedChallenge && (
          <>
            <DialogTitle>
              {selectedChallenge.name} Progress
            </DialogTitle>
            <DialogContent>
              <Box display="flex" flexDirection="column" gap={2}>
                {/* Leaderboard */}
                <Typography variant="subtitle1">Leaderboard</Typography>
                <List>
                  {selectedChallenge.participants
                    .sort((a, b) => b.progress - a.progress)
                    .map((participant, index) => (
                      <ListItem key={participant.id}>
                        <ListItemAvatar>
                          <Badge
                            badgeContent={index + 1}
                            color={
                              index === 0
                                ? 'primary'
                                : index === 1
                                ? 'secondary'
                                : index === 2
                                ? 'success'
                                : 'default'
                            }
                          >
                            <Avatar>{participant.name[0]}</Avatar>
                          </Badge>
                        </ListItemAvatar>
                        <ListItemText
                          primary={participant.name}
                          secondary={
                            <Box>
                              <Typography variant="body2">
                                Progress: {participant.progress} / {selectedChallenge.target} {selectedChallenge.unit}
                              </Typography>
                              <LinearProgress
                                variant="determinate"
                                value={(participant.progress / selectedChallenge.target) * 100}
                                sx={{ mt: 1 }}
                              />
                            </Box>
                          }
                        />
                      </ListItem>
                    ))}
                </List>

                {/* Achievements */}
                <Typography variant="subtitle1">Achievements</Typography>
                <Grid container spacing={2}>
                  {selectedChallenge.participants[0]?.achievements.map(achievement => (
                    <Grid item xs={12} sm={6} md={4} key={achievement.id}>
                      <Card
                        sx={{
                          opacity: achievement.completed ? 1 : 0.5,
                          height: '100%',
                        }}
                      >
                        <CardContent>
                          <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
                            <Typography variant="h4">{achievement.icon}</Typography>
                            <Typography variant="subtitle1">{achievement.name}</Typography>
                            <Typography variant="body2" color="text.secondary" textAlign="center">
                              {achievement.description}
                            </Typography>
                            {!achievement.completed && (
                              <LinearProgress
                                variant="determinate"
                                value={achievement.progress}
                                sx={{ width: '100%', mt: 1 }}
                              />
                            )}
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedChallenge(null)}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Card>
  );
}; 