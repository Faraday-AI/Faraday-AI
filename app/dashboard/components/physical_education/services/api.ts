import { ApiResponse, PaginatedResponse } from '../types';
import { analyticsService } from './analytics';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:3000/api';
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: Record<string, any>,
    public status?: number
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const retry = async <T>(
  fn: () => Promise<T>,
  retries = MAX_RETRIES,
  delay = RETRY_DELAY
): Promise<T> => {
  try {
    return await fn();
  } catch (error) {
    if (retries === 0) throw error;
    await sleep(delay);
    return retry(fn, retries - 1, delay * 2);
  }
};

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.code || 'UNKNOWN_ERROR',
      errorData.message || 'An unknown error occurred',
      errorData.details,
      response.status
    );
  }
  return response.json();
};

const fetchWithTimeout = async (
  url: string,
  options: RequestInit = {},
  timeout = 10000
): Promise<Response> => {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError('TIMEOUT_ERROR', 'Request timed out');
    }
    throw error;
  }
};

const withPerformanceMonitoring = async <T>(
  operation: string,
  fn: () => Promise<T>
): Promise<T> => {
  const startTime = performance.now();
  try {
    const result = await fn();
    const endTime = performance.now();
    
    analyticsService.recordEvent({
      name: `api_${operation}`,
      category: 'system',
      metadata: {
        duration: endTime - startTime,
        success: true,
      },
    });
    
    return result;
  } catch (error) {
    const endTime = performance.now();
    
    analyticsService.recordEvent({
      name: `api_${operation}_error`,
      category: 'system',
      metadata: {
        duration: endTime - startTime,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      },
    });
    
    throw error;
  }
};

export const apiService = {
  // Progress endpoints
  getProgressData: async (userId: string, category: string, timeRange: string) => {
    return withPerformanceMonitoring('getProgressData', async () => {
      return retry(async () => {
        const response = await fetchWithTimeout(
          `${API_BASE_URL}/progress?userId=${userId}&category=${category}&timeRange=${timeRange}`
        );
        return handleResponse<ApiResponse<PaginatedResponse<any>>>(response);
      });
    });
  },

  getMilestones: async (userId: string, category: string) => {
    return withPerformanceMonitoring('getMilestones', async () => {
      return retry(async () => {
        const response = await fetchWithTimeout(
          `${API_BASE_URL}/milestones?userId=${userId}&category=${category}`
        );
        return handleResponse<ApiResponse<PaginatedResponse<any>>>(response);
      });
    });
  },

  // Assessment endpoints
  getAssessments: async (userId: string, category: string) => {
    return withPerformanceMonitoring('getAssessments', async () => {
      return retry(async () => {
        const response = await fetchWithTimeout(
          `${API_BASE_URL}/assessments?userId=${userId}&category=${category}`
        );
        return handleResponse<ApiResponse<PaginatedResponse<any>>>(response);
      });
    });
  },

  getAssessmentReports: async (userId: string) => {
    return withPerformanceMonitoring('getAssessmentReports', async () => {
      return retry(async () => {
        const response = await fetchWithTimeout(
          `${API_BASE_URL}/assessment-reports?userId=${userId}`
        );
        return handleResponse<ApiResponse<PaginatedResponse<any>>>(response);
      });
    });
  },

  // CRUD operations
  createAssessment: async (userId: string, data: any) => {
    return withPerformanceMonitoring('createAssessment', async () => {
      return retry(async () => {
        const response = await fetchWithTimeout(`${API_BASE_URL}/assessments`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ ...data, userId }),
        });
        return handleResponse<ApiResponse<any>>(response);
      });
    });
  },

  updateAssessment: async (id: string, data: any) => {
    return withPerformanceMonitoring('updateAssessment', async () => {
      return retry(async () => {
        const response = await fetchWithTimeout(`${API_BASE_URL}/assessments/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });
        return handleResponse<ApiResponse<any>>(response);
      });
    });
  },

  deleteAssessment: async (id: string) => {
    return withPerformanceMonitoring('deleteAssessment', async () => {
      return retry(async () => {
        const response = await fetchWithTimeout(`${API_BASE_URL}/assessments/${id}`, {
          method: 'DELETE',
        });
        return handleResponse<ApiResponse<void>>(response);
      });
    });
  },

  // Error handling
  handleError: (error: unknown): ApiError => {
    if (error instanceof ApiError) {
      return error;
    }
    if (error instanceof Error) {
      return new ApiError('UNKNOWN_ERROR', error.message);
    }
    return new ApiError('UNKNOWN_ERROR', 'An unknown error occurred');
  },
}; 