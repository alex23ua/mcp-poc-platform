import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8001';

function App() {
    const [prompt, setPrompt] = useState('');
    const [response, setResponse] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [serverStatus, setServerStatus] = useState('checking');
    const textareaRef = useRef(null);

    // Check server status on mount
    useEffect(() => {
        checkServerStatus();
    }, []);

    const checkServerStatus = async () => {
        try {
            const healthResponse = await axios.get(`${API_BASE_URL}/health`);
            console.log('Health Response:', healthResponse.data);

            setServerStatus(healthResponse.data.mcp_initialized ? 'connected' : 'initializing');
        } catch (err) {
            setServerStatus('disconnected');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!prompt.trim()) {
            setError('Please enter a prompt');
            return;
        }

        setIsLoading(true);
        setError(null);
        setResponse(null);

        try {
            const result = await axios.post(`${API_BASE_URL}/prompt`, {
                prompt: prompt.trim(),
                user_id: 'react_client_user',
                session_id: `session_${Date.now()}`
            });

            setResponse(result.data);
            setPrompt(''); // Clear the input after successful submission
        } catch (err) {
            console.error('Error:', err);
            setError(
                err.response?.data?.detail ||
                'Failed to process prompt. Please check if the MCP server is running.'
            );
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const getStatusColor = () => {
        switch (serverStatus) {
            case 'connected': return '#4ade80';
            case 'initializing': return '#fbbf24';
            case 'disconnected': return '#ef4444';
            default: return '#6b7280';
        }
    };

    const getStatusText = () => {
        switch (serverStatus) {
            case 'connected': return 'Connected';
            case 'initializing': return 'Initializing...';
            case 'disconnected': return 'Disconnected';
            default: return 'Checking...';
        }
    };

    return (
        <div className="app">
            <div className="container">
                {/* Header */}
                <header className="header">
                    <div className="logo-section">
                        <div className="logo">
                            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <rect width="48" height="48" rx="12" fill="url(#gradient)" />
                                <path d="M12 16L24 12L36 16V32L24 36L12 32V16Z" stroke="white" strokeWidth="2" fill="none" />
                                <circle cx="24" cy="24" r="4" fill="white" />
                                <defs>
                                    <linearGradient id="gradient" x1="0" y1="0" x2="48" y2="48">
                                        <stop offset="0%" stopColor="#667eea" />
                                        <stop offset="100%" stopColor="#764ba2" />
                                    </linearGradient>
                                </defs>
                            </svg>
                        </div>
                        <div className="title-section">
                            <h1 className="title">MCP Platform</h1>
                            <p className="subtitle">Model Context Protocol Interface</p>
                        </div>
                    </div>

                    <div className="status-indicator">
                        <div
                            className="status-dot"
                            style={{ backgroundColor: getStatusColor() }}
                        ></div>
                        <span className="status-text">{getStatusText()}</span>
                    </div>
                </header>

                {/* Main Content */}
                <main className="main-content">
                    {/* Fixed Prompt Section */}
                    <div className="prompt-section">
                        <form onSubmit={handleSubmit} className="prompt-form">
                            <div className="input-group">
                                <label htmlFor="prompt" className="input-label">
                                    Enter your prompt
                                </label>
                                <textarea
                                    ref={textareaRef}
                                    id="prompt"
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Ask the MCP platform anything... (Press Enter to send, Shift+Enter for new line)"
                                    className="prompt-textarea"
                                    rows="4"
                                    disabled={isLoading || serverStatus !== 'connected'}
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={isLoading || !prompt.trim() || serverStatus !== 'connected'}
                                className="send-button"
                            >
                                {isLoading ? (
                                    <>
                                        <div className="spinner"></div>
                                        Processing...
                                    </>
                                ) : (
                                    <>
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                            <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                        Send
                                    </>
                                )}
                            </button>
                        </form>
                    </div>

                    {/* Scrollable Content Area */}
                    <div className="content-area">
                        {/* Error Display */}
                        {error && (
                            <div className="error-message">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
                                    <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" strokeWidth="2" />
                                    <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" strokeWidth="2" />
                                </svg>
                                {error}
                                <button
                                    onClick={() => setError(null)}
                                    className="error-close"
                                    aria-label="Dismiss error"
                                >
                                    ×
                                </button>
                            </div>
                        )}

                        {/* Response Display */}
                        {response && (
                            <div className="response-section">
                                <div className="response-header">
                                    <h3>Response</h3>
                                    {response.tools_used && response.tools_used.length > 0 && (
                                        <div className="tools-used">
                                            <span>Tools used: </span>
                                            {response.tools_used.map((tool, index) => (
                                                <span key={index} className="tool-badge">{tool}</span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                                <div className="response-content">
                                    <pre>{response.result}</pre>
                                </div>
                            </div>
                        )}

                        {/* Placeholder content when no response */}
                        {!response && !error && (
                            <div style={{
                                padding: '40px',
                                textAlign: 'center',
                                color: '#6b7280',
                                fontStyle: 'italic'
                            }}>
                                <p>💡 Enter a prompt above to start interacting with the MCP Platform</p>
                                <p style={{ marginTop: '20px', fontSize: '0.9rem' }}>
                                    Try asking: "Hello! Please add 15 and 27" or "Show me the Bancor privacy policy"
                                </p>
                            </div>
                        )}
                    </div>
                </main>

                {/* Footer */}
                <footer className="footer">
                    <p>
                        Powered by <strong>FastAPI</strong> & <strong>OpenAI</strong> |
                        Built for <strong>Bancor Privacy Compliance</strong>
                    </p>
                    <button
                        onClick={checkServerStatus}
                        className="refresh-status"
                        title="Refresh server status"
                    >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M23 4V10H17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M20.49 15C19.9828 16.6214 18.9209 18.0291 17.4845 18.9808C16.0481 19.9324 14.3352 20.3699 12.6386 20.2201C10.942 20.0703 9.3452 19.3415 8.10481 18.1395C6.86441 16.9375 6.06116 15.3389 5.82 13.6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M1 20V14H7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M3.51 9C4.01716 7.37856 5.07905 5.97087 6.51545 5.01921C7.95185 4.06755 9.66455 3.63008 11.3612 3.77988C13.0578 3.92968 14.6546 4.65848 15.895 5.86048C17.1354 7.06248 17.9388 8.66108 18.18 10.34" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </button>
                </footer>
            </div>
        </div>
    );
}

export default App;
