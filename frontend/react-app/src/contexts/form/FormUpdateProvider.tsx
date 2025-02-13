// FormUpdateContext.tsx
import React, { createContext, useContext } from 'react';
import { Table } from 'types/schema/schemaType';

/**
 * Type definition for the form update context.
 * Provides a generic updateField function to update form values by a given path.
 */
interface FormUpdateContextType {
  /**
   * Updates a field in the form.
   *
   * @param path - A string representing the path to the field (e.g. "columns[2].name").
   * @param value - The new value to assign to the field.
   */
  updateField: (path: string, value: Table | any) => void;
}

// Create the context with a default value of null.
const FormUpdateContext = createContext<FormUpdateContextType | null>(null);

/**
 * Custom hook to access the FormUpdateContext.
 * Must be used within a FormUpdateProvider.
 *
 * @returns The form update context value.
 * @throws If the hook is used outside of a FormUpdateProvider.
 */
export const useFormUpdate = (): FormUpdateContextType => {
  const context = useContext(FormUpdateContext);
  if (!context) {
    throw new Error('useFormUpdate must be used within a FormUpdateProvider');
  }
  return context;
};

interface FormUpdateProviderProps {
  /**
   * A function that updates a form field given a path and a value.
   */
  updateField: (path: string, value: any) => void;
  /**
   * The child nodes that require access to the update function.
   */
  children: React.ReactNode;
}

/**
 * Provider component for the FormUpdateContext.
 * Wrap your nested form components with this provider to reduce prop drilling
 * and centralize form update logic.
 *
 * @param props - Props containing the updateField function and children.
 * @returns A React element that provides the FormUpdateContext.
 */
export const FormUpdateProvider: React.FC<FormUpdateProviderProps> = ({ updateField, children }) => {
  const handleUpdate = (path: string, value: any) => {
    try {
      updateField(path, value);
    } catch (error) {
      console.error('Error updating form field:', error);
    }
  };

  return (
    <FormUpdateContext.Provider value={{ updateField: handleUpdate }}>
      {children}
    </FormUpdateContext.Provider>
  );
};
