import React, { createContext, useContext, useState, useEffect } from 'react';
import { Box, useTheme } from '@mui/material';
import { ExternalSessionData } from 'types/authentication/externalUserSessionData';
import { fetchContextSession } from 'services/chatInterface';
import { getSetting } from 'services/tenantSetting';
import { fetchChatInterfaceSettings } from 'services/chatInterfaceSettingsService';
import { toast } from 'react-toastify';
import LeftPanel from 'components/sqlexecutor-playground/left-cards/LeftCards';
import MiddleCards from 'components/sqlexecutor-playground/middle-cards/MiddleCards';
import RightCards from 'components/sqlexecutor-playground/right-cards/RightCards';
import { TransformedSettings } from 'types/chat-interface/chatInterfaceSettings';
import { transformSettingsResponse } from 'hooks/sqlexecutor-playground/right-cards/useSettingsManagement';
import { SchemaSummary } from 'types/schema/schemaType';

interface ContextUserContextType {
  sessionData: ExternalSessionData | null;
  loadContextSession: () => Promise<void>;
  stopImpersonation: () => void;
  isModalOpen: boolean;
  setIsModalOpen: (isOpen: boolean) => void;
  sqlSettings: TransformedSettings | null;
  selectedSchema: SchemaSummary | null;           
  setSelectedSchema: (schema: SchemaSummary | null) => void; 
}

const SQLExecutorContext = createContext<ContextUserContextType | undefined>(undefined);

export const useSQLExecutorContext = () => {
  const context = useContext(SQLExecutorContext);
  if (!context) {
    throw new Error('useSQLExecutorContext must be used within SQLExecutorPlayground');
  }
  return context;
};

function SQLExecutorPlayground() {
  const [sessionData, setSessionData] = useState<ExternalSessionData | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [sqlSettings, setSqlSettings] = useState<TransformedSettings | null>(null);
  const [selectedSchema, setSelectedSchema] = useState<SchemaSummary | null>(null); // new state
  const theme = useTheme();

  const loadContextSession = async () => {
    const sessionId = sessionStorage.getItem('contextUserSessionId');
    if (!sessionId) {
      setSessionData(null);
      setSqlSettings(null);
      return;
    }

    try {
      const apiKeyResponse = await getSetting('API_KEYS', 'TENANT_APPLICATION_TOKEN');
      const apiKey = apiKeyResponse.setting_detail.setting_value;
      const data = await fetchContextSession(sessionId, apiKey);
      setSessionData(data);
      
      // Load settings
      try {
        const settingsResponse = await fetchChatInterfaceSettings(sessionId);
        setSqlSettings(transformSettingsResponse(settingsResponse));
      } catch (error) {
        console.error('Failed to load settings:', error);
        setSqlSettings(null);
      }
    } catch (error) {
      console.error('Session error:', error);
      sessionStorage.removeItem('contextUserSessionId');
      setSessionData(null);
      setSqlSettings(null);
      toast.error('Session expired or invalid. Please log in again.');
    }
  };

  useEffect(() => {
    loadContextSession();
  }, []);

  useEffect(() => {
    const fetchIntegrationType = async () => {
      const storedType = sessionStorage.getItem('chatInterfaceIntegrationType');
      if (!storedType) {
        try {
          const response = await getSetting(
            'FRONTEND_SANDBOX_CHAT_INTERFACE',
            'CHAT_CONTEXT_INTEGRATION_TYPE'
          );
          const integrationType = response.setting_detail.setting_value;
          sessionStorage.setItem('chatInterfaceIntegrationType', integrationType);
        } catch (error) {
          console.error('Error fetching integration type:', error);
        }
      }
    };
    fetchIntegrationType();
  }, []);

  const stopImpersonation = () => {
    sessionStorage.removeItem('contextUserSessionId');
    setSessionData(null);
    setSqlSettings(null);
  };

  const contextValue = {
    sessionData,
    loadContextSession,
    stopImpersonation,
    isModalOpen,
    setIsModalOpen,
    sqlSettings,
    selectedSchema,       // pass in context
    setSelectedSchema     // pass in context
  };

  return (
    <SQLExecutorContext.Provider value={contextValue}>
      <Box 
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            md: '1fr 2fr 1fr'
          },
          gap: { xs: 2, md: 3 },
          padding: 3,
          backgroundColor: theme.palette.mode === 'dark' ? '#2b2b2b' : '#f9f9f9',
        }}
      >
        {/* Left cards: User context card and impersonation modal */}
        <LeftPanel />

        {/* Middle cards: Chat interface and SQL results */}
        <MiddleCards 
          sessionData={sessionData}
          setSessionData={setSessionData}
          selectedSchema={selectedSchema}
          setSelectedSchema={setSelectedSchema}
        />

        {/* Right cards: SQL settings*/}
        <RightCards />
      </Box>
    </SQLExecutorContext.Provider>
  );
}

export default SQLExecutorPlayground;

