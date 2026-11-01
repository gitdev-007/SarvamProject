import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Sparkles, Settings, RefreshCw, AlertCircle } from 'lucide-react';

const DEFAULT_BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I am your Sarvam AI assistant powered by sarvam-105b-conversations. How can I help you today?',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [backendUrl, setBackendUrl] = useState(DEFAULT_BACKEND_URL);
  const [showSettings, setShowSettings] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');
  const messagesEndRef = useRef(null);

  const checkHealth = async (url) => {
    try {
      setBackendStatus('checking');
      const res = await fetch(`${url.replace(/\/$/, '')}/api/health`, { method: 'GET' });
      if (res.ok) {
        setBackendStatus('connected');
      } else {
        setBackendStatus('error');
      }
    } catch {
      setBackendStatus('disconnected');
    }
  };

  useEffect(() => {
    checkHealth(backendUrl);
  }, [backendUrl]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    const userMessage = { role: 'user', content: text };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);

    try {
      const baseUrl = backendUrl.replace(/\/$/, '');
      const response = await fetch(`${baseUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: updatedMessages.slice(1, -1),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.reply },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ Failed to get response: ${err.message}. Please check your backend connection.`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const samplePrompts = [
    'नमस्ते, आप क्या-क्या कर सकते हैं?',
    'Explain the vision of Sarvam AI for India.',
    'Write a poem about the monsoon in Mumbai.',
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', maxWidth: '900px', margin: '0 auto', padding: '16px' }}>
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 20px', background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ background: '#6366f1', padding: '8px', borderRadius: '10px', display: 'flex' }}>
            <Sparkles size={22} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '18px', fontWeight: 600 }}>Sarvam AI Chat</h1>
            <p style={{ fontSize: '12px', color: '#94a3b8' }}>Model: sarvam-105b-conversations</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', background: '#0f172a', padding: '6px 10px', borderRadius: '20px', border: '1px solid #334155' }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: backendStatus === 'connected' ? '#22c55e' : backendStatus === 'checking' ? '#eab308' : '#ef4444',
            }} />
            <span style={{ textTransform: 'capitalize', color: '#cbd5e1' }}>{backendStatus}</span>
          </div>

          <button
            onClick={() => setShowSettings(!showSettings)}
            style={{ background: '#334155', border: 'none', color: '#f8fafc', padding: '8px', borderRadius: '8px', display: 'flex' }}
            title="Configure Backend URL"
          >
            <Settings size={18} />
          </button>
        </div>
      </header>

      {/* Settings Bar */}
      {showSettings && (
        <div style={{ background: '#1e293b', padding: '14px 20px', borderRadius: '10px', border: '1px solid #475569', marginBottom: '16px', display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <label style={{ fontSize: '13px', color: '#94a3b8' }}>Backend API URL:</label>
          <input
            type="text"
            value={backendUrl}
            onChange={(e) => setBackendUrl(e.target.value)}
            placeholder="http://localhost:8000 or https://your-app.onrender.com"
            style={{ flex: 1, minWidth: '240px', background: '#0f172a', border: '1px solid #334155', color: '#f8fafc', padding: '6px 12px', borderRadius: '6px', fontSize: '13px' }}
          />
          <button
            onClick={() => checkHealth(backendUrl)}
            style={{ background: '#6366f1', border: 'none', color: '#ffffff', padding: '6px 14px', borderRadius: '6px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <RefreshCw size={14} /> Test
          </button>
        </div>
      )}

      {/* Messages Feed */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px', background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              display: 'flex',
              gap: '12px',
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%',
            }}
          >
            {msg.role === 'assistant' && (
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#6366f1', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Bot size={18} color="#ffffff" />
              </div>
            )}
            <div
              style={{
                background: msg.role === 'user' ? '#4f46e5' : '#0f172a',
                color: '#f8fafc',
                padding: '12px 16px',
                borderRadius: '12px',
                border: msg.role === 'user' ? 'none' : '1px solid #334155',
                fontSize: '14px',
                lineHeight: '1.5',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}
            >
              {msg.content}
            </div>
            {msg.role === 'user' && (
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#3b82f6', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <User size={18} color="#ffffff" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', gap: '12px', alignSelf: 'flex-start', maxWidth: '80%' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#6366f1', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Bot size={18} color="#ffffff" />
            </div>
            <div style={{ background: '#0f172a', padding: '12px 16px', borderRadius: '12px', border: '1px solid #334155', color: '#94a3b8', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>●</span> Sarvam is thinking...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompts */}
      <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', padding: '10px 0' }}>
        {samplePrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            disabled={loading}
            style={{
              background: '#1e293b',
              border: '1px solid #334155',
              color: '#cbd5e1',
              padding: '6px 12px',
              borderRadius: '16px',
              fontSize: '12px',
              whiteSpace: 'nowrap',
            }}
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        style={{ display: 'flex', gap: '10px', marginTop: '4px' }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Sarvam AI in English, Hindi, or any Indic language..."
          disabled={loading}
          style={{
            flex: 1,
            background: '#1e293b',
            border: '1px solid #334155',
            color: '#f8fafc',
            padding: '12px 16px',
            borderRadius: '10px',
            fontSize: '14px',
            outline: 'none',
          }}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{
            background: input.trim() && !loading ? '#6366f1' : '#334155',
            color: '#ffffff',
            border: 'none',
            padding: '0 20px',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'background 0.2s',
          }}
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}

