/**
 * Supabase Realtime Integration for Dashboard
 * - Connects to Supabase Realtime on page load
 * - Subscribes to measurements for user's devices
 * - Updates UI and charts in real-time
 * - Maintains in-memory history
 * - Cleans up on page unload
 */

class SupabaseRealtimeManager {
    constructor(supabaseUrl, supabaseKey, deviceId, userId) {
        this.supabaseUrl = supabaseUrl;
        this.supabaseKey = supabaseKey;
        this.deviceId = deviceId;
        this.userId = userId;
        
        // Import Supabase client from CDN
        this.client = null;
        this.channel = null;
        this.measurements = []; // In-memory history
        this.maxHistorySize = 1000;
        this.charts = {}; // Store chart instances
        this.isConnected = false;
        
        console.log(`[Realtime] Initialized for device: ${deviceId}, user: ${userId}`);
    }

    /**
     * Initialize Supabase client and connect to Realtime
     */
    async init() {
        try {
            // Wait for Supabase to be available globally
            if (typeof supabase === 'undefined') {
                console.error('[Realtime] Supabase client not loaded');
                return false;
            }

            this.client = supabase.createClient(this.supabaseUrl, this.supabaseKey);
            console.log('[Realtime] Supabase client initialized');
            
            // Connect to Realtime
            await this.connectToRealtime();
            return true;
        } catch (error) {
            console.error('[Realtime] Initialization failed:', error);
            return false;
        }
    }

    /**
     * Connect to Supabase Realtime and subscribe to measurements
     */
    async connectToRealtime() {
        try {
            // Subscribe to measurements table for this device
            // Filter by device_id using Realtime's filtering
            this.channel = this.client
                .channel(`measurements:device_id=eq.${this.deviceId}`)
                .on(
                    'postgres_changes',
                    {
                        event: 'INSERT',
                        schema: 'public',
                        table: 'measurements',
                        filter: `device_id=eq.${this.deviceId}`
                    },
                    (payload) => this.handleMeasurementInsert(payload)
                )
                .on(
                    'postgres_changes',
                    {
                        event: 'UPDATE',
                        schema: 'public',
                        table: 'measurements',
                        filter: `device_id=eq.${this.deviceId}`
                    },
                    (payload) => this.handleMeasurementUpdate(payload)
                )
                .subscribe((status) => {
                    if (status === 'SUBSCRIBED') {
                        this.isConnected = true;
                        console.log(`[Realtime] ✅ Connected and subscribed to device ${this.deviceId}`);
                        this.showNotification('Connected to real-time updates', 'success');
                    } else if (status === 'CLOSED') {
                        this.isConnected = false;
                        console.log('[Realtime] Channel closed');
                    } else if (status === 'CHANNEL_ERROR') {
                        this.isConnected = false;
                        console.error('[Realtime] Channel error');
                        this.showNotification('Connection error', 'error');
                    }
                });

        } catch (error) {
            console.error('[Realtime] Failed to connect:', error);
            this.showNotification('Failed to connect to real-time updates', 'error');
        }
    }

    /**
     * Handle new measurement INSERT event
     */
    handleMeasurementInsert(payload) {
        const measurement = payload.new;
        console.log('[Realtime] New measurement received:', measurement);
        
        // Add to in-memory history
        this.addToHistory(measurement);
        
        // Update UI elements
        this.updateSensorValues(measurement);
        
        // Update all charts
        this.updateCharts(measurement);
        
        // Show visual feedback
        this.showNotification('📊 Measurement updated', 'info');
    }

    /**
     * Handle measurement UPDATE event
     */
    handleMeasurementUpdate(payload) {
        const measurement = payload.new;
        console.log('[Realtime] Measurement updated:', measurement);
        
        // Update UI elements
        this.updateSensorValues(measurement);
        
        // Update charts
        this.updateCharts(measurement);
        
        this.showNotification('📊 Measurement updated', 'info');
    }

    /**
     * Add measurement to in-memory history
     */
    addToHistory(measurement) {
        this.measurements.push(measurement);
        
        // Keep only last maxHistorySize measurements
        if (this.measurements.length > this.maxHistorySize) {
            this.measurements.shift();
        }
        
        console.log(`[Realtime] History size: ${this.measurements.length}`);
    }

    /**
     * Update sensor value displays
     */
    updateSensorValues(measurement) {
        const sensorMap = {
            'temperatura': ['temperatura', '°C'],
            'umiditate': ['umiditate', '%'],
            'presiune': ['presiune', ' hPa'],
            'co2': ['co2', ' ppm'],
            'pm1': ['pm1', ''],
            'pm25': ['pm25', ''],
            'pm10': ['pm10', ''],
            'voc': ['voc', ''],
            'lux': ['lux', '']
        };

        for (const [key, [dataKey, unit]] of Object.entries(sensorMap)) {
            const value = measurement[dataKey];
            if (value !== undefined && value !== null) {
                const elements = document.querySelectorAll(
                    `[data-sensor-value="${key}"], [data-sensor="${key}"]`
                );
                
                elements.forEach(el => {
                    // Format value
                    let displayValue = value;
                    if (typeof value === 'number') {
                        displayValue = value.toLocaleString('ro-RO', {
                            minimumFractionDigits: 1,
                            maximumFractionDigits: 1
                        });
                    }
                    
                    el.textContent = displayValue + unit;
                    el.style.animation = 'pulse 0.5s ease-in-out';
                    
                    // Remove animation after it completes
                    setTimeout(() => {
                        el.style.animation = '';
                    }, 500);
                });
            }
        }

        // Update timestamp
        const timestamp = measurement.created_at;
        if (timestamp) {
            const date = new Date(timestamp);
            const formatted = date.toLocaleString('ro-RO');
            const timestampElements = document.querySelectorAll('[data-sensor="timestamp"]');
            timestampElements.forEach(el => {
                el.textContent = formatted;
            });
        }
    }

    /**
     * Update Chart.js charts with new data
     */
    updateCharts(measurement) {
        if (!window.chartInstances) {
            console.log('[Realtime] No charts found on this page');
            return;
        }

        const chartsToUpdate = [
            { key: 'temperatura', chartId: 'temperatureChart' },
            { key: 'umiditate', chartId: 'humidityChart' },
            { key: 'presiune', chartId: 'pressureChart' },
            { key: 'co2', chartId: 'co2Chart' },
            { key: 'pm1', chartId: 'pm1Chart' },
            { key: 'pm25', chartId: 'pm25Chart' },
            { key: 'pm10', chartId: 'pm10Chart' },
            { key: 'voc', chartId: 'vocChart' },
            { key: 'lux', chartId: 'luxChart' }
        ];

        chartsToUpdate.forEach(({ key, chartId }) => {
            const chart = window.chartInstances[chartId];
            if (!chart) return;

            const value = measurement[key];
            if (value === undefined || value === null) return;

            // Add timestamp to labels
            const timestamp = new Date(measurement.created_at).toLocaleTimeString('ro-RO');
            
            // Keep only last 100 data points for performance
            const maxDataPoints = 100;
            
            chart.data.labels.push(timestamp);
            chart.data.datasets[0].data.push(value);
            
            // Remove oldest data points if exceeding limit
            if (chart.data.labels.length > maxDataPoints) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            
            // Update chart
            chart.update('none'); // 'none' = no animation, just update
            
            console.log(`[Realtime] Updated chart: ${chartId}`);
        });
    }

    /**
     * Store chart instances globally for updates
     */
    registerChart(chartId, chartInstance) {
        if (!window.chartInstances) {
            window.chartInstances = {};
        }
        window.chartInstances[chartId] = chartInstance;
        console.log(`[Realtime] Registered chart: ${chartId}`);
    }

    /**
     * Get in-memory history
     */
    getHistory() {
        return this.measurements;
    }

    /**
     * Clear in-memory history
     */
    clearHistory() {
        this.measurements = [];
        console.log('[Realtime] History cleared');
    }

    /**
     * Show notification to user
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.role = 'alert';
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '300px';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    /**
     * Disconnect from Realtime
     */
    disconnect() {
        if (this.channel) {
            console.log('[Realtime] Disconnecting from Realtime...');
            this.client.removeChannel(this.channel);
            this.isConnected = false;
            console.log('[Realtime] ✅ Disconnected');
        }
    }

    /**
     * Reconnect to Realtime
     */
    async reconnect() {
        console.log('[Realtime] Reconnecting...');
        this.disconnect();
        await this.connectToRealtime();
    }
}

// Global instance
let realtimeManager = null;

/**
 * Initialize Realtime when page loads
 */
function initializeRealtime(supabaseUrl, supabaseKey, deviceId, userId) {
    console.log('[Realtime] Initializing Supabase Realtime...');
    
    realtimeManager = new SupabaseRealtimeManager(
        supabaseUrl,
        supabaseKey,
        deviceId,
        userId
    );
    
    realtimeManager.init();
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (realtimeManager) {
            realtimeManager.disconnect();
        }
    });

    // Cleanup when navigating away
    window.addEventListener('pagehide', () => {
        if (realtimeManager) {
            realtimeManager.disconnect();
        }
    });

    return realtimeManager;
}

// CSS for pulse animation
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .realtime-updating {
        animation: pulse 0.5s ease-in-out;
    }
    
    .realtime-status {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    
    .realtime-status.connected {
        background-color: #28a745;
        animation: pulse 2s infinite;
    }
    
    .realtime-status.disconnected {
        background-color: #dc3545;
    }
`;
document.head.appendChild(style);

console.log('[Realtime] Script loaded and ready');
