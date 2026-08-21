/**
 * Devices Service - Handles all device-related API calls
 * 
 * Provides methods to:
 * - List user devices
 * - Get device details
 * - Create/update devices
 * - Get device status
 */

class DevicesService {
    constructor(apiClient) {
        this.api = apiClient;
    }
    
    /**
     * Get all devices for current user
     * @param {object} options - Options {limit, offset}
     * @returns {Promise<array>} List of devices
     */
    async listDevices(options = {}) {
        try {
            const url = getAPIUrl(API_CONFIG.ENDPOINTS.devices.list);
            const params = {
                limit: options.limit || 100,
                offset: options.offset || 0,
                ...options,
            };
            
            return await this.api.get(url, params);
        } catch (error) {
            console.error('Error fetching devices:', error);
            throw error;
        }
    }
    
    /**
     * Get specific device details
     * @param {string} deviceId - Device ID
     * @returns {Promise<object>} Device details
     */
    async getDevice(deviceId) {
        try {
            const url = getEndpointUrl('devices', 'detail', { id: deviceId });
            return await this.api.get(url);
        } catch (error) {
            console.error(`Error fetching device ${deviceId}:`, error);
            throw error;
        }
    }
    
    /**
     * Create new device
     * @param {object} deviceData - Device data {name, location, type}
     * @returns {Promise<object>} Created device
     */
    async createDevice(deviceData) {
        try {
            const url = getAPIUrl(API_CONFIG.ENDPOINTS.devices.create);
            return await this.api.post(url, deviceData);
        } catch (error) {
            console.error('Error creating device:', error);
            throw error;
        }
    }
    
    /**
     * Update device
     * @param {string} deviceId - Device ID
     * @param {object} updates - Fields to update
     * @returns {Promise<object>} Updated device
     */
    async updateDevice(deviceId, updates) {
        try {
            const url = getEndpointUrl('devices', 'update', { id: deviceId });
            return await this.api.put(url, updates);
        } catch (error) {
            console.error(`Error updating device ${deviceId}:`, error);
            throw error;
        }
    }
    
    /**
     * Get device status (online/offline, last update)
     * @param {string} deviceId - Device ID
     * @returns {Promise<object>} Device status
     */
    async getDeviceStatus(deviceId) {
        try {
            const url = getEndpointUrl('devices', 'detail', { id: deviceId });
            const device = await this.api.get(url);
            
            return {
                deviceId,
                isOnline: device.is_online || device.last_update ? 
                    this.isRecentlyActive(device.last_update) : false,
                lastUpdate: device.last_update || device.updated_at,
                location: device.location || 'Unknown',
                name: device.name,
            };
        } catch (error) {
            console.error(`Error getting device status ${deviceId}:`, error);
            return { deviceId, isOnline: false, error: error.message };
        }
    }
    
    /**
     * Check if device was active recently (within last 5 minutes)
     * @param {string} lastUpdate - ISO timestamp
     * @returns {boolean}
     */
    isRecentlyActive(lastUpdate) {
        if (!lastUpdate) return false;
        const lastUpdateTime = new Date(lastUpdate);
        const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
        return lastUpdateTime > fiveMinutesAgo;
    }
    
    /**
     * Format devices for display
     * @param {array} devices - Raw device list
     * @returns {array} Formatted devices
     */
    formatDevices(devices) {
        if (!Array.isArray(devices)) return [];
        
        return devices.map(device => ({
            id: device.id,
            name: device.name || 'Unnamed Device',
            location: device.location || 'Unknown Location',
            type: device.type || 'sensor',
            lastMeasurement: device.last_measurement || device.last_update,
            status: this.isRecentlyActive(device.last_update) ? 'online' : 'offline',
            isOnline: this.isRecentlyActive(device.last_update),
            createdAt: device.created_at,
            ...device,
        }));
    }
}

// Create global instance
const devicesService = new DevicesService(apiClient);

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DevicesService, devicesService };
}
