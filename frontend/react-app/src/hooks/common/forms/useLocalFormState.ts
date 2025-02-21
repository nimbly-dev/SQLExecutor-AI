import { useReducer, useCallback, useRef, useMemo } from 'react';
import { createDebouncedUpdate, memoizedUpdateByPath } from 'utils/forms/formUtils';

type Action<T extends Record<string, any>> =
  | { type: 'SET_FIELD'; field: keyof T & string; value: T[keyof T] }
  | { type: 'RESET'; value: T };

function localFormReducer<T extends Record<string, any>>(state: T, action: Action<T>): T {
  switch (action.type) {
    case 'SET_FIELD':
      return { ...state, [action.field]: action.value } as T;
    case 'RESET':
      return action.value as T;
    default:
      return state;
  }
}

/**
 * A hook for managing local form state with type safety.
 *
 * This hook allows you to manage a form's local state in isolation,
 * updating individual fields without causing parent re-renders.
 * It provides helper functions to update fields, commit the current state,
 * and reset the form to its initial state.
 *
 * @template T - An object type extending Record<string, any> that defines the form state structure.
 * @param initialState - The initial state object for the form.
 * @returns A tuple containing:
 *  - **state:** The current form state.
 *  - **setField:** A function to update an individual field.
 *    - **field:** The key of the field to update.
 *    - **value:** The new value for the field.
 *  - **commit:** A function that returns the current local state for batch committing to the parent.
 *  - **reset:** A function to reset the local state to the initial state.
 *
 * @example
 * ```typescript
 * // Initialize local state with default values.
 * const [formState, setField, commit, reset] = useLocalFormState({ name: '', email: '' });
 *
 * // Update a field.
 * setField('name', 'John');
 *
 * // Batch commit the local state to the parent.
 * const updatedState = commit();
 * updateParentState(updatedState);
 *
 * // Reset the form state to its initial values.
 * reset();
 * ```
 */
export function useLocalFormState<T extends Record<string, any>>(initialState: T) {
  const initialRef = useRef(initialState);
  const [state, dispatch] = useReducer(localFormReducer, initialState);

  const setField = useCallback(<K extends keyof T>(field: K, value: T[K]) => {
    dispatch({ type: 'SET_FIELD', field: field as string, value });
  }, []);
  //To be Deprecated debouncedUpdate
  const debouncedUpdate = useMemo(() => createDebouncedUpdate<T>(200), []);

  const commit = useCallback((): T => state as T, [state]);
  const reset = useCallback(() => {
    dispatch({ type: 'RESET', value: initialRef.current });
  }, []);
  const updateState = useCallback((newState: T) => {
    dispatch({ type: 'RESET', value: newState });
  }, []);

  return [state, setField, commit, reset, updateState, debouncedUpdate] as const;
}

export type UseLocalFormStateReturn<T> = readonly [
  T,
  <K extends keyof T>(field: K, value: T[K]) => void,
  () => T,
  () => void,
  (newState: T) => void
];
