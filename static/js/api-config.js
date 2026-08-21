/**
 * Centralized API Configuration for Railway FastAPI Backend Integration
 * 
 * This file defines all API endpoints and configuration for the FastAPI backend
 * hosted on Railway. Update BASE_URL here to switch between environments.
 */

const API_CONFIG = {
    // Railway FastAPI Backend URL
    BASE_URL: 'https://ai-senzor-de-calitate-a-aerului-production.up.railway.app',
    
    // API version (if the backend uses versioning)
    API_VERSION: 'v1',
    
    // Timeout for requests (in milliseconds)
    TIMEOUT: 30000,
    
    // Endpoints mapping
    ENDPOINTS: {
        // Measurements endpoints
        measurements: {
            list: '/measurements/list',
            latest: '/measurements/latest',
            history: '/measurements/history',
            byDevice: '/measurements/device',
        },
        
        // Devices endpoints
        devices: {
            list: '/devices/list',
            detail: '/devices/{id}',
            create: '/devices/create',
            update: '/devices/{id}/update',
        },
        
        // AI endpoints
        ai: {
            predict: '/predict',
            predictCustom: '/predict-custom',
            chat: '/chat',
            train: '/train',
            anomaly: '/anomaly',
        },
        
        // User endpoints
        user: {
            profile: '/user/profile',
            update: '/user/update',
        },
        
        // Health check
        health: '/health',
    },
};

/**
 * Get full URL for an endpoint
 * @param {string} endpointPath - The endpoint path
 * @returns {string} Full URL
 */
function getAPIUrl(endpointPath) {
    return API_CONFIG.BASE_URL + endpointPath;
}

/**
 * Get a specific endpoint URL with parameter substitution
 * @param {string} category - The endpoint category
 * @param {string} name - The endpoint name
 * @param {object} params - Optional parameters for path substitution
 * @returns {string} Full URL
 */
function getEndpointUrl(category, name, params = {}) {
    const categoryEndpoints = API_CONFIG.ENDPOINTS[category];
    if (!categoryEndpoints || !categoryEndpoints[name]) {
        console.error(`Endpoint not found: ${category}.${name}`);
        return null;
    }
    
    let url = getAPIUrl(categoryEndpoints[name]);
    
    // Replace path parameters
    for (const [key, value] of Object.entries(params)) {
        url = url.replace(`{${key}}`, value);
    }
    
    return url;
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_CONFIG, getAPIUrl, getEndpointUrl };
}
