import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { lightTheme } from './themes/lightTheme';
import { darkTheme } from './themes/darkTheme';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import MainLayout from './components/layout/MainLayout';
import LoginPage from 'pages/LoginPage';
import SQLExecutorPlayground from 'pages/SQLExecutorPlayground';
import SchemaManager from 'pages/SchemaManager';
import LandingPage from 'pages/LandingPage';
import SchemaView from 'pages/schema-manager/SchemaView';
import ToastProvider from './components/common/ToastProvider';
import './styles/themes/index.scss'; 
import SchemaAddWizard from 'pages/schema-manager/SchemaAddWizard';
import RulesetManager from 'pages/RulesetManager';
import RulesetView from 'pages/ruleset-manager/RulesetView';
import RulesetAddWizard from 'pages/ruleset-manager/RulesetAddWizard';

// Protected Route Component
const ProtectedRoute: React.FC = () => {
  const { isLoggedIn } = useAuth();
  return isLoggedIn ? <Outlet /> : <Navigate to="/login" replace />;
};

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false);
  const toggleTheme = () => setDarkMode(!darkMode);

  return (
    <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
      <CssBaseline />
      <ToastProvider />
      <ToastContainer position="top-right" autoClose={3000} />
      <Router>
        <AuthProvider>
          <Routes>
            {/* Public Route */}
            <Route path="/login" element={<LoginPage />} />

            {/* Protected Routes */}
            <Route element={<ProtectedRoute />}>
              <Route element={<MainLayout darkMode={darkMode} toggleTheme={toggleTheme} />}>
                <Route path="/getting-started" element={<LandingPage />} />
                <Route path="/sqlexecutor-playground" element={<SQLExecutorPlayground />} />
                <Route path="/schema-manager" element={<SchemaManager />} />
                {/*Schema Child-links below*/}
                <Route path="/schema-manager/view/:schema_name" element={<SchemaView />} />
                <Route path="/schema-manager/add" element={<SchemaAddWizard />} />

                <Route path="/ruleset-manager" element={<RulesetManager />} />
                {/*Ruleset Child-links below*/}
                <Route path="/ruleset-manager/view/:ruleset_name" element={<RulesetView />} />
                <Route path="/ruleset-manager/add/" element={<RulesetAddWizard />} />
              </Route>
              {/* Wildcard inside Protected Routes */}
              <Route path="*" element={<Navigate to="/getting-started" replace />} />
            </Route>
          </Routes>
        </AuthProvider>
      </Router>
    </ThemeProvider>
  );
};

export default App;
