import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute: React.FC = () => {
  const { isLoggedIn } = useAuth();
  const token = localStorage.getItem('token'); // Check token existence

  return isLoggedIn && token ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
