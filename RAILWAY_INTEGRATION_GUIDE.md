# Railway FastAPI Integration Guide

**Integration Date:** August 2024  
**Backend URL:** `https://ai-senzor-de-calitate-a-aerului-production.up.railway.app`  
**Frontend Type:** Django with JavaScript/Fetch API

---

## Overview

This document explains how the frontend has been integrated with the FastAPI backend hosted on Railway. The integration provides:

- **Centralized API Configuration** - All endpoints defined in one place
- **API Client Layer** - Handles requests, errors, and retries
- **Service Classes** - Domain-specific functionality (Measurements, Devices, AI)
- **UI Manager** - Loading states, error handling, notifications
- **Error Handling** - Network errors, timeouts, and user-friendly messages
- **Real-time Updates** - Support for live sensor data and AI predictions

---

## Architecture

### JavaScript File Structure

```
static/js/
├── api-config.js           # Centralized configuration (BASE_URL, endpoints)
├── api-client.js           # HTTP client with retry logic
├── measurements-service.js # Measurement data operations
├── devices-service.js      # Device management operations
├── ai-service.js          # AI chat and predictions
├── ui-manager.js          # UI state and notifications
└── supabase-realtime.js   # Existing Supabase real-time (kept for compatibility)
```

### Global Instances

Each service creates a global instance that can be used anywhere:

```javascript
// API Configuration
API_CONFIG          // Contains BASE_URL and endpoint mappings
getAPIUrl()        // Get full URL for an endpoint
getEndpointUrl()   // Get URL with parameter substitution

// API Client
apiClient          // Main HTTP client instance

// Services
measurementsService // Measurement operations
devicesService     // Device operations
aiService          // AI chat and predictions

// UI Management
uiManager          // Loading states and notifications
```

---

## Configuration

### 1. Update Backend URL

**File:** `static/js/api-config.js`

To change the backend URL (e.g., for local development or different environment):

```javascript
const API_CONFIG = {
    // Change this URL
    BASE_URL: 'https://ai-senzor-de-calitate-a-aerului-production.up.railway.app',
    // or locally: 'http://localhost:8000'
    // or testing: 'https://api-staging.example.com'
    
    API_VERSION: 'v1',
    TIMEOUT: 30000,
    // ... endpoints
};
```

### 2. Environment-Specific Configuration

Create different config files for different environments:

**For local development:** `static/js/api-config-local.js`
```javascript
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',
    // ...
};
```

**For production:** Already using Railway URL

### 3. Available Endpoints

All endpoints are defined in `api-config.js`:

```javascript
ENDPOINTS: {
    measurements: {
        list: '/measurements/list',
        latest: '/measurements/latest',
        history: '/measurements/history',
        byDevice: '/measurements/device',
    },
    devices: {
        list: '/devices/list',
        detail: '/devices/{id}',
        create: '/devices/create',
        update: '/devices/{id}/update',
    },
    ai: {
        predict: '/ai/predict',
        chat: '/ai/chat',
        train: '/ai/train',
        status: '/ai/status',
    },
    user: {
        profile: '/user/profile',
        update: '/user/update',
    },
    health: '/health',
}
```

---

## Usage Examples

### 1. Fetch Measurements

```javascript
// Get measurements for a device
const deviceId = 'AQM-12345';

try {
    const measurements = await measurementsService.getDeviceMeasurements(deviceId, {
        limit: 100,
        offset: 0,
    });
    
    console.log(measurements);
    // Automatically handles loading states and errors
} catch (error) {
    console.error('Failed to fetch measurements:', error);
}
```

### 2. Get Latest Sensor Reading

```javascript
// Get the latest measurement
const reading = await measurementsService.getCurrentReadings(deviceId);

console.log(reading);
// Output:
// {
//     timestamp: '2024-08-07T10:30:00Z',
//     pm25: 25.5,
//     pm10: 45.2,
//     temperature: 22.5,
//     humidity: 65,
//     // ...
// }
```

### 3. Format Measurements for Charts

```javascript
const measurements = await measurementsService.getDeviceMeasurements(deviceId);
const chartData = measurementsService.formatForChart(measurements);

// {
//     timestamps: ['2024-08-07T10:00Z', '2024-08-07T10:30Z', ...],
//     metrics: {
//         pm25: [24.5, 25.5, 26.0],
//         temperature: [22.0, 22.5, 23.0],
//         ...
//     }
// }

// Use with Chart.js
const ctx = document.getElementById('myChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: chartData.timestamps,
        datasets: [
            {
                label: 'PM2.5',
                data: chartData.metrics.pm25,
                borderColor: '#ff6b6b',
            },
            {
                label: 'Temperature',
                data: chartData.metrics.temperature,
                borderColor: '#4ecdc4',
            },
        ],
    },
});
```

### 4. List Devices

```javascript
// Get all user devices
try {
    const devices = await devicesService.listDevices({ limit: 50 });
    console.log(devices);
    
    // Get formatted devices with status
    const formatted = devicesService.formatDevices(devices);
    console.log(formatted);
    
} catch (error) {
    console.error('Failed to fetch devices:', error);
}
```

### 5. Get Device Status

```javascript
// Check if device is online and when it last reported
const status = await devicesService.getDeviceStatus(deviceId);

console.log(status);
// {
//     deviceId: 'AQM-12345',
//     isOnline: true,
//     lastUpdate: '2024-08-07T10:30:00Z',
//     location: 'Office',
//     name: 'Air Quality Monitor #1'
// }
```

### 6. AI Chat

```javascript
// Send a message to AI
try {
    const response = await aiService.chat('What is the air quality status?', {
        deviceId: 'AQM-12345',
        deviceName: 'Office Monitor',
    });
    
    console.log(response.message);
    // "Based on the latest measurements, the air quality is good..."
    
} catch (error) {
    console.error('Chat failed:', error);
}
```

### 7. Get AI Prediction

```javascript
// Get AI prediction based on sensor data
const prediction = await aiService.predict({
    pm25: 25.5,
    temperature: 22.5,
    humidity: 65,
    timestamp: new Date().toISOString(),
});

const formatted = aiService.formatPrediction(prediction);
console.log(formatted);
// {
//     prediction: 'Air quality will remain good',
//     confidence: 0.95,
//     recommendation: 'No action needed',
//     ...
// }
```

### 8. UI Notifications

```javascript
// Show loading
uiManager.showLoading('Fetching data...');

// Show success
uiManager.showSuccess('Data loaded successfully!');

// Show error
uiManager.showError('Failed to load data', 5000); // Auto-dismiss after 5 seconds

// Show warning
uiManager.showWarning('Device offline for 10 minutes');

// Show info
uiManager.showInfo('Data refreshed');

// Show confirmation dialog
uiManager.showConfirm(
    'Are you sure you want to delete this device?',
    () => {
        // On confirm
        deleteDevice();
    },
    () => {
        // On cancel
        console.log('Cancelled');
    }
);
```

---

## Error Handling

### Automatic Error Handling

The API client automatically handles errors and displays user-friendly messages:

```javascript
// Network timeout -> "Request timed out. Please check your connection."
// 401 Not Found -> "You need to be logged in. Please refresh the page."
// 403 Forbidden -> "You do not have permission to access this resource."
// 404 Not Found -> "The requested resource was not found."
// 500 Server Error -> "Server error. Please try again later."
```

### Custom Error Handling

```javascript
// Listen to errors
apiClient.onError((error) => {
    console.error('API Error:', error);
    console.error('Error message:', error.message);
    console.error('Status code:', error.status);
    
    // Handle specific errors
    if (error.status === 401) {
        // Redirect to login
        window.location.href = '/qr-login/';
    }
});
```

---

## Loading States

### Global Loading Spinner

Automatically managed by `uiManager`:

```javascript
// Automatically shown during API calls
// Automatically hidden when calls complete
// Triggered by apiClient.onLoadingChange()
```

### Element-Level Loading

```javascript
// Show loading state on a button
uiManager.setElementLoading('saveButton', true, 'Saving...');

// After operation completes
uiManager.setElementLoading('saveButton', false);
```

---

## Real-Time Updates

### Using Supabase Realtime (Existing)

The existing `supabase-realtime.js` is kept for backward compatibility:

```javascript
// Already integrated in device dashboard
const realtimeManager = new SupabaseRealtimeManager(
    supabaseUrl,
    supabaseKey,
    deviceId,
    userId
);

await realtimeManager.init();
// Automatically subscribes to measurements changes
```

### Polling for Updates (Alternative)

If you need to poll the API for updates:

```javascript
// Poll measurements every 10 seconds
setInterval(async () => {
    try {
        const latest = await measurementsService.getLatestMeasurement(deviceId);
        updateUI(latest);
    } catch (error) {
        console.error('Polling failed:', error);
    }
}, 10000);
```

---

## Debugging

### Enable/Disable Logging

```javascript
// Enable detailed logging (default)
apiClient.logEnabled = true;

// Disable logging for production
apiClient.logEnabled = false;
```

### Check API Health

```javascript
// Check if backend is available
const isHealthy = await apiClient.checkHealth();
console.log('API Health:', isHealthy ? 'OK' : 'Unavailable');
```

### View Last Error

```javascript
console.log('Last API error:', apiClient.lastError);
```

### Monitor Loading State

```javascript
apiClient.onLoadingChange((isLoading) => {
    console.log('Loading:', isLoading);
});
```

---

## Authentication

### Session-Based (Django)

The session ID is automatically included in requests via Django's session middleware.

### Token-Based (Optional)

If your FastAPI backend uses JWT tokens:

```javascript
// Store token in localStorage
localStorage.setItem('auth_token', jwtToken);

// Automatically added to headers in apiClient.getHeaders()
// Headers: Authorization: Bearer <token>
```

### User ID (Supabase)

If using Supabase Auth:

```javascript
// Store in sessionStorage (from Django session)
sessionStorage.setItem('supabase_user_id', userId);

// Automatically added to headers in apiClient.getHeaders()
// Headers: X-User-ID: <userId>
```

---

## Implementation Checklist

- [x] Create centralized API configuration (`api-config.js`)
- [x] Implement API client with retry logic (`api-client.js`)
- [x] Create measurement service (`measurements-service.js`)
- [x] Create devices service (`devices-service.js`)
- [x] Create AI service (`ai-service.js`)
- [x] Implement UI manager (`ui-manager.js`)
- [x] Update base template with scripts
- [ ] Update dashboard template to use new services
- [ ] Update device detail template for real-time updates
- [ ] Update measurements history page
- [ ] Implement AI chat interface
- [ ] Add error boundaries and fallbacks
- [ ] Test all endpoints with Railway backend
- [ ] Verify authentication flow
- [ ] Performance testing and optimization

---

## Migration from Local API

### Before (Django views)

```javascript
fetch("{% url 'measurements:latest_data' %}", {
    method: 'GET',
})
.then(r => r.json())
.then(data => console.log(data))
.catch(e => console.error(e));
```

### After (Railway API)

```javascript
const data = await measurementsService.getLatestMeasurement(deviceId);
console.log(data);
```

### Benefits

- ✅ Centralized configuration
- ✅ Automatic error handling
- ✅ Retry logic for failed requests
- ✅ Loading state management
- ✅ Better code organization
- ✅ Easier testing and maintenance
- ✅ Consistent across all components

---

## Troubleshooting

### Backend not responding

**Symptom:** All API calls return timeout errors

**Solution:**
1. Check Railway backend is running: `curl https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/health`
2. Verify network connection
3. Check CORS configuration on backend

### 401 Unauthorized Errors

**Symptom:** All requests return 401

**Solution:**
1. Verify user is logged in
2. Check authentication token/session ID
3. Verify backend authentication expects

### CORS Errors

**Symptom:** Browser console shows CORS error

**Solution:**
1. Ensure FastAPI backend has CORS middleware configured
2. Check `ALLOWED_ORIGINS` includes your frontend URL
3. Add proper CORS headers to backend responses

### Endpoints not found

**Symptom:** 404 errors on all requests

**Solution:**
1. Verify endpoint paths match backend API documentation
2. Update `API_CONFIG.ENDPOINTS` if paths changed
3. Check API version compatibility

---

## Performance Tips

1. **Cache measurements** - Store recent data locally to reduce requests
2. **Lazy load charts** - Only fetch data when chart becomes visible
3. **Batch requests** - Combine multiple measurements in one request if possible
4. **Adjust timeout** - Increase `API_CONFIG.TIMEOUT` for slow connections
5. **Disable logging in production** - Set `apiClient.logEnabled = false`

---

## Next Steps

1. Test integration with actual Railway backend
2. Update all templates to use new services
3. Implement real-time chart updates
4. Add offline support with localStorage caching
5. Performance optimization and monitoring

