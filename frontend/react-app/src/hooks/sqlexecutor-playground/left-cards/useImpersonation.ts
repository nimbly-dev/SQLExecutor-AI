import { useState, useCallback } from 'react';
import { ExternalContextUserRow } from '../../../types/chat-interface/contextUsers';
import { getUsersContext, createContextSession } from '../../../services/chatInterface';
import { getSetting } from '../../../services/tenantSetting';

export const useImpersonation = (onSessionCreated: () => void) => {
  const [users, setUsers] = useState<ExternalContextUserRow[]>([]);
  const [identifierField, setIdentifierField] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [totalCount, setTotalCount] = useState<number>(0);

  const fetchUsers = useCallback(async (currentPage: number, limit: number) => {
    setIsLoading(true);
    try {
      const response = await getUsersContext(currentPage + 1, 'ASC', limit);
      setUsers(response.data);
      setTotalCount(response.total_count);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleUserSelect = async (user: ExternalContextUserRow) => {
    try {
      const apiKeyResponse = await getSetting('API_KEYS', 'TENANT_APPLICATION_TOKEN');
      const apiKey = apiKeyResponse.setting_detail.setting_value;

      const sessionData = await createContextSession(user.user_identifier, apiKey);
      
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
