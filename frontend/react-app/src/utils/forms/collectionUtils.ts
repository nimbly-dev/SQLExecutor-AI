interface CollectionOperationsConfig {
  onError?: (message: string) => void;
  onSuccess?: (message: string) => void;
  errorMessages?: Partial<{  
    addFailed: string;
    updateFailed: string;
    removeFailed: string;
    renameFailed: string;
    itemNotFound: string;
  }>;
  successMessages?: Partial<{  
    addSuccess: string;
    updateSuccess: string;
    removeSuccess: string;
    renameSuccess: string;
  }>;
}

const DEFAULT_ERROR_MESSAGES = {
  addFailed: 'Failed to add item',
  updateFailed: 'Failed to update item',  
  removeFailed: 'Failed to remove item',
  renameFailed: 'Failed to rename item',
  itemNotFound: 'Item not found',
} as const;

const DEFAULT_SUCCESS_MESSAGES = {
  addSuccess: 'Item added successfully',
  updateSuccess: 'Item updated successfully', 
  removeSuccess: 'Item removed successfully',
  renameSuccess: 'Item renamed successfully',
} as const;


/**
 * Collection Operations for Nested Form Management
 * ---------------------------------------------
 * Provides CRUD operations for managing collections in nested forms while maintaining
 * both local and parent state synchronization.
 * 
 * Component/State Hierarchy Example:
 * -------------------------
 * SchemaView (Parent)
 * ├── FormUpdateProvider (Global State Updates)
 * │   └── updateField (updates entire schema)
 * │
 * └── SchemaTablesView
 *     ├── useFormUpdate() (gets updateField)
 *     │
 *     └── SchemaFormTablesRelationships
 *         ├── Local State (useLocalFormState)
 *         └── collectionOperations
 *             ├── Local Updates (updateState)
 *             └── Parent Sync (updateField)
 * 
 * Parameters:
 * -----------
 * @param localItems - Record<string, T>
 *   The current collection of items indexed by string keys.
 *   This represents the local state of the collection.
 * 
 * @param updateState - (items: Record<string, T>) => void
 *   Function to update the local state.
 *   Used for immediate UI updates without waiting for parent state updates.
 * 
 * @param updateField - (path: string, value: any) => void
 *   Function from FormUpdateProvider to update parent state.
 *   Handles the synchronization with the global form state.
 * 
 * @param pathPrefix - string
 *   The dot-notation path to the collection in the parent state.
 *   Example: 'tables' or 'tables.columns'
 * 
 * @param propertyName - string
 *   Name of the collection property being managed.
 *   Used for constructing paths and error messages.
 * 
 * @param config - Partial<CollectionOperationsConfig>
 *   Optional configuration for customizing behavior:
 *   - onError: Error callback function
 *   - onSuccess: Success callback function
 *   - errorMessages: Custom error messages
 *   - successMessages: Custom success messages
 * 
 * Returns:
 * --------
 * {
 *   handleAdd: (key: string, item: T) => void,
 *   handleUpdate: (key: string, item: T) => void,
 *   handleRemove: (key: string) => void,
 *   handleRename: (oldKey: string, newKey: string, item: T) => void
 * }
 * 
 * Usage Example:
 * -------------
 * ```typescript
 * const MyNestedFormComponent = ({ pathPrefix, updateField }) => {
 *   // 1. Local State Setup
 *   const [localItems, _, __, ___, updateState] = useLocalFormState(initialItems);
 * 
 *   // 2. Initialize Operations
 *   const { handleAdd, handleUpdate, handleRemove, handleRename } = collectionOperations(
 *     localItems,
 *     updateState,
 *     updateField,
 *     pathPrefix,
 *     'items',
 *     {
 *       onError: (msg) => showFeedback(msg, 'error'),
 *       onSuccess: (msg) => showFeedback(msg, 'success')
 *     }
 *   );
 * 
 *   // 3. Use in Component
 *   return (
 *     <>
 *       <Button onClick={() => handleAdd('new_key', newItem)}>Add</Button>
 *       {items.map(item => (
 *         <ItemCard
 *           key={item.id}
 *           onUpdate={(updated) => handleUpdate(item.id, updated)}
 *           onRemove={() => handleRemove(item.id)}
 *           onRename={(newKey) => handleRename(item.id, newKey, item)}
 *         />
 *       ))}
 *     </>
 *   );
 * };
 * ```
 * 
 * Common Integration Points:
 * ------------------------
 * - EditableCardFormContent - For inline editing with rename support
 * - PaginatedForm - For managing lists of items
 * - useValidationFeedback - For error/success messages
 * - useLocalFormState - For local state management
 * 
 * State Flow:
 * ----------
 * User Action → Local State Update → Collection Operation → Parent State Update → Root State Update
 */
export const collectionOperations = <T extends Record<string, any>>(
  localItems: Record<string, T>,
  updateState: (items: Record<string, T>) => void,
  updateField: (path: string, value: any) => void,
  pathPrefix: string,
  propertyName: string,
  config: Partial<CollectionOperationsConfig> = {}
) => {
  const {
    onError,
    onSuccess,
    errorMessages: customErrorMessages = {},
    successMessages: customSuccessMessages = {},
  } = config;

  // Merge custom messages with defaults
  const errorMessages = { ...DEFAULT_ERROR_MESSAGES, ...customErrorMessages };
  const successMessages = { ...DEFAULT_SUCCESS_MESSAGES, ...customSuccessMessages };

  const handleAdd = (key: string, newItem: T) => {
    try {
      if (localItems[key]) {
        onError?.('Item with this key already exists');
        return;
      }
      const updatedItems = { ...localItems, [key]: newItem };
      updateState(updatedItems);
      updateField(`${pathPrefix}.${propertyName}`, updatedItems);
      onSuccess?.(successMessages.addSuccess);
    } catch (error) {
      onError?.(errorMessages.addFailed);
      console.error(`Error adding item to ${propertyName}:`, error);
    }
  };

  const handleUpdate = (key: string, updatedItem: T) => {
    try {
      if (!localItems[key]) {
        onError?.(errorMessages.itemNotFound);
        return;
      }
      const updatedItems = { 
        ...localItems, 
        [key]: updatedItem 
      };
      updateState(updatedItems);
      updateField(`${pathPrefix}.${propertyName}`, updatedItems);
      onSuccess?.(successMessages.updateSuccess); // Add success message
    } catch (error) {
      onError?.(errorMessages.updateFailed); // Use new error message
      console.error(`Error updating item in ${propertyName}:`, error);
    }
  };

  const handleRemove = (key: string) => {
    try {
      if (!localItems[key]) {
        onError?.(errorMessages.itemNotFound);
        return;
      }

      const updatedItems = { ...localItems };
      delete updatedItems[key];
      updateState(updatedItems);
      updateField(`${pathPrefix}.${propertyName}`, updatedItems);
      onSuccess?.(successMessages.removeSuccess);
      console.debug(`Removed item from ${propertyName}:`, { key });
    } catch (error) {
      onError?.(errorMessages.removeFailed);
      console.error(`Error removing item from ${propertyName}:`, error);
    }
  };

  const handleRename = (oldKey: string, newKey: string, itemData: T) => {
    try {
      if (!localItems[oldKey]) {
        onError?.(errorMessages.itemNotFound);
        return;
      }
      if (localItems[newKey]) {
        onError?.(`${propertyName} with this name already exists`);
        return;
      }

      const basePath = `${pathPrefix}.${propertyName}`;
      const updatedItems = { ...localItems };
      
      // Remove old key and add new one
      delete updatedItems[oldKey];
      updatedItems[newKey] = { ...itemData };

      // Update both local and parent state
      updateState(updatedItems);
      updateField(basePath, updatedItems);
      
      onSuccess?.(successMessages.renameSuccess);
      console.debug(`Renamed item in ${propertyName}:`, { oldKey, newKey });
    } catch (error) {
      onError?.(errorMessages.renameFailed);
      console.error(`Error renaming item in ${propertyName}:`, error);
    }
  };

  return {
    handleAdd,   
    handleUpdate, 
    handleRemove, 
    handleRename  
  };
};
