# Quick Start Guide - Railway API Integration

**Last Updated:** August 2024  
**Status:** ✅ Ready for Implementation

---

## What's New

A complete JavaScript API integration layer has been added to connect the Django frontend with the FastAPI backend hosted on Railway. This includes:

- ✅ Centralized API configuration
- ✅ Automatic request/response handling
- ✅ Error handling and retry logic
- ✅ Service classes for Measurements, Devices, and AI
- ✅ UI utilities for loading states and notifications
- ✅ Example implementations for Dashboard and AI Chat

---

## File Structure

```
static/js/
├── api-config.js              # 🎯 API endpoints and configuration
├── api-client.js              # 📡 HTTP client with retries
├── measurements-service.js    # 📊 Measurement operations
├── devices-service.js         # 🖥️ Device operations
├── ai-service.js             # 🤖 AI chat and predictions
├── ui-manager.js             # 🎨 UI state management
├── dashboard-manager.js      # 📈 Dashboard implementation example
├── ai-chat-manager.js        # 💬 AI chat interface example
└── supabase-realtime.js      # ⏱️ (existing) Real-time updates
```

---

## Quick Integration Steps

### 1. Verify Scripts are Loaded

Open browser DevTools (F12) → Console and check:

```javascript
// These should all exist
console.log(API_CONFIG);      // ✓ Configuration object
console.log(apiClient);       // ✓ API client instance
console.log(measurementsService); // ✓ Measurements service
console.log(devicesService);  // ✓ Devices service
console.log(aiService);       // ✓ AI service
console.log(uiManager);       // ✓ UI manager
```

### 2. Check Backend Connection

```javascript
// Check if backend is responding
apiClient.checkHealth().then(health => {
    console.log('Backend status:', health ? 'OK ✓' : 'Offline ✗');
});
```

### 3. Fetch Sample Data

```javascript
// Get devices
devicesService.listDevices().then(devices => {
    console.log('Devices:', devices);
});

// Get latest measurement for a device
measurementsService.getLatestMeasurement('DEVICE_ID').then(measurement => {
    console.log('Latest reading:', measurement);
});
```

### 4. Test UI Notifications

```javascript
// Test notifications
uiManager.showSuccess('This is a success message!');
setTimeout(() => uiManager.showError('This is an error message!'), 1000);
setTimeout(() => uiManager.showWarning('This is a warning!'), 2000);
setTimeout(() => uiManager.showInfo('This is info!'), 3000);
```

---

## Implementation Examples

### Example 1: Display Current Sensor Readings

```html
<!-- In your template -->
<div id="sensor-display"></div>

<script>
async function displaySensors() {
    const deviceId = 'AQM-12345';
    
    try {
        const reading = await measurementsService.getCurrentReadings(deviceId);
        
        document.getElementById('sensor-display').innerHTML = `
            <div class="sensor-card">
                <div>PM2.5: ${reading.pm25?.toFixed(1) || '—'} μg/m³</div>
                <div>Temp: ${reading.temperature?.toFixed(1) || '—'}°C</div>
                <div>Humidity: ${reading.humidity?.toFixed(0) || '—'}%</div>
                <div>Last: ${new Date(reading.timestamp).toLocaleString()}</div>
            </div>
        `;
    } catch (error) {
        uiManager.showError('Failed to load sensor data');
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', displaySensors);
</script>
```

### Example 2: Create Live Dashboard with Auto-Refresh

```html
<!-- In your template -->
<div id="devices-container" class="row"></div>

<script src="{% static 'js/dashboard-manager.js' %}"></script>
<script>
// Dashboard manager automatically handles loading,
// displaying, and updating device data
const dashboard = new DashboardManager();
</script>
```

### Example 3: Add AI Chat to Your Page

```html
<!-- In your template -->
<div id="ai-chat-container"></div>

<script src="{% static 'js/ai-chat-manager.js' %}"></script>
<script>
// AI Chat manager handles chat UI and interactions
const chat = new AIChatManager();

// Optional: Set device context
chat.setDeviceContext('AQM-12345', 'Office Monitor');
</script>
```

### Example 4: Display Measurement Chart

```html
<!-- In your template -->
<canvas id="myChart"></canvas>

<script>
async function createChart() {
    const deviceId = 'AQM-12345';
    const measurements = await measurementsService.getDeviceMeasurements(deviceId, { limit: 50 });
    const chartData = measurementsService.formatForChart(measurements);
    
    const ctx = document.getElementById('myChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.timestamps.map(t => new Date(t).toLocaleTimeString()),
            datasets: [
                {
                    label: 'PM2.5',
                    data: chartData.metrics.pm25,
                    borderColor: '#dc3545',
                    tension: 0.3,
                },
                {
                    label: 'Temperature',
                    data: chartData.metrics.temperature,
                    borderColor: '#ffc107',
                    tension: 0.3,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' } },
        },
    });
}

document.addEventListener('DOMContentLoaded', createChart);
</script>
```

### Example 5: Handle Loading States

```javascript
// Automatic loading state management
apiClient.onLoadingChange((isLoading) => {
    if (isLoading) {
        console.log('API is loading...');
        // Show spinner, disable buttons, etc.
    } else {
        console.log('API call completed');
        // Hide spinner, enable buttons, etc.
    }
});

// Manual loading state on elements
uiManager.setElementLoading('submitBtn', true, 'Saving...');
// ... do work ...
uiManager.setElementLoading('submitBtn', false);
```

### Example 6: Error Handling

```javascript
// Listen to all API errors
apiClient.onError((error) => {
    console.error('API Error:', error.message);
    
    if (error.status === 401) {
        // Handle unauthorized - redirect to login
        window.location.href = '/qr-login/';
    } else if (error.status === 500) {
        // Handle server error
        uiManager.showError('Server error. Please try again later.');
    }
});

// Catch errors in individual calls
try {
    const devices = await devicesService.listDevices();
} catch (error) {
    const message = uiManager.formatError(error);
    console.error('Error:', message);
}
```

---

## Troubleshooting

### Issue: Scripts not loading

**Check:**
```javascript
// In browser console, you should see these files loaded
// API Configuration
// API Client
// Measurements Service
// Devices Service
// AI Service
// UI Manager
```

**Fix:**
1. Verify `{% load static %}` is in base.html
2. Check static files are collected: `python manage.py collectstatic`
3. Check file paths in base.html match actual files
4. Clear browser cache

### Issue: Backend not responding (404 on all endpoints)

**Check:**
```javascript
// Verify backend URL
console.log(API_CONFIG.BASE_URL);

// Check if backend is running
await apiClient.checkHealth();
```

**Fix:**
1. Update `BASE_URL` in `api-config.js` to correct Railway URL
2. Verify backend endpoints match those defined in `API_CONFIG.ENDPOINTS`
3. Check backend API documentation for correct endpoint paths
4. Ensure CORS is configured on backend

### Issue: 401 Unauthorized errors

**Check:**
```javascript
// Verify authentication
console.log(sessionStorage.getItem('supabase_user_id'));
console.log(localStorage.getItem('auth_token'));
```

**Fix:**
1. Ensure user is logged in
2. Verify session/token is valid
3. Check backend authentication requirements
4. Look at network tab in DevTools to see request headers

### Issue: Slow performance

**Improve:**
1. Reduce update frequency: `dashboard.updateInterval = 60000` (1 minute)
2. Limit data fetched: `limit: 50` instead of `limit: 1000`
3. Disable logging in production: `apiClient.logEnabled = false`
4. Cache data locally: Store recent measurements in sessionStorage
5. Use request debouncing for frequent operations

---

## Testing Checklist

Before deploying to production, verify:

- [ ] Backend is accessible and responds to health check
- [ ] All endpoints in `API_CONFIG.ENDPOINTS` match backend API
- [ ] Can list devices successfully
- [ ] Can fetch latest measurements
- [ ] Can fetch measurement history
- [ ] Charts display correctly with real data
- [ ] AI chat sends and receives messages
- [ ] Error messages display correctly
- [ ] Loading states work correctly
- [ ] Notifications display correctly
- [ ] Auto-update feature works (dashboard refreshes)
- [ ] Works on mobile devices
- [ ] Offline gracefully (shows error messages)

---

## Next Steps

1. **Update Dashboard Template** - Replace Django template variables with API calls
2. **Update Measurement History Page** - Add charts and filtering
3. **Implement Device Management** - Add device CRUD operations
4. **Add Real-time Updates** - Use Supabase Realtime or polling
5. **Optimize Performance** - Add caching and request debouncing
6. **Add Tests** - Write JavaScript tests for API calls
7. **Monitor in Production** - Set up error logging and monitoring

---

## Development Tips

### Enable Detailed Logging

```javascript
// Turn on detailed logging
apiClient.logEnabled = true;

// View all API calls in console
// Shows: [API Client] [GET/POST/etc] URL, responses, errors
```

### Test API Directly

```javascript
// Open browser console on any page and test:

// Test GET
await apiClient.get(getAPIUrl('/measurements/latest'), { device_id: 'AQM-12345' });

// Test POST
await apiClient.post(getAPIUrl('/ai/chat'), { 
    message: 'How is the air quality?',
    context: { device_id: 'AQM-12345' }
});
```

### Monitor Loading State

```javascript
// Listen to loading changes
apiClient.onLoadingChange((isLoading) => {
    console.log('Loading:', isLoading);
});
```

### View Last Error

```javascript
// After an error occurs
console.log('Last error:', apiClient.lastError);
```

---

## Support

For issues or questions:

1. Check [RAILWAY_INTEGRATION_GUIDE.md](RAILWAY_INTEGRATION_GUIDE.md) for detailed documentation
2. Review console logs for errors and stack traces
3. Check network tab in DevTools for API responses
4. Verify backend endpoints in FastAPI documentation
5. Check Django logs for server-side errors

---

**🚀 Ready to integrate? Start with the examples above and test one feature at a time!**

