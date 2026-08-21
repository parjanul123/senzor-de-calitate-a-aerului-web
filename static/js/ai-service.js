/**
 * AI Service - Handles all AI-related API calls
 * 
 * Provides methods to:
 * - Send chat messages to AI
 * - Get AI predictions
 * - Train AI model
 * - Check AI status
 */

class AIService {
    constructor(apiClient) {
        this.api = apiClient;
        this.chatHistory = [];
        this.maxChatHistory = 50;
    }
    
    /**
     * Send message to AI chat
     * @param {string} message - User message
     * @param {object} context - Optional context {deviceId, deviceName}
     * @returns {Promise<object>} AI response
     */
    async chat(message, context = {}) {
        try {
            const url = getAPIUrl(API_CONFIG.ENDPOINTS.ai.chat);
            
            const payload = {
                message,
                history: context.conversationHistory || [],
            };
            
            const response = await this.api.post(url, payload);
            
            // Store in chat history
            this.addToHistory({
                role: 'user',
                content: message,
                timestamp: new Date().toISOString(),
            });
            
            this.addToHistory({
                role: 'assistant',
                content: response.reply,
                timestamp: new Date().toISOString(),
            });
            
            return response;
        } catch (error) {
            console.error('Error in AI chat:', error);
            throw error;
        }
    }
    
    /**
     * Get AI prediction for sensor data
     * @param {object} data - Measurement data
     * @returns {Promise<object>} Prediction results
     */
    async predict(data) {
        try {
            const url = getAPIUrl(API_CONFIG.ENDPOINTS.ai.predictCustom);
            
            return await this.api.post(url, data);
        } catch (error) {
            console.error('Error in AI prediction:', error);
            throw error;
        }
    }
    
    /**
     * Train AI model
     * @param {object} params - Training parameters
     * @returns {Promise<object>} Training status
     */
    async train(params = {}) {
        try {
            const url = getAPIUrl(API_CONFIG.ENDPOINTS.ai.train);
            
            const payload = {
                ...params,
                timestamp: new Date().toISOString(),
            };
            
            return await this.api.post(url, payload);
        } catch (error) {
            console.error('Error in AI training:', error);
            throw error;
        }
    }
    
    /**
     * Detect anomalies in measurements
     * @param {array} measurements - Array of measurement data
     * @param {object} options - Detection options
     * @returns {Promise<object>} Anomaly detection results
     */
    async detectAnomalies(measurements, options = {}) {
        try {
            const url = getAPIUrl(API_CONFIG.ENDPOINTS.ai.anomaly);
            
            const payload = {
                measurements,
                threshold: options.threshold || 0.5,
                window_size: options.windowSize || 10,
                ...options,
                timestamp: new Date().toISOString(),
            };
            
            return await this.api.post(url, payload);
        } catch (error) {
            console.error('Error in anomaly detection:', error);
            throw error;
        }
    }
    
    /**
     * Get AI service status
     * @returns {Promise<object>} Status information
     */
    async getStatus() {
        try {
            const url = getAPIUrl(API_CONFIG.ENDPOINTS.ai.status);
            return await this.api.get(url);
        } catch (error) {
            console.error('Error getting AI status:', error);
            return { status: 'unavailable', error: error.message };
        }
    }
    
    /**
     * Add message to chat history
     * @param {object} message - Message {role, content, timestamp}
     */
    addToHistory(message) {
        this.chatHistory.push(message);
        
        // Keep history size manageable
        if (this.chatHistory.length > this.maxChatHistory) {
            this.chatHistory = this.chatHistory.slice(-this.maxChatHistory);
        }
    }
    
    /**
     * Get chat history
     * @returns {array} Chat messages
     */
    getHistory() {
        return [...this.chatHistory];
    }
    
    /**
     * Clear chat history
     */
    clearHistory() {
        this.chatHistory = [];
    }
    
    /**
     * Format prediction for display
     * @param {object} prediction - Raw prediction
     * @returns {object} Formatted prediction
     */
    formatPrediction(prediction) {
        return {
            prediction: prediction.prediction,
            confidence: prediction.confidence || 0.95,
            timestamp: prediction.timestamp || new Date().toISOString(),
            metrics: prediction.metrics || {},
            recommendation: prediction.recommendation || 'Monitor closely',
            ...prediction,
        };
    }
    
    /**
     * Format AI response for display
     * @param {string} response - AI response text
     * @returns {object} Formatted response
     */
    formatResponse(response) {
        return {
            text: response,
            timestamp: new Date().toISOString(),
            type: 'text',
            actions: this.extractActions(response),
        };
    }
    
    /**
     * Extract actionable items from AI response
     * @param {string} response - Response text
     * @returns {array} Extracted actions
     */
    extractActions(response) {
        const actions = [];
        
        // Look for common action patterns
        const patterns = [
            { pattern: /check.*device/i, action: 'checkDevice' },
            { pattern: /calibrate/i, action: 'calibrateDevice' },
            { pattern: /replace.*filter/i, action: 'replaceFilter' },
            { pattern: /contact.*support/i, action: 'contactSupport' },
        ];
        
        patterns.forEach(({ pattern, action }) => {
            if (pattern.test(response)) {
                actions.push(action);
            }
        });
        
        return actions;
    }
}

// Create global instance
const aiService = new AIService(apiClient);

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AIService, aiService };
}
