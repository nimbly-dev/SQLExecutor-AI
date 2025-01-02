import React, { createContext, useContext, useState, ReactNode, useEffect, useRef } from 'react';
import Cookies from 'js-cookie';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import { AuthContextType } from '../types/authentication/authContextType';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const redirecting = useRef<boolean>(false);

  const validateToken = (): boolean => {
    const token = Cookies.get('token');
    if (!token) return false;

    try {
      const decoded: any = jwtDecode(token);
      const currentTime = Date.now() / 1000;
      return decoded.exp > currentTime;
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
    if (intervalRef.current) clearInterval(intervalRef.current); // Clear interval
  };

  const syncAuthState = () => {
    const token = Cookies.get('token');
    const hasValidToken = validateToken();

    setIsLoggedIn(!!token && hasValidToken);

    if (token && !hasValidToken && !redirecting.current) {
      redirecting.current = true;
      clearAuthState();
      toast.error('Session expired. Redirecting to login...');
      navigate('/login');
    }
  };

  useEffect(() => {
    syncAuthState();

    intervalRef.current = setInterval(() => {
      const hasValidToken = validateToken();
      if (!hasValidToken && !redirecting.current) {
        clearAuthState();
        toast.error('Session expired. Redirecting to login...');
        navigate('/login');
      }
    }, 60000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current); // Cleanup interval
    };
  }, [navigate]);

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
