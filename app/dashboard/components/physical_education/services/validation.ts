import { logger } from './logger';
import { monitoringService } from './monitoring';

interface ValidationRule<T> {
  validate: (value: T) => boolean;
  message: string;
}

interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

class ValidationService {
  private static instance: ValidationService;

  private constructor() {}

  public static getInstance(): ValidationService {
    if (!ValidationService.instance) {
      ValidationService.instance = new ValidationService();
    }
    return ValidationService.instance;
  }

  public validateString(value: string, rules: ValidationRule<string>[]): ValidationResult {
    return this.validateValue(value, rules);
  }

  public validateNumber(value: number, rules: ValidationRule<number>[]): ValidationResult {
    return this.validateValue(value, rules);
  }

  public validateDate(value: Date, rules: ValidationRule<Date>[]): ValidationResult {
    return this.validateValue(value, rules);
  }

  public validateObject<T extends object>(value: T, rules: ValidationRule<T>[]): ValidationResult {
    return this.validateValue(value, rules);
  }

  public validateArray<T>(value: T[], rules: ValidationRule<T[]>[]): ValidationResult {
    return this.validateValue(value, rules);
  }

  private validateValue<T>(value: T, rules: ValidationRule<T>[]): ValidationResult {
    const errors: string[] = [];
    
    for (const rule of rules) {
      try {
        if (!rule.validate(value)) {
          errors.push(rule.message);
        }
      } catch (error) {
        monitoringService.trackError(error as Error);
        logger.error('Validation error', { rule: rule.message }, error as Error);
        errors.push(`Validation failed: ${rule.message}`);
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  // Common validation rules
  public required<T>(message: string = 'This field is required'): ValidationRule<T> {
    return {
      validate: (value: T) => {
        if (value === null || value === undefined) return false;
        if (typeof value === 'string') return value.trim().length > 0;
        if (Array.isArray(value)) return value.length > 0;
        return true;
      },
      message,
    };
  }

  public minLength(min: number, message: string = `Minimum length is ${min}`): ValidationRule<string> {
    return {
      validate: (value: string) => value.length >= min,
      message,
    };
  }

  public maxLength(max: number, message: string = `Maximum length is ${max}`): ValidationRule<string> {
    return {
      validate: (value: string) => value.length <= max,
      message,
    };
  }

  public minValue(min: number, message: string = `Minimum value is ${min}`): ValidationRule<number> {
    return {
      validate: (value: number) => value >= min,
      message,
    };
  }

  public maxValue(max: number, message: string = `Maximum value is ${max}`): ValidationRule<number> {
    return {
      validate: (value: number) => value <= max,
      message,
    };
  }

  public pattern(regex: RegExp, message: string = 'Invalid format'): ValidationRule<string> {
    return {
      validate: (value: string) => regex.test(value),
      message,
    };
  }

  public email(message: string = 'Invalid email format'): ValidationRule<string> {
    return this.pattern(/^[^\s@]+@[^\s@]+\.[^\s@]+$/, message);
  }

  public url(message: string = 'Invalid URL format'): ValidationRule<string> {
    return {
      validate: (value: string) => {
        try {
          new URL(value);
          return true;
        } catch {
          return false;
        }
      },
      message,
    };
  }

  public dateRange(min: Date, max: Date, message: string = 'Date is out of range'): ValidationRule<Date> {
    return {
      validate: (value: Date) => value >= min && value <= max,
      message,
    };
  }

  public arrayLength(min: number, max: number, message: string = `Array length must be between ${min} and ${max}`): ValidationRule<any[]> {
    return {
      validate: (value: any[]) => value.length >= min && value.length <= max,
      message,
    };
  }

  public custom<T>(validate: (value: T) => boolean, message: string): ValidationRule<T> {
    return {
      validate,
      message,
    };
  }
}

export const validationService = ValidationService.getInstance(); 