/**
 * Dashboard Real-Time Updates - Example Implementation
 * 
 * This file demonstrates how to use the new Railway API integration
 * to display real-time sensor data and AI predictions on the dashboard.
 */

class DashboardManager {
    constructor() {
        this.devices = [];
        this.selectedDevice = null;
        this.updateInterval = 30000; // Update every 30 seconds
        this.updateTimer = null;
        this.charts = {};
        
        this.init();
    }
    
    /**
     * Initialize dashboard
     */
    async init() {
        console.log('[Dashboard] Initializing...');
        
        try {
            // Check API health
            const isHealthy = await apiClient.checkHealth();
            if (!isHealthy) {
                uiManager.showWarning('Backend API is not responding. Some features may be unavailable.', 10000);
            }
            
            // Load devices
            await this.loadDevices();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Start periodic updates
            this.startAutoUpdates();
            
            console.log('[Dashboard] Initialization complete');
        } catch (error) {
            console.error('[Dashboard] Initialization failed:', error);
            uiManager.showError('Failed to initialize dashboard', 5000);
        }
    }
    
    /**
     * Load all devices for current user
     */
    async loadDevices() {
        try {
            uiManager.showLoading('Loading devices...');
            
            const devices = await devicesService.listDevices({ limit: 100 });
            this.devices = devicesService.formatDevices(devices);
            
            console.log('[Dashboard] Loaded devices:', this.devices.length);
            
            this.renderDeviceCards();
            uiManager.hideLoading();
            
        } catch (error) {
            console.error('[Dashboard] Error loading devices:', error);
            uiManager.showError('Failed to load devices');
            throw error;
        }
    }
    
    /**
     * Render device cards on dashboard
     */
    renderDeviceCards() {
        const container = document.getElementById('devices-container');
        if (!container) {
            console.warn('[Dashboard] Container not found');
            return;
        }
        
        container.innerHTML = '';
        
        if (this.devices.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-info">
                        No devices found. <a href="/devices/">Add a device</a>
                    </div>
                </div>
            `;
            return;
        }
        
        this.devices.forEach(device => {
            const card = this.createDeviceCard(device);
            container.appendChild(card);
        });
    }
    
    /**
     * Create a device card element
     */
    createDeviceCard(device) {
        const div = document.createElement('div');
        div.className = 'col-md-6 col-lg-4 mb-4';
        div.dataset.deviceId = device.id;
        
        const statusClass = device.isOnline ? 'online' : 'offline';
        const statusText = device.isOnline ? '🟢 Online' : '⚫ Offline';
        const statusColor = device.isOnline ? '#28a745' : '#6c757d';
        
        div.innerHTML = `
            <div class="card device-card ${device.isOnline ? '' : 'offline'}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div>
                            <h5 class="card-title mb-1">${this.escapeHtml(device.name)}</h5>
                            <p class="text-muted mb-0" style="font-size: 0.875rem;">
                                ${this.escapeHtml(device.location || 'Unknown')}
                            </p>
                        </div>
                        <span class="device-status ${statusClass}" style="color: ${statusColor}">
                            ${statusText}
                        </span>
                    </div>
                    
                    <!-- Measurements Placeholder -->
                    <div class="mb-3 p-2 bg-light rounded">
                        <div id="measurements-${device.id}" class="measurements-loading">
                            <div class="spinner-border spinner-border-sm" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <span class="ms-2">Loading measurements...</span>
                        </div>
                    </div>
                    
                    <!-- Last Update -->
                    <p class="last-sync mb-0">
                        Last update: <span id="lastupdate-${device.id}">—</span>
                    </p>
                    
                    <!-- Actions -->
                    <div class="mt-3 d-flex gap-2">
                        <a href="/measurements/device/${device.id}/" class="btn btn-sm btn-outline-primary flex-grow-1">
                            History
                        </a>
                        <button class="btn btn-sm btn-outline-secondary" onclick="dashboardManager.refreshDevice('${device.id}')">
                            🔄 Refresh
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return div;
    }
    
    /**
     * Load and display measurements for a device
     */
    async loadDeviceMeasurements(deviceId) {
        try {
            const latest = await measurementsService.getLatestMeasurement(deviceId);
            const formatted = measurementsService.formatSensorReading(latest);
            
            this.displayMeasurements(deviceId, formatted);
            
        } catch (error) {
            console.error(`[Dashboard] Error loading measurements for ${deviceId}:`, error);
            this.displayMeasurementsError(deviceId);
        }
    }
    
    /**
     * Display measurements in device card
     */
    displayMeasurements(deviceId, measurement) {
        const container = document.getElementById(`measurements-${deviceId}`);
        if (!container) return;
        
        container.classList.remove('measurements-loading');
        container.innerHTML = `
            <p class="mb-2"><strong>Latest Reading:</strong></p>
            <div class="row g-2 text-center" style="font-size: 0.9rem;">
                ${measurement.pm25 !== null ? `
                    <div class="col-6">
                        <div class="measurement-value">
                            <div style="font-size: 1.25rem; font-weight: bold;">${measurement.pm25.toFixed(1)}</div>
                            <div style="color: #6c757d;">PM2.5 (μg/m³)</div>
                        </div>
                    </div>
                ` : ''}
                
                ${measurement.pm10 !== null ? `
                    <div class="col-6">
                        <div class="measurement-value">
                            <div style="font-size: 1.25rem; font-weight: bold;">${measurement.pm10.toFixed(1)}</div>
                            <div style="color: #6c757d;">PM10 (μg/m³)</div>
                        </div>
                    </div>
                ` : ''}
                
                ${measurement.temperature !== null ? `
                    <div class="col-6">
                        <div class="measurement-value">
                            <div style="font-size: 1.25rem; font-weight: bold;">${measurement.temperature.toFixed(1)}°C</div>
                            <div style="color: #6c757d;">Temperature</div>
                        </div>
                    </div>
                ` : ''}
                
                ${measurement.humidity !== null ? `
                    <div class="col-6">
                        <div class="measurement-value">
                            <div style="font-size: 1.25rem; font-weight: bold;">${measurement.humidity.toFixed(0)}%</div>
                            <div style="color: #6c757d;">Humidity</div>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        // Update last update time
        const timeElement = document.getElementById(`lastupdate-${deviceId}`);
        if (timeElement && measurement.timestamp) {
            const time = new Date(measurement.timestamp);
            timeElement.textContent = time.toLocaleString();
        }
    }
    
    /**
     * Display error loading measurements
     */
    displayMeasurementsError(deviceId) {
        const container = document.getElementById(`measurements-${deviceId}`);
        if (!container) return;
        
        container.classList.remove('measurements-loading');
        container.innerHTML = `
            <div class="alert alert-warning mb-0" style="font-size: 0.875rem;">
                ⚠️ Unable to load measurements
            </div>
        `;
    }
    
    /**
     * Manually refresh device data
     */
    async refreshDevice(deviceId) {
        console.log(`[Dashboard] Refreshing device ${deviceId}`);
        await this.loadDeviceMeasurements(deviceId);
        uiManager.showSuccess('Measurements updated');
    }
    
    /**
     * Start automatic updates
     */
    startAutoUpdates() {
        if (this.updateTimer) clearInterval(this.updateTimer);
        
        this.updateTimer = setInterval(async () => {
            console.log('[Dashboard] Auto-updating measurements...');
            
            for (const device of this.devices) {
                await this.loadDeviceMeasurements(device.id);
            }
        }, this.updateInterval);
    }
    
    /**
     * Stop automatic updates
     */
    stopAutoUpdates() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Stop updates when leaving page
        window.addEventListener('beforeunload', () => {
            this.stopAutoUpdates();
        });
        
        // Listen for API errors
        apiClient.onError((error) => {
            console.error('[Dashboard] API Error:', error);
        });
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize dashboard when document is ready
document.addEventListener('DOMContentLoaded', () => {
    // Create global dashboard instance
    window.dashboardManager = new DashboardManager();
    
    // Load all device measurements
    dashboardManager.devices.forEach(device => {
        dashboardManager.loadDeviceMeasurements(device.id);
    });
});
