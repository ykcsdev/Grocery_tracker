import React from 'react';
import { Moon, Sun, MessageSquare } from 'lucide-react';

const Navbar = ({ theme, toggleTheme, toggleChat }) => {
  return (
    <nav style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '1rem 2rem',
      backgroundColor: 'var(--panel-bg)',
      borderBottom: '1px solid var(--border-color)',
      color: 'var(--text-primary)'
    }}>
      <div style={{ fontWeight: 700, fontSize: '1.25rem' }}>
        AI Grocery Tracker
      </div>
      <div style={{ display: 'flex', gap: '1rem' }}>
        <button className="chat-toggle-btn" onClick={toggleChat} style={{
          background: 'var(--color-blue)',
          color: 'white',
          border: 'none',
          padding: '0.5rem 1rem',
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          cursor: 'pointer'
        }}>
          <MessageSquare size={18} />
          <span className="chat-btn-text">Chat</span>
        </button>
        <button onClick={toggleTheme} style={{
          background: 'transparent',
          border: '1px solid var(--border-color)',
          color: 'var(--text-primary)',
          borderRadius: 'var(--radius-md)',
          padding: '0.5rem',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center'
        }}>
          {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
