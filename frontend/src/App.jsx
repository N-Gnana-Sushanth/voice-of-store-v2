import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';
import FeedbackStreamPage from './pages/FeedbackStreamPage';
import IssueAnalysisPage from './pages/IssueAnalysisPage';
import EmergingIssuesPage from './pages/EmergingIssuesPage';
import ActionQueuePage from './pages/ActionQueuePage';
import RegionalReportsPage from './pages/RegionalReportsPage';
import StoresPage from './pages/StoresPage';
import SettingsPage from './pages/SettingsPage';
import { AppProvider } from './context/AppContext';
import './styles/tokens.css';
import './styles/index.css';

export default function App() {
  return (
    <BrowserRouter>
      <AppProvider>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/feedback-stream" element={<FeedbackStreamPage />} />
          <Route path="/issue-analysis" element={<IssueAnalysisPage />} />
          <Route path="/emerging-issues" element={<EmergingIssuesPage />} />
          <Route path="/action-queue" element={<ActionQueuePage />} />
          <Route path="/regional-reports" element={<RegionalReportsPage />} />
          <Route path="/stores" element={<StoresPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppProvider>
    </BrowserRouter>
  );
}
