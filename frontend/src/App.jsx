import React, { useState, useEffect } from 'react';
import './App.css';
import Navbar from './components/Navbar';
import SummaryStrip from './components/SummaryStrip';
import DashboardCharts from './components/DashboardCharts';
import DataExploration from './components/DataExploration';
import Uploader from './components/Uploader';
import ChatPanel from './components/ChatPanel';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [theme, setTheme] = useState(() => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'dark';
  });
  const [isChatOpen, setIsChatOpen] = useState(false);

  useEffect(() => {
    // Apply theme to document root for global CSS variables
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');
  const toggleChat = () => setIsChatOpen(prev => !prev);
  const triggerRefresh = () => setRefreshTrigger(prev => prev + 1);

  return (
    <div className="app-layout">
      <Navbar theme={theme} toggleTheme={toggleTheme} toggleChat={toggleChat} />
      
      <div className="app-container">
        {/* Dashboard Panel */}
        <main className="dashboard-panel">
          <header>
            <h1 style={{ marginBottom: '0.5rem', fontWeight: 600, fontSize: '1.75rem' }}>Overview</h1>
            <p style={{ color: 'var(--text-secondary)' }}>Your grocery spending insights.</p>
          </header>

          <SummaryStrip refreshTrigger={refreshTrigger} />
          <DashboardCharts refreshTrigger={refreshTrigger} />
          <Uploader onUploadSuccess={triggerRefresh} />
          <DataExploration refreshTrigger={refreshTrigger} />
        </main>

        {/* AI Chat Panel - slides in on mobile, split screen on desktop */}
        <aside className={`chat-panel ${isChatOpen ? 'open' : ''}`}>
          {/* Mobile close handle */}
          <div className="mobile-chat-header" onClick={toggleChat}>
            <div className="drag-handle"></div>
          </div>
          <ChatPanel />
        </aside>
        
        {/* Backdrop for mobile */}
        {isChatOpen && <div className="chat-backdrop" onClick={toggleChat}></div>}
      </div>
    </div>
  );
}

export default App;
