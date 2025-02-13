export type ValidationResultType = 'error' | 'warning' | 'success';

export interface ValidationResult {
  message: string;
  type: ValidationResultType;
}

export interface ValidationResultWithUpdates<T> extends ValidationResult {
  updatedValue?: T;
}
