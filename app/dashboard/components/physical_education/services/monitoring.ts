import { configService } from './config';
import { logger } from './logger';
import { storageService } from './storage';

interface SystemMetrics {
  memory: {
    used: number;
    total: number;
    limit: number;
  };
  performance: {
    loadTime: number;
    renderTime: number;
    apiLatency: number;
  };
  cache: {
    size: number;
    hitRate: number;
    missRate: number;
  };
  errors: {
    count: number;
    types: Record<string, number>;
  };
}

interface Alert {
  id: string;
  type: 'error' | 'warning' | 'info';
  message: string;
  timestamp: number;
  metadata?: Record<string, any>;
}

class MonitoringService {
  private static instance: MonitoringService;
  private metrics: SystemMetrics;
  private alerts: Alert[];
  private readonly maxAlerts = 100;
  private readonly checkInterval: number;

  private constructor() {
    this.metrics = {
      memory: { used: 0, total: 0, limit: 0 },
      performance: { loadTime: 0, renderTime: 0, apiLatency: 0 },
      cache: { size: 0, hitRate: 0, missRate: 0 },
      errors: { count: 0, types: {} },
    };
    this.alerts = [];
    this.checkInterval = 60000; // 1 minute
    this.startMonitoring();
  }

  public static getInstance(): MonitoringService {
    if (!MonitoringService.instance) {
      MonitoringService.instance = new MonitoringService();
    }
    return MonitoringService.instance;
  }

  private startMonitoring() {
    setInterval(() => {
      this.checkSystemHealth();
    }, this.checkInterval);
  }

  private async checkSystemHealth() {
    try {
      // Check memory usage
      if (window.performance && (window.performance as any).memory) {
        const memory = (window.performance as any).memory;
        this.metrics.memory = {
          used: memory.usedJSHeapSize,
          total: memory.totalJSHeapSize,
          limit: memory.jsHeapSizeLimit,
        };

        // Alert if memory usage is high
        if (memory.usedJSHeapSize > memory.jsHeapSizeLimit * 0.8) {
          this.addAlert('warning', 'High memory usage detected', {
            used: memory.usedJSHeapSize,
            limit: memory.jsHeapSizeLimit,
          });
        }
      }

      // Check cache performance
      const cacheSize = storageService.getSize();
      this.metrics.cache = {
        size: cacheSize,
        hitRate: 0, // TODO: Implement hit rate tracking
        missRate: 0, // TODO: Implement miss rate tracking
      };

      // Alert if cache size is too large
      if (cacheSize > configService.getPerformanceConfig().maxCacheSize) {
        this.addAlert('warning', 'Cache size is large', {
          size: cacheSize,
          limit: configService.getPerformanceConfig().maxCacheSize,
        });
      }

      // Save metrics
      await this.saveMetrics();
    } catch (error) {
      logger.error('Monitoring error', {}, error as Error);
    }
  }

  private async saveMetrics() {
    try {
      const timestamp = Date.now();
      const key = `metrics_${timestamp}`;
      await storageService.set(key, this.metrics, { 
        ttl: configService.getPerformanceConfig().cacheTTL 
      });
    } catch (error) {
      logger.error('Failed to save metrics', {}, error as Error);
    }
  }

  public addAlert(type: Alert['type'], message: string, metadata?: Record<string, any>) {
    const alert: Alert = {
      id: Math.random().toString(36).substring(2),
      type,
      message,
      timestamp: Date.now(),
      metadata,
    };

    this.alerts.push(alert);
    if (this.alerts.length > this.maxAlerts) {
      this.alerts.shift();
    }

    // Log alert
    if (type === 'error') {
      logger.error(message, metadata);
    } else if (type === 'warning') {
      logger.warn(message, metadata);
    } else {
      logger.info(message, metadata);
    }
  }

  public getMetrics(): SystemMetrics {
    return { ...this.metrics };
  }

  public getAlerts(): Alert[] {
    return [...this.alerts];
  }

  public clearAlerts(): void {
    this.alerts = [];
  }

  public async getHistoricalMetrics(startTime: number, endTime: number): Promise<SystemMetrics[]> {
    try {
      const metrics: SystemMetrics[] = [];
      const keys = await storageService.getKeys();
      
      for (const key of keys) {
        if (key.startsWith('metrics_')) {
          const timestamp = parseInt(key.split('_')[1], 10);
          if (timestamp >= startTime && timestamp <= endTime) {
            const metric = await storageService.get<SystemMetrics>(key);
            if (metric) {
              metrics.push(metric);
            }
          }
        }
      }

      return metrics.sort((a, b) => a.memory.used - b.memory.used);
    } catch (error) {
      logger.error('Failed to get historical metrics', {}, error as Error);
      return [];
    }
  }

  public trackError(error: Error) {
    this.metrics.errors.count++;
    const errorType = error.constructor.name;
    this.metrics.errors.types[errorType] = (this.metrics.errors.types[errorType] || 0) + 1;

    // Alert on error
    this.addAlert('error', error.message, {
      type: errorType,
      stack: error.stack,
    });
  }

  public trackPerformance(metric: keyof SystemMetrics['performance'], value: number) {
    this.metrics.performance[metric] = value;

    // Alert on slow performance
    if (value > 1000) { // 1 second
      this.addAlert('warning', `Slow ${metric} detected`, {
        value,
        metric,
      });
    }
  }
}

export const monitoringService = MonitoringService.getInstance(); 