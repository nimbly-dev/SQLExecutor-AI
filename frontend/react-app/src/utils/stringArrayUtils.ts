export const convertToStringArray = (value: string | string[]): string[] => {
  if (Array.isArray(value)) {
    return value;
  }
  
  // Split by comma and trim whitespace
  return value
    .split(',')
    .map(item => item.trim())
    .filter(item => item.length > 0);
};

export const isStringArray = (value: unknown): value is string[] => {
  return Array.isArray(value) && value.every(item => typeof item === 'string');
};
