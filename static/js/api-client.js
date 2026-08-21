/**
 * Railway FastAPI Client - Unified API communication layer
 * 
 * Handles all HTTP requests to the FastAPI backend with:
 * - Centralized error handling
 * - Request/response logging
 * - Loading state management
 * - Authentication header management
 * - Retry logic for failed requests
 */

class RailwayAPIClient {
    constructor() {
        this.timeout = API_CONFIG.TIMEOUT || 30000;
        this.isLoading = false;
        this.lastError = null;
        this.retryAttempts = 3;
        this.retryDelay = 1000; // milliseconds
        
        // Callbacks for UI updates
        this.loadingCallbacks = [];
        this.errorCallbacks = [];
        
        this.logEnabled = true; // Set to false in production
    }
    
    /**
     * Log messages to console (can be disabled in production)
     */
    log(message, data = null) {
        if (this.logEnabled) {
            console.log(`[API Client] ${message}`, data || '');
        }
    }
    
    /**
     * Register callback for loading state changes
     * @param {function} callback - Called with (isLoading) boolean
     */
    onLoadingChange(callback) {
        this.loadingCallbacks.push(callback);
    }
    
    /**
     * Register callback for errors
     * @param {function} callback - Called with (error) object
     */
    onError(callback) {
        this.errorCallbacks.push(callback);
    }
    
    /**
     * Notify loading state change
     */
    setLoading(isLoading) {
        this.isLoading = isLoading;
        this.loadingCallbacks.forEach(cb => cb(isLoading));
    }
    
    /**
     * Notify error
     */
    notifyError(error) {
        this.lastError = error;
        this.errorCallbacks.forEach(cb => cb(error));
    }
    
    /**
     * Get authentication headers (if needed)
     * @returns {object} Headers object
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        // Add authentication token if available
        const authToken = localStorage.getItem('auth_token');
        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }
        
        // Add user ID if available (for Supabase auth)
        const userId = sessionStorage.getItem('supabase_user_id');
        if (userId) {
            headers['X-User-ID'] = userId;
        }
        
        return headers;
    }
    
    /**
     * Make HTTP request with retry logic
     * @param {string} url - Full URL
     * @param {object} options - Fetch options (method, body, etc.)
     * @param {number} attempt - Current retry attempt
     * @returns {Promise<object>} Response data
     */
    async fetchWithRetry(url, options = {}, attempt = 1) {
        try {
            this.log(`[${options.method || 'GET'}] ${url} (Attempt ${attempt})`);
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            const response = await fetch(url, {
                ...options,
                headers: {
                    ...this.getHeaders(),
                    ...options.headers,
                },
                signal: controller.signal,
            });
            
            clearTimeout(timeoutId);
            
            // Handle non-JSON responses
            const contentType = response.headers.get('content-type');
            let data = null;
            
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }
            
            // Log response
            this.log(`Response Status: ${response.status}`, data);
            
            if (!response.ok) {
                const error = new Error(
                    data?.detail || data?.message || 
                    `HTTP ${response.status}: ${response.statusText}`
                );
                error.status = response.status;
                error.data = data;
                throw error;
            }
            
            return data;
            
        } catch (error) {
            // Retry on network errors or timeouts (but not on HTTP errors)
            if (attempt < this.retryAttempts && 
                (error.name === 'AbortError' || error instanceof TypeError)) {
                
                this.log(`Retry attempt ${attempt + 1} after ${this.retryDelay}ms`);
                await new Promise(resolve => setTimeout(resolve, this.retryDelay));
                return this.fetchWithRetry(url, options, attempt + 1);
            }
            
            throw error;
        }
    }
    
    /**
     * GET request
     * @param {string} url - Endpoint URL
     * @param {object} params - Query parameters
     * @returns {Promise<object>} Response data
     */
    async get(url, params = {}) {
        try {
            this.setLoading(true);
            
            // Build query string
            const queryString = new URLSearchParams(params).toString();
            const fullUrl = queryString ? `${url}?${queryString}` : url;
            
            const data = await this.fetchWithRetry(fullUrl, { method: 'GET' });
            this.setLoading(false);
            return data;
            
        } catch (error) {
            this.setLoading(false);
            this.notifyError(error);
            this.log('Error in GET request:', error.message);
            throw error;
        }
    }
    
    /**
     * POST request
     * @param {string} url - Endpoint URL
     * @param {object} body - Request body
     * @returns {Promise<object>} Response data
     */
    async post(url, body = {}) {
        try {
            this.setLoading(true);
            
            const data = await this.fetchWithRetry(url, {
                method: 'POST',
                body: JSON.stringify(body),
            });
            
            this.setLoading(false);
            return data;
            
        } catch (error) {
            this.setLoading(false);
            this.notifyError(error);
            this.log('Error in POST request:', error.message);
            throw error;
        }
    }
    
    /**
     * PUT request
     * @param {string} url - Endpoint URL
     * @param {object} body - Request body
     * @returns {Promise<object>} Response data
     */
    async put(url, body = {}) {
        try {
            this.setLoading(true);
            
            const data = await this.fetchWithRetry(url, {
                method: 'PUT',
                body: JSON.stringify(body),
            });
            
            this.setLoading(false);
            return data;
            
        } catch (error) {
            this.setLoading(false);
            this.notifyError(error);
            this.log('Error in PUT request:', error.message);
            throw error;
        }
    }
    
    /**
     * DELETE request
     * @param {string} url - Endpoint URL
     * @returns {Promise<object>} Response data
     */
    async delete(url) {
        try {
            this.setLoading(true);
            
            const data = await this.fetchWithRetry(url, { method: 'DELETE' });
            
            this.setLoading(false);
            return data;
            
        } catch (error) {
            this.setLoading(false);
            this.notifyError(error);
            this.log('Error in DELETE request:', error.message);
            throw error;
        }
    }
    
    /**
     * Check API health/availability
     * @returns {Promise<boolean>} True if API is available
     */
    async checkHealth() {
        try {
            const response = await fetch(getAPIUrl(API_CONFIG.ENDPOINTS.health), {
                method: 'GET',
                timeout: 5000,
            });
            return response.ok;
        } catch (error) {
            this.log('Health check failed:', error.message);
            return false;
        }
    }
}

// Create global instance
const apiClient = new RailwayAPIClient();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { RailwayAPIClient, apiClient };
}
