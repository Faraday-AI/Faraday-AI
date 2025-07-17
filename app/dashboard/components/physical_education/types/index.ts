// Common Types
export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

// Progress Types
export interface ProgressData extends BaseEntity {
  date: string;
  value: number;
  target: number;
  category: string;
  userId: string;
}

export interface Milestone extends BaseEntity {
  title: string;
  description: string;
  targetDate: string;
  status: 'completed' | 'in-progress' | 'upcoming';
  progress: number;
  category: string;
  userId: string;
}

export interface ProgressMetrics {
  currentValue: number;
  targetValue: number;
  progressPercentage: number;
  trend: 'up' | 'down' | 'stable';
  lastUpdated: string;
}

// Assessment Types
export interface Assessment extends BaseEntity {
  skill: string;
  level: number;
  lastAssessed: string;
  nextAssessment: string;
  status: 'excellent' | 'good' | 'needs-improvement' | 'poor';
  notes: string;
  category: string;
  userId: string;
  history: AssessmentHistory[];
}

export interface AssessmentHistory {
  date: string;
  level: number;
  notes: string;
}

export interface AssessmentReport extends BaseEntity {
  date: string;
  overallScore: number;
  skills: Assessment[];
  feedback: string;
  recommendations: string[];
  userId: string;
}

// Common Enums
export enum Category {
  FITNESS = 'fitness',
  NUTRITION = 'nutrition',
  HEALTH = 'health',
  SYSTEM = 'system',
  ALL = 'all',
}

export enum TimeRange {
  ONE_MONTH = '1m',
  THREE_MONTHS = '3m',
  SIX_MONTHS = '6m',
  ONE_YEAR = '1y',
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  status: 'success' | 'error';
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  page: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
}

// Error Types
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

// Context Types
export interface DashboardContextType {
  userId: string;
  refreshKey: number;
  setRefreshKey: (key: number) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
} 