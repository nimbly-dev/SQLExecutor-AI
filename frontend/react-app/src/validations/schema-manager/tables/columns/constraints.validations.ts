import { VALID_CONSTRAINTS_ENUM } from '../../../../types/schema/schemaType';
import { SelectOption } from '../../../../components/common/forms/field-forms/SelectTagsFormField';
import { ValidationResultWithUpdates } from '../../../../types/validations/commonValidationResult';

export type ConstraintValidationResult = ValidationResultWithUpdates<string[]>;

export const validateConstraints = (
  newConstraints: string[],
  currentConstraints: string[]
): ConstraintValidationResult => {
  let updatedConstraints = [...newConstraints];
  
  // Handle PRIMARY KEY constraints
  const hasPrimaryKey = updatedConstraints.includes(VALID_CONSTRAINTS_ENUM.PRIMARY_KEY);
  const addingPrimaryKey = hasPrimaryKey && !currentConstraints.includes(VALID_CONSTRAINTS_ENUM.PRIMARY_KEY);
  
  if (hasPrimaryKey) {
    // Auto-add NOT NULL and UNIQUE when PRIMARY KEY is present
    if (!updatedConstraints.includes(VALID_CONSTRAINTS_ENUM.NOT_NULL)) {
      updatedConstraints.push(VALID_CONSTRAINTS_ENUM.NOT_NULL);
    }
    if (!updatedConstraints.includes(VALID_CONSTRAINTS_ENUM.UNIQUE)) {
      updatedConstraints.push(VALID_CONSTRAINTS_ENUM.UNIQUE);
    }
    
    if (addingPrimaryKey) {
      return {
        message: 'PRIMARY KEY requires NOT NULL and UNIQUE. Applied automatically.',
        type: 'success',
        updatedValue: updatedConstraints
      };
    }
  }

  // Handle PRIMARY KEY and FOREIGN KEY exclusion
  const hasForeignKey = updatedConstraints.includes(VALID_CONSTRAINTS_ENUM.FOREIGN_KEY);
  if (hasPrimaryKey && hasForeignKey) {
    return {
      message: 'A column cannot be both PRIMARY KEY and FOREIGN KEY',
      type: 'error'
    };
  }

  return { 
    message: '', 
    type: 'success', 
    updatedValue: updatedConstraints 
  };
};

export const getAvailableConstraints = (currentConstraints: string[]): SelectOption[] => {
  const hasPrimaryKey = currentConstraints.includes(VALID_CONSTRAINTS_ENUM.PRIMARY_KEY);
  const hasForeignKey = currentConstraints.includes(VALID_CONSTRAINTS_ENUM.FOREIGN_KEY);

  return Object.values(VALID_CONSTRAINTS_ENUM).map(constraint => ({
    value: constraint,
    disabled: (
      // Disable PRIMARY KEY if FOREIGN KEY is selected
      (constraint === VALID_CONSTRAINTS_ENUM.PRIMARY_KEY && hasForeignKey) ||
      // Disable FOREIGN KEY if PRIMARY KEY is selected
      (constraint === VALID_CONSTRAINTS_ENUM.FOREIGN_KEY && hasPrimaryKey) ||
      // Disable NOT NULL and UNIQUE if they're required by PRIMARY KEY
      ((constraint === VALID_CONSTRAINTS_ENUM.NOT_NULL || 
        constraint === VALID_CONSTRAINTS_ENUM.UNIQUE) && 
        hasPrimaryKey)
    )
  }));
};
