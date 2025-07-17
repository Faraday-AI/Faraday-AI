import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Rating,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  History as HistoryIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer } from 'recharts';

interface Skill {
  id: string;
  name: string;
  category: SkillCategory;
  description: string;
  rubric: RubricCriteria[];
}

interface RubricCriteria {
  id: string;
  name: string;
  description: string;
  weightage: number;
}

interface Assessment {
  id: string;
  studentId: string;
  skillId: string;
  date: string;
  scores: {
    criteriaId: string;
    score: number;
  }[];
  feedback: string;
  overallScore: number;
}

type SkillCategory = 'physical' | 'tactical' | 'technical' | 'mental';

const DEFAULT_SKILLS: Skill[] = [
  {
    id: '1',
    name: 'Running Form',
    category: 'physical',
    description: 'Proper running technique and form',
    rubric: [
      {
        id: '1-1',
        name: 'Posture',
        description: 'Maintains upright posture with relaxed shoulders',
        weightage: 0.3,
      },
      {
        id: '1-2',
        name: 'Arm Movement',
        description: 'Arms swing naturally at 90-degree angles',
        weightage: 0.3,
      },
      {
        id: '1-3',
        name: 'Foot Strike',
        description: 'Proper foot landing and push-off',
        weightage: 0.4,
      },
    ],
  },
  {
    id: '2',
    name: 'Ball Handling',
    category: 'technical',
    description: 'Control and manipulation of the ball',
    rubric: [
      {
        id: '2-1',
        name: 'Control',
        description: 'Maintains consistent control of the ball',
        weightage: 0.4,
      },
      {
        id: '2-2',
        name: 'Movement',
        description: 'Smooth transitions while moving with the ball',
        weightage: 0.3,
      },
      {
        id: '2-3',
        name: 'Vision',
        description: 'Maintains awareness while handling the ball',
        weightage: 0.3,
      },
    ],
  },
];

const SKILL_CATEGORIES: SkillCategory[] = ['physical', 'tactical', 'technical', 'mental'];

export const SkillAssessmentWidget: React.FC = () => {
  const [skills, setSkills] = useState<Skill[]>(DEFAULT_SKILLS);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);
  const [showSkillDialog, setShowSkillDialog] = useState(false);
  const [showAssessmentDialog, setShowAssessmentDialog] = useState(false);
  const [showHistoryDialog, setShowHistoryDialog] = useState(false);
  const [newSkill, setNewSkill] = useState<Partial<Skill>>({
    category: 'physical',
  });
  const [newAssessment, setNewAssessment] = useState<Partial<Assessment>>({
    date: new Date().toISOString().split('T')[0],
    scores: [],
  });
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState<SkillCategory>('physical');

  const addSkill = (skill: Skill) => {
    setSkills([...skills, skill]);
    setShowSkillDialog(false);
    setNewSkill({ category: 'physical' });
  };

  const addAssessment = (assessment: Assessment) => {
    setAssessments([...assessments, assessment]);
    setShowAssessmentDialog(false);
    setNewAssessment({
      date: new Date().toISOString().split('T')[0],
      scores: [],
    });
  };

  const calculateOverallScore = (scores: { criteriaId: string; score: number }[], skill: Skill): number => {
    return scores.reduce((total, score) => {
      const criteria = skill.rubric.find(r => r.id === score.criteriaId);
      return total + (score.score * (criteria?.weightage || 0));
    }, 0);
  };

  const getSkillProgress = (skillId: string): { date: string; score: number }[] => {
    return assessments
      .filter(a => a.skillId === skillId)
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
      .map(a => ({
        date: a.date,
        score: a.overallScore,
      }));
  };

  const exportData = () => {
    const data = {
      skills,
      assessments,
      date: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `skill_assessments_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Skill Assessment</Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowSkillDialog(true)}
              >
                Add Skill
              </Button>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={exportData}
              >
                Export
              </Button>
            </Box>
          </Box>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Category Filter */}
          <FormControl fullWidth>
            <InputLabel>Category</InputLabel>
            <Select
              value={selectedCategory}
              label="Category"
              onChange={(e) => setSelectedCategory(e.target.value as SkillCategory)}
            >
              {SKILL_CATEGORIES.map(category => (
                <MenuItem key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Skills List */}
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Skill</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Last Assessment</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {skills
                  .filter(skill => skill.category === selectedCategory)
                  .map(skill => {
                    const lastAssessment = assessments
                      .filter(a => a.skillId === skill.id)
                      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())[0];
                    return (
                      <TableRow key={skill.id}>
                        <TableCell>{skill.name}</TableCell>
                        <TableCell>
                          <Chip
                            label={skill.category}
                            color={
                              skill.category === 'physical'
                                ? 'primary'
                                : skill.category === 'tactical'
                                ? 'secondary'
                                : skill.category === 'technical'
                                ? 'success'
                                : 'warning'
                            }
                          />
                        </TableCell>
                        <TableCell>{skill.description}</TableCell>
                        <TableCell>
                          {lastAssessment ? (
                            <Box display="flex" alignItems="center" gap={1}>
                              <Rating
                                value={lastAssessment.overallScore / 20}
                                readOnly
                                precision={0.5}
                              />
                              <Typography variant="body2" color="text.secondary">
                                ({lastAssessment.date})
                              </Typography>
                            </Box>
                          ) : (
                            'Not assessed'
                          )}
                        </TableCell>
                        <TableCell>
                          <Box display="flex" gap={1}>
                            <Tooltip title="Assess">
                              <IconButton
                                size="small"
                                onClick={() => {
                                  setSelectedSkill(skill);
                                  setShowAssessmentDialog(true);
                                }}
                              >
                                <AssessmentIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="History">
                              <IconButton
                                size="small"
                                onClick={() => {
                                  setSelectedSkill(skill);
                                  setShowHistoryDialog(true);
                                }}
                              >
                                <HistoryIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  })}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </CardContent>

      {/* Add Skill Dialog */}
      <Dialog open={showSkillDialog} onClose={() => setShowSkillDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Skill</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Skill Name"
              fullWidth
              onChange={(e) => setNewSkill({ ...newSkill, name: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                label="Category"
                value={newSkill.category}
                onChange={(e) => setNewSkill({ ...newSkill, category: e.target.value as SkillCategory })}
              >
                {SKILL_CATEGORIES.map(category => (
                  <MenuItem key={category} value={category}>
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Description"
              multiline
              rows={2}
              fullWidth
              onChange={(e) => setNewSkill({ ...newSkill, description: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSkillDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (newSkill.name && newSkill.category && newSkill.description) {
                addSkill({
                  ...newSkill as Skill,
                  id: Date.now().toString(),
                  rubric: [],
                });
              } else {
                setError('Please fill in all fields');
              }
            }}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Assessment Dialog */}
      <Dialog open={showAssessmentDialog} onClose={() => setShowAssessmentDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Assess Skill: {selectedSkill?.name}</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            {selectedSkill?.rubric.map(criteria => (
              <Box key={criteria.id}>
                <Typography variant="subtitle2">{criteria.name}</Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {criteria.description}
                </Typography>
                <Rating
                  value={newAssessment.scores?.find(s => s.criteriaId === criteria.id)?.score || 0}
                  onChange={(_, value) => {
                    const scores = [...(newAssessment.scores || [])];
                    const index = scores.findIndex(s => s.criteriaId === criteria.id);
                    if (index >= 0) {
                      scores[index].score = value || 0;
                    } else {
                      scores.push({ criteriaId: criteria.id, score: value || 0 });
                    }
                    setNewAssessment({ ...newAssessment, scores });
                  }}
                />
              </Box>
            ))}
            <TextField
              label="Feedback"
              multiline
              rows={3}
              fullWidth
              onChange={(e) => setNewAssessment({ ...newAssessment, feedback: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAssessmentDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (selectedSkill && newAssessment.scores?.length === selectedSkill.rubric.length) {
                const overallScore = calculateOverallScore(newAssessment.scores, selectedSkill);
                addAssessment({
                  ...newAssessment as Assessment,
                  id: Date.now().toString(),
                  skillId: selectedSkill.id,
                  overallScore,
                });
              } else {
                setError('Please complete all criteria assessments');
              }
            }}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* History Dialog */}
      <Dialog open={showHistoryDialog} onClose={() => setShowHistoryDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Skill History: {selectedSkill?.name}</DialogTitle>
        <DialogContent>
          <Box height={300} mt={2}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={selectedSkill ? getSkillProgress(selectedSkill.id) : []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 5]} />
                <ChartTooltip />
                <Line type="monotone" dataKey="score" stroke="#2196F3" />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHistoryDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}; 