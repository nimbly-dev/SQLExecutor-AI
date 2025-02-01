import { useState, useCallback } from 'react';
import { ExternalContextUserRow } from '../../../types/chat-interface/contextUsers';
import { getUsersContext, createContextSession } from '../../../services/chatInterface';
import { getSetting } from '../../../services/tenantSetting';

/**
 * Custom hook for user impersonation.
 * @param onSessionCreated Callback invoked when a new session is successfully created.
 */
export const useImpersonation = (onSessionCreated: () => void) => {
  const [users, setUsers] = useState<ExternalContextUserRow[]>([]);
  const [identifierField, setIdentifierField] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [totalCount, setTotalCount] = useState<number>(0);

  /**
   * Fetch users given the current page, limit, and schema.
   * @param currentPage Current page number.
   * @param limit Number of items per page.
   * @param schema Schema name to filter users.
   */
  const fetchUsers = useCallback(async (currentPage: number, limit: number, schema: string) => {
    setIsLoading(true);
    try {
      const response = await getUsersContext(currentPage + 1, 'ASC', limit, schema);
      setUsers(response.data);
      setTotalCount(response.total_count);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Handle user selection and create a context session.
   * @param user The selected user.
   * @param schema Schema name required for context session.
   */
  const handleUserSelect = async (user: ExternalContextUserRow, schema: string) => {
    console.log('handleUserSelect called with:', user, schema);

    const extractedIdentifier = user.context_identifier;
    if (!extractedIdentifier) {
      console.error('Selected user does not have a valid identifier.');
      return;
    }

    try {
      const apiKeyResponse = await getSetting('API_KEYS', 'TENANT_APPLICATION_TOKEN');
      const apiKey = apiKeyResponse.setting_detail.setting_value;
      const sessionData = await createContextSession(extractedIdentifier, apiKey, schema);
      console.log('Session data received:', sessionData);
      
      if (sessionData && sessionData.session_id) {
        sessionStorage.setItem('contextUserSessionId', sessionData.session_id);
        onSessionCreated();
      } else {
        throw new Error('Invalid session data received');
      }
    } catch (error) {
      console.error('Error handling user selection:', error);
    }
  };

  const fetchIdentifierField = async () => {
    try {
      const response = await getSetting(
        'FRONTEND_SANDBOX_CHAT_INTERFACE',
        'CHAT_CONTEXT_DISPLAY_IDENTIFIER_FIELD'
      );
      setIdentifierField(response.setting_detail.setting_value);
    } catch (error) {
      console.error('Error fetching identifier field:', error);
    }
  };

  return {
    users,
    identifierField,
    isLoading,
    isTransitioning,
    totalCount,
    setUsers,
    setIsLoading,
    setIsTransitioning,
    fetchUsers,
    handleUserSelect,
    fetchIdentifierField,
  };
};
