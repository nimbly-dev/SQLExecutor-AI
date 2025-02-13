import React, { createContext, useContext, useState, useEffect } from 'react';
import { ExternalSessionData } from 'types/authentication/externalUserSessionData';

interface ContextUserContextType {
  sessionData: ExternalSessionData | null;
  loadContextSession: () => Promise<void>;
  stopImpersonation: () => void;
  isModalOpen: boolean;
  setIsModalOpen: (isOpen: boolean) => void;
  loadSettings: (sessionId: string) => Promise<void>;
}

const ContextUserContext = createContext<ContextUserContextType | undefined>(undefined);

// Export the hook
export const useContextUserContext = () => {
  const context = useContext(ContextUserContext);
  if (!context) {
    throw new Error('useContextUserContext must be used within a ContextUserProvider');
  }
  return context;
};
