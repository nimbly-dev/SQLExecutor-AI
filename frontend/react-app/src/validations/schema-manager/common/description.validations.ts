import { ValidationResult } from '@sqlexecutor-types/validations/commonValidationResult';

const MAX_DESCRIPTION_LENGTH = 64;

/**
 * Validates column description
 * @param description - The description to validate
 */
export const validateColumnDescription = (description: string): ValidationResult => {
  if (description.length > MAX_DESCRIPTION_LENGTH) {
    return {
      message: `Description must be ${MAX_DESCRIPTION_LENGTH} characters or less`,
      type: 'error'
    };
  }

  return {
    message: '',
    type: 'success'
  };
};
