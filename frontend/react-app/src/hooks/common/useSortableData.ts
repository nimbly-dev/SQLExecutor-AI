import { useMemo, useState } from 'react';

/**
 * Interface for sort configuration.
 *
 * @template T - The type of items to sort.
 */
interface SortConfig<T> {
  key: keyof T | null;
  direction: 'ascending' | 'descending';
}

/**
 * Custom hook to sort an array of items.
 *
 * @template T - The type of items to sort.
 * @param items - The array of items to sort.
 * @param config - Optional initial sort configuration.
 * @returns An object containing the sorted items, sort configuration,
 *          and a function to update the sort based on a key.
 */
function useSortableData<T>(items: T[], config: SortConfig<T> = { key: null, direction: 'ascending' }) {
  const [sortConfig, setSortConfig] = useState<SortConfig<T>>(config);

  const sortedItems = useMemo(() => {
    if (!sortConfig.key) return [...items];

    return [...items].sort((a, b) => {
      const key = sortConfig.key!;
      const aVal = a[key];
      const bVal = b[key];

      if (aVal < bVal) {
        return sortConfig.direction === 'ascending' ? -1 : 1;
      }
      if (aVal > bVal) {
        return sortConfig.direction === 'ascending' ? 1 : -1;
      }
      return 0;
    });
  }, [items, sortConfig]);

  /**
   * Function to update the sort configuration based on the provided key.
   *
   * @param key - The key on which to sort the items.
   */
  const requestSort = (key: keyof T) => {
    let direction: 'ascending' | 'descending' = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  return { items: sortedItems, requestSort, sortConfig };
}

export default useSortableData;
