import { configService } from './config';

interface StorageOptions {
  ttl?: number; // Time to live in milliseconds
  version?: string;
}

class StorageService {
  private static instance: StorageService;
  private storage: Storage;
  private prefix: string;

  private constructor() {
    this.storage = window.localStorage;
    this.prefix = 'faraday_pe_';
  }

  public static getInstance(): StorageService {
    if (!StorageService.instance) {
      StorageService.instance = new StorageService();
    }
    return StorageService.instance;
  }

  public async set<T>(key: string, value: T, options: StorageOptions = {}): Promise<void> {
    try {
      const item = {
        value,
        timestamp: Date.now(),
        ttl: options.ttl,
        version: options.version,
      };
      this.storage.setItem(this.prefix + key, JSON.stringify(item));
    } catch (error) {
      console.error('Storage error:', error);
      this.clearExpired();
    }
  }

  public async get<T>(key: string): Promise<T | null> {
    try {
      const item = this.storage.getItem(this.prefix + key);
      if (!item) return null;

      const { value, timestamp, ttl, version } = JSON.parse(item);
      
      if (ttl && Date.now() - timestamp > ttl) {
        this.remove(key);
        return null;
      }

      return value as T;
    } catch (error) {
      console.error('Storage error:', error);
      return null;
    }
  }

  public remove(key: string): void {
    this.storage.removeItem(this.prefix + key);
  }

  public clear(): void {
    const keys = this.getKeys();
    keys.forEach(key => this.remove(key));
  }

  private clearExpired(): void {
    const keys = this.getKeys();
    keys.forEach(key => {
      const item = this.storage.getItem(this.prefix + key);
      if (item) {
        const { timestamp, ttl } = JSON.parse(item);
        if (ttl && Date.now() - timestamp > ttl) {
          this.remove(key);
        }
      }
    });
  }

  public getKeys(): string[] {
    const keys: string[] = [];
    for (let i = 0; i < this.storage.length; i++) {
      const key = this.storage.key(i);
      if (key?.startsWith(this.prefix)) {
        keys.push(key.substring(this.prefix.length));
      }
    }
    return keys;
  }

  public getSize(): number {
    let total = 0;
    const keys = this.getKeys();
    keys.forEach(key => {
      const item = this.storage.getItem(this.prefix + key);
      if (item) {
        total += item.length * 2; // Approximate size in bytes
      }
    });
    return total;
  }
}

export const storageService = StorageService.getInstance(); 