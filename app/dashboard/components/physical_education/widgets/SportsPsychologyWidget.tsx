import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  Alert,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Rating,
  Slider,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  SentimentSatisfied as MoodIcon,
  Assignment as AssessmentIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  Star as StarIcon,
  TrendingUp as TrendingUpIcon,
  Flag as GoalIcon,
} from '@mui/icons-material';

interface Student {
  id: string;
  name: string;
  grade: string;
  mentalHealthProfile: {
    stressLevel: number;
    confidenceLevel: number;
    motivationLevel: number;
    lastAssessment: string;
  };
  goals: PsychologyGoal[];
  strategies: CopingStrategy[];
  assessments: MentalAssessment[];
}

interface PsychologyGoal {
  id: string;
  description: string;
  targetDate: string;
  progress: number;
  status: 'active' | 'completed' | 'needs-attention';
  notes: string;
}

interface CopingStrategy {
  id: string;
  name: string;
  description: string;
  effectiveness: number;
  lastUsed?: string;
  situations: string[];
}

interface MentalAssessment {
  id: string;
  date: string;
  type: 'stress' | 'confidence' | 'motivation' | 'comprehensive';
  scores: {
    category: string;
    score: number;
    notes?: string;
  }[];
  recommendations: string[];
}

const DEFAULT_STUDENTS: Student[] = [
  {
    id: '1',
    name: 'Michael Brown',
    grade: '9th',
    mentalHealthProfile: {
      stressLevel: 3,
      confidenceLevel: 4,
      motivationLevel: 4,
      lastAssessment: '2024-03-01',
    },
    goals: [
      {
        id: '1',
        description: 'Develop pre-game relaxation routine',
        targetDate: '2024-04-15',
        progress: 60,
        status: 'active',
        notes: 'Making good progress with breathing exercises',
      },
    ],
    strategies: [
      {
        id: '1',
        name: 'Deep Breathing',
        description: 'Controlled breathing exercises for stress management',
        effectiveness: 4,
        lastUsed: '2024-03-01',
        situations: ['Pre-game anxiety', 'Performance pressure'],
      },
    ],
    assessments: [
      {
        id: '1',
        date: '2024-03-01',
        type: 'comprehensive',
        scores: [
          { category: 'Stress Management', score: 3, notes: 'Shows improvement in handling pressure' },
          { category: 'Self-Confidence', score: 4, notes: 'Good progress in team activities' },
          { category: 'Focus', score: 3, notes: 'Needs work on maintaining concentration' },
        ],
        recommendations: [
          'Continue with breathing exercises',
          'Practice visualization techniques',
        ],
      },
    ],
  },
  {
    id: '2',
    name: 'Sofia Rodriguez',
    grade: '10th',
    mentalHealthProfile: {
      stressLevel: 2,
      confidenceLevel: 5,
      motivationLevel: 5,
      lastAssessment: '2024-03-02',
    },
    goals: [
      {
        id: '2',
        description: 'Enhance team leadership skills',
        targetDate: '2024-05-01',
        progress: 75,
        status: 'active',
        notes: 'Showing excellent progress in communication',
      },
    ],
    strategies: [
      {
        id: '2',
        name: 'Positive Self-Talk',
        description: 'Using affirmations and encouragement',
        effectiveness: 5,
        lastUsed: '2024-03-02',
        situations: ['Performance anxiety', 'Team leadership'],
      },
    ],
    assessments: [
      {
        id: '2',
        date: '2024-03-02',
        type: 'motivation',
        scores: [
          { category: 'Leadership', score: 5, notes: 'Excellent team motivation skills' },
          { category: 'Goal Setting', score: 4, notes: 'Clear understanding of objectives' },
        ],
        recommendations: [
          'Continue peer mentoring program',
          'Develop advanced leadership workshops',
        ],
      },
    ],
  },
];

export const SportsPsychologyWidget: React.FC = () => {
  const [students, setStudents] = useState<Student[]>(DEFAULT_STUDENTS);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [showAssessmentDialog, setShowAssessmentDialog] = useState(false);
  const [showStrategyDialog, setShowStrategyDialog] = useState(false);
  const [showGoalDialog, setShowGoalDialog] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const defaultAssessment: MentalAssessment = {
    id: '',
    date: new Date().toISOString().split('T')[0],
    type: 'comprehensive',
    scores: [],
    recommendations: [],
  };
  const [newAssessment, setNewAssessment] = useState<MentalAssessment>(defaultAssessment);
  const [newStrategy, setNewStrategy] = useState<Partial<CopingStrategy>>({
    effectiveness: 3,
  });
  const [newGoal, setNewGoal] = useState<Partial<PsychologyGoal>>({
    status: 'active',
    progress: 0,
  });

  const handleAddAssessment = () => {
    if (!selectedStudent || !newAssessment.type || newAssessment.scores.length === 0) {
      setError('Please fill in all required fields');
      return;
    }

    const assessment: MentalAssessment = {
      id: Date.now().toString(),
      date: new Date().toISOString().split('T')[0],
      type: newAssessment.type as MentalAssessment['type'],
      scores: newAssessment.scores,
      recommendations: newAssessment.recommendations || [],
    };

    setStudents(students.map(student =>
      student.id === selectedStudent.id
        ? { ...student, assessments: [...student.assessments, assessment] }
        : student
    ));
    setShowAssessmentDialog(false);
    setNewAssessment(defaultAssessment);
  };

  const handleAddStrategy = () => {
    if (!selectedStudent || !newStrategy.name || !newStrategy.description) {
      setError('Please fill in all required fields');
      return;
    }

    const strategy: CopingStrategy = {
      id: Date.now().toString(),
      name: newStrategy.name,
      description: newStrategy.description,
      effectiveness: newStrategy.effectiveness || 3,
      lastUsed: new Date().toISOString().split('T')[0],
      situations: newStrategy.situations || [],
    };

    setStudents(students.map(student =>
      student.id === selectedStudent.id
        ? { ...student, strategies: [...student.strategies, strategy] }
        : student
    ));
    setShowStrategyDialog(false);
    setNewStrategy({ effectiveness: 3 });
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Sports Psychology</Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                startIcon={<AssessmentIcon />}
                onClick={() => {
                  if (selectedStudent) {
                    setShowAssessmentDialog(true);
                  } else {
                    setError('Please select a student first');
                  }
                }}
              >
                New Assessment
              </Button>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => {
                  if (selectedStudent) {
                    setShowStrategyDialog(true);
                  } else {
                    setError('Please select a student first');
                  }
                }}
              >
                Add Strategy
              </Button>
            </Box>
          </Box>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Tabs */}
          <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value)}>
            <Tab label="Students" />
            <Tab label="Strategies" />
            <Tab label="Assessments" />
          </Tabs>

          {/* Students Tab */}
          {activeTab === 0 && (
            <Grid container spacing={2}>
              {students.map(student => (
                <Grid item xs={12} key={student.id}>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Box display="flex" alignItems="center" gap={2}>
                        <PsychologyIcon color="primary" />
                        <Typography variant="subtitle1">{student.name}</Typography>
                        <Chip label={student.grade} size="small" />
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                          <Paper sx={{ p: 2 }}>
                            <Typography variant="subtitle2" gutterBottom>
                              Mental Health Profile
                            </Typography>
                            <Box display="flex" flexDirection="column" gap={2}>
                              <Box>
                                <Typography variant="body2">Stress Level</Typography>
                                <Rating
                                  value={student.mentalHealthProfile.stressLevel}
                                  readOnly
                                  icon={<MoodIcon />}
                                  emptyIcon={<MoodIcon />}
                                />
                              </Box>
                              <Box>
                                <Typography variant="body2">Confidence Level</Typography>
                                <Rating
                                  value={student.mentalHealthProfile.confidenceLevel}
                                  readOnly
                                  icon={<StarIcon />}
                                  emptyIcon={<StarIcon />}
                                />
                              </Box>
                              <Box>
                                <Typography variant="body2">Motivation Level</Typography>
                                <Rating
                                  value={student.mentalHealthProfile.motivationLevel}
                                  readOnly
                                  icon={<TrendingUpIcon />}
                                  emptyIcon={<TrendingUpIcon />}
                                />
                              </Box>
                            </Box>
                          </Paper>
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <Paper sx={{ p: 2 }}>
                            <Typography variant="subtitle2" gutterBottom>
                              Active Goals
                            </Typography>
                            <List dense>
                              {student.goals.map(goal => (
                                <ListItem key={goal.id}>
                                  <ListItemText
                                    primary={goal.description}
                                    secondary={`Progress: ${goal.progress}%`}
                                  />
                                  <ListItemSecondaryAction>
                                    <Chip
                                      label={goal.status}
                                      color={
                                        goal.status === 'completed'
                                          ? 'success'
                                          : goal.status === 'needs-attention'
                                          ? 'warning'
                                          : 'default'
                                      }
                                      size="small"
                                    />
                                  </ListItemSecondaryAction>
                                </ListItem>
                              ))}
                            </List>
                            <Button
                              variant="outlined"
                              size="small"
                              startIcon={<AddIcon />}
                              onClick={() => {
                                setSelectedStudent(student);
                                setShowGoalDialog(true);
                              }}
                            >
                              Add Goal
                            </Button>
                          </Paper>
                        </Grid>
                      </Grid>
                    </AccordionDetails>
                  </Accordion>
                </Grid>
              ))}
            </Grid>
          )}

          {/* Strategies Tab */}
          {activeTab === 1 && (
            <Grid container spacing={2}>
              {students.flatMap(student =>
                student.strategies.map(strategy => (
                  <Grid item xs={12} md={6} key={`${student.id}-${strategy.id}`}>
                    <Paper sx={{ p: 2 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                        <Box>
                          <Typography variant="subtitle1">{strategy.name}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {student.name}
                          </Typography>
                        </Box>
                        <Rating value={strategy.effectiveness} readOnly />
                      </Box>
                      <Typography variant="body2" mt={1}>
                        {strategy.description}
                      </Typography>
                      <Box mt={2}>
                        <Typography variant="body2" gutterBottom>
                          Applicable Situations:
                        </Typography>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          {strategy.situations.map((situation, index) => (
                            <Chip key={index} label={situation} size="small" />
                          ))}
                        </Box>
                      </Box>
                      {strategy.lastUsed && (
                        <Typography variant="body2" mt={1} color="text.secondary">
                          Last used: {new Date(strategy.lastUsed).toLocaleDateString()}
                        </Typography>
                      )}
                    </Paper>
                  </Grid>
                ))
              )}
            </Grid>
          )}

          {/* Assessments Tab */}
          {activeTab === 2 && (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Student</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Scores</TableCell>
                    <TableCell>Recommendations</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {students.flatMap(student =>
                    student.assessments.map(assessment => (
                      <TableRow key={`${student.id}-${assessment.id}`}>
                        <TableCell>{student.name}</TableCell>
                        <TableCell>
                          {new Date(assessment.date).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <Chip label={assessment.type} size="small" />
                        </TableCell>
                        <TableCell>
                          <List dense>
                            {assessment.scores.map((score, index) => (
                              <ListItem key={index}>
                                <ListItemText
                                  primary={`${score.category}: ${score.score}/5`}
                                  secondary={score.notes}
                                />
                              </ListItem>
                            ))}
                          </List>
                        </TableCell>
                        <TableCell>
                          <List dense>
                            {assessment.recommendations.map((rec, index) => (
                              <ListItem key={index}>
                                <ListItemText primary={rec} />
                              </ListItem>
                            ))}
                          </List>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      </CardContent>

      {/* Add Assessment Dialog */}
      <Dialog open={showAssessmentDialog} onClose={() => setShowAssessmentDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>New Assessment</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <FormControl fullWidth>
              <InputLabel>Assessment Type</InputLabel>
              <Select
                value={newAssessment.type || 'comprehensive'}
                label="Assessment Type"
                onChange={(e) => setNewAssessment({ ...newAssessment, type: e.target.value as MentalAssessment['type'] })}
              >
                <MenuItem value="comprehensive">Comprehensive</MenuItem>
                <MenuItem value="stress">Stress Management</MenuItem>
                <MenuItem value="confidence">Confidence</MenuItem>
                <MenuItem value="motivation">Motivation</MenuItem>
              </Select>
            </FormControl>
            <Typography variant="subtitle2" gutterBottom>
              Scores
            </Typography>
            {['Stress Management', 'Self-Confidence', 'Focus', 'Team Interaction'].map((category, index) => (
              <Box key={index} display="flex" alignItems="center" gap={2}>
                <Typography variant="body2" sx={{ minWidth: 150 }}>
                  {category}
                </Typography>
                <Slider
                  value={newAssessment.scores?.find(s => s.category === category)?.score || 0}
                  min={0}
                  max={5}
                  step={1}
                  marks
                  onChange={(_, value) => {
                    const scores = [...(newAssessment.scores || [])];
                    const existingIndex = scores.findIndex(s => s.category === category);
                    if (existingIndex >= 0) {
                      scores[existingIndex].score = value as number;
                    } else {
                      scores.push({ category, score: value as number });
                    }
                    setNewAssessment({ ...newAssessment, scores });
                  }}
                />
              </Box>
            ))}
            <TextField
              label="Recommendations (one per line)"
              multiline
              rows={3}
              fullWidth
              onChange={(e) => setNewAssessment({
                ...newAssessment,
                recommendations: e.target.value.split('\n'),
              })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowAssessmentDialog(false);
            setNewAssessment(defaultAssessment);
          }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleAddAssessment}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Strategy Dialog */}
      <Dialog open={showStrategyDialog} onClose={() => setShowStrategyDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Coping Strategy</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Strategy Name"
              fullWidth
              onChange={(e) => setNewStrategy({ ...newStrategy, name: e.target.value })}
            />
            <TextField
              label="Description"
              multiline
              rows={2}
              fullWidth
              onChange={(e) => setNewStrategy({ ...newStrategy, description: e.target.value })}
            />
            <Box>
              <Typography variant="body2" gutterBottom>
                Effectiveness Rating
              </Typography>
              <Rating
                value={newStrategy.effectiveness}
                onChange={(_, value) => setNewStrategy({ ...newStrategy, effectiveness: value || 3 })}
              />
            </Box>
            <TextField
              label="Applicable Situations (one per line)"
              multiline
              rows={3}
              fullWidth
              onChange={(e) => setNewStrategy({
                ...newStrategy,
                situations: e.target.value.split('\n'),
              })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowStrategyDialog(false);
            setNewStrategy({ effectiveness: 3 });
          }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleAddStrategy}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}; 