import React, { useState, useRef, useEffect } from 'react';
import { Upload, Send, File, Loader2, MessageSquare, FileText, Trash2 } from 'lucide-react';
// const REACT_APP_BACKEND_URL = process.env.REACT_APP_BACKEND_URL
export default function AIChatbot() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [uploadedDocuments, setUploadedDocuments] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleFileUpload = async (e) => {
        const files = Array.from(e.target.files);
        if (files.length === 0) return;

        setIsUploading(true);

        try {
            const formData = new FormData();
            files.forEach(file => {
                formData.append('files', file);
            });

            // Upload documents to backend
            const response = await fetch(`https://face-detection-ai-1.onrender.com/upload`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Failed to upload documents');
            }

            const data = await response.json();

            // Add uploaded documents to the list
            const newDocs = files.map((file, idx) => ({
                name: file.name,
                id: data.file_ids ? data.file_ids[idx] : Date.now() + idx,
                uploadedAt: new Date().toISOString()
            }));

            setUploadedDocuments(prev => [...prev, ...newDocs]);

            // Show success message
            const successMessage = {
                role: 'assistant',
                content: `Successfully uploaded ${files.length} document(s). You can now ask questions about them!`,
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, successMessage]);

        } catch (error) {
            const errorMessage = {
                role: 'assistant',
                content: `Error uploading documents: ${error.message}`,
                timestamp: new Date().toISOString(),
                isError: true
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsUploading(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const removeDocument = async (docId) => {
        try {
            // Optionally call backend to delete the document
            await fetch(`https://face-detection-ai-1.onrender.com/api/documents/${docId}`, {
                method: 'DELETE',
            });

            setUploadedDocuments(prev => prev.filter(doc => doc.id !== docId));

            const message = {
                role: 'assistant',
                content: 'Document removed successfully.',
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, message]);
        } catch (error) {
            console.error('Error removing document:', error);
        }
    };

    const handleAskQuestion = async () => {
        if (!input.trim()) return;

        const userMessage = {
            role: 'user',
            content: input,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            // Determine which endpoint to use based on whether documents are uploaded
            const endpoint = uploadedDocuments.length > 0
                ? `https://face-detection-ai-1.onrender.com/ask`
                : `https://face-detection-ai-1.onrender.com/chat`;

            const requestBody = uploadedDocuments.length > 0
                ? {
                    question: input,
                    document_ids: uploadedDocuments.map(doc => doc.id)
                }
                : {
                    message: input
                };

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) {
                throw new Error('Failed to get response from server');
            }

            const data = await response.json();

            const assistantMessage = {
                role: 'assistant',
                content: data.answer || data.response || 'No response received',
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            const errorMessage = {
                role: 'assistant',
                content: `Error: ${error.message}. Make sure your Python backend is running at REACT_APP_BACKEND_URL

`,
                timestamp: new Date().toISOString(),
                isError: true
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleAskQuestion();
        }
    };

    return (
        <div style={styles.container}>
            {/* Header */}
            <div style={styles.header}>
                <div style={styles.headerContent}>
                    <div style={styles.iconContainer}>
                        <MessageSquare style={styles.icon} />
                    </div>
                    <div>
                        <h1 style={styles.title}>AI Document Assistant</h1>
                        <p style={styles.subtitle}>Upload documents for specific questions, or chat freely</p>
                    </div>
                </div>
            </div>

            <div style={styles.mainContent}>
                {/* Sidebar - Uploaded Documents */}
                <div style={styles.sidebar}>
                    <div style={styles.sidebarHeader}>
                        <FileText style={styles.sidebarIcon} />
                        <h2 style={styles.sidebarTitle}>Uploaded Documents</h2>
                    </div>

                    <div style={styles.uploadSection}>
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileUpload}
                            multiple
                            style={styles.hiddenInput}
                            accept=".pdf,.txt,.doc,.docx,.csv,.json"
                        />

                        <button
                            onClick={() => fileInputRef.current?.click()}
                            style={styles.uploadButton}
                            disabled={isUploading}
                        >
                            {isUploading ? (
                                <>
                                    <Loader2 style={{ ...styles.buttonIcon, animation: 'spin 1s linear infinite' }} />
                                    Uploading...
                                </>
                            ) : (
                                <>
                                    <Upload style={styles.buttonIcon} />
                                    Upload Documents
                                </>
                            )}
                        </button>
                    </div>

                    <div style={styles.documentsList}>
                        {uploadedDocuments.length === 0 ? (
                            <div style={styles.emptyDocuments}>
                                <FileText style={styles.emptyDocIcon} />
                                <p style={styles.emptyDocText}>No documents uploaded yet</p>
                            </div>
                        ) : (
                            uploadedDocuments.map((doc) => (
                                <div key={doc.id} style={styles.documentItem}>
                                    <File style={styles.docIcon} />
                                    <div style={styles.docInfo}>
                                        <div style={styles.docName}>{doc.name}</div>
                                        <div style={styles.docTime}>
                                            {new Date(doc.uploadedAt).toLocaleTimeString()}
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => removeDocument(doc.id)}
                                        style={styles.deleteButton}
                                        title="Remove document"
                                    >
                                        <Trash2 style={styles.deleteIcon} />
                                    </button>
                                </div>
                            ))
                        )}
                    </div>

                    <div style={styles.documentCount}>
                        {uploadedDocuments.length} document(s) loaded
                    </div>
                </div>

                {/* Chat Area */}
                <div style={styles.chatArea}>
                    {/* Messages */}
                    <div style={styles.messagesContainer}>
                        {messages.length === 0 ? (
                            <div style={styles.emptyState}>
                                <div style={styles.emptyIconContainer}>
                                    <MessageSquare style={styles.emptyIcon} />
                                </div>
                                <h2 style={styles.emptyTitle}>Welcome to AI Assistant</h2>
                                <p style={styles.emptyText}>
                                    Start chatting with the AI, or:<br />
                                    Upload your documents <br />
                                    Ask questions and Get AI-powered answers instantly<br />
                                </p>
                            </div>
                        ) : (
                            messages.map((msg, idx) => (
                                <div
                                    key={idx}
                                    style={{
                                        ...styles.messageWrapper,
                                        justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
                                    }}
                                >
                                    <div
                                        style={{
                                            ...styles.messageBubble,
                                            ...(msg.role === 'user' ? styles.userMessage :
                                                msg.isError ? styles.errorMessage : styles.assistantMessage)
                                        }}
                                    >
                                        <div style={styles.messageContent}>{msg.content}</div>
                                        <div style={styles.timestamp}>
                                            {new Date(msg.timestamp).toLocaleTimeString()}
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                        {isLoading && (
                            <div style={styles.messageWrapper}>
                                <div style={styles.loadingMessage}>
                                    <div style={styles.loadingContent}>
                                        <Loader2 style={styles.loader} />
                                        <span>AI is analyzing your {uploadedDocuments.length > 0 ? 'documents' : 'question'}...</span>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div style={styles.inputArea}>
                        <div style={styles.inputContainer}>
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder={uploadedDocuments.length > 0 ? "Ask a question about your documents..." : "Ask me anything..."}
                                style={styles.textInput}
                                disabled={isLoading}
                            />

                            <button
                                onClick={handleAskQuestion}
                                disabled={isLoading || !input.trim()}
                                style={{
                                    ...styles.sendButton,
                                    ...(isLoading || !input.trim() ? styles.disabledButton : {})
                                }}
                                title="Ask question"
                            >
                                <Send style={styles.buttonIcon} />
                            </button>
                        </div>

                        <div style={styles.backendUrl}>
                            {/* {uploadedDocuments.length > 0
                                ? 'Using: POST /api/ask (with documents)'
                                : 'Using: POST /api/chat (general chat)'} */}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

const styles = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        background: 'linear-gradient(135deg, #1e1b4b 0%, #581c87 50%, #1e1b4b 100%)',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    },
    header: {
        backgroundColor: 'rgba(30, 41, 59, 0.5)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(168, 85, 247, 0.2)',
        padding: '16px 24px',
    },
    headerContent: {
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
    },
    iconContainer: {
        backgroundColor: '#a855f7',
        padding: '8px',
        borderRadius: '8px',
    },
    icon: {
        width: '24px',
        height: '24px',
        color: 'white',
    },
    title: {
        fontSize: '20px',
        fontWeight: 'bold',
        color: 'white',
        margin: 0,
    },
    subtitle: {
        fontSize: '14px',
        color: '#d8b4fe',
        margin: 0,
    },
    mainContent: {
        display: 'flex',
        flex: 1,
        overflow: 'hidden',
    },
    sidebar: {
        width: '320px',
        backgroundColor: 'rgba(30, 41, 59, 0.5)',
        backdropFilter: 'blur(10px)',
        borderRight: '1px solid rgba(168, 85, 247, 0.2)',
        display: 'flex',
        flexDirection: 'column',
        padding: '20px',
    },
    sidebarHeader: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginBottom: '20px',
    },
    sidebarIcon: {
        width: '20px',
        height: '20px',
        color: '#a855f7',
    },
    sidebarTitle: {
        fontSize: '16px',
        fontWeight: 'bold',
        color: 'white',
        margin: 0,
    },
    uploadSection: {
        marginBottom: '20px',
    },
    uploadButton: {
        width: '100%',
        backgroundColor: '#a855f7',
        color: 'white',
        padding: '12px',
        borderRadius: '8px',
        border: 'none',
        cursor: 'pointer',
        fontSize: '14px',
        fontWeight: '500',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        transition: 'background-color 0.2s',
    },
    documentsList: {
        flex: 1,
        overflowY: 'auto',
        marginBottom: '16px',
    },
    emptyDocuments: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px 20px',
        textAlign: 'center',
    },
    emptyDocIcon: {
        width: '48px',
        height: '48px',
        color: '#6b7280',
        marginBottom: '12px',
    },
    emptyDocText: {
        color: '#9ca3af',
        fontSize: '14px',
        margin: 0,
    },
    documentItem: {
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '12px',
        backgroundColor: 'rgba(168, 85, 247, 0.1)',
        border: '1px solid rgba(168, 85, 247, 0.2)',
        borderRadius: '8px',
        marginBottom: '8px',
    },
    docIcon: {
        width: '20px',
        height: '20px',
        color: '#a855f7',
        flexShrink: 0,
    },
    docInfo: {
        flex: 1,
        minWidth: 0,
    },
    docName: {
        color: 'white',
        fontSize: '14px',
        fontWeight: '500',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
    },
    docTime: {
        color: '#9ca3af',
        fontSize: '12px',
        marginTop: '2px',
    },
    deleteButton: {
        background: 'none',
        border: 'none',
        cursor: 'pointer',
        padding: '4px',
        display: 'flex',
        alignItems: 'center',
        borderRadius: '4px',
        transition: 'background-color 0.2s',
    },
    deleteIcon: {
        width: '16px',
        height: '16px',
        color: '#ef4444',
    },
    documentCount: {
        color: '#9ca3af',
        fontSize: '12px',
        textAlign: 'center',
        padding: '8px',
        backgroundColor: 'rgba(0, 0, 0, 0.2)',
        borderRadius: '6px',
    },
    chatArea: {
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
    },
    messagesContainer: {
        flex: 1,
        overflowY: 'auto',
        padding: '24px',
    },
    emptyState: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        textAlign: 'center',
    },
    emptyIconContainer: {
        backgroundColor: 'rgba(168, 85, 247, 0.1)',
        padding: '24px',
        borderRadius: '50%',
        marginBottom: '16px',
    },
    emptyIcon: {
        width: '64px',
        height: '64px',
        color: '#c084fc',
    },
    emptyTitle: {
        fontSize: '24px',
        fontWeight: 'bold',
        color: 'white',
        marginBottom: '16px',
    },
    emptyText: {
        color: '#d8b4fe',
        maxWidth: '500px',
        lineHeight: '1.8',
        fontSize: '16px',
    },
    messageWrapper: {
        display: 'flex',
        marginBottom: '16px',
    },
    messageBubble: {
        maxWidth: '70%',
        borderRadius: '16px',
        padding: '16px 24px',
    },
    userMessage: {
        backgroundColor: '#a855f7',
        color: 'white',
    },
    assistantMessage: {
        backgroundColor: 'rgba(30, 41, 59, 0.8)',
        color: 'white',
        border: '1px solid rgba(168, 85, 247, 0.2)',
    },
    errorMessage: {
        backgroundColor: 'rgba(239, 68, 68, 0.2)',
        color: '#fecaca',
        border: '1px solid rgba(239, 68, 68, 0.3)',
    },
    messageContent: {
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
        lineHeight: '1.5',
    },
    timestamp: {
        fontSize: '12px',
        opacity: 0.5,
        marginTop: '8px',
    },
    loadingMessage: {
        backgroundColor: 'rgba(30, 41, 59, 0.8)',
        color: 'white',
        borderRadius: '16px',
        padding: '16px 24px',
        border: '1px solid rgba(168, 85, 247, 0.2)',
    },
    loadingContent: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
    },
    loader: {
        width: '20px',
        height: '20px',
        color: '#c084fc',
        animation: 'spin 1s linear infinite',
    },
    inputArea: {
        backgroundColor: 'rgba(30, 41, 59, 0.5)',
        backdropFilter: 'blur(10px)',
        borderTop: '1px solid rgba(168, 85, 247, 0.2)',
        padding: '24px',
    },
    inputContainer: {
        display: 'flex',
        gap: '12px',
    },
    hiddenInput: {
        display: 'none',
    },
    textInput: {
        flex: 1,
        backgroundColor: '#334155',
        color: 'white',
        border: '1px solid rgba(168, 85, 247, 0.3)',
        borderRadius: '12px',
        padding: '12px 24px',
        fontSize: '16px',
        outline: 'none',
    },
    sendButton: {
        backgroundColor: '#a855f7',
        color: 'white',
        padding: '12px',
        borderRadius: '12px',
        border: 'none',
        cursor: 'pointer',
        transition: 'background-color 0.2s',
    },
    disabledButton: {
        backgroundColor: '#334155',
        cursor: 'not-allowed',
        opacity: 0.5,
    },
    buttonIcon: {
        width: '20px',
        height: '20px',
    },
    backendUrl: {
        marginTop: '12px',
        textAlign: 'center',
        fontSize: '12px',
        color: 'rgba(216, 180, 254, 0.6)',
    },
};

// Add CSS animation for loader
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;
document.head.appendChild(styleSheet);