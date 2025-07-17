import { configService } from './config';
import { storageService } from './storage';
import { analyticsService } from './analytics';

type LogLevel = 'debug' | 'info' | 'warn' | 'error';
type LogContext = Record<string, any>;

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: LogContext;
  stack?: string;
}

class Logger {
  private static instance: Logger;
  private logs: LogEntry[] = [];
  private readonly maxLogs = 1000;
  private readonly logLevels: Record<LogLevel, number> = {
    debug: 0,
    info: 1,
    warn: 2,
    error: 3,
  };

  private constructor() {
    // Initialize logging
    if (typeof window !== 'undefined') {
      window.addEventListener('error', this.handleGlobalError);
      window.addEventListener('unhandledrejection', this.handleUnhandledRejection);
    }
  }

  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  private handleGlobalError = (event: ErrorEvent) => {
    this.error('Unhandled error', {
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      error: event.error,
    });
  };

  private handleUnhandledRejection = (event: PromiseRejectionEvent) => {
    this.error('Unhandled promise rejection', {
      reason: event.reason,
    });
  };

  private shouldLog(level: LogLevel): boolean {
    const config = configService.getConfig();
    const minLevel = config.performance.enabled ? 'debug' : 'info';
    return this.logLevels[level] >= this.logLevels[minLevel];
  }

  private async log(level: LogLevel, message: string, context?: LogContext, error?: Error) {
    if (!this.shouldLog(level)) return;

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      stack: error?.stack,
    };

    // Add to in-memory logs
    this.logs.push(entry);
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    // Store in localStorage for persistence
    await storageService.set('logs', this.logs, { ttl: 24 * 60 * 60 * 1000 }); // 24 hours

    // Record in analytics if error
    if (level === 'error') {
      analyticsService.recordEvent({
        name: 'error_logged',
        category: 'system',
        metadata: {
          message,
          context,
          stack: error?.stack,
        },
      });
    }

    // Console logging
    const logFn = console[level] || console.log;
    logFn(`[${level.toUpperCase()}] ${message}`, context || '', error || '');
  }

  public debug(message: string, context?: LogContext) {
    this.log('debug', message, context);
  }

  public info(message: string, context?: LogContext) {
    this.log('info', message, context);
  }

  public warn(message: string, context?: LogContext) {
    this.log('warn', message, context);
  }

  public error(message: string, context?: LogContext, error?: Error) {
    this.log('error', message, context, error);
  }

  public async getLogs(level?: LogLevel): Promise<LogEntry[]> {
    const logs = await storageService.get<LogEntry[]>('logs') || [];
    return level ? logs.filter(log => this.logLevels[log.level] >= this.logLevels[level]) : logs;
  }

  public async clearLogs(): Promise<void> {
    this.logs = [];
    await storageService.remove('logs');
  }

  public async exportLogs(): Promise<string> {
    const logs = await this.getLogs();
    return JSON.stringify(logs, null, 2);
  }
}

export const logger = Logger.getInstance(); 