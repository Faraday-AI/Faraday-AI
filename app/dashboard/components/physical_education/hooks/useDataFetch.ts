import { useState, useEffect, useCallback, useRef } from 'react';
import { apiService } from '../services/api';
import { ApiResponse } from '../types';

interface UseDataFetchOptions<T> {
  initialData?: T;
  enabled?: boolean;
  cacheTime?: number;
  staleTime?: number;
}

interface UseDataFetchResult<T> {
  data: T | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

const CACHE = new Map<string, { data: any; timestamp: number }>();

export function useDataFetch<T>(
  key: string,
  fetchFn: () => Promise<ApiResponse<T>>,
  options: UseDataFetchOptions<T> = {}
): UseDataFetchResult<T> {
  const {
    initialData = null,
    enabled = true,
    cacheTime = 5 * 60 * 1000, // 5 minutes
    staleTime = 30 * 1000, // 30 seconds
  } = options;

  const [data, setData] = useState<T | null>(initialData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const mountedRef = useRef(true);

  const fetchData = useCallback(async () => {
    if (!enabled) return;

    const cachedData = CACHE.get(key);
    const now = Date.now();

    if (
      cachedData &&
      now - cachedData.timestamp < cacheTime &&
      now - cachedData.timestamp < staleTime
    ) {
      setData(cachedData.data);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetchFn();
      const newData = response.data;

      if (mountedRef.current) {
        setData(newData);
        CACHE.set(key, { data: newData, timestamp: now });
      }
    } catch (err) {
      if (mountedRef.current) {
        setError(apiService.handleError(err));
      }
    } finally {
      if (mountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [key, fetchFn, enabled, cacheTime, staleTime]);

  useEffect(() => {
    mountedRef.current = true;
    fetchData();

    return () => {
      mountedRef.current = false;
    };
  }, [fetchData]);

  const refetch = useCallback(async () => {
    CACHE.delete(key);
    await fetchData();
  }, [key, fetchData]);

  return { data, isLoading, error, refetch };
} 