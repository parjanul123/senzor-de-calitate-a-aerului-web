/**
 * UI Utilities - Manage loading states, error displays, and notifications
 * 
 * Provides helper functions for:
 * - Showing/hiding loading spinners
 * - Displaying error messages
 * - Showing success/info notifications
 * - Managing modal dialogs
 */

class UIManager {
    constructor() {
        this.loadingElement = null;
        this.errorElement = null;
        this.notificationQueue = [];
        this.setupDefaultUI();
    }
    
    /**
     * Setup default UI elements if not already present
     */
    setupDefaultUI() {
        // Create default loading spinner if not exists
        if (!document.getElementById('global-loading')) {
            const loading = document.createElement('div');
            loading.id = 'global-loading';
            loading.className = 'spinner-container hidden';
            loading.innerHTML = `
                <div class="spinner-overlay">
                    <div class="spinner">
                        <div class="spinner-border" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2">Loading...</p>
                    </div>
                </div>
            `;
            document.body.appendChild(loading);
        }
        
        // Create default error container if not exists
        if (!document.getElementById('global-error')) {
            const error = document.createElement('div');
            error.id = 'global-error';
            error.className = 'alert alert-danger alert-dismissible fade hidden mt-3';
            error.role = 'alert';
            error.innerHTML = `
                <strong>Error:</strong>
                <span id="error-message"></span>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.insertBefore(error, document.body.firstChild);
        }
        
        // Create notification container if not exists
        if (!document.getElementById('notifications-container')) {
            const container = document.createElement('div');
            container.id = 'notifications-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
        
        this.loadingElement = document.getElementById('global-loading');
        this.errorElement = document.getElementById('global-error');
    }
    
    /**
     * Show loading spinner
     * @param {string} message - Optional loading message
     */
    showLoading(message = 'Loading...') {
        if (this.loadingElement) {
            const msgElement = this.loadingElement.querySelector('p');
            if (msgElement) msgElement.textContent = message;
            this.loadingElement.classList.remove('hidden');
        }
    }
    
    /**
     * Hide loading spinner
     */
    hideLoading() {
        if (this.loadingElement) {
            this.loadingElement.classList.add('hidden');
        }
    }
    
    /**
     * Show error message
     * @param {string} message - Error message
     * @param {number} duration - Auto-dismiss duration in ms (0 = no auto-dismiss)
     */
    showError(message, duration = 0) {
        if (this.errorElement) {
            const msgElement = this.errorElement.querySelector('#error-message');
            if (msgElement) msgElement.textContent = message;
            this.errorElement.classList.remove('hidden');
            
            if (duration > 0) {
                setTimeout(() => this.hideError(), duration);
            }
        }
    }
    
    /**
     * Hide error message
     */
    hideError() {
        if (this.errorElement) {
            this.errorElement.classList.add('hidden');
        }
    }
    
    /**
     * Show notification (toast)
     * @param {string} message - Notification message
     * @param {string} type - Type: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Auto-dismiss duration in ms
     */
    showNotification(message, type = 'info', duration = 3000) {
        const alertClass = {
            success: 'alert-success',
            error: 'alert-danger',
            warning: 'alert-warning',
            info: 'alert-info',
        }[type] || 'alert-info';
        
        const notificationId = `notif-${Date.now()}`;
        const notification = document.createElement('div');
        notification.id = notificationId;
        notification.className = `alert ${alertClass} alert-dismissible fade show`;
        notification.role = 'alert';
        notification.style.marginBottom = '10px';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.getElementById('notifications-container');
        if (container) {
            container.appendChild(notification);
            
            if (duration > 0) {
                setTimeout(() => {
                    const notif = document.getElementById(notificationId);
                    if (notif) {
                        notif.remove();
                    }
                }, duration);
            }
        }
    }
    
    /**
     * Show success notification
     */
    showSuccess(message, duration = 3000) {
        this.showNotification(message, 'success', duration);
    }
    
    /**
     * Show warning notification
     */
    showWarning(message, duration = 3000) {
        this.showNotification(message, 'warning', duration);
    }
    
    /**
     * Show info notification
     */
    showInfo(message, duration = 3000) {
        this.showNotification(message, 'info', duration);
    }
    
    /**
     * Show confirmation dialog
     * @param {string} message - Confirmation message
     * @param {function} onConfirm - Callback on confirm
     * @param {function} onCancel - Callback on cancel
     */
    showConfirm(message, onConfirm, onCancel) {
        const result = confirm(message);
        if (result && onConfirm) {
            onConfirm();
        } else if (!result && onCancel) {
            onCancel();
        }
    }
    
    /**
     * Format error message for display
     * @param {Error} error - Error object
     * @returns {string} Formatted error message
     */
    formatError(error) {
        if (error.status === 401) {
            return 'You need to be logged in. Please refresh the page.';
        } else if (error.status === 403) {
            return 'You do not have permission to access this resource.';
        } else if (error.status === 404) {
            return 'The requested resource was not found.';
        } else if (error.status === 500) {
            return 'Server error. Please try again later.';
        } else if (error.name === 'AbortError') {
            return 'Request timed out. Please check your connection.';
        } else {
            return error.message || 'An error occurred. Please try again.';
        }
    }
    
    /**
     * Update element with loading state
     * @param {string} elementId - Element ID
     * @param {boolean} isLoading - Loading state
     * @param {string} loadingText - Text to show while loading
     */
    setElementLoading(elementId, isLoading, loadingText = 'Loading...') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        if (isLoading) {
            element.disabled = true;
            element.classList.add('disabled');
            element.dataset.originalText = element.textContent;
            element.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                ${loadingText}
            `;
        } else {
            element.disabled = false;
            element.classList.remove('disabled');
            element.textContent = element.dataset.originalText || 'Submit';
        }
    }
}

// Create global instance
const uiManager = new UIManager();

// Setup API Client listeners for automatic UI updates
apiClient.onLoadingChange((isLoading) => {
    if (isLoading) {
        uiManager.showLoading('Loading data...');
    } else {
        uiManager.hideLoading();
    }
});

apiClient.onError((error) => {
    uiManager.showError(uiManager.formatError(error), 5000);
    console.error('API Error:', error);
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { UIManager, uiManager };
}
