/**
 * Measurements Service - Handles all measurement-related API calls
 * 
 * Provides methods to:
 * - Fetch measurements for a device
 * - Get latest measurements
 * - Get measurement history
 */

class MeasurementsService {
    constructor(apiClient) {
        this.api = apiClient;
    }
    
    /**
     * Get all measurements for a device
     * @param {string} deviceId - Device ID
     * @param {object} options - Options {limit, offset, order}
     * @returns {Promise<array>} List of measurements
     */
    async getDeviceMeasurements(deviceId, options = {}) {
        try {
            const url = getEndpointUrl('measurements', 'byDevice');
            const params = {
                device_id: deviceId,
                limit: options.limit || 100,
                offset: options.offset || 0,
                ...options,
            };
            
            return await this.api.get(url, params);
        } catch (error) {
            console.error('Error fetching device measurements:', error);
            throw error;
        }
    }
    
    /**
     * Get latest measurement for a device
     * @param {string} deviceId - Device ID
     * @returns {Promise<object>} Latest measurement
     */
    async getLatestMeasurement(deviceId) {
        try {
            const url = getEndpointUrl('measurements', 'latest');
            return await this.api.get(url, { device_id: deviceId });
        } catch (error) {
            console.error('Error fetching latest measurement:', error);
            throw error;
        }
    }
    
    /**
     * Get measurement history for a device
     * @param {string} deviceId - Device ID
     * @param {object} options - Options {startDate, endDate, limit}
     * @returns {Promise<object>} History data with timestamps and values
     */
    async getMeasurementHistory(deviceId, options = {}) {
        try {
            const url = getEndpointUrl('measurements', 'history');
            const params = {
                device_id: deviceId,
                ...options,
            };
            
            return await this.api.get(url, params);
        } catch (error) {
            console.error('Error fetching measurement history:', error);
            throw error;
        }
    }
    
    /**
     * Format measurement data for chart display
     * @param {array} measurements - Raw measurement data
     * @returns {object} Formatted data suitable for charting
     */
    formatForChart(measurements) {
        if (!Array.isArray(measurements)) {
            return { timestamps: [], values: {} };
        }
        
        const timestamps = [];
        const metrics = {};
        
        measurements.forEach(m => {
            timestamps.push(m.created_at || m.timestamp);
            
            // Extract all numeric fields as metrics
            Object.entries(m).forEach(([key, value]) => {
                if (key !== 'id' && key !== 'device_id' && key !== 'created_at' && key !== 'timestamp') {
                    if (!metrics[key]) metrics[key] = [];
                    metrics[key].push(value);
                }
            });
        });
        
        return { timestamps, metrics };
    }
    
    /**
     * Get current sensor readings (latest values)
     * @param {string} deviceId - Device ID
     * @returns {Promise<object>} Current sensor values
     */
    async getCurrentReadings(deviceId) {
        try {
            const latest = await this.getLatestMeasurement(deviceId);
            return this.formatSensorReading(latest);
        } catch (error) {
            console.error('Error getting current readings:', error);
            return {};
        }
    }
    
    /**
     * Format a single measurement as sensor reading
     * @param {object} measurement - Raw measurement
     * @returns {object} Formatted sensor reading
     */
    formatSensorReading(measurement) {
        if (!measurement) return {};
        
        return {
            timestamp: measurement.created_at || measurement.timestamp || new Date().toISOString(),
            pm25: measurement.pm25 || measurement.PM2_5 || null,
            pm10: measurement.pm10 || measurement.PM10 || null,
            temperature: measurement.temperature || measurement.temp || null,
            humidity: measurement.humidity || null,
            pressure: measurement.pressure || null,
            co2: measurement.co2 || null,
            tvoc: measurement.tvoc || null,
            // Add other fields as they exist
            ...measurement,
        };
    }
}

// Create global instance
const measurementsService = new MeasurementsService(apiClient);

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MeasurementsService, measurementsService };
}
