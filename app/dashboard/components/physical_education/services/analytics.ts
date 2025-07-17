import { Category } from '../types';

interface AnalyticsEvent {
  name: string;
  category: Category;
  timestamp: string;
  metadata?: Record<string, any>;
}

interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  apiLatency: number;
  memoryUsage: number;
}

class AnalyticsService {
  private static instance: AnalyticsService;
  private events: AnalyticsEvent[] = [];
  private performanceMetrics: PerformanceMetrics[] = [];

  private constructor() {
    // Initialize performance monitoring
    if (typeof window !== 'undefined') {
      window.addEventListener('load', this.recordLoadTime);
      window.addEventListener('beforeunload', this.flushEvents);
    }
  }

  public static getInstance(): AnalyticsService {
    if (!AnalyticsService.instance) {
      AnalyticsService.instance = new AnalyticsService();
    }
    return AnalyticsService.instance;
  }

  private recordLoadTime = () => {
    const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
    this.recordPerformanceMetric({
      loadTime,
      renderTime: 0, // Will be updated by components
      apiLatency: 0, // Will be updated by API calls
      memoryUsage: (window.performance as any).memory?.usedJSHeapSize || 0,
    });
  };

  public recordEvent(event: Omit<AnalyticsEvent, 'timestamp'>) {
    this.events.push({
      ...event,
      timestamp: new Date().toISOString(),
    });

    // Flush events if we have more than 100
    if (this.events.length > 100) {
      this.flushEvents();
    }
  }

  public recordPerformanceMetric(metric: PerformanceMetrics) {
    this.performanceMetrics.push(metric);

    // Flush metrics if we have more than 50
    if (this.performanceMetrics.length > 50) {
      this.flushPerformanceMetrics();
    }
  }

  private async flushEvents() {
    if (this.events.length === 0) return;

    try {
      // In a real app, this would send to your analytics service
      console.log('Flushing analytics events:', this.events);
      this.events = [];
    } catch (error) {
      console.error('Failed to flush analytics events:', error);
    }
  }

  private async flushPerformanceMetrics() {
    if (this.performanceMetrics.length === 0) return;

    try {
      // In a real app, this would send to your performance monitoring service
      console.log('Flushing performance metrics:', this.performanceMetrics);
      this.performanceMetrics = [];
    } catch (error) {
      console.error('Failed to flush performance metrics:', error);
    }
  }

  public getEvents(): AnalyticsEvent[] {
    return [...this.events];
  }

  public getPerformanceMetrics(): PerformanceMetrics[] {
    return [...this.performanceMetrics];
  }
}

export const analyticsService = AnalyticsService.getInstance(); 