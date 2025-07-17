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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Checkbox,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  CalendarToday as CalendarIcon,
  School as SchoolIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';

interface LessonPlan {
  id: string;
  title: string;
  date: string;
  grade: string;
  objectives: string[];
  activities: string[];
  equipment: string[];
  standards: string[];
  duration: number; // in minutes
  notes?: string;
}

interface Curriculum {
  id: string;
  name: string;
  description: string;
  grade: string;
  standards: string[];
  lessonPlans: string[]; // IDs of lesson plans
}

const DEFAULT_LESSON_PLANS: LessonPlan[] = [
  {
    id: '1',
    title: 'Introduction to Basketball',
    date: '2024-03-01',
    grade: '9th',
    objectives: [
      'Learn basic dribbling techniques',
      'Practice shooting form',
      'Understand basic rules',
    ],
    activities: [
      'Dribbling drills',
      'Shooting practice',
      'Small-sided games',
    ],
    equipment: ['Basketballs', 'Cones', 'Whistle'],
    standards: ['PE.9.1.1', 'PE.9.2.2'],
    duration: 45,
    notes: 'Focus on proper form and safety',
  },
  {
    id: '2',
    title: 'Cardiovascular Fitness',
    date: '2024-03-02',
    grade: '10th',
    objectives: [
      'Improve endurance',
      'Learn proper running form',
      'Understand heart rate zones',
    ],
    activities: [
      'Warm-up jog',
      'Interval training',
      'Cool-down stretches',
    ],
    equipment: ['Stopwatch', 'Heart rate monitors'],
    standards: ['PE.10.1.3', 'PE.10.2.1'],
    duration: 60,
    notes: 'Monitor students for fatigue',
  },
];

const DEFAULT_CURRICULA: Curriculum[] = [
  {
    id: '1',
    name: '9th Grade PE',
    description: 'Comprehensive physical education curriculum for 9th grade',
    grade: '9th',
    standards: ['PE.9.1.1', 'PE.9.2.2', 'PE.9.3.1'],
    lessonPlans: ['1'],
  },
  {
    id: '2',
    name: '10th Grade PE',
    description: 'Advanced physical education curriculum for 10th grade',
    grade: '10th',
    standards: ['PE.10.1.3', 'PE.10.2.1', 'PE.10.3.2'],
    lessonPlans: ['2'],
  },
];

const PE_STANDARDS = [
  'PE.9.1.1',
  'PE.9.2.2',
  'PE.9.3.1',
  'PE.10.1.3',
  'PE.10.2.1',
  'PE.10.3.2',
];

export const CurriculumPlannerWidget: React.FC = () => {
  const [lessonPlans, setLessonPlans] = useState<LessonPlan[]>(DEFAULT_LESSON_PLANS);
  const [curricula, setCurricula] = useState<Curriculum[]>(DEFAULT_CURRICULA);
  const [selectedLessonPlan, setSelectedLessonPlan] = useState<LessonPlan | null>(null);
  const [showLessonPlanDialog, setShowLessonPlanDialog] = useState(false);
  const [showCurriculumDialog, setShowCurriculumDialog] = useState(false);
  const [newLessonPlan, setNewLessonPlan] = useState<Partial<LessonPlan>>({
    grade: '9th',
    duration: 45,
  });
  const [newCurriculum, setNewCurriculum] = useState<Partial<Curriculum>>({
    grade: '9th',
  });
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  const addLessonPlan = (lessonPlan: LessonPlan) => {
    setLessonPlans([...lessonPlans, lessonPlan]);
    setShowLessonPlanDialog(false);
    setNewLessonPlan({ grade: '9th', duration: 45 });
  };

  const addCurriculum = (curriculum: Curriculum) => {
    setCurricula([...curricula, curriculum]);
    setShowCurriculumDialog(false);
    setNewCurriculum({ grade: '9th' });
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Curriculum Planner</Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => setShowCurriculumDialog(true)}
              >
                Add Curriculum
              </Button>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowLessonPlanDialog(true)}
              >
                Add Lesson Plan
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
            <Tab label="Lesson Plans" />
            <Tab label="Curricula" />
            <Tab label="Standards" />
          </Tabs>

          {/* Lesson Plans Tab */}
          {activeTab === 0 && (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Title</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Grade</TableCell>
                    <TableCell>Duration</TableCell>
                    <TableCell>Standards</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {lessonPlans.map(plan => (
                    <TableRow key={plan.id}>
                      <TableCell>{plan.title}</TableCell>
                      <TableCell>{new Date(plan.date).toLocaleDateString()}</TableCell>
                      <TableCell>{plan.grade}</TableCell>
                      <TableCell>{plan.duration} minutes</TableCell>
                      <TableCell>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          {plan.standards.map(standard => (
                            <Chip key={standard} label={standard} size="small" />
                          ))}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => {
                            setSelectedLessonPlan(plan);
                            setShowLessonPlanDialog(true);
                          }}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => {
                            setLessonPlans(lessonPlans.filter(p => p.id !== plan.id));
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Curricula Tab */}
          {activeTab === 1 && (
            <Grid container spacing={2}>
              {curricula.map(curriculum => (
                <Grid item xs={12} md={6} key={curriculum.id}>
                  <Paper sx={{ p: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="subtitle1">{curriculum.name}</Typography>
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => {
                            setNewCurriculum(curriculum);
                            setShowCurriculumDialog(true);
                          }}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => {
                            setCurricula(curricula.filter(c => c.id !== curriculum.id));
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {curriculum.description}
                    </Typography>
                    <Box mt={1}>
                      <Typography variant="subtitle2">Standards:</Typography>
                      <Box display="flex" gap={1} flexWrap="wrap">
                        {curriculum.standards.map(standard => (
                          <Chip key={standard} label={standard} size="small" />
                        ))}
                      </Box>
                    </Box>
                    <Box mt={1}>
                      <Typography variant="subtitle2">Lesson Plans:</Typography>
                      <List dense>
                        {curriculum.lessonPlans.map(planId => {
                          const plan = lessonPlans.find(p => p.id === planId);
                          return plan ? (
                            <ListItem key={planId}>
                              <ListItemText
                                primary={plan.title}
                                secondary={new Date(plan.date).toLocaleDateString()}
                              />
                            </ListItem>
                          ) : null;
                        })}
                      </List>
                    </Box>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          )}

          {/* Standards Tab */}
          {activeTab === 2 && (
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Physical Education Standards
              </Typography>
              <List>
                {PE_STANDARDS.map(standard => (
                  <ListItem key={standard}>
                    <ListItemText
                      primary={standard}
                      secondary="Standard description would go here"
                    />
                    <ListItemSecondaryAction>
                      <Checkbox edge="end" />
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}
        </Box>
      </CardContent>

      {/* Add/Edit Lesson Plan Dialog */}
      <Dialog open={showLessonPlanDialog} onClose={() => setShowLessonPlanDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedLessonPlan ? 'Edit Lesson Plan' : 'Add Lesson Plan'}
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Title"
              fullWidth
              defaultValue={selectedLessonPlan?.title}
              onChange={(e) => setNewLessonPlan({ ...newLessonPlan, title: e.target.value })}
            />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  label="Date"
                  type="date"
                  fullWidth
                  defaultValue={selectedLessonPlan?.date || new Date().toISOString().split('T')[0]}
                  onChange={(e) => setNewLessonPlan({ ...newLessonPlan, date: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Grade</InputLabel>
                  <Select
                    value={newLessonPlan.grade || selectedLessonPlan?.grade || '9th'}
                    label="Grade"
                    onChange={(e) => setNewLessonPlan({ ...newLessonPlan, grade: e.target.value })}
                  >
                    <MenuItem value="9th">9th Grade</MenuItem>
                    <MenuItem value="10th">10th Grade</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
            <TextField
              label="Duration (minutes)"
              type="number"
              fullWidth
              defaultValue={selectedLessonPlan?.duration || 45}
              onChange={(e) => setNewLessonPlan({ ...newLessonPlan, duration: parseInt(e.target.value) })}
            />
            <TextField
              label="Objectives"
              multiline
              rows={3}
              fullWidth
              defaultValue={selectedLessonPlan?.objectives.join('\n')}
              onChange={(e) => setNewLessonPlan({ ...newLessonPlan, objectives: e.target.value.split('\n') })}
            />
            <TextField
              label="Activities"
              multiline
              rows={3}
              fullWidth
              defaultValue={selectedLessonPlan?.activities.join('\n')}
              onChange={(e) => setNewLessonPlan({ ...newLessonPlan, activities: e.target.value.split('\n') })}
            />
            <TextField
              label="Equipment"
              multiline
              rows={2}
              fullWidth
              defaultValue={selectedLessonPlan?.equipment.join(', ')}
              onChange={(e) => setNewLessonPlan({ ...newLessonPlan, equipment: e.target.value.split(',').map(item => item.trim()) })}
            />
            <TextField
              label="Standards"
              multiline
              rows={2}
              fullWidth
              defaultValue={selectedLessonPlan?.standards.join(', ')}
              onChange={(e) => setNewLessonPlan({ ...newLessonPlan, standards: e.target.value.split(',').map(item => item.trim()) })}
            />
            <TextField
              label="Notes"
              multiline
              rows={3}
              fullWidth
              defaultValue={selectedLessonPlan?.notes}
              onChange={(e) => setNewLessonPlan({ ...newLessonPlan, notes: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowLessonPlanDialog(false);
            setSelectedLessonPlan(null);
          }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={() => {
              if (newLessonPlan.title && newLessonPlan.date && newLessonPlan.grade) {
                if (selectedLessonPlan) {
                  setLessonPlans(lessonPlans.map(plan =>
                    plan.id === selectedLessonPlan.id
                      ? { ...newLessonPlan as LessonPlan, id: selectedLessonPlan.id }
                      : plan
                  ));
                } else {
                  addLessonPlan({
                    ...newLessonPlan as LessonPlan,
                    id: Date.now().toString(),
                  });
                }
                setShowLessonPlanDialog(false);
                setSelectedLessonPlan(null);
              } else {
                setError('Please fill in all required fields');
              }
            }}
          >
            {selectedLessonPlan ? 'Save' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add/Edit Curriculum Dialog */}
      <Dialog open={showCurriculumDialog} onClose={() => setShowCurriculumDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {newCurriculum.id ? 'Edit Curriculum' : 'Add Curriculum'}
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Name"
              fullWidth
              defaultValue={newCurriculum.name}
              onChange={(e) => setNewCurriculum({ ...newCurriculum, name: e.target.value })}
            />
            <TextField
              label="Description"
              multiline
              rows={3}
              fullWidth
              defaultValue={newCurriculum.description}
              onChange={(e) => setNewCurriculum({ ...newCurriculum, description: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Grade</InputLabel>
              <Select
                value={newCurriculum.grade || '9th'}
                label="Grade"
                onChange={(e) => setNewCurriculum({ ...newCurriculum, grade: e.target.value })}
              >
                <MenuItem value="9th">9th Grade</MenuItem>
                <MenuItem value="10th">10th Grade</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Standards"
              multiline
              rows={2}
              fullWidth
              defaultValue={newCurriculum.standards?.join(', ')}
              onChange={(e) => setNewCurriculum({ ...newCurriculum, standards: e.target.value.split(',').map(item => item.trim()) })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowCurriculumDialog(false);
            setNewCurriculum({ grade: '9th' });
          }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={() => {
              if (newCurriculum.name && newCurriculum.description && newCurriculum.grade) {
                if (newCurriculum.id) {
                  setCurricula(curricula.map(curriculum =>
                    curriculum.id === newCurriculum.id
                      ? { ...newCurriculum as Curriculum }
                      : curriculum
                  ));
                } else {
                  addCurriculum({
                    ...newCurriculum as Curriculum,
                    id: Date.now().toString(),
                    lessonPlans: [],
                  });
                }
                setShowCurriculumDialog(false);
                setNewCurriculum({ grade: '9th' });
              } else {
                setError('Please fill in all required fields');
              }
            }}
          >
            {newCurriculum.id ? 'Save' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}; 