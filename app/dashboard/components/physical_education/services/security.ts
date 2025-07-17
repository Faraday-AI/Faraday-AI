import { configService } from './config';
import { logger } from './logger';
import { storageService } from './storage';

interface SecurityOptions {
  expiresIn?: string;
  algorithm?: string;
}

class SecurityService {
  private static instance: SecurityService;
  private secretKey: string;

  private constructor() {
    this.secretKey = process.env.NEXT_PUBLIC_SECRET_KEY || 'default-secret-key';
  }

  public static getInstance(): SecurityService {
    if (!SecurityService.instance) {
      SecurityService.instance = new SecurityService();
    }
    return SecurityService.instance;
  }

  public async encrypt(data: string): Promise<string> {
    try {
      const encoder = new TextEncoder();
      const key = await this.getKey();
      const iv = crypto.getRandomValues(new Uint8Array(12));
      const encodedData = encoder.encode(data);

      const encryptedData = await crypto.subtle.encrypt(
        {
          name: 'AES-GCM',
          iv,
        },
        key,
        encodedData
      );

      const encryptedArray = new Uint8Array(encryptedData);
      const result = new Uint8Array(iv.length + encryptedArray.length);
      result.set(iv);
      result.set(encryptedArray, iv.length);

      return btoa(String.fromCharCode(...result));
    } catch (error) {
      logger.error('Encryption error', {}, error as Error);
      throw new Error('Failed to encrypt data');
    }
  }

  public async decrypt(encryptedData: string): Promise<string> {
    try {
      const decoder = new TextDecoder();
      const key = await this.getKey();
      const encryptedArray = Uint8Array.from(atob(encryptedData), c => c.charCodeAt(0));
      const iv = encryptedArray.slice(0, 12);
      const data = encryptedArray.slice(12);

      const decryptedData = await crypto.subtle.decrypt(
        {
          name: 'AES-GCM',
          iv,
        },
        key,
        data
      );

      return decoder.decode(decryptedData);
    } catch (error) {
      logger.error('Decryption error', {}, error as Error);
      throw new Error('Failed to decrypt data');
    }
  }

  public async hash(data: string): Promise<string> {
    try {
      const encoder = new TextEncoder();
      const encodedData = encoder.encode(data);
      const hashBuffer = await crypto.subtle.digest('SHA-256', encodedData);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    } catch (error) {
      logger.error('Hashing error', {}, error as Error);
      throw new Error('Failed to hash data');
    }
  }

  public async generateToken(payload: Record<string, any>, options: SecurityOptions = {}): Promise<string> {
    try {
      const header = {
        alg: options.algorithm || 'HS256',
        typ: 'JWT',
      };

      const encodedHeader = btoa(JSON.stringify(header));
      const encodedPayload = btoa(JSON.stringify(payload));
      const signature = await this.hash(`${encodedHeader}.${encodedPayload}`);

      return `${encodedHeader}.${encodedPayload}.${signature}`;
    } catch (error) {
      logger.error('Token generation error', {}, error as Error);
      throw new Error('Failed to generate token');
    }
  }

  public async verifyToken(token: string): Promise<Record<string, any>> {
    try {
      const [encodedHeader, encodedPayload, signature] = token.split('.');
      const expectedSignature = await this.hash(`${encodedHeader}.${encodedPayload}`);

      if (signature !== expectedSignature) {
        throw new Error('Invalid token signature');
      }

      return JSON.parse(atob(encodedPayload));
    } catch (error) {
      logger.error('Token verification error', {}, error as Error);
      throw new Error('Failed to verify token');
    }
  }

  public async secureStorageSet(key: string, value: any, options: SecurityOptions = {}): Promise<void> {
    try {
      const encryptedValue = await this.encrypt(JSON.stringify(value));
      await storageService.set(key, encryptedValue, {
        ttl: options.expiresIn ? this.parseExpiresIn(options.expiresIn) : undefined,
      });
    } catch (error) {
      logger.error('Secure storage set error', {}, error as Error);
      throw new Error('Failed to securely store data');
    }
  }

  public async secureStorageGet<T>(key: string): Promise<T | null> {
    try {
      const encryptedValue = await storageService.get<string>(key);
      if (!encryptedValue) return null;

      const decryptedValue = await this.decrypt(encryptedValue);
      return JSON.parse(decryptedValue) as T;
    } catch (error) {
      logger.error('Secure storage get error', {}, error as Error);
      return null;
    }
  }

  public async secureStorageRemove(key: string): Promise<void> {
    try {
      await storageService.remove(key);
    } catch (error) {
      logger.error('Secure storage remove error', {}, error as Error);
      throw new Error('Failed to remove secure data');
    }
  }

  private async getKey(): Promise<CryptoKey> {
    const encoder = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      encoder.encode(this.secretKey),
      { name: 'PBKDF2' },
      false,
      ['deriveBits', 'deriveKey']
    );

    return crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: encoder.encode('salt'),
        iterations: 100000,
        hash: 'SHA-256',
      },
      keyMaterial,
      { name: 'AES-GCM', length: 256 },
      false,
      ['encrypt', 'decrypt']
    );
  }

  private parseExpiresIn(expiresIn: string): number {
    const value = parseInt(expiresIn);
    if (expiresIn.endsWith('s')) return value * 1000;
    if (expiresIn.endsWith('m')) return value * 60 * 1000;
    if (expiresIn.endsWith('h')) return value * 60 * 60 * 1000;
    if (expiresIn.endsWith('d')) return value * 24 * 60 * 60 * 1000;
    return value;
  }
}

export const securityService = SecurityService.getInstance(); 