/**
 * AI Interface Manager
 * Comprehensive AI features: Chat, Prediction, Training, Anomaly Detection
 * All integrated with Railway FastAPI backend
 */

class AIInterfaceManager {
    constructor() {
        this.currentTab = 'chat';
        this.chatHistory = [];
        this.currentDevice = null;
        this.isProcessing = false;
        this.predictionResults = null;
        this.anomalyResults = null;
        this.trainingStatus = 'idle';
        
        this.init();
    }
    
    /**
     * Initialize the AI interface
     */
    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupUI());
        } else {
            this.setupUI();
        }
    }
    
    /**
     * Setup UI and event listeners
     */
    setupUI() {
        this.setupTabs();
        this.setupChatUI();
        this.setupPredictionUI();
        this.setupAnomalyUI();
        this.setupTrainingUI();
        this.setupDeviceSelector();
    }
    
    /**
     * Setup tab switching
     */
    setupTabs() {
        const tabButtons = document.querySelectorAll('[data-tab]');
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tabName = e.currentTarget.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    async postAI(endpoint, payload = {}) {
        const response = await fetch(API_CONFIG.BASE_URL + endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(this.formatApiError(error.detail));
        }

        return response.json();
    }

    formatApiError(detail) {
        if (typeof detail === 'string' && detail.trim()) {
            return detail;
        }

        if (Array.isArray(detail)) {
            const messages = detail.map((item) => {
                if (typeof item === 'string') return item;
                if (!item || typeof item !== 'object') return '';

                const field = Array.isArray(item.loc) ? item.loc.filter(part => part !== 'body').join('.') : '';
                return field ? `${field}: ${item.msg || 'valoare invalidă'}` : (item.msg || 'valoare invalidă');
            }).filter(Boolean);
            if (messages.length > 0) return messages.join('; ');
        }

        if (detail && typeof detail === 'object') {
            return detail.message || detail.msg || JSON.stringify(detail);
        }

        return 'Solicitarea AI nu a putut fi procesată.';
    }

    async getLatestMeasurement() {
        const response = await fetch(
            `/measurements/device/${encodeURIComponent(this.currentDevice)}/latest/`,
            { credentials: 'same-origin' }
        );

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || 'Ultima masuratoare nu a putut fi incarcata.');
        }

        return response.json();
    }

    normalizePredictionValue(value, minimum, maximum, fallback) {
        const numericValue = Number(value);
        if (!Number.isFinite(numericValue)) return fallback;
        return Math.min(maximum, Math.max(minimum, numericValue));
    }

    getPredictionPayload(measurement, algorithm) {
        return {
            device_id: this.currentDevice,
            temperature: this.normalizePredictionValue(measurement.temperatura, -50, 60, 20),
            humidity: this.normalizePredictionValue(measurement.umiditate, 0, 100, 50),
            pm25: this.normalizePredictionValue(measurement.pm25, 0, 500, 0),
            pm10: this.normalizePredictionValue(measurement.pm10, 0, 500, 0),
            co2: this.normalizePredictionValue(measurement.co2, 400, 5000, 400),
            algorithm
        };
    }

    async getProfileEvaluation(values, overallQuality) {
        const response = await fetch(`/devices/${encodeURIComponent(this.currentDevice)}/transport-profile/data/`, {
            credentials: 'same-origin',
        });
        if (!response.ok) throw new Error('Profilul activ nu a putut fi incarcat.');

        const profile = await response.json();
        const predictionKeys = {
            temperatura: 'temperature', umiditate: 'humidity', co2: 'co2',
            pm25: 'pm25', pm10: 'pm10', voc: 'voc',
        };
        const normalizedQuality = String(overallQuality || '').toLowerCase();
        if (profile.profile_name === 'Standard' && ['good', 'moderate', 'poor'].includes(normalizedQuality)) {
            const checks = Object.entries(predictionKeys).map(([parameter, key]) => ({
                parameter,
                value: values[key],
                label: normalizedQuality,
                in_range: normalizedQuality === 'good',
            }));
            return { profile_name: 'Standard', checks, in_range: normalizedQuality === 'good' };
        }
        const checks = Object.entries(profile.thresholds || {}).map(([parameter, threshold]) => {
            const value = values[predictionKeys[parameter]];
            if (!Number.isFinite(Number(value))) return null;
            const minimum = Number(threshold.minimum);
            const maximum = Number(threshold.maximum);
            const numericValue = Number(value);
            const label = numericValue < minimum ? 'sub_minim' : numericValue > maximum ? 'peste_maxim' : 'in_interval';
            return { parameter, value: numericValue, minimum, maximum, label, in_range: label === 'in_interval' };
        }).filter(Boolean);
        return {
            profile_name: profile.profile_name || 'Standard',
            checks,
            in_range: checks.length ? checks.every((check) => check.in_range) : null,
        };
    }
    
    /**
     * Switch between tabs
     */
    switchTab(tabName) {
        this.currentTab = tabName;
        
        // Update button styles
        document.querySelectorAll('[data-tab]').forEach(btn => {
            btn.classList.remove('active', 'btn-primary');
            btn.classList.add('btn-outline-primary');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active', 'btn-primary');
        document.querySelector(`[data-tab="${tabName}"]`).classList.remove('btn-outline-primary');
        
        // Update tab content
        document.querySelectorAll('[data-tab-content]').forEach(content => {
            content.style.display = 'none';
        });
        const tabContent = document.querySelector(`[data-tab-content="${tabName}"]`);
        if (tabContent) {
            tabContent.style.display = 'block';
        }
    }
    
    // ===== CHATBOT =====
    
    /**
     * Setup chatbot UI
     */
    setupChatUI() {
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('chat-send-button');
        const clearButton = document.getElementById('chat-clear-button');

        const chatDisplay = document.getElementById('chat-display');
        if (chatDisplay && chatDisplay.children.length === 0) {
            this.addChatMessage({
                role: 'assistant',
                content: 'Bună! Sunt agentul Aerosenzor. Pentru a continua conversația, selectează un dispozitiv din listă și apoi pot să-ți răspund despre calitatea aerului, senzorii și recomandări.',
                timestamp: new Date()
            });
        }

        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendChatMessage());
        }

        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    if (!this.currentDevice) {
                        e.preventDefault();
                        return;
                    }
                    e.preventDefault();
                    this.sendChatMessage();
                }
            });
        }
        
        if (clearButton) {
            clearButton.addEventListener('click', () => this.clearChatHistory());
        }

        this.updateChatInputState();
    }
    
    /**
     * Send chat message to AI
     */
    async sendChatMessage() {
        const chatInput = document.getElementById('chat-input');
        const message = chatInput.value.trim();

        if (!message) return;

        if (!this.currentDevice) {
            const deviceNames = this.getAvailableDeviceNames();
            const listText = deviceNames.length > 0
                ? `Dispozitive disponibile: ${deviceNames.join(', ')}.`
                : 'Momentan nu există dispozitive disponibile.';

            this.addChatMessage({
                role: 'assistant',
                content: `Bună! Sunt agentul Aerosenzor. Pentru a continua discuția, selectează un dispozitiv din listă. ${listText}`,
                timestamp: new Date()
            });
            return;
        }
        
        this.addChatMessage({
            role: 'user',
            content: message,
            timestamp: new Date()
        });
        
        chatInput.value = '';
        this.showChatTypingIndicator();
        
        try {
            const response = await this.postAI(API_CONFIG.ENDPOINTS.ai.chat, {
                message,
                device_id: this.currentDevice,
                history: this.chatHistory.slice(-12).map(({ role, content }) => ({ role, content }))
            });
            
            this.removeChatTypingIndicator();
            
            this.addChatMessage({
                role: 'assistant',
                content: response.reply || response.message || 'Backendul AI nu a returnat un raspuns text.',
                timestamp: new Date()
            });
            
            // Handle any actions from AI response
            if (response.actions) {
                await this.handleAIActions(response.actions);
            }
        } catch (error) {
            this.removeChatTypingIndicator();
            uiManager.showError('Failed to get AI response: ' + error.message);
            if (typeof addTestResult === 'function') addTestResult('Chat error: ' + error.message, 'error');
        }
    }
    
    /**
     * Add message to chat display
     */
    addChatMessage(message) {
        const chatDisplay = document.getElementById('chat-display');
        if (!chatDisplay) return;
        
        this.chatHistory.push(message);
        
        const messageEl = document.createElement('div');
        messageEl.className = `chat-message chat-${message.role}`;
        messageEl.innerHTML = `
            <div class="message-content">
                <p>${this.escapeHtml(message.content)}</p>
                <small class="message-time">${message.timestamp.toLocaleTimeString()}</small>
            </div>
        `;
        
        chatDisplay.appendChild(messageEl);
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }
    
    /**
     * Show typing indicator
     */
    showChatTypingIndicator() {
        const chatDisplay = document.getElementById('chat-display');
        if (!chatDisplay) return;
        
        const typingEl = document.createElement('div');
        typingEl.id = 'typing-indicator';
        typingEl.className = 'chat-message chat-assistant';
        typingEl.innerHTML = `
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        
        chatDisplay.appendChild(typingEl);
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }
    
    /**
     * Remove typing indicator
     */
    removeChatTypingIndicator() {
        const typingEl = document.getElementById('typing-indicator');
        if (typingEl) typingEl.remove();
    }
    
    /**
     * Clear chat history
     */
    clearChatHistory() {
        this.chatHistory = [];
        const chatDisplay = document.getElementById('chat-display');
        if (chatDisplay) chatDisplay.innerHTML = '';
        uiManager.showSuccess('Chat history cleared');
    }
    
    /**
     * Handle AI actions (calibrate, check device, etc.)
     */
    async handleAIActions(actions) {
        for (const action of actions) {
            switch (action.type) {
                case 'check_device':
                    this.addChatMessage({
                        role: 'system',
                        content: `🔍 Checking device: ${action.deviceId}`,
                        timestamp: new Date()
                    });
                    break;
                case 'calibrate':
                    this.addChatMessage({
                        role: 'system',
                        content: `⚙️ Calibrating device...`,
                        timestamp: new Date()
                    });
                    break;
                case 'replace_filter':
                    this.addChatMessage({
                        role: 'system',
                        content: `🔄 Filter replacement recommended`,
                        timestamp: new Date()
                    });
                    break;
            }
        }
    }
    
    // ===== PREDICTION =====
    
    /**
     * Setup prediction UI
     */
    setupPredictionUI() {
        const predictButton = document.getElementById('predict-button');
        if (predictButton) {
            predictButton.addEventListener('click', () => this.runPrediction());
        }
    }
    
    /**
     * Run AI prediction
     */
    async runPrediction() {
        if (!this.currentDevice) {
            uiManager.showWarning('Please select a device first');
            return;
        }
        
        this.isProcessing = true;
        uiManager.showLoading('Running prediction...');
        
        try {
            const measurement = await this.getLatestMeasurement();
            const algorithm = document.getElementById('prediction-algorithm')?.value || 'random_forest';
            const predictionPayload = this.getPredictionPayload(measurement, algorithm);
            const prediction = await this.postAI(
                `${API_CONFIG.ENDPOINTS.ai.predictCustom}?algorithm=${encodeURIComponent(algorithm)}`,
                predictionPayload
            );
            prediction.algorithm = algorithm;
            prediction.input_values = prediction.input_values || predictionPayload;
            try {
                prediction.profile_evaluation = await this.getProfileEvaluation(prediction.input_values, prediction.prediction);
            } catch (error) {
                prediction.profileEvaluationError = error.message;
            }

            const forecastHorizon = Number(document.getElementById('forecast-horizon')?.value || 24);
            const forecastHorizons = Array.from(document.querySelectorAll('#forecast-horizon option'))
                .map((option) => Number(option.value))
                .filter((horizon) => horizon > 0 && horizon <= forecastHorizon)
                .join(',');
            try {
                const forecast = await this.postAI(
                    `${API_CONFIG.ENDPOINTS.ai.predict}?device_id=${encodeURIComponent(this.currentDevice)}&algorithm=${encodeURIComponent(algorithm)}&include_forecast=true&forecast_horizons=${encodeURIComponent(forecastHorizons)}`,
                    predictionPayload
                );
                prediction.forecast = forecast.forecast;
                prediction.forecast_device_id = this.currentDevice;
            } catch (error) {
                prediction.forecastError = error.message;
            }
            
            uiManager.hideLoading();
            
            this.predictionResults = prediction;
            this.displayPredictionResults(prediction);
            uiManager.showSuccess('Prediction completed successfully');
            
        } catch (error) {
            uiManager.hideLoading();
            this.displayActionError('prediction-results', 'Predicția sau prognoza nu poate rula', error.message);
            uiManager.showError('Prediction failed: ' + error.message);
            if (typeof addTestResult === 'function') addTestResult('Prediction error: ' + error.message, 'error');
        } finally {
            this.isProcessing = false;
        }
    }
    
    /**
     * Display prediction results
     */
    displayPredictionResults(prediction) {
        const resultsDiv = document.getElementById('prediction-results');
        if (!resultsDiv) return;
        
        let html = '';

        if (prediction.algorithm) {
            html += `
                <div class="prediction-metric">
                    <h6><i class="bi bi-cpu"></i> Algoritm folosit</h6>
                    <p class="mb-0">${this.escapeHtml(prediction.algorithm)}</p>
                </div>
            `;
        }

        if (prediction.prediction || prediction.input_values) {
            const inputValues = prediction.input_values || {};
            const profileChecks = prediction.profile_evaluation?.checks || [];
            const profileParameterMap = { temperature: 'temperatura', humidity: 'umiditate', co2: 'co2', pm25: 'pm25', pm10: 'pm10', voc: 'voc' };
            const formatValue = (metric, suffix = '') => typeof inputValues[metric] === 'number'
                ? `${inputValues[metric].toFixed(1)}${suffix}`
                : '—';
            const formatProfileLabel = (metric) => {
                const check = profileChecks.find((item) => item.parameter === profileParameterMap[metric]);
                if (!check) return '<br><span class="badge bg-secondary">Not configured</span>';
                const labels = {
                    in_interval: ['success', 'Good'],
                    sub_minim: ['warning', 'Moderate'],
                    peste_maxim: ['danger', 'Poor'],
                    good: ['success', 'Good'],
                    moderate: ['warning', 'Moderate'],
                    poor: ['danger', 'Poor'],
                };
                const [color, text] = labels[check.label] || ['secondary', 'Fara prag'];
                return `<br><span class="badge bg-${color}">${text}</span>`;
            };
            const confidence = typeof prediction.confidence === 'number'
                ? `${(prediction.confidence * 100).toFixed(1)}%`
                : '—';
            html += `
                <div class="prediction-metric">
                    <strong>Predicție curentă:</strong>
                    <div class="table-responsive mt-2">
                        <table class="table table-sm table-striped mb-0">
                            <thead>
                                <tr>
                                    <th>Calitate</th>
                                    <th>Încredere</th>
                                    <th>PM2.5</th>
                                    <th>PM10</th>
                                    <th>CO2</th>
                                    <th>Temperatură</th>
                                    <th>Umiditate</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>${this.escapeHtml(String(prediction.prediction || '—'))}</strong></td>
                                    <td>${confidence}</td>
                                    <td>${formatValue('pm25', ' µg/m³')}${formatProfileLabel('pm25')}</td>
                                    <td>${formatValue('pm10', ' µg/m³')}${formatProfileLabel('pm10')}</td>
                                    <td>${formatValue('co2', ' ppm')}${formatProfileLabel('co2')}</td>
                                    <td>${formatValue('temperature', ' °C')}${formatProfileLabel('temperature')}</td>
                                    <td>${formatValue('humidity', '%')}${formatProfileLabel('humidity')}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        if (prediction.profile_evaluation) {
            const evaluation = prediction.profile_evaluation;
            const statusClass = evaluation.in_range === true ? 'success' : evaluation.in_range === false ? 'danger' : 'secondary';
            const statusText = evaluation.in_range === true ? 'Toate valorile sunt in pragurile profilului.' : evaluation.in_range === false ? 'Cel putin o valoare depaseste pragul profilului.' : 'Nu exista valori predictate pentru pragurile configurate.';
            const checks = (evaluation.checks || []).map((check) => `<li>${this.escapeHtml(check.parameter)}: ${this.escapeHtml(String(check.value))} (${this.escapeHtml(String(check.minimum))} - ${this.escapeHtml(String(check.maximum))}) ${check.in_range ? 'in interval' : 'in afara intervalului'}</li>`).join('');
            html += `
                <div class="prediction-metric">
                    <strong>Profil activ: ${this.escapeHtml(evaluation.profile_name || 'Standard')}</strong>
                    <span class="badge bg-${statusClass} ms-2">${this.escapeHtml(statusText)}</span>
                    ${checks ? `<ul class="mb-0 mt-2">${checks}</ul>` : ''}
                </div>
            `;
        }
        
        if (prediction.quality_index !== undefined) {
            html += `
                <div class="prediction-metric">
                    <strong>Air Quality Index:</strong>
                    <span class="badge bg-${this.getQualityColor(prediction.quality_index)}">
                        ${prediction.quality_index.toFixed(2)}
                    </span>
                </div>
            `;
        }
        
        if (Array.isArray(prediction.forecast) && prediction.forecast.length > 0) {
            html += `
                <div class="prediction-metric">
                    <strong>Prognoză viitoare pentru dispozitivul ${this.escapeHtml(String(prediction.forecast_device_id || this.currentDevice))}:</strong>
                    <div class="table-responsive mt-2">
                        <table class="table table-sm table-striped mb-0">
                            <thead>
                                <tr>
                                    <th>Peste</th>
                                    <th>Calitate</th>
                                    <th>Încredere</th>
                                    <th>PM2.5</th>
                                    <th>PM10</th>
                                    <th>CO2</th>
                                    <th>Temperatură</th>
                                    <th>Umiditate</th>
                                </tr>
                            </thead>
                            <tbody>
            `;
            prediction.forecast.forEach((item) => {
                const horizon = item.horizon_hours || item.hours_ahead || item.horizon || item.hour || 'următoarea perioadă';
                const value = item.prediction || item.quality || item.status || JSON.stringify(item);
                const inputValues = item.input_values || {};
                const confidence = typeof item.confidence === 'number' ? `${(item.confidence * 100).toFixed(1)}%` : '—';
                const formatValue = (metric, suffix = '') => typeof inputValues[metric] === 'number'
                    ? `${inputValues[metric].toFixed(1)}${suffix}`
                    : '—';
                html += `
                    <tr>
                        <td>${this.escapeHtml(String(horizon))} ore</td>
                        <td><strong>${this.escapeHtml(String(value))}</strong></td>
                        <td>${confidence}</td>
                        <td>${formatValue('pm25', ' µg/m³')}</td>
                        <td>${formatValue('pm10', ' µg/m³')}</td>
                        <td>${formatValue('co2', ' ppm')}</td>
                        <td>${formatValue('temperature', ' °C')}</td>
                        <td>${formatValue('humidity', '%')}</td>
                    </tr>
                `;
            });
            html += '</tbody></table></div></div>';
        } else if (prediction.forecastError) {
            html += `<div class="alert alert-warning mt-3 mb-0"><strong>Prognoza nu este disponibilă:</strong> ${this.escapeHtml(prediction.forecastError)}</div>`;
        }
        
        if (prediction.recommendations) {
            html += `
                <div class="prediction-metric">
                    <strong>Recommendations:</strong>
                    <ul class="mb-0">
                        ${prediction.recommendations.map(rec => 
                            `<li>${this.escapeHtml(rec)}</li>`
                        ).join('')}
                    </ul>
                </div>
            `;
        }
        
        if (prediction.confidence) {
            html += `
                <div class="prediction-metric">
                    <strong>Confidence:</strong>
                    <div class="progress">
                        <div class="progress-bar" style="width: ${prediction.confidence * 100}%">
                            ${(prediction.confidence * 100).toFixed(1)}%
                        </div>
                    </div>
                </div>
            `;
        }

        if (prediction.feature_assessment) {
            const labels = {
                temperature: 'Temperatură',
                humidity: 'Umiditate',
                pm25: 'PM2.5',
                pm10: 'PM10',
                co2: 'CO2'
            };
            const assessmentRows = Object.entries(prediction.feature_assessment).map(([metric, assessment]) => {
                const value = typeof assessment.value === 'number' ? assessment.value.toFixed(1) : '—';
                const unit = assessment.unit || '';
                const classification = assessment.condition || assessment.status || 'neevaluat';
                const details = assessment.message || assessment.reason || '—';
                const color = {
                    good: 'success',
                    moderate: 'warning',
                    poor: 'danger',
                    bad: 'danger'
                }[assessment.status] || 'secondary';
                return `
                    <tr>
                        <th scope="row">${this.escapeHtml(labels[metric] || metric)}</th>
                        <td>${this.escapeHtml(String(value))} ${this.escapeHtml(unit)}</td>
                        <td><span class="badge bg-${color}">${this.escapeHtml(classification)}</span></td>
                        <td>${this.escapeHtml(details)}</td>
                    </tr>
                `;
            }).join('');

            html += `
                <div class="prediction-metric">
                    <strong>Clasificarea indicatorilor:</strong>
                    <div class="table-responsive mt-2">
                        <table class="table table-sm table-striped align-middle mb-0">
                            <thead>
                                <tr>
                                    <th>Indicator</th>
                                    <th>Valoare</th>
                                    <th>Clasificare</th>
                                    <th>Detalii</th>
                                </tr>
                            </thead>
                            <tbody>${assessmentRows}</tbody>
                        </table>
                    </div>
                </div>
            `;
        }
        
        resultsDiv.innerHTML = html;
    }
    
    /**
     * Get color for quality index
     */
    getQualityColor(index) {
        if (index < 50) return 'success';      // Good
        if (index < 100) return 'info';        // Moderate
        if (index < 150) return 'warning';     // Unhealthy for sensitive
        if (index < 200) return 'danger';      // Unhealthy
        return 'dark';                         // Very Unhealthy
    }
    
    // ===== ANOMALY DETECTION =====
    
    /**
     * Setup anomaly detection UI
     */
    setupAnomalyUI() {
        const detectButton = document.getElementById('anomaly-button');
        if (detectButton) {
            detectButton.addEventListener('click', () => this.detectAnomalies());
        }
    }
    
    /**
     * Detect anomalies in sensor data
     */
    async detectAnomalies() {
        if (!this.currentDevice) {
            uiManager.showWarning('Please select a device first');
            return;
        }
        
        this.isProcessing = true;
        uiManager.showLoading('Detecting anomalies...');
        
        try {
            const anomalies = await this.postAI(API_CONFIG.ENDPOINTS.ai.anomaly, {
                device_id: this.currentDevice
            });
            
            uiManager.hideLoading();
            
            this.anomalyResults = anomalies;
            this.displayAnomalyResults(anomalies);
            uiManager.showSuccess('Anomaly detection completed');
            
        } catch (error) {
            uiManager.hideLoading();
            this.displayActionError('anomaly-results', 'Detectarea anomaliilor nu poate rula', error.message);
            uiManager.showError('Anomaly detection failed: ' + error.message);
            if (typeof addTestResult === 'function') addTestResult('Anomaly detection error: ' + error.message, 'error');
        } finally {
            this.isProcessing = false;
        }
    }
    
    /**
     * Display anomaly detection results
     */
    displayAnomalyResults(results) {
        const resultsDiv = document.getElementById('anomaly-results');
        if (!resultsDiv) return;
        
        let html = '';

        if (results.result && typeof results.result === 'object') {
            const result = results.result;
            const isAnomaly = Boolean(result.is_anomaly);
            html += `
                <div class="alert alert-${isAnomaly ? 'warning' : 'success'}">
                    <strong>${isAnomaly ? 'A fost detectată o anomalie.' : 'Nu a fost detectată nicio anomalie.'}</strong>
                    ${typeof result.score === 'number' ? ` Scor: ${result.score.toFixed(4)}.` : ''}
                </div>
            `;

            if (Array.isArray(result.feature_analysis) && result.feature_analysis.length > 0) {
                const rows = result.feature_analysis.map((feature) => {
                    const value = typeof feature.value === 'number' ? feature.value.toFixed(2) : '—';
                    const status = feature.is_outlier ? 'În afara intervalului' : 'Normal';
                    const statusClass = feature.is_outlier ? 'danger' : 'success';
                    return `
                        <tr>
                            <th scope="row">${this.escapeHtml(feature.feature || '—')}</th>
                            <td>${value}</td>
                            <td><span class="badge bg-${statusClass}">${status}</span></td>
                            <td>${this.escapeHtml(feature.sensor_warning || '—')}</td>
                        </tr>
                    `;
                }).join('');
                html += `
                    <div class="table-responsive">
                        <table class="table table-sm table-striped align-middle mb-0">
                            <thead><tr><th>Indicator</th><th>Valoare</th><th>Verificare</th><th>Avertizare senzor</th></tr></thead>
                            <tbody>${rows}</tbody>
                        </table>
                    </div>
                `;
            }

            if (Array.isArray(result.sensor_health_warnings) && result.sensor_health_warnings.length > 0) {
                html += `<div class="alert alert-warning mt-3 mb-0"><strong>Avertizări senzori:</strong><ul class="mb-0 mt-2">${result.sensor_health_warnings.map((warning) => `<li>${this.escapeHtml(warning)}</li>`).join('')}</ul></div>`;
            }
        } else if (results.anomalies && results.anomalies.length > 0) {
            html += `
                <div class="alert alert-warning">
                    <strong>⚠️ Anomalies Detected: ${results.anomalies.length}</strong>
                </div>
                <div class="anomaly-list">
            `;
            
            results.anomalies.forEach((anomaly, index) => {
                html += `
                    <div class="anomaly-item alert alert-light border-left border-warning">
                        <strong>Anomaly ${index + 1}</strong>
                        <p class="mb-1"><small class="text-muted">${new Date(anomaly.timestamp).toLocaleString()}</small></p>
                        <p class="mb-1"><strong>Type:</strong> ${this.escapeHtml(anomaly.type)}</p>
                        <p class="mb-1"><strong>Metric:</strong> ${this.escapeHtml(anomaly.metric)} = ${anomaly.value.toFixed(2)}</p>
                        <p class="mb-0"><strong>Expected Range:</strong> ${anomaly.expected_min.toFixed(2)} - ${anomaly.expected_max.toFixed(2)}</p>
                        <span class="badge bg-warning mt-2">Severity: ${anomaly.severity || 'medium'}</span>
                    </div>
                `;
            });
            
            html += '</div>';
        } else {
            html = '<div class="alert alert-success">✓ No anomalies detected. All sensors operating normally.</div>';
        }
        
        if (results.summary) {
            html += `
                <div class="alert alert-info mt-3">
                    <strong>Summary:</strong> ${this.escapeHtml(results.summary)}
                </div>
            `;
        }
        
        resultsDiv.innerHTML = html;
    }
    
    // ===== TRAINING =====
    
    /**
     * Setup training UI
     */
    setupTrainingUI() {
        const trainButton = document.getElementById('train-button');
        
        if (trainButton) {
            trainButton.addEventListener('click', () => this.startTraining());
        }
    }
    
    /**
     * Start model training
     */
    async startTraining() {
        if (!this.currentDevice) {
            uiManager.showWarning('Please select a device first');
            return;
        }
        
        const hoursInput = document.getElementById('training-hours');
        const minutesInput = document.getElementById('training-minutes');
        const hours = Math.min(720, Math.max(1, parseInt(hoursInput?.value, 10) || 24));
        const minutesValue = minutesInput?.value.trim();
        const minutes = minutesValue ? Math.min(60, Math.max(1, parseInt(minutesValue, 10) || 1)) : null;
        const model = document.getElementById('training-model')?.value || 'random_forest';
        
        if (this.trainingStatus === 'training') {
            uiManager.showWarning('Training already in progress');
            return;
        }
        
        this.trainingStatus = 'training';
        const interval = minutes === null ? `${hours} ore` : `${minutes} minute`;
        uiManager.showLoading(`Antrenez modelul cu agregare la ${interval}...`);
        this.updateTrainingProgress(0);
        
        try {
            const payload = {
                device_id: this.currentDevice,
                dataset_name: this.currentDevice,
                notes: `Antrenare ${model} solicitata din interfata web cu agregare la ${interval}.`,
                training_model: model,
                aggregation_hours: hours,
                allow_derived_label_fallback: true
            };
            if (minutes !== null) payload.aggregation_minutes = minutes;

            const result = await this.postAI(API_CONFIG.ENDPOINTS.ai.train, payload);
            
            this.updateTrainingProgress(100);
            
            uiManager.hideLoading();
            this.trainingStatus = 'completed';
            this.displayTrainingResults(result);
            uiManager.showSuccess('Model training completed successfully');
            
        } catch (error) {
            uiManager.hideLoading();
            this.trainingStatus = 'error';
            this.displayActionError('training-results', 'Antrenarea modelului nu poate rula', error.message);
            uiManager.showError('Training failed: ' + error.message);
            if (typeof addTestResult === 'function') addTestResult('Training error: ' + error.message, 'error');
        } finally {
            this.trainingStatus = 'idle';
        }
    }
    
    /**
     * Simulate training progress
     */
    async simulateTrainingProgress() {
        for (let i = 0; i <= 100; i += 10) {
            await new Promise(resolve => setTimeout(resolve, 500));
            this.updateTrainingProgress(i);
        }
    }
    
    /**
     * Update training progress bar
     */
    updateTrainingProgress(percent) {
        const progressBar = document.getElementById('training-progress-bar');
        const progressText = document.getElementById('training-progress-text');
        
        if (progressBar) {
            progressBar.style.width = percent + '%';
        }
        
        if (progressText) {
            progressText.textContent = percent + '%';
        }
    }
    
    /**
     * Display training results
     */
    displayTrainingResults(results) {
        const resultsDiv = document.getElementById('training-results');
        if (!resultsDiv) return;
        
        let html = `<div class="alert alert-success"><strong>${this.escapeHtml(results.message || 'Training completed!')}</strong></div>`;

        if (results.status) {
            html += `<p><strong>Status:</strong> ${this.escapeHtml(results.status)}</p>`;
        }
        
        if (results.accuracy !== undefined) {
            html += `
                <div class="training-metric">
                    <strong>Model Accuracy:</strong>
                    <div class="progress">
                        <div class="progress-bar bg-success" style="width: ${results.accuracy * 100}%">
                            ${(results.accuracy * 100).toFixed(1)}%
                        </div>
                    </div>
                </div>
            `;
        }
        
        if (results.samples_used !== undefined) {
            html += `
                <div class="training-metric">
                    <strong>Data Points Used:</strong>
                    <span class="badge bg-info">${results.samples_used}</span>
                </div>
            `;
        }
        
        if (results.training_time !== undefined) {
            html += `
                <div class="training-metric">
                    <strong>Training Time:</strong>
                    <span class="badge bg-secondary">${results.training_time.toFixed(2)} seconds</span>
                </div>
            `;
        }
        
        if (results.metrics) {
            html += '<strong>Performance Metrics:</strong><ul>';
            Object.entries(results.metrics).forEach(([key, value]) => {
                const metricLabel = /^(svm|xgboost)$/i.test(key) ? `${key} (antrenare)` : key;
                html += `<li>${this.escapeHtml(metricLabel)}: ${typeof value === 'number' ? value.toFixed(3) : value}</li>`;
            });
            html += '</ul>';
        }

        const trainingReport = results.training_report;
        const modelInfo = trainingReport?.model_info;
        const evolution = trainingReport?.technical_details?.evolution;
        const recommendedMetric = trainingReport?.recommended_metric || trainingReport?.evaluation?.recommended_metric;
        if (modelInfo?.n_estimators !== undefined) {
            html += `<div class="training-metric"><strong>Număr de arbori:</strong> <span class="badge bg-primary">${this.escapeHtml(String(modelInfo.n_estimators))}</span></div>`;
        }

        if (recommendedMetric?.label) {
            const scores = [];
            if (typeof recommendedMetric.accuracy === 'number') {
                scores.push(`Accuracy: ${recommendedMetric.accuracy.toFixed(4)}`);
            }
            if (typeof recommendedMetric.f1_score === 'number') {
                scores.push(`F1-score: ${recommendedMetric.f1_score.toFixed(4)}`);
            }
            if (typeof recommendedMetric.oob_score === 'number') {
                scores.push(`OOB score: ${(recommendedMetric.oob_score * 100).toFixed(2)}%`);
            }
            if (typeof recommendedMetric.mean_score === 'number') {
                scores.push(`Mean score: ${(recommendedMetric.mean_score * 100).toFixed(2)}%`);
            }
            if (recommendedMetric.iteration_count !== undefined) {
                scores.push(`Iterații: ${recommendedMetric.iteration_count}`);
            }

            html += `<div class="training-metric"><strong>${this.escapeHtml(recommendedMetric.label)}:</strong> ${this.escapeHtml(scores.join(' | '))}</div>`;
        }

        if (Array.isArray(evolution) && evolution.length > 0) {
            const hasOobScore = evolution.some((item) => typeof item.oob_score === 'number');
            const evolutionTitle = hasOobScore ? 'Evoluție OOB score:' : 'Evoluție antrenare:';
            let totalOobScore = 0;
            let oobScoreCount = 0;
            html += `
                <div class="training-metric">
                    <strong>${evolutionTitle}</strong>
                    <div class="table-responsive mt-2">
                        <table class="table table-sm table-striped mb-0">
                            <thead>
                                <tr><th>Iterație</th><th>OOB score</th><th>Mean score</th></tr>
                            </thead>
                            <tbody>
            `;
            evolution.forEach((item) => {
                const iteration = item.step ?? item.iteration ?? '—';
                if (typeof item.oob_score === 'number') {
                    totalOobScore += item.oob_score;
                    oobScoreCount += 1;
                }
                const oobScore = typeof item.oob_score === 'number'
                    ? `${(item.oob_score * 100).toFixed(2)}%`
                    : '—';
                const meanScore = typeof item.mean_score === 'number'
                    ? item.mean_score
                    : oobScoreCount > 0 ? totalOobScore / oobScoreCount : null;
                const trainingMetric = typeof item.oob_score === 'number'
                    ? ''
                    : Object.entries(item)
                        .filter(([key]) => key !== 'step' && key !== 'iteration')
                        .map(([key, value]) => `${key}: ${typeof value === 'number' ? value.toFixed(4) : value}`)
                        .join(', ') || 'fără metrică disponibilă';
                const oobDisplay = typeof item.oob_score === 'number' ? oobScore : trainingMetric;
                html += `
                    <tr>
                        <td>${this.escapeHtml(String(iteration))}</td>
                        <td>${this.escapeHtml(oobDisplay)}</td>
                        <td>${typeof meanScore === 'number' ? `${(meanScore * 100).toFixed(2)}%` : '—'}</td>
                    </tr>
                `;
            });
            html += '</tbody></table></div></div>';
        }
        
        resultsDiv.innerHTML = html;
    }
    
    // ===== DEVICE SELECTOR =====
    
    /**
     * Setup device selector
     */
    setupDeviceSelector() {
        this.loadDevices();

        this.getDeviceSelectors().forEach((deviceSelect) => {
            deviceSelect.addEventListener('change', (e) => {
                this.currentDevice = e.target.value;
                this.onDeviceChanged();
            });
        });
    }

    getDeviceSelectors() {
        return Array.from(document.querySelectorAll('#ai-device-select, #chat-device-select, .ai-operation-device-select'));
    }

    updateChatInputState() {
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('chat-send-button');

        const isEnabled = Boolean(this.currentDevice);
        if (chatInput) {
            chatInput.disabled = !isEnabled;
            chatInput.placeholder = isEnabled
                ? 'Scrie întrebarea pentru Aerosenzor...'
                : 'Selectează un dispozitiv pentru a continua...';
        }
        if (sendButton) {
            sendButton.disabled = !isEnabled;
        }
    }

    getAvailableDeviceNames() {
        const selectors = this.getDeviceSelectors();
        const names = [];

        selectors.forEach((select) => {
            Array.from(select.options).forEach((option) => {
                if (option.value && option.textContent && option.textContent.trim() !== 'Selectează un dispozitiv...' && !names.includes(option.textContent.trim())) {
                    names.push(option.textContent.trim());
                }
            });
        });

        return names;
    }
    
    /**
     * Load devices into selector
     */
    async loadDevices() {
        const deviceSelectors = this.getDeviceSelectors();
        if (deviceSelectors.length === 0) return;
        
        try {
            const response = await fetch('/ai/devices/', { credentials: 'same-origin' });
            if (!response.ok) {
                throw new Error(response.status === 401 ? 'Autentifică-te pentru a vedea dispozitivele.' : 'Dispozitivele nu au putut fi încărcate.');
            }
            const { devices } = await response.json();
            
            deviceSelectors.forEach((deviceSelect) => {
                deviceSelect.innerHTML = '<option value="">Selectează un dispozitiv...</option>';
                devices.forEach((device) => {
                    const option = document.createElement('option');
                    option.value = device.id;
                    option.textContent = device.name || device.id;
                    deviceSelect.appendChild(option);
                });
            });

            if (devices.length > 0) {
                const deviceNames = devices.map((device) => device.name || device.id);
                const chatDisplay = document.getElementById('chat-display');
                if (chatDisplay && chatDisplay.children.length > 0) {
                    this.addChatMessage({
                        role: 'assistant',
                        content: `Bună! Sunt agentul Aerosenzor. Pentru a continua discuția, selectează un dispozitiv din listă: ${deviceNames.join(', ')}.`,
                        timestamp: new Date()
                    });
                }
            }
        } catch (error) {
            console.error('Error loading devices:', error);
            if (typeof uiManager !== 'undefined' && uiManager.showError) {
                uiManager.showError('Failed to load devices: ' + error.message);
            }
        }
    }
    
    /**
     * Handle device selection change
     */
    onDeviceChanged() {
        this.getDeviceSelectors().forEach((deviceSelect) => {
            deviceSelect.value = this.currentDevice || '';
        });

        this.updateChatInputState();

        const deviceInfo = document.getElementById('ai-device-info');
        if (deviceInfo && this.currentDevice) {
            deviceInfo.innerHTML = `<small class="text-muted">Selected: ${this.currentDevice}</small>`;
        }
    }
    
    // ===== UTILITIES =====
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    displayActionError(resultElementId, title, message) {
        const resultsDiv = document.getElementById(resultElementId);
        if (!resultsDiv) return;

        const configurationHint = message.includes('SUPABASE_URL') || message.includes('SUPABASE_SERVICE_ROLE_KEY')
            ? '<p class="mb-0 mt-2">Configurează <code>SUPABASE_URL</code> și <code>SUPABASE_SERVICE_ROLE_KEY</code> în variabilele serviciului Railway AI, apoi redeployează serviciul.</p>'
            : '';
        resultsDiv.innerHTML = `<div class="alert alert-danger"><strong>${this.escapeHtml(title)}.</strong><br>${this.escapeHtml(message)}${configurationHint}</div>`;
    }
}

// Create global instance
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.aiInterfaceManager = new AIInterfaceManager();
    });
} else {
    window.aiInterfaceManager = new AIInterfaceManager();
}

console.log('AI Interface Manager loaded');
