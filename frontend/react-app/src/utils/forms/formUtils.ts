interface Action<T> {
  type: 'SET_FIELD';
  field: keyof T & string;
  value: T[keyof T];
}

type PropertyPath = string | (string | number)[];

/**
 * Safely checks if a value is an object (excluding null and arrays)
 */
const isObject = (value: unknown): value is Record<string, unknown> => {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
};

/**
 * Parses a string path into an array of path segments
 * Handles both dot notation and bracket notation
 * @example
 * parsePropertyPath('users[0].name') // ['users', '0', 'name']
 * parsePropertyPath('deep.nested["key-with-dots"]') // ['deep', 'nested', 'key-with-dots']
 */
export const parsePropertyPath = (path: PropertyPath): string[] => {
  if (Array.isArray(path)) {
    return path.map(String);
  }

  const parts: string[] = [];
  const length = path.length;
  let position = 0;
  let currentPart = '';
  let inBracket = false;
  let inQuote = false;

  while (position < length) {
    const char = path[position];

    if (char === '[' && !inQuote) {
      if (currentPart) parts.push(currentPart);
      currentPart = '';
      inBracket = true;
    } else if (char === ']' && !inQuote) {
      if (currentPart) parts.push(currentPart);
      currentPart = '';
      inBracket = false;
    } else if ((char === '"' || char === "'") && inBracket) {
      inQuote = !inQuote;
    } else if (char === '.' && !inBracket && !inQuote) {
      if (currentPart) parts.push(currentPart);
      currentPart = '';
    } else {
      currentPart += char;
    }
    position++;
  }

  if (currentPart) {
    parts.push(currentPart);
  }

  return parts.map(part => part.trim()).filter(Boolean);
};

/**
 * Type-safe deep clone utility
 */
const deepClone = <T>(obj: T): T => {
  if (!isObject(obj) && !Array.isArray(obj)) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(item => deepClone(item)) as unknown as T;
  }

  const cloned: Record<string, unknown> = {};
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      cloned[key] = deepClone((obj as Record<string, unknown>)[key]);
    }
  }

  return cloned as T;
};

/**
 * Updates an object by a given path safely and immutably
 * @param obj - The object to update
 * @param path - The path to the property to update (dot notation or array)
 * @param value - The new value to set
 * @param options - Configuration options
 * @returns A new object with the updated value
 * @throws {Error} If the path is invalid or the operation is unsafe
 */
export const updateByPath = <T extends Record<string, any>>(
  obj: T,
  path: PropertyPath,
  value: unknown,
  options: {
    strict?: boolean; // If true, throws on invalid paths
    createMissing?: boolean; // If true, creates missing objects in path
  } = { strict: true, createMissing: false }
): T => {
  const segments = parsePropertyPath(path);

  if (segments.length === 0) {
    throw new Error('Invalid path: path cannot be empty');
  }

  // Create a deep clone of the original object to ensure immutability
  const result = deepClone(obj);
  let current: any = result;

  for (let i = 0; i < segments.length - 1; i++) {
    const segment = segments[i];
    const nextSegment = segments[i + 1];
    const isNextNumber = !isNaN(Number(nextSegment));

    if (!(segment in current)) {
      if (!options.createMissing && options.strict) {
        throw new Error(`Invalid path: ${segment} does not exist`);
      }
      // Create appropriate container based on next segment
      current[segment] = isNextNumber ? [] : {};
    }

    if (isObject(current[segment]) || Array.isArray(current[segment])) {
      current = current[segment];
    } else if (options.strict) {
      throw new Error(`Cannot traverse through primitive value at ${segment}`);
    }
  }

  const lastSegment = segments[segments.length - 1];
  current[lastSegment] = value;

  return result;
};

/**
 * Gets a value from an object by path safely
 * @param obj - The object to get the value from
 * @param path - The path to the property
 * @param defaultValue - The default value if the path doesn't exist
 */
export const getByPath = <T extends Record<string, any>, D = undefined>(
  obj: T,
  path: PropertyPath,
  defaultValue?: D
): D | any => {
  const segments = parsePropertyPath(path);
  let current: any = obj;

  for (const segment of segments) {
    if (current == null || typeof current !== 'object') {
      return defaultValue;
    }
    current = current[segment];
  }

  return current === undefined ? defaultValue : current;
};

/**
 * Creates a debounced version of updateByPath
 * @param delay - Delay in milliseconds
 */
export const createDebouncedUpdate = <T extends Record<string, any>>(delay = 300) => {
  let timeoutId: NodeJS.Timeout;
  
  return (
    dispatch: (action: Action<T>) => void,
    field: keyof T & string,
    value: T[keyof T],
    options: Parameters<typeof updateByPath>[3] = {}
  ) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      dispatch({ type: 'SET_FIELD', field, value });
    }, delay);
  };
};

// Optional: Add a memoized version for better performance
export const memoizedUpdateByPath = (() => {
  const cache = new Map<string, any>();
  const MAX_CACHE_SIZE = 100;

  return <T extends Record<string, any>>(
    obj: T,
    path: PropertyPath,
    value: unknown,
    options = { strict: true, createMissing: false }
  ): T => {
    const cacheKey = `${JSON.stringify(obj)}-${path}-${JSON.stringify(value)}`;
    
    if (cache.has(cacheKey)) {
      return cache.get(cacheKey);
    }

    const result = updateByPath(obj, path, value, options);

    if (cache.size >= MAX_CACHE_SIZE) {
      const firstKey = cache.keys().next().value;
      cache.delete(firstKey);
    }

    cache.set(cacheKey, result);
    return result;
  };
})();
