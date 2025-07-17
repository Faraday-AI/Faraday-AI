import { configService } from './config';
import { storageService } from './storage';
import { analyticsService } from './analytics';
import { logger } from './logger';
import { monitoringService } from './monitoring';

export class Utils {
  public static debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number = configService.getPerformanceConfig().debounceTime
  ): (...args: Parameters<T>) => void {
    let timeout: NodeJS.Timeout;
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  }

  public static throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number = configService.getPerformanceConfig().throttleTime
  ): (...args: Parameters<T>) => void {
    let inThrottle: boolean;
    return (...args: Parameters<T>) => {
      if (!inThrottle) {
        func(...args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  }

  public static async retryWithBackoff<T>(
    fn: () => Promise<T>,
    maxRetries: number = configService.getApiConfig().maxRetries,
    delay: number = configService.getApiConfig().retryDelay
  ): Promise<T> {
    let lastError: Error;
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;
        if (i < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
        }
      }
    }
    throw lastError!;
  }

  public static formatDate(date: Date): string {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  }

  public static formatTime(date: Date): string {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  public static formatDateTime(date: Date): string {
    return `${this.formatDate(date)} at ${this.formatTime(date)}`;
  }

  public static async memoize<T>(
    key: string,
    fn: () => Promise<T>,
    ttl: number = 5 * 60 * 1000 // 5 minutes
  ): Promise<T> {
    const cached = await storageService.get<T>(key);
    if (cached) {
      return cached;
    }

    const result = await fn();
    await storageService.set(key, result, { ttl });
    return result;
  }

  public static async withErrorHandling<T>(
    operation: string,
    fn: () => Promise<T>
  ): Promise<T> {
    try {
      return await fn();
    } catch (error) {
      monitoringService.trackError(error as Error);
      logger.error(`Error in ${operation}`, {}, error as Error);
      throw error;
    }
  }

  public static async withPerformance<T>(
    operation: string,
    fn: () => Promise<T>
  ): Promise<T> {
    const start = performance.now();
    try {
      const result = await fn();
      const duration = performance.now() - start;
      monitoringService.trackPerformance('apiLatency', duration);
      return result;
    } catch (error) {
      const duration = performance.now() - start;
      monitoringService.trackPerformance('apiLatency', duration);
      throw error;
    }
  }

  public static isOnline(): boolean {
    return navigator.onLine;
  }

  public static async wait(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  public static generateId(): string {
    return Math.random().toString(36).substring(2) + Date.now().toString(36);
  }

  public static deepClone<T>(obj: T): T {
    return JSON.parse(JSON.stringify(obj));
  }

  public static mergeObjects<T extends object>(target: T, source: Partial<T>): T {
    return { ...target, ...source };
  }

  public static getRandomInt(min: number, max: number): number {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  public static capitalize(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  public static truncate(str: string, length: number): string {
    return str.length > length ? str.substring(0, length) + '...' : str;
  }

  public static isValidEmail(email: string): boolean {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  }

  public static isValidUrl(url: string): boolean {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  public static formatBytes(bytes: number, decimals = 2): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }

  public static formatDuration(ms: number): string {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ${hours % 24}h`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  }

  public static async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  public static async timeout<T>(
    promise: Promise<T>,
    ms: number
  ): Promise<T> {
    const timeout = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error('Operation timed out')), ms);
    });
    return Promise.race([promise, timeout]);
  }

  public static async parallel<T>(
    tasks: (() => Promise<T>)[]
  ): Promise<T[]> {
    return Promise.all(tasks.map(task => task()));
  }

  public static async sequential<T>(
    tasks: (() => Promise<T>)[]
  ): Promise<T[]> {
    const results: T[] = [];
    for (const task of tasks) {
      results.push(await task());
    }
    return results;
  }
} 