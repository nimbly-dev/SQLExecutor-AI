import { useState, useEffect, useCallback } from 'react';
import { ExternalSessionData } from 'types/authentication/externalUserSessionData';
import { fetchContextSession, invalidateContextSession } from 'services/chatInterface';
import { getSettingDetail } from 'services/tenantSetting';
import { toast } from 'react-toastify';

export const useContextUser = () => {
  const [sessionData, setSessionData] = useState<ExternalSessionData | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchSession = useCallback(async (contextType: string) => {
    const sessionId = sessionStorage.getItem('contextUserSessionId');
    if (!sessionId) {
      setSessionData(null);
      return;
    }

    setLoading(true);
    try {
      const apiKeyResponse = await getSettingDetail('API_KEYS', 'TENANT_APPLICATION_TOKEN');
      const apiKey = apiKeyResponse.setting_detail.setting_value;
      // Make sure context type is properly passed through
      const data = await fetchContextSession(sessionId, apiKey, contextType.toLowerCase());
      setSessionData(data);
    } catch (error) {
      console.error('Session error:', error);
      sessionStorage.removeItem('contextUserSessionId');
      setSessionData(null);
      toast.error('Session expired or invalid. Please log in again.');
    } finally {
      setLoading(false);
    }
  }, []);

  const stopImpersonation = async () => {
    if (sessionData?.session_id) {
      try {
        const apiKeyResponse = await getSettingDetail('API_KEYS', 'TENANT_APPLICATION_TOKEN');
        const apiKey = apiKeyResponse.setting_detail.setting_value;
        
        await invalidateContextSession(sessionData.session_id, apiKey);
        sessionStorage.removeItem('contextUserSessionId');
        setSessionData(null);
      } catch (error) {
        console.error('Error invalidating session:', error);
      }
    }
  };

  useEffect(() => {
    fetchSession('sql');
  }, []);

  return {
    sessionData,
    loading,
    setSessionData,
    fetchSession,
    stopImpersonation
  };
};
