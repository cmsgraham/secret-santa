/**
 * Toast Notification System
 * Provides elegant, accessible notification messages for the Secret Santa app
 */

class NotificationSystem {
    constructor() {
        this.container = null;
        this.toasts = [];
        this.init();
    }

    init() {
        // Create container for toasts
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);
    }

    /**
     * Show a toast notification
     * @param {string} type - 'success', 'error', 'warning', 'info'
     * @param {string} title - Notification title
     * @param {string} message - Optional detailed message
     * @param {number} duration - Auto-dismiss time in ms (0 = manual)
     */
    show(type, title, message = '', duration = 5000) {
        const toastId = `toast-${Date.now()}-${Math.random()}`;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.id = toastId;

        // Icon based on type
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        // Build toast HTML
        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || '•'}</div>
            <div class="toast-content">
                <div class="toast-title">${this.escapeHtml(title)}</div>
                ${message ? `<div class="toast-message">${this.escapeHtml(message)}</div>` : ''}
            </div>
            <button class="toast-close" aria-label="Close">×</button>
        `;

        // Close button handler
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.dismiss(toastId);
        });

        this.container.appendChild(toast);
        this.toasts.push({ id: toastId, element: toast, timeout: null });

        // Auto-dismiss
        if (duration > 0) {
            const timeout = setTimeout(() => {
                this.dismiss(toastId);
            }, duration);
            
            const toastObj = this.toasts.find(t => t.id === toastId);
            if (toastObj) {
                toastObj.timeout = timeout;
            }
        }

        return toastId;
    }

    /**
     * Show success notification
     */
    success(title, message = '', duration = 5000) {
        return this.show('success', title, message, duration);
    }

    /**
     * Show error notification
     */
    error(title, message = '', duration = 5000) {
        return this.show('error', title, message, duration);
    }

    /**
     * Show warning notification
     */
    warning(title, message = '', duration = 5000) {
        return this.show('warning', title, message, duration);
    }

    /**
     * Show info notification
     */
    info(title, message = '', duration = 5000) {
        return this.show('info', title, message, duration);
    }

    /**
     * Dismiss a toast by ID
     */
    dismiss(toastId) {
        const toastIndex = this.toasts.findIndex(t => t.id === toastId);
        if (toastIndex === -1) return;

        const toast = this.toasts[toastIndex];
        
        // Clear timeout if exists
        if (toast.timeout) {
            clearTimeout(toast.timeout);
        }

        // Add hide animation
        toast.element.classList.add('hide');

        // Remove after animation
        setTimeout(() => {
            if (toast.element.parentNode) {
                toast.element.parentNode.removeChild(toast.element);
            }
            this.toasts.splice(toastIndex, 1);
        }, 300);
    }

    /**
     * Dismiss all toasts
     */
    dismissAll() {
        const ids = this.toasts.map(t => t.id);
        ids.forEach(id => this.dismiss(id));
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

/**
 * Confirmation Dialog System
 * Provides elegant confirmation prompts
 */
class ConfirmationDialog {
    /**
     * Show a confirmation dialog
     * @param {object} options - Configuration object
     * @returns {Promise<boolean>} - Resolves to true if confirmed, false if cancelled
     */
    static show(options = {}) {
        const {
            title = 'Confirm Action',
            message = 'Are you sure?',
            confirmText = 'Confirm',
            cancelText = 'Cancel',
            isDangerous = false
        } = options;

        return new Promise((resolve) => {
            const overlay = document.createElement('div');
            overlay.className = 'modal-overlay';

            const modal = document.createElement('div');
            modal.className = 'modal';

            modal.innerHTML = `
                <div class="modal-header">
                    <h3>${this.escapeHtml(title)}</h3>
                </div>
                <div class="modal-body">
                    ${this.escapeHtml(message)}
                </div>
                <div class="modal-footer">
                    <button class="btn-cancel">${this.escapeHtml(cancelText)}</button>
                    <button class="btn-confirm ${isDangerous ? 'danger' : ''}">${this.escapeHtml(confirmText)}</button>
                </div>
            `;

            overlay.appendChild(modal);
            document.body.appendChild(overlay);

            const cancelBtn = modal.querySelector('.btn-cancel');
            const confirmBtn = modal.querySelector('.btn-confirm');

            const cleanup = () => {
                overlay.style.animation = 'fadeOut 0.2s ease-out';
                setTimeout(() => {
                    if (overlay.parentNode) {
                        overlay.parentNode.removeChild(overlay);
                    }
                }, 200);
            };

            cancelBtn.addEventListener('click', () => {
                cleanup();
                resolve(false);
            });

            confirmBtn.addEventListener('click', () => {
                cleanup();
                resolve(true);
            });

            // Allow Escape key to cancel
            const escapeHandler = (e) => {
                if (e.key === 'Escape') {
                    document.removeEventListener('keydown', escapeHandler);
                    cleanup();
                    resolve(false);
                }
            };
            document.addEventListener('keydown', escapeHandler);
        });
    }

    /**
     * Escape HTML to prevent XSS
     */
    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize notification system globally
let notify = new NotificationSystem();

// Compatibility layer for existing code using alert() and confirm()
// This provides a migration path for the codebase
window.showToast = function(type, title, message = '', duration = 5000) {
    return notify.show(type, title, message, duration);
};

// For backward compatibility with existing showMessage() function
window.showMessage = function(type, text) {
    const typeMap = {
        'success': 'success',
        'error': 'error',
        'warning': 'warning',
        'info': 'info'
    };
    return notify.show(typeMap[type] || 'info', text);
};
