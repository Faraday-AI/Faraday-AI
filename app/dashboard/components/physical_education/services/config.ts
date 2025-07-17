import { Category } from '../types';

interface Config {
  api: {
    baseUrl: string;
    timeout: number;
    maxRetries: number;
    retryDelay: number;
  };
  analytics: {
    enabled: boolean;
    maxEvents: number;
    sampleRate: number;
  };
  performance: {
    cacheTTL: number;
    maxCacheSize: number;
    debounceTime: number;
    throttleTime: number;
  };
  features: {
    offlineMode: boolean;
    realtimeUpdates: boolean;
    errorTracking: boolean;
    performanceMonitoring: boolean;
  };
}

class ConfigService {
  private static instance: ConfigService;
  private config: Config;

  private constructor() {
    this.config = {
      api: {
        baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000',
        timeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '5000', 10),
        maxRetries: parseInt(process.env.NEXT_PUBLIC_API_MAX_RETRIES || '3', 10),
        retryDelay: parseInt(process.env.NEXT_PUBLIC_API_RETRY_DELAY || '1000', 10),
      },
      analytics: {
        enabled: process.env.NEXT_PUBLIC_ANALYTICS_ENABLED === 'true',
        maxEvents: parseInt(process.env.NEXT_PUBLIC_ANALYTICS_MAX_EVENTS || '1000', 10),
        sampleRate: parseFloat(process.env.NEXT_PUBLIC_ANALYTICS_SAMPLE_RATE || '1.0'),
      },
      performance: {
        cacheTTL: parseInt(process.env.NEXT_PUBLIC_CACHE_TTL || '300000', 10), // 5 minutes
        maxCacheSize: parseInt(process.env.NEXT_PUBLIC_MAX_CACHE_SIZE || '10485760', 10), // 10MB
        debounceTime: parseInt(process.env.NEXT_PUBLIC_DEBOUNCE_TIME || '300', 10),
        throttleTime: parseInt(process.env.NEXT_PUBLIC_THROTTLE_TIME || '1000', 10),
      },
      features: {
        offlineMode: process.env.NEXT_PUBLIC_OFFLINE_MODE === 'true',
        realtimeUpdates: process.env.NEXT_PUBLIC_REALTIME_UPDATES === 'true',
        errorTracking: process.env.NEXT_PUBLIC_ERROR_TRACKING === 'true',
        performanceMonitoring: process.env.NEXT_PUBLIC_PERFORMANCE_MONITORING === 'true',
      },
    };
  }

  public static getInstance(): ConfigService {
    if (!ConfigService.instance) {
      ConfigService.instance = new ConfigService();
    }
    return ConfigService.instance;
  }

  public getApiConfig() {
    return this.config.api;
  }

  public getAnalyticsConfig() {
    return this.config.analytics;
  }

  public getPerformanceConfig() {
    return this.config.performance;
  }

  public isFeatureEnabled(feature: keyof Config['features']): boolean {
    return this.config.features[feature];
  }

  public updateConfig(newConfig: Partial<Config>) {
    this.config = {
      ...this.config,
      ...newConfig,
    };
  }
}

export const configService = ConfigService.getInstance(); 