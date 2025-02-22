import React, { createContext, useContext, useState, ReactNode, useEffect, useRef } from 'react';
import Cookies from 'js-cookie';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import { AuthContextType } from 'types/authentication/authContextType';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const redirecting = useRef<boolean>(false);
  const currentPath = useRef<string>(window.location.pathname);

  const validateToken = (): boolean => {
    const token = Cookies.get('token');
    if (!token) return false;

    try {
      const decoded: any = jwtDecode(token);
      const currentTime = Date.now() / 1000;
      // Add 5 second buffer for token expiration
      return decoded.exp > currentTime + 5;
    } catch {
      return false;
    }
  };

  const clearAuthState = () => {
    Cookies.remove('token');
    Cookies.remove('tenant_id');
    Cookies.remove('user_id');
    Cookies.remove('role');
    setIsLoggedIn(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const handleSessionExpiry = () => {
    if (!redirecting.current) {
      redirecting.current = true;
      clearAuthState();
      toast.error('Session expired. Redirecting to login...');
      navigate('/login', { replace: true });
    }
  };

  const syncAuthState = () => {
    const hasValidToken = validateToken();
    setIsLoggedIn(hasValidToken);
    
    if (!hasValidToken && !redirecting.current) {
      handleSessionExpiry();
    }
  };

  useEffect(() => {
    syncAuthState();
    intervalRef.current = setInterval(syncAuthState, 60000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      redirecting.current = false;
    };
  }, []);

  const login = () => {
    syncAuthState();
    setIsLoggedIn(true);
  };

  const logout = () => {
    clearAuthState();
    toast.success('Logged out successfully!');
    navigate('/login'); 
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
