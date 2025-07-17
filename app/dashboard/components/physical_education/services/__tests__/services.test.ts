import { describe, it, expect, beforeEach } from 'vitest';
import { configService } from '../config';
import { storageService } from '../storage';
import { validationService } from '../validation';
import { securityService } from '../security';
import { cacheService } from '../cache';
import { monitoringService } from '../monitoring';

interface UserData {
  email: string;
  name?: string;
}

describe('Services Integration Tests', () => {
  beforeEach(() => {
    // Clear storage and cache before each test
    storageService.clear();
    cacheService.clear();
    monitoringService.clearAlerts();
  });

  describe('Configuration Service', () => {
    it('should load default configuration', () => {
      const apiConfig = configService.getApiConfig();
      expect(apiConfig.baseUrl).toBeDefined();
      expect(apiConfig.timeout).toBeGreaterThan(0);
      expect(apiConfig.maxRetries).toBeGreaterThan(0);
    });

    it('should check feature flags', () => {
      expect(configService.isFeatureEnabled('offlineMode')).toBeDefined();
      expect(configService.isFeatureEnabled('realtimeUpdates')).toBeDefined();
    });
  });

  describe('Storage Service', () => {
    it('should store and retrieve data', async () => {
      const testData = { key: 'value' };
      await storageService.set('test', testData);
      const retrieved = await storageService.get<typeof testData>('test');
      expect(retrieved).toEqual(testData);
    });

    it('should handle TTL expiration', async () => {
      const testData = { key: 'value' };
      await storageService.set('test', testData, { ttl: 100 });
      await new Promise(resolve => setTimeout(resolve, 150));
      const retrieved = await storageService.get('test');
      expect(retrieved).toBeNull();
    });

    it('should handle large data objects', async () => {
      const largeData = { data: 'x'.repeat(10000) };
      await storageService.set('large', largeData);
      const retrieved = await storageService.get<typeof largeData>('large');
      expect(retrieved).toEqual(largeData);
    });

    it('should handle concurrent operations', async () => {
      const promises = Array(10).fill(null).map(async (_, i) => {
        await storageService.set(`key${i}`, { value: i });
        return storageService.get<{ value: number }>(`key${i}`);
      });
      const results = await Promise.all(promises);
      expect(results).toHaveLength(10);
      results.forEach((result, i) => {
        expect(result).toEqual({ value: i });
      });
    });
  });

  describe('Validation Service', () => {
    it('should validate strings', () => {
      const result = validationService.validateString('test', [
        validationService.required(),
        validationService.minLength(3),
      ]);
      expect(result.isValid).toBe(true);
    });

    it('should validate numbers', () => {
      const result = validationService.validateNumber(5, [
        validationService.minValue(0),
        validationService.maxValue(10),
      ]);
      expect(result.isValid).toBe(true);
    });

    it('should validate emails', () => {
      const result = validationService.validateString('test@example.com', [
        validationService.email(),
      ]);
      expect(result.isValid).toBe(true);
    });

    it('should handle complex validation rules', () => {
      const result = validationService.validateString('test@example.com', [
        validationService.required(),
        validationService.email(),
        validationService.pattern(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/),
      ]);
      expect(result.isValid).toBe(true);
    });

    it('should handle validation errors with custom messages', () => {
      const result = validationService.validateNumber(15, [
        validationService.minValue(0, 'Value must be positive'),
        validationService.maxValue(10, 'Value must be less than or equal to 10'),
      ]);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Value must be less than or equal to 10');
    });
  });

  describe('Security Service', () => {
    it('should encrypt and decrypt data', async () => {
      const data = 'sensitive data';
      const encrypted = await securityService.encrypt(data);
      const decrypted = await securityService.decrypt(encrypted);
      expect(decrypted).toBe(data);
    });

    it('should generate and verify tokens', async () => {
      const payload = { userId: 123 };
      const token = await securityService.generateToken(payload);
      const verified = await securityService.verifyToken(token);
      expect(verified).toEqual(payload);
    });

    it('should handle secure storage', async () => {
      const data = { secret: 'value' };
      await securityService.secureStorageSet('secure', data);
      const retrieved = await securityService.secureStorageGet<typeof data>('secure');
      expect(retrieved).toEqual(data);
    });

    it('should handle encryption of different data types', async () => {
      const testCases = [
        'string',
        JSON.stringify({ key: 'value' }),
        JSON.stringify([1, 2, 3]),
      ];

      for (const data of testCases) {
        const encrypted = await securityService.encrypt(data);
        const decrypted = await securityService.decrypt(encrypted);
        expect(decrypted).toBe(data);
      }
    });

    it('should handle token expiration', async () => {
      const payload = { userId: 123 };
      const token = await securityService.generateToken(payload, { expiresIn: '100ms' });
      await new Promise(resolve => setTimeout(resolve, 150));
      await expect(securityService.verifyToken(token)).rejects.toThrow();
    });
  });

  describe('Cache Service', () => {
    it('should cache and retrieve data', async () => {
      const data = { key: 'value' };
      await cacheService.set('test', data);
      const retrieved = await cacheService.get<typeof data>('test');
      expect(retrieved).toEqual(data);
    });

    it('should handle TTL expiration', async () => {
      const data = { key: 'value' };
      await cacheService.set('test', data, { ttl: 100 });
      await new Promise(resolve => setTimeout(resolve, 150));
      const retrieved = await cacheService.get('test');
      expect(retrieved).toBeNull();
    });

    it('should handle version invalidation', async () => {
      const data = { key: 'value' };
      await cacheService.set('test', data, { version: 'v1' });
      cacheService.invalidateByVersion('v1');
      const retrieved = await cacheService.get('test');
      expect(retrieved).toBeNull();
    });

    it('should handle cache size limits', async () => {
      const maxSize = 1000;
      const largeData = { data: 'x'.repeat(1000) };
      
      await cacheService.set('large1', largeData);
      await cacheService.set('large2', largeData);
      
      const size = cacheService.getSize();
      expect(size).toBeLessThanOrEqual(maxSize);
    });

    it('should handle cache tag invalidation', async () => {
      const data1 = { key: 'value1' };
      const data2 = { key: 'value2' };
      
      await cacheService.set('key1', data1, { tags: ['user'] });
      await cacheService.set('key2', data2, { tags: ['user', 'profile'] });
      
      cacheService.invalidateByTag('user');
      
      const result1 = await cacheService.get('key1');
      const result2 = await cacheService.get('key2');
      
      expect(result1).toBeNull();
      expect(result2).toBeNull();
    });
  });

  describe('Monitoring Service', () => {
    it('should track errors', () => {
      const error = new Error('Test error');
      monitoringService.trackError(error);
      const metrics = monitoringService.getMetrics();
      expect(metrics.errors.count).toBeGreaterThan(0);
    });

    it('should track performance', () => {
      monitoringService.trackPerformance('apiLatency', 100);
      const metrics = monitoringService.getMetrics();
      expect(metrics.performance.apiLatency).toBe(100);
    });

    it('should generate alerts', () => {
      monitoringService.addAlert('warning', 'Test warning');
      const alerts = monitoringService.getAlerts();
      expect(alerts.length).toBeGreaterThan(0);
      expect(alerts[0].type).toBe('warning');
    });

    it('should track system metrics', () => {
      monitoringService.trackPerformance('apiLatency', 100);
      monitoringService.trackPerformance('loadTime', 200);
      monitoringService.trackPerformance('renderTime', 300);
      
      const metrics = monitoringService.getMetrics();
      expect(metrics.performance.apiLatency).toBe(100);
      expect(metrics.performance.loadTime).toBe(200);
      expect(metrics.performance.renderTime).toBe(300);
    });

    it('should handle multiple alerts', () => {
      monitoringService.addAlert('warning', 'Warning 1');
      monitoringService.addAlert('error', 'Error 1');
      monitoringService.addAlert('info', 'Info 1');
      
      const alerts = monitoringService.getAlerts();
      expect(alerts).toHaveLength(3);
      expect(alerts.map(a => a.type)).toEqual(['warning', 'error', 'info']);
    });
  });

  describe('Service Integration', () => {
    it('should handle errors across services', async () => {
      try {
        await securityService.encrypt(null as any);
      } catch (e) {
        monitoringService.trackError(e as Error);
      }
      const metrics = monitoringService.getMetrics();
      expect(metrics.errors.count).toBeGreaterThan(0);
    });

    it('should validate cached data', async () => {
      const data: UserData = { email: 'test@example.com' };
      await cacheService.set('user', data);
      const cached = await cacheService.get<UserData>('user');
      if (cached) {
        const result = validationService.validateString(cached.email, [
          validationService.email(),
        ]);
        expect(result.isValid).toBe(true);
      }
    });

    it('should secure sensitive data', async () => {
      const sensitiveData = { password: 'secret' };
      await securityService.secureStorageSet('user', sensitiveData);
      const encrypted = await storageService.get('user');
      expect(encrypted).not.toEqual(sensitiveData);
      const decrypted = await securityService.secureStorageGet<typeof sensitiveData>('user');
      expect(decrypted).toEqual(sensitiveData);
    });

    it('should handle complex service interactions', async () => {
      // 1. Store sensitive data
      const userData: UserData = {
        email: 'test@example.com',
        name: 'Test User'
      };
      
      // 2. Validate data
      const validationResult = validationService.validateString(userData.email, [
        validationService.email()
      ]);
      expect(validationResult.isValid).toBe(true);
      
      // 3. Store securely
      await securityService.secureStorageSet('user', userData);
      
      // 4. Cache the encrypted data
      const encrypted = await storageService.get('user');
      await cacheService.set('user-cache', encrypted);
      
      // 5. Monitor the operation
      monitoringService.trackPerformance('apiLatency', 100);
      
      // 6. Verify the flow
      const cached = await cacheService.get('user-cache');
      const decrypted = await securityService.secureStorageGet<UserData>('user');
      
      expect(decrypted).toEqual(userData);
      expect(cached).not.toEqual(userData);
      
      const metrics = monitoringService.getMetrics();
      expect(metrics.performance.apiLatency).toBe(100);
    });

    it('should handle error recovery', async () => {
      // 1. Simulate an error
      try {
        await securityService.encrypt(null as any);
      } catch (error) {
        // 2. Track the error
        monitoringService.trackError(error as Error);
        
        // 3. Add an alert
        monitoringService.addAlert('error', 'Encryption failed');
        
        // 4. Verify error handling
        const metrics = monitoringService.getMetrics();
        expect(metrics.errors.count).toBeGreaterThan(0);
        
        const alerts = monitoringService.getAlerts();
        expect(alerts[0].message).toBe('Encryption failed');
      }
    });
  });
}); 