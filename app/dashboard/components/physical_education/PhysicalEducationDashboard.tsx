import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Tabs,
  Tab,
  Alert,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { HealthMetricsPanel } from './panels/HealthMetricsPanel';
import { FitnessGoalsPanel } from './panels/FitnessGoalsPanel';
import { WorkoutPlanPanel } from './panels/WorkoutPlanPanel';
import { NutritionPlanPanel } from './panels/NutritionPlanPanel';
import { SafetyPanel } from './panels/SafetyPanel';
import { ActivityPanel } from './panels/ActivityPanel';
import { ProgressPanel } from './panels/ProgressPanel';
import { AssessmentPanel } from './panels/AssessmentPanel';
import { DashboardProvider, useDashboard } from './context/DashboardContext';
import { ErrorBoundary } from './components/ErrorBoundary';
import { LoadingState } from './components/LoadingState';
import { Category } from './types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`pe-tabpanel-${index}`}
      aria-labelledby={`pe-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const DashboardContent: React.FC = () => {
  const { loading, error, refreshKey } = useDashboard();
  const [activeTab, setActiveTab] = React.useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={handleTabChange} aria-label="PE Dashboard tabs">
          <Tab label="Overview" />
          <Tab label="Health Metrics" />
          <Tab label="Fitness Goals" />
          <Tab label="Workouts" />
          <Tab label="Nutrition" />
          <Tab label="Safety" />
          <Tab label="Activities" />
          <Tab label="Progress" />
          <Tab label="Assessments" />
        </Tabs>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ position: 'relative' }}>
        {loading && <LoadingState fullScreen />}

        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <ErrorBoundary>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Quick Stats
                    </Typography>
                    {/* Add summary statistics */}
                  </CardContent>
                </Card>
              </ErrorBoundary>
            </Grid>
            <Grid item xs={12} md={6}>
              <ErrorBoundary>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Recent Activities
                    </Typography>
                    {/* Add recent activities list */}
                  </CardContent>
                </Card>
              </ErrorBoundary>
            </Grid>
            <Grid item xs={12}>
              <ErrorBoundary>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Progress Overview
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={[]}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="progress" stroke="#8884d8" />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </ErrorBoundary>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <ErrorBoundary>
            <HealthMetricsPanel key={refreshKey} />
          </ErrorBoundary>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <ErrorBoundary>
            <FitnessGoalsPanel key={refreshKey} />
          </ErrorBoundary>
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <ErrorBoundary>
            <WorkoutPlanPanel key={refreshKey} />
          </ErrorBoundary>
        </TabPanel>

        <TabPanel value={activeTab} index={4}>
          <ErrorBoundary>
            <NutritionPlanPanel key={refreshKey} />
          </ErrorBoundary>
        </TabPanel>

        <TabPanel value={activeTab} index={5}>
          <ErrorBoundary>
            <SafetyPanel key={refreshKey} />
          </ErrorBoundary>
        </TabPanel>

        <TabPanel value={activeTab} index={6}>
          <ErrorBoundary>
            <ActivityPanel key={refreshKey} />
          </ErrorBoundary>
        </TabPanel>

        <TabPanel value={activeTab} index={7}>
          <ErrorBoundary>
            <ProgressPanel key={refreshKey} />
          </ErrorBoundary>
        </TabPanel>

        <TabPanel value={activeTab} index={8}>
          <ErrorBoundary>
            <AssessmentPanel key={refreshKey} />
          </ErrorBoundary>
        </TabPanel>
      </Box>
    </Box>
  );
};

export const PhysicalEducationDashboard: React.FC = () => {
  // In a real app, this would come from authentication
  const userId = 'current-user-id';

  return (
    <DashboardProvider userId={userId}>
      <ErrorBoundary>
        <DashboardContent />
      </ErrorBoundary>
    </DashboardProvider>
  );
}; 