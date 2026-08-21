# Railway Backend Endpoints Verification Checklist

**Before implementing frontend integration, verify all available endpoints on the Railway FastAPI backend.**

---

## Testing Backend Endpoints

Use one of these methods to test each endpoint:

### Method 1: Browser Console
```javascript
// Test in browser console on any page
await apiClient.get('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/health');
```

### Method 2: cURL
```bash
curl https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/health
```

### Method 3: Postman
1. Create a new request in Postman
2. Set URL and method
3. Send and check response

---

## Health & Status Endpoints

### ✓ Health Check
- **Endpoint:** `GET /health`
- **Expected:** `{"status": "ok"}`
- **Status:** [ ] Verified

```javascript
await apiClient.get('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/health');
```

---

## Measurements Endpoints

### List Measurements
- **Endpoint:** `GET /measurements/list`
- **Query Params:** `device_id`, `limit`, `offset`
- **Expected Response:** Array of measurements
- **Status:** [ ] Verified

```javascript
await apiClient.get('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/measurements/list', {
    device_id: 'AQM-12345',
    limit: 100,
    offset: 0
});
```

### Get Latest Measurement
- **Endpoint:** `GET /measurements/latest`
- **Query Params:** `device_id`
- **Expected Response:** Latest measurement object
- **Status:** [ ] Verified

```javascript
await apiClient.get('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/measurements/latest', {
    device_id: 'AQM-12345'
});
```

### Get Measurement History
- **Endpoint:** `GET /measurements/history`
- **Query Params:** `device_id`, `start_date`, `end_date`, `limit`
- **Expected Response:** History data with timestamps
- **Status:** [ ] Verified

```javascript
await apiClient.get('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/measurements/history', {
    device_id: 'AQM-12345',
    limit: 100
});
```

### Get Device Measurements
- **Endpoint:** `GET /measurements/device`
- **Query Params:** `device_id`, `limit`, `offset`
- **Expected Response:** Array of measurements for device
- **Status:** [ ] Verified

```javascript
await apiClient.get('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/measurements/device', {
    device_id: 'AQM-12345',
    limit: 50
});
```

---

## Devices Endpoints

### List Devices
- **Endpoint:** `GET /devices/list`
- **Query Params:** `limit`, `offset`
- **Expected Response:** Array of devices
- **Status:** [ ] Verified

```javascript
await apiClient.get('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/devices/list', {
    limit: 100
});
```

### Get Device Details
- **Endpoint:** `GET /devices/{id}`
- **Path Params:** `{id}` = device_id
- **Expected Response:** Device object with details
- **Status:** [ ] Verified

```javascript
await apiClient.get('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/devices/AQM-12345');
```

### Create Device
- **Endpoint:** `POST /devices/create`
- **Body:** `{name, location, type}`
- **Expected Response:** Created device object
- **Status:** [ ] Verified

```javascript
await apiClient.post('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/devices/create', {
    name: 'Test Device',
    location: 'Office',
    type: 'sensor'
});
```

### Update Device
- **Endpoint:** `PUT /devices/{id}/update`
- **Path Params:** `{id}` = device_id
- **Body:** Fields to update
- **Expected Response:** Updated device object
- **Status:** [ ] Verified

```javascript
await apiClient.put('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/devices/AQM-12345/update', {
    name: 'Updated Name',
    location: 'New Location'
});
```

---

## AI Endpoints

### AI Chat
- **Endpoint:** `POST /ai/chat`
- **Body:** `{message, context?}`
- **Expected Response:** `{message, response}`
- **Status:** [ ] Verified

```javascript
await apiClient.post('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/ai/chat', {
    message: 'What is the air quality?',
    context: { device_id: 'AQM-12345' }
});
```

### AI Predict
- **Endpoint:** `POST /ai/predict`
- **Body:** `{measurements, timestamp?}`
- **Expected Response:** `{prediction, confidence}`
- **Status:** [ ] Verified

```javascript
await apiClient.post('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/ai/predict', {
    pm25: 25.5,
    temperature: 22.0,
    humidity: 65,
    timestamp: new Date().toISOString()
});
```

### AI Train
- **Endpoint:** `POST /ai/train`
- **Body:** Training parameters
- **Expected Response:** Training status
- **Status:** [ ] Verified

```javascript
await apiClient.post('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/ai/train', {
    epochs: 10,
    batch_size: 32
});
```

### AI Status
- **Endpoint:** `GET /ai/status`
- **Expected Response:** Status information
- **Status:** [ ] Verified

```javascript
await apiClient.get('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/ai/status');
```

---

## User Endpoints

### Get User Profile
- **Endpoint:** `GET /user/profile`
- **Expected Response:** User object
- **Status:** [ ] Verified

```javascript
await apiClient.get('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/user/profile');
```

### Update User Profile
- **Endpoint:** `PUT /user/update`
- **Body:** Fields to update
- **Expected Response:** Updated user object
- **Status:** [ ] Verified

```javascript
await apiClient.put('https://ai-senzor-de-calitate-a-aerului-production.up.railway.app/user/update', {
    name: 'New Name',
    email: 'newemail@example.com'
});
```

---

## Endpoint Response Format

Expected response formats for different endpoints:

### Measurements Response
```json
{
    "id": "measure-123",
    "device_id": "AQM-12345",
    "timestamp": "2024-08-07T10:30:00Z",
    "created_at": "2024-08-07T10:30:00Z",
    "pm25": 25.5,
    "pm10": 45.2,
    "temperature": 22.5,
    "humidity": 65.0,
    "pressure": 1013.25,
    "co2": 420.0,
    "tvoc": 500
}
```

### Device Response
```json
{
    "id": "AQM-12345",
    "device_id": "AQM-12345",
    "name": "Office Monitor",
    "location": "Office",
    "type": "sensor",
    "is_online": true,
    "last_update": "2024-08-07T10:30:00Z",
    "created_at": "2024-07-01T00:00:00Z",
    "updated_at": "2024-08-07T10:30:00Z"
}
```

### AI Response
```json
{
    "message": "Based on the readings, air quality is good...",
    "response": "Based on the readings, air quality is good...",
    "confidence": 0.95,
    "prediction": "Air quality will remain stable",
    "actions": ["monitor"]
}
```

---

## Issues Found

List any issues discovered during testing:

1. **Issue:** 
   - **Endpoint:** 
   - **Error:** 
   - **Solution:** 

---

## Endpoint Mapping

Once verified, update `static/js/api-config.js` with any corrected endpoints:

```javascript
const API_CONFIG = {
    BASE_URL: 'https://ai-senzor-de-calitate-a-aerului-production.up.railway.app',
    ENDPOINTS: {
        measurements: {
            list: '/measurements/list',          // ✓ Verified
            latest: '/measurements/latest',      // ✓ Verified
            history: '/measurements/history',    // ✓ Verified
            byDevice: '/measurements/device',    // ✓ Verified
        },
        devices: {
            list: '/devices/list',              // ✓ Verified
            detail: '/devices/{id}',            // ✓ Verified
            create: '/devices/create',          // ✓ Verified
            update: '/devices/{id}/update',     // ✓ Verified
        },
        ai: {
            predict: '/ai/predict',             // ✓ Verified
            chat: '/ai/chat',                   // ✓ Verified
            train: '/ai/train',                 // ✓ Verified
            status: '/ai/status',               // ✓ Verified
        },
        user: {
            profile: '/user/profile',           // ✓ Verified
            update: '/user/update',             // ✓ Verified
        },
        health: '/health',                      // ✓ Verified
    }
};
```

---

## Test Script

Run this script in browser console to test all endpoints at once:

```javascript
async function testAllEndpoints() {
    const baseUrl = 'https://ai-senzor-de-calitate-a-aerului-production.up.railway.app';
    const results = {};
    
    // Test health
    try {
        const health = await fetch(baseUrl + '/health');
        results.health = { status: health.status, ok: health.ok };
    } catch (e) {
        results.health = { error: e.message };
    }
    
    // Test measurements
    try {
        const measurements = await fetch(baseUrl + '/measurements/latest?device_id=AQM-12345');
        results.measurements = { status: measurements.status, ok: measurements.ok };
    } catch (e) {
        results.measurements = { error: e.message };
    }
    
    // Test devices
    try {
        const devices = await fetch(baseUrl + '/devices/list');
        results.devices = { status: devices.status, ok: devices.ok };
    } catch (e) {
        results.devices = { error: e.message };
    }
    
    // Test AI
    try {
        const ai = await fetch(baseUrl + '/ai/status');
        results.ai = { status: ai.status, ok: ai.ok };
    } catch (e) {
        results.ai = { error: e.message };
    }
    
    console.table(results);
    return results;
}

// Run it
testAllEndpoints();
```

---

## Sign-off

- [ ] All endpoints verified and working
- [ ] Response formats match expectations
- [ ] Error handling works correctly
- [ ] CORS configured on backend
- [ ] Authentication/authorization working
- [ ] Ready for frontend integration

**Verified by:** ________________  
**Date:** ________________  
**Notes:** ________________________________________

