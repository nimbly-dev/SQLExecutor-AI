import { useState, useEffect } from 'react';
import { ExternalSessionData } from 'types/authentication/externalUserSessionData';
import { fetchContextSession, invalidateContextSession } from 'services/chatInterface';
import { getSetting } from 'services/tenantSetting';
import { toast } from 'react-toastify';

export const useContextUser = () => {
  const [sessionData, setSessionData] = useState<ExternalSessionData | null>(null);

  const loadContextSession = async () => {
    const sessionId = sessionStorage.getItem('contextUserSessionId');
    
    if (!sessionId) {
      setSessionData(null);
      return;
    }

    try {
      const apiKeyResponse = await getSetting('API_KEYS', 'TENANT_APPLICATION_TOKEN');
      const apiKey = apiKeyResponse.setting_detail.setting_value;
      const data = await fetchContextSession(sessionId, apiKey);
      setSessionData(data);
    } catch (error) {
      console.error('Session error:', error);
      sessionStorage.removeItem('contextUserSessionId');
      setSessionData(null);
      toast.error('Session expired or invalid. Please log in again.');
    }
  };

  const stopImpersonation = async () => {
    if (sessionData?.session_id) {
      try {
        const apiKeyResponse = await getSetting('API_KEYS', 'TENANT_APPLICATION_TOKEN');
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
    loadContextSession();
  }, []);

  return {
    sessionData,
    setSessionData,
    loadContextSession,
    stopImpersonation
  };
};
