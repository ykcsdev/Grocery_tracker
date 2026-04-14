import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Sparkles } from 'lucide-react';

const SUGGESTED_PROMPTS = [
  "Where did I spend the most?",
  "How can I save money?"
];

// Helper to highlight numbers and currency in the text
const highlightNumbers = (text) => {
  const regex = /(€\d+(?:\.\d+)?|\d+(?:\.\d+)?)/g;
  const parts = text.split(regex);
  return parts.map((part, index) => 
    regex.test(part) ? (
      <strong key={index} style={{ color: 'var(--color-blue)', backgroundColor: 'rgba(59, 130, 246, 0.1)', padding: '0 4px', borderRadius: '4px' }}>
        {part}
      </strong>
    ) : (
      <span key={index}>{part}</span>
    )
  );
};

const ChatPanel = () => {
  const [messages, setMessages] = useState([
    { id: 1, sender: 'ai', text: "Hello! I'm your AI Grocery Assistant. How can I help you analyze your spending today?" }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async (text) => {
    if (!text.trim()) return;

    const userMsg = { id: Date.now(), sender: 'user', text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await axios.post('http://localhost:8000/chat', { message: text });
      
      const aiMsg = { id: Date.now() + 1, sender: 'ai', text: response.data.reply };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      const errorMsg = { id: Date.now() + 1, sender: 'ai', text: "Sorry, I'm having trouble connecting to the server." };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%' }}>
      
      {/* Header */}
      <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{ background: 'var(--color-blue)', padding: '0.5rem', borderRadius: '8px' }}>
          <Bot size={24} color="white" />
        </div>
        <div>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, margin: 0 }}>Grocery AI</h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', margin: 0 }}>Powered by your data</p>
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {messages.map((msg) => (
          <div key={msg.id} style={{ 
            display: 'flex', 
            flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row', 
            gap: '0.75rem',
            alignItems: 'flex-start'
          }}>
            <div style={{ 
              width: '32px', height: '32px', borderRadius: '50%', 
              backgroundColor: msg.sender === 'user' ? 'var(--border-color)' : 'var(--color-blue)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0
            }}>
              {msg.sender === 'user' ? <User size={18} color="var(--text-secondary)" /> : <Sparkles size={18} color="white" />}
            </div>
            
            <div style={{ 
              maxWidth: '80%',
              padding: '0.75rem 1rem',
              borderRadius: '12px',
              backgroundColor: msg.sender === 'user' ? 'var(--text-primary)' : 'var(--bg-color)',
              color: msg.sender === 'user' ? 'var(--panel-bg)' : 'var(--text-primary)',
              border: msg.sender === 'ai' ? '1px solid var(--border-color)' : 'none',
              lineHeight: 1.5,
              fontSize: '0.925rem'
            }}>
               {msg.sender === 'ai' ? highlightNumbers(msg.text) : msg.text}
            </div>
          </div>
        ))}

        {isTyping && (
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
             <div style={{ 
              width: '32px', height: '32px', borderRadius: '50%', 
              backgroundColor: 'var(--color-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <Sparkles size={18} color="white" />
            </div>
            <div style={{ padding: '0.75rem 1rem', borderRadius: '12px', backgroundColor: 'var(--bg-color)', border: '1px solid var(--border-color)' }}>
              <span className="dot-pulse">thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border-color)', backgroundColor: 'var(--bg-color)' }}>
        
        {/* Suggestions */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
          {SUGGESTED_PROMPTS.map((prompt, idx) => (
            <button 
              key={idx} 
              onClick={() => handleSend(prompt)}
              style={{ 
                padding: '0.5rem 0.75rem', 
                whiteSpace: 'nowrap',
                backgroundColor: 'var(--panel-bg)', 
                border: '1px solid var(--border-color)',
                borderRadius: '999px',
                fontSize: '0.8rem',
                color: 'var(--color-blue)',
                cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input box */}
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
            placeholder="Ask about your spending..."
            style={{ 
              flex: 1, 
              padding: '0.75rem 1rem', 
              borderRadius: '99px', 
              border: '1px solid var(--border-color)',
              backgroundColor: 'var(--panel-bg)',
              color: 'var(--text-primary)',
              outline: 'none',
              fontSize: '0.925rem'
            }}
          />
          <button 
            onClick={() => handleSend(input)}
            style={{ 
              width: '44px', height: '44px', 
              borderRadius: '50%', 
              backgroundColor: 'var(--color-blue)', 
              color: 'white', 
              border: 'none', 
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer',
              flexShrink: 0
            }}
          >
            <Send size={18} style={{ marginLeft: '0.1rem' }} />
          </button>
        </div>
      </div>

    </div>
  );
};

export default ChatPanel;
