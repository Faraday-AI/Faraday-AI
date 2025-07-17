import { useEffect, useRef } from 'react';
import { analyticsService } from '../services/analytics';

interface UsePerformanceOptions {
  componentName: string;
  enabled?: boolean;
}

export function usePerformance({ componentName, enabled = true }: UsePerformanceOptions) {
  const startTime = useRef<number>(0);
  const renderCount = useRef<number>(0);

  useEffect(() => {
    if (!enabled) return;

    // Record initial render time
    const measureRender = () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime.current;

      analyticsService.recordPerformanceMetric({
        loadTime: 0,
        renderTime,
        apiLatency: 0,
        memoryUsage: (window.performance as any).memory?.usedJSHeapSize || 0,
      });

      renderCount.current++;
    };

    // Start measuring
    startTime.current = performance.now();

    // Schedule measurement after render
    requestAnimationFrame(measureRender);

    return () => {
      // Cleanup if needed
    };
  }, [enabled]);

  const startApiMeasurement = () => {
    if (!enabled) return () => {};
    
    const start = performance.now();
    return () => {
      const end = performance.now();
      const latency = end - start;

      analyticsService.recordPerformanceMetric({
        loadTime: 0,
        renderTime: 0,
        apiLatency: latency,
        memoryUsage: (window.performance as any).memory?.usedJSHeapSize || 0,
      });
    };
  };

  return {
    startApiMeasurement,
    renderCount: renderCount.current,
  };
} 