import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { lightTheme } from './themes/lightTheme';
import { darkTheme } from './themes/darkTheme';
import { AuthProvider } from './contexts/AuthContext';
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
import TenantSettingsManager from 'pages/TenantSettingsManager';
import TenantSettingCategoryDetailsView from 'pages/tenant-setting-manager/TenantSettingCategoryDetailsView';
import ProtectedRoute from './routes/ProtectedRoute';

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
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<Navigate to="/getting-started" replace />} />
            
            <Route element={<ProtectedRoute />}>
              <Route path="/*" element={
                <MainLayout darkMode={darkMode} toggleTheme={toggleTheme}>
                  <Routes>
                    {/* Core Routes */}
                    <Route path="/getting-started" element={<LandingPage />} />
                    <Route path="/sqlexecutor-playground" element={<SQLExecutorPlayground />} />

                    {/* Schema Manager Routes */}
                    <Route path="/schema-manager">
                      <Route index element={<SchemaManager />} />
                      <Route path="view/:schema_name" element={<SchemaView />} />
                      <Route path="add" element={<SchemaAddWizard />} />
                    </Route>

                    {/* Ruleset Manager Routes */}
                    <Route path="/ruleset-manager">
                      <Route index element={<RulesetManager />} />
                      <Route path="view/:ruleset_name" element={<RulesetView />} />
                      <Route path="add" element={<RulesetAddWizard />} />
                    </Route>

                    {/* Tenant Settings Routes */}
                    <Route path="/tenant-settings-manager">
                      <Route index element={<TenantSettingsManager />} />
                      <Route path=":categoryKey" element={<TenantSettingCategoryDetailsView />} />
                    </Route>

                    {/* Catch-all route - must be last */}
                    <Route path="*" element={<Navigate to="/getting-started" replace />} />
                  </Routes>
                </MainLayout>
              } />
            </Route>
          </Routes>
        </AuthProvider>
      </Router>
    </ThemeProvider>
  );
};

export default App;
