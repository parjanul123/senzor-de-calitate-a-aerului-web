# 🤖 AI Interface - Quick Start Guide

**Status:** ✅ Ready to Use  
**URL:** `http://localhost:8000/ai/interface/`  
**Features:** Chat, Prediction, Anomaly Detection, Training

---

## 2-Minute Quick Start

### Step 1: Open the AI Interface
```
http://localhost:8000/ai/interface/
```

### Step 2: Select Your Device
- Click the device dropdown
- Choose a device you want to work with

### Step 3: Try Each Feature

**Chat (💬)**
```
Type: "What's the air quality?"
Press: Enter or click Send
```

**Prediction (🔮)**
```
Click: "Run Prediction" button
See: Air quality forecast and recommendations
```

**Anomaly Detection (⚠️)**
```
Click: "Detect Anomalies" button
See: List of unusual sensor readings (if any)
```

**Training (🧠)**
```
Enter: 30 days of data
Click: "Start Training" button
Watch: Progress bar and accuracy results
```

---

## Features Overview

### 💬 Chat - Ask the AI

**What it does:**
- Answer questions about air quality
- Provide personalized recommendations
- Suggest device actions (calibrate, check, etc.)

**Example questions:**
- "What's happening with my air quality?"
- "Should I turn on the air purifier?"
- "What do these readings mean?"
- "Any recommendations?"

**How it works:**
1. Understands context (which device)
2. Analyzes current sensor data
3. Provides relevant answers
4. Can suggest actions

---

### 🔮 Prediction - Forecast Air Quality

**What it does:**
- Predicts next 24 hours of air quality
- Calculates confidence score
- Gives recommendations

**Output:**
```
Air Quality Index: 78 (Moderate)
Forecast: Quality will improve by evening
Confidence: 92%
Recommendations: Good time for outdoor exercise in morning
```

**How it works:**
1. Gets latest measurements
2. Analyzes historical patterns
3. Uses ML model to predict
4. Shows results with confidence score

---

### ⚠️ Anomaly Detection - Find Problems

**What it does:**
- Detects unusual sensor readings
- Identifies potential sensor failures
- Flags unexpected changes

**Example anomalies:**
```
Anomaly 1: PM2.5 spike to 450 (expected 10-100)
Anomaly 2: Temperature drop 15°C in 1 minute
Anomaly 3: Humidity constantly 0% (sensor issue?)
```

**How it works:**
1. Analyzes last 100 measurements
2. Compares to expected ranges
3. Flags unusual patterns
4. Rates severity (low/medium/high)

---

### 🧠 Training - Improve AI Models

**What it does:**
- Trains model on your data
- Improves prediction accuracy
- Customizes for your location

**Training options:**
- **7 days:** Quick training, less accurate
- **30 days:** Balanced (recommended)
- **90+ days:** Very accurate, takes longer

**Results:**
```
Model Accuracy: 92%
Data points used: 720
Training time: 45 seconds
Performance: MAE=5.2, RMSE=7.8
```

---

## Code Examples

### Using AI Services Directly

```javascript
// Chat
const response = await aiService.chat("Hello AI");
console.log(response.message);

// Prediction
const prediction = await aiService.predict({
    pm25: 35.5,
    temperature: 22.5,
    humidity: 65
});
console.log(prediction.quality_index);

// Anomaly Detection
const anomalies = await aiService.detectAnomalies(measurements);
console.log(anomalies.anomalies.length);

// Training
const result = await aiService.train({
    device_id: "AQM-12345",
    days: 30
});
console.log(result.accuracy);
```

### Embedding in Your Page

```html
<!-- Add to any page -->
<iframe src="/ai/interface/" style="width: 100%; height: 600px;"></iframe>

<!-- Or link to interface -->
<a href="{% url 'ai:interface' %}" class="btn btn-primary">
    Open AI Interface
</a>
```

---

## What Each Tab Does

### 📱 Interface Layout

```
┌─────────────────────────────────────┐
│  🤖 AI Interface                    │
├─────────────────────────────────────┤
│ Device: [AQM-12345 ▼]               │
├─────────────────────────────────────┤
│ [Chat] [Prediction] [Anomaly] [Train]
├─────────────────────────────────────┤
│                                     │
│  [Tab Content]                      │
│  - Chat messages                    │
│  - Prediction results               │
│  - Anomaly list                     │
│  - Training progress                │
│                                     │
└─────────────────────────────────────┘
```

---

## API Endpoints

All features use these backend endpoints (on Railway):

| Feature | Endpoint | Method |
|---------|----------|--------|
| Chat | `/ai/chat` | POST |
| Prediction | `/ai/predict` | POST |
| Anomaly | `/ai/anomaly` | POST |
| Training | `/ai/train` | POST |

**Base URL:** `https://ai-senzor-de-calitate-a-aerului-production.up.railway.app`

---

## Common Tasks

### Task: Ask AI for Device Status
```javascript
// In Chat tab, type:
"What's the status of my device?"

// AI will:
// - Check device health
// - Review recent data
// - Suggest maintenance if needed
```

### Task: Get Air Quality Forecast
```javascript
// In Prediction tab, click:
"Run Prediction"

// You get:
// - 24-hour forecast
// - Quality index
// - Confidence score
// - Recommendations
```

### Task: Check for Sensor Issues
```javascript
// In Anomaly tab, click:
"Detect Anomalies"

// You get:
// - List of anomalies
// - Severity level
// - Expected vs actual values
// - Which metric is affected
```

### Task: Improve Model Accuracy
```javascript
// In Training tab:
// 1. Set period: 30 days
// 2. Check: Auto-retrain weekly
// 3. Click: Start Training
// 4. Wait for progress bar

// Results:
// - Model accuracy %
// - Performance metrics
// - Training time
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Send chat message |
| Shift+Enter | New line in chat |
| Tab | Switch focus to next element |
| Esc | Close any modal/popup |

---

## Tips & Tricks

### For Better Predictions
1. **Train regularly** - Monthly training improves accuracy
2. **Use consistent data** - Ensure device always has measurements
3. **Provide context** - Tell AI about your location/environment

### For Anomaly Detection
1. **Run weekly** - Check for issues before they become problems
2. **Check severity** - Focus on "high" severity anomalies first
3. **Compare devices** - Compare readings across multiple devices

### For Training
1. **Start with 30 days** - Good balance of data and speed
2. **Train during off-peak** - Training takes computational resources
3. **Monitor accuracy** - Track if accuracy improves over time

### For Chat
1. **Be specific** - "PM2.5 is high" vs "What's wrong?"
2. **Use device context** - AI knows which device you selected
3. **Ask for recommendations** - AI suggests actions automatically

---

## Troubleshooting

### Chat not working
```
✓ Check: Device is selected
✓ Check: Internet connection
✓ Check: Browser console (F12) for errors
✓ Try: Refresh page
```

### Prediction shows nothing
```
✓ Check: Device has recent measurements
✓ Check: Device ID is correct
✓ Try: Run prediction again
✓ Check: Backend is responding
```

### Anomaly detection is empty
```
This is GOOD! - Means no anomalies found
- Sensors are working normally
- Try with different device
- Check if data is recent
```

### Training is slow
```
✓ This is normal - depends on data volume
✓ Use fewer days (30 instead of 90)
✓ Check backend CPU usage
✓ Training happens in background
```

---

## Browser Requirements

| Feature | Requirement |
|---------|-------------|
| Chat | Modern browser, JavaScript enabled |
| Prediction | Fetch API, Promise support |
| Anomaly | Modern browser, 10MB RAM |
| Training | Stable connection, don't close tab |

**Supported Browsers:**
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Performance Notes

| Task | Duration |
|------|----------|
| Send chat message | 1-3 seconds |
| Run prediction | 3-5 seconds |
| Detect anomalies | 5-10 seconds |
| Train model | 30-120 seconds |

*Times vary based on:
- Internet speed
- Backend load
- Data volume
- Device performance*

---

## Files Reference

| File | Purpose |
|------|---------|
| `templates/ai/interface.html` | Main UI page |
| `static/js/ai-interface-manager.js` | JavaScript logic |
| `apps/ai/views.py` | Django view |
| `apps/ai/urls.py` | URL routing |

---

## Next Steps

1. **Try all features** - Spend 5 minutes exploring
2. **Read full guide** - `AI_INTERFACE_GUIDE.md`
3. **Test with real data** - Use your actual device
4. **Enable auto-training** - Check the weekly option
5. **Set up alerts** - Configure anomaly notifications

---

## Support

### Quick Help
- **Chat not working?** Check internet connection
- **No predictions?** Ensure device has measurements
- **Confused?** Click the ℹ️ icons for help text

### Detailed Help
- Read: `AI_INTERFACE_GUIDE.md` (comprehensive)
- Visit: `/test-api/` (system test page)
- Check: Browser console (F12) for errors

### Report Issues
Check browser console (F12) for error messages:
```javascript
// Look for red error messages
// Copy and include in bug report
```

---

## Success Checklist

✅ AI Interface page loads  
✅ Can select device  
✅ Chat sends message  
✅ Prediction shows results  
✅ Anomaly detection runs  
✅ Training shows progress  
✅ No console errors  
✅ Mobile responsive  

---

**Ready to use!** 🚀

Open now: `http://localhost:8000/ai/interface/`

