import { configService } from './config';
import { logger } from './logger';
import { storageService } from './storage';

interface CacheOptions {
  ttl?: number;
  version?: string;
  tags?: string[];
}

interface CacheEntry<T> {
  value: T;
  timestamp: number;
  ttl?: number;
  version?: string;
  tags?: string[];
}

class CacheService {
  private static instance: CacheService;
  private cache: Map<string, CacheEntry<any>>;
  private readonly maxSize: number;
  private readonly cleanupInterval: number;

  private constructor() {
    this.cache = new Map();
    this.maxSize = configService.getPerformanceConfig().maxCacheSize;
    this.cleanupInterval = 60000; // 1 minute
    this.startCleanup();
  }

  public static getInstance(): CacheService {
    if (!CacheService.instance) {
      CacheService.instance = new CacheService();
    }
    return CacheService.instance;
  }

  public async get<T>(key: string): Promise<T | null> {
    try {
      const entry = this.cache.get(key);
      if (!entry) {
        // Try to get from storage
        const stored = await storageService.get<CacheEntry<T>>(key);
        if (stored) {
          this.cache.set(key, stored);
          return this.checkEntry(key, stored);
        }
        return null;
      }
      return this.checkEntry(key, entry);
    } catch (error) {
      logger.error('Cache get error', { key }, error as Error);
      return null;
    }
  }

  public async set<T>(key: string, value: T, options: CacheOptions = {}): Promise<void> {
    try {
      const entry: CacheEntry<T> = {
        value,
        timestamp: Date.now(),
        ttl: options.ttl,
        version: options.version,
        tags: options.tags,
      };

      this.cache.set(key, entry);
      await storageService.set(key, entry, { ttl: options.ttl });

      // Check cache size
      if (this.getSize() > this.maxSize) {
        this.cleanup();
      }
    } catch (error) {
      logger.error('Cache set error', { key }, error as Error);
    }
  }

  public remove(key: string): void {
    this.cache.delete(key);
    storageService.remove(key);
  }

  public clear(): void {
    this.cache.clear();
    storageService.clear();
  }

  public invalidateByTag(tag: string): void {
    const entries = Array.from(this.cache.entries());
    for (const [key, entry] of entries) {
      if (entry.tags?.includes(tag)) {
        this.remove(key);
      }
    }
  }

  public invalidateByVersion(version: string): void {
    const entries = Array.from(this.cache.entries());
    for (const [key, entry] of entries) {
      if (entry.version === version) {
        this.remove(key);
      }
    }
  }

  public getSize(): number {
    let size = 0;
    const entries = Array.from(this.cache.values());
    for (const entry of entries) {
      size += JSON.stringify(entry).length;
    }
    return size;
  }

  private startCleanup(): void {
    setInterval(() => {
      this.cleanup();
    }, this.cleanupInterval);
  }

  private cleanup(): void {
    const now = Date.now();
    const entries = Array.from(this.cache.entries());
    
    // Remove expired entries
    for (const [key, entry] of entries) {
      if (entry.ttl && now - entry.timestamp > entry.ttl) {
        this.remove(key);
      }
    }

    // Remove oldest entries if still over size limit
    if (this.getSize() > this.maxSize) {
      const sortedEntries = entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
      for (const [key] of sortedEntries) {
        this.remove(key);
        if (this.getSize() <= this.maxSize) break;
      }
    }
  }

  private checkEntry<T>(key: string, entry: CacheEntry<T>): T | null {
    const now = Date.now();
    if (entry.ttl && now - entry.timestamp > entry.ttl) {
      this.remove(key);
      return null;
    }
    return entry.value;
  }

  public async memoize<T>(
    key: string,
    fn: () => Promise<T>,
    options: CacheOptions = {}
  ): Promise<T> {
    const cached = await this.get<T>(key);
    if (cached) {
      return cached;
    }

    const result = await fn();
    await this.set(key, result, options);
    return result;
  }
}

export const cacheService = CacheService.getInstance(); 