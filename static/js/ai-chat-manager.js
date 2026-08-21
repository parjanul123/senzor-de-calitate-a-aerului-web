/**
 * AI Chat Interface - Example Implementation
 * 
 * Demonstrates how to implement a chat interface for interacting with the AI backend.
 */

class AIChatManager {
    constructor(containerId = 'ai-chat-container') {
        this.containerId = containerId;
        this.chatElement = document.getElementById(containerId);
        this.messageInputId = 'chat-message-input';
        this.sendButtonId = 'chat-send-button';
        this.messagesContainerId = 'chat-messages';
        
        this.conversationId = this.generateConversationId();
        this.deviceContext = null;
        this.isWaitingForResponse = false;
        
        this.init();
    }
    
    /**
     * Initialize chat interface
     */
    init() {
        if (!this.chatElement) {
            console.warn('[AIChatManager] Chat container not found');
            return;
        }
        
        this.renderChatUI();
        this.setupEventListeners();
        this.addWelcomeMessage();
        
        console.log('[AIChatManager] Initialized');
    }
    
    /**
     * Render chat interface HTML
     */
    renderChatUI() {
        this.chatElement.innerHTML = `
            <div class="ai-chat-wrapper">
                <div class="ai-chat-header">
                    <h5>🤖 AI Assistant</h5>
                    <button class="btn-close" aria-label="Close" onclick="aiChatManager.close()"></button>
                </div>
                
                <div id="${this.messagesContainerId}" class="ai-chat-messages">
                    <!-- Messages will be added here -->
                </div>
                
                <div class="ai-chat-input-area">
                    <div class="input-group">
                        <input 
                            type="text" 
                            id="${this.messageInputId}" 
                            class="form-control" 
                            placeholder="Ask about air quality..."
                            autocomplete="off"
                        >
                        <button 
                            id="${this.sendButtonId}" 
                            class="btn btn-primary"
                        >
                            Send
                        </button>
                    </div>
                </div>
            </div>
            
            <style>
                .ai-chat-wrapper {
                    display: flex;
                    flex-direction: column;
                    height: 600px;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    background: white;
                    overflow: hidden;
                }
                
                .ai-chat-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px 16px;
                    background-color: #f8f9fa;
                    border-bottom: 1px solid #dee2e6;
                }
                
                .ai-chat-header h5 {
                    margin: 0;
                    font-size: 1rem;
                }
                
                .ai-chat-messages {
                    flex: 1;
                    overflow-y: auto;
                    padding: 16px;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }
                
                .chat-message {
                    display: flex;
                    gap: 8px;
                    animation: slideIn 0.3s ease-in-out;
                }
                
                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                .chat-message.user {
                    justify-content: flex-end;
                }
                
                .chat-message.assistant {
                    justify-content: flex-start;
                }
                
                .chat-bubble {
                    max-width: 70%;
                    padding: 8px 12px;
                    border-radius: 8px;
                    word-wrap: break-word;
                    font-size: 0.9rem;
                    line-height: 1.4;
                }
                
                .chat-bubble.user {
                    background-color: #007bff;
                    color: white;
                }
                
                .chat-bubble.assistant {
                    background-color: #e9ecef;
                    color: #333;
                }
                
                .chat-timestamp {
                    font-size: 0.75rem;
                    color: #999;
                    margin-top: 4px;
                }
                
                .ai-chat-input-area {
                    padding: 12px;
                    border-top: 1px solid #dee2e6;
                    background-color: #f8f9fa;
                }
                
                .ai-chat-input-area .input-group {
                    gap: 8px;
                }
                
                .ai-chat-input-area input {
                    border-radius: 4px;
                }
                
                .ai-chat-input-area button {
                    border-radius: 4px;
                }
            </style>
        `;
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        const input = document.getElementById(this.messageInputId);
        const button = document.getElementById(this.sendButtonId);
        
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        if (button) {
            button.addEventListener('click', () => this.sendMessage());
        }
    }
    
    /**
     * Add welcome message
     */
    addWelcomeMessage() {
        this.addMessage(
            'Hello! I\'m your AI assistant. Ask me about air quality, sensor readings, or get predictions. How can I help?',
            'assistant',
            true
        );
    }
    
    /**
     * Set device context for the conversation
     */
    setDeviceContext(deviceId, deviceName) {
        this.deviceContext = { deviceId, deviceName };
        console.log('[AIChatManager] Device context set:', this.deviceContext);
    }
    
    /**
     * Send message to AI
     */
    async sendMessage() {
        const input = document.getElementById(this.messageInputId);
        if (!input) return;
        
        const message = input.value.trim();
        if (!message) return;
        
        // Clear input
        input.value = '';
        
        // Add user message to UI
        this.addMessage(message, 'user');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send to AI backend
            const response = await aiService.chat(message, this.deviceContext || {});
            
            // Remove typing indicator
            this.removeTypingIndicator();
            
            // Add AI response
            if (response.message) {
                this.addMessage(response.message, 'assistant');
            } else if (response.response) {
                this.addMessage(response.response, 'assistant');
            } else {
                this.addMessage('I could not process your request. Please try again.', 'assistant');
            }
            
            // Handle actions if any
            if (response.actions) {
                this.handleActions(response.actions);
            }
            
        } catch (error) {
            this.removeTypingIndicator();
            
            console.error('[AIChatManager] Error:', error);
            
            const errorMessage = uiManager.formatError(error);
            this.addMessage(`Sorry, I encountered an error: ${errorMessage}`, 'assistant');
        }
    }
    
    /**
     * Add message to chat
     */
    addMessage(text, sender = 'assistant', isWelcome = false) {
        const container = document.getElementById(this.messagesContainerId);
        if (!container) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        
        const timestamp = new Date().toLocaleTimeString('ro-RO', {
            hour: '2-digit',
            minute: '2-digit',
        });
        
        messageDiv.innerHTML = `
            <div>
                <div class="chat-bubble ${sender}">
                    ${this.escapeHtml(text)}
                </div>
                ${!isWelcome ? `<div class="chat-timestamp">${timestamp}</div>` : ''}
            </div>
        `;
        
        container.appendChild(messageDiv);
        
        // Auto-scroll to bottom
        container.scrollTop = container.scrollHeight;
    }
    
    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        const container = document.getElementById(this.messagesContainerId);
        if (!container) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'chat-message assistant';
        typingDiv.innerHTML = `
            <div>
                <div class="chat-bubble assistant">
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    <span class="ms-2">Thinking...</span>
                </div>
            </div>
        `;
        
        container.appendChild(typingDiv);
        container.scrollTop = container.scrollHeight;
    }
    
    /**
     * Remove typing indicator
     */
    removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    /**
     * Handle actions from AI response
     */
    handleActions(actions) {
        if (!Array.isArray(actions)) return;
        
        actions.forEach(action => {
            console.log('[AIChatManager] Handling action:', action);
            
            switch (action) {
                case 'checkDevice':
                    this.addMessage('I recommend checking your device settings.', 'assistant');
                    break;
                case 'calibrateDevice':
                    this.addMessage('Your device might need calibration. Please check the device documentation.', 'assistant');
                    break;
                case 'replaceFilter':
                    this.addMessage('It\'s time to replace the sensor filter.', 'assistant');
                    break;
                case 'contactSupport':
                    this.addMessage('Please contact support at support@example.com', 'assistant');
                    break;
            }
        });
    }
    
    /**
     * Get conversation history
     */
    getHistory() {
        return aiService.getHistory();
    }
    
    /**
     * Clear chat history
     */
    clearHistory() {
        aiService.clearHistory();
        const container = document.getElementById(this.messagesContainerId);
        if (container) {
            container.innerHTML = '';
        }
        this.addWelcomeMessage();
    }
    
    /**
     * Close chat interface
     */
    close() {
        if (this.chatElement) {
            this.chatElement.style.display = 'none';
        }
    }
    
    /**
     * Open chat interface
     */
    open() {
        if (this.chatElement) {
            this.chatElement.style.display = 'flex';
        }
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Generate unique conversation ID
     */
    generateConversationId() {
        return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
}

// Initialize AI Chat when document is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if chat container exists
    if (document.getElementById('ai-chat-container')) {
        window.aiChatManager = new AIChatManager();
        console.log('[AIChatManager] Global instance created');
    }
});
