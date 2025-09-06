/**
 * Restaurant Management System - Main JavaScript
 */

// Global variables
let currentUser = null;
let notifications = [];

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    initializeTooltips();
    initializePopovers();
    initializeFormValidation();
    initializeSearchFunctionality();
    initializeAjaxSetup();
    initializeNotifications();
    
    // Add loading states to forms
    addFormLoadingStates();
    
    // Initialize auto-refresh for certain pages
    initializeAutoRefresh();
    
    console.log('Restaurant Management System initialized');
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    // Add custom validation styles
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showToast('Please fill in all required fields', 'error');
            }
            form.classList.add('was-validated');
        });
    });

    // Real-time validation for specific fields
    const emailFields = document.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        field.addEventListener('blur', validateEmail);
    });

    const phoneFields = document.querySelectorAll('input[name*="phone"]');
    phoneFields.forEach(field => {
        field.addEventListener('blur', validatePhone);
        field.addEventListener('input', formatPhone);
    });

    const priceFields = document.querySelectorAll('input[name*="price"]');
    priceFields.forEach(field => {
        field.addEventListener('input', formatPrice);
    });
}

/**
 * Email validation
 */
function validateEmail(event) {
    const email = event.target.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        event.target.setCustomValidity('Please enter a valid email address');
        event.target.classList.add('is-invalid');
    } else {
        event.target.setCustomValidity('');
        event.target.classList.remove('is-invalid');
        if (email) event.target.classList.add('is-valid');
    }
}

/**
 * Phone validation
 */
function validatePhone(event) {
    const phone = event.target.value;
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    
    if (phone && !phoneRegex.test(phone.replace(/\D/g, ''))) {
        event.target.setCustomValidity('Please enter a valid phone number');
        event.target.classList.add('is-invalid');
    } else {
        event.target.setCustomValidity('');
        event.target.classList.remove('is-invalid');
        if (phone) event.target.classList.add('is-valid');
    }
}

/**
 * Format phone number input
 */
function formatPhone(event) {
    let value = event.target.value.replace(/\D/g, '');
    if (value.length >= 6) {
        value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
    } else if (value.length >= 3) {
        value = value.replace(/(\d{3})(\d{0,3})/, '($1) $2');
    }
    event.target.value = value;
}

/**
 * Format price input
 */
function formatPrice(event) {
    let value = event.target.value;
    value = value.replace(/[^\d.]/g, '');
    
    // Ensure only one decimal point
    const parts = value.split('.');
    if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('');
    }
    
    // Limit to 2 decimal places
    if (parts[1] && parts[1].length > 2) {
        value = parts[0] + '.' + parts[1].substring(0, 2);
    }
    
    event.target.value = value;
}

/**
 * Initialize search functionality
 */
function initializeSearchFunctionality() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value, this.dataset.searchType);
            }, 300);
        });
    });
}

/**
 * Perform search
 */
function performSearch(query, type) {
    if (query.length < 2) return;
    
    const searchEndpoints = {
        'customers': '/customers/ajax/search/',
        'menu': '/menu/ajax/search/',
        'orders': '/orders/ajax/search/'
    };
    
    const endpoint = searchEndpoints[type];
    if (!endpoint) return;
    
    fetch(`${endpoint}?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data, type);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

/**
 * Display search results
 */
function displaySearchResults(results, type) {
    const resultsContainer = document.getElementById(`${type}-search-results`);
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = '';
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<p class="text-muted">No results found</p>';
        return;
    }
    
    results.forEach(item => {
        const resultElement = createSearchResultElement(item, type);
        resultsContainer.appendChild(resultElement);
    });
}

/**
 * Create search result element
 */
function createSearchResultElement(item, type) {
    const div = document.createElement('div');
    div.className = 'search-result-item p-2 border-bottom';
    
    switch(type) {
        case 'customers':
            div.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="customer-avatar me-3">${item.name.charAt(0)}</div>
                    <div>
                        <strong>${item.name}</strong><br>
                        <small class="text-muted">${item.phone} • ${item.email}</small>
                    </div>
                </div>
            `;
            break;
        case 'menu':
            div.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="me-3">
                        ${item.image ? `<img src="${item.image}" class="rounded" width="40" height="40">` : 
                          '<div class="bg-primary rounded d-flex align-items-center justify-content-center" style="width:40px;height:40px;"><i class="bi bi-image text-white"></i></div>'}
                    </div>
                    <div>
                        <strong>${item.name}</strong><br>
                        <small class="text-muted">$${item.price} • ${item.category}</small>
                    </div>
                </div>
            `;
            break;
    }
    
    div.style.cursor = 'pointer';
    div.addEventListener('click', () => selectSearchResult(item, type));
    
    return div;
}

/**
 * Handle search result selection
 */
function selectSearchResult(item, type) {
    const event = new CustomEvent('searchResultSelected', {
        detail: { item, type }
    });
    document.dispatchEvent(event);
}

/**
 * Initialize AJAX setup
 */
function initializeAjaxSetup() {
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    // Setup default headers for all requests
    if (window.fetch) {
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            if (options.method && options.method.toUpperCase() !== 'GET') {
                options.headers = {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                    ...options.headers
                };
            }
            return originalFetch(url, options);
        };
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    const toastId = 'toast-' + Date.now();
    
    const iconMap = {
        'success': 'check-circle-fill',
        'error': 'exclamation-triangle-fill',
        'warning': 'exclamation-circle-fill',
        'info': 'info-circle-fill'
    };
    
    const colorMap = {
        'success': 'text-success',
        'error': 'text-danger',
        'warning': 'text-warning',
        'info': 'text-primary'
    };
    
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center">
                    <i class="bi bi-${iconMap[type]} me-2 ${colorMap[type]}"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: duration
    });
    
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

/**
 * Create toast container if it doesn't exist
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

/**
 * Initialize notifications
 */
function initializeNotifications() {
    // Check for new notifications every 30 seconds
    setInterval(checkNotifications, 30000);
}

/**
 * Check for new notifications
 */
function checkNotifications() {
    // This would be an AJAX call to check for new orders, etc.
    // For demo purposes, we'll simulate it
    if (Math.random() < 0.1) { // 10% chance of notification
        const notifications = [
            'New order received!',
            'Order #123 is ready for pickup',
            'Customer John Doe added to system'
        ];
        const randomNotification = notifications[Math.floor(Math.random() * notifications.length)];
        showToast(randomNotification, 'info');
    }
}

/**
 * Add loading states to forms
 */
function addFormLoadingStates() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                const originalText = submitButton.textContent;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                
                // Re-enable button after 10 seconds (fallback)
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.textContent = originalText;
                }, 10000);
            }
        });
    });
}

/**
 * Initialize auto-refresh for certain pages
 */
function initializeAutoRefresh() {
    const refreshablePages = ['/orders/', '/dashboard/'];
    const currentPath = window.location.pathname;
    
    if (refreshablePages.some(page => currentPath.includes(page))) {
        // Refresh page data every 2 minutes
        setInterval(() => {
            refreshPageData();
        }, 120000);
    }
}

/**
 * Refresh page data without full page reload
 */
function refreshPageData() {
    // This would update specific sections of the page
    console.log('Refreshing page data...');
    
    // Update timestamps
    const timestamps = document.querySelectorAll('[data-timestamp]');
    timestamps.forEach(timestamp => {
        updateTimestamp(timestamp);
    });
}

/**
 * Update timestamp display
 */
function updateTimestamp(element) {
    const timestamp = element.dataset.timestamp;
    if (timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        let timeAgo;
        if (days > 0) {
            timeAgo = `${days} day${days > 1 ? 's' : ''} ago`;
        } else if (hours > 0) {
            timeAgo = `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else if (minutes > 0) {
            timeAgo = `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        } else {
            timeAgo = 'Just now';
        }
        
        element.textContent = timeAgo;
    }
}

/**
 * Utility function to format currency
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Utility function to format date
 */
function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return new Intl.DateTimeFormat('en-US', { ...defaultOptions, ...options }).format(new Date(date));
}

/**
 * Confirm dialog with custom styling
 */
function confirmDialog(message, title = 'Confirm Action') {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" id="confirmButton">Confirm</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        modal.querySelector('#confirmButton').addEventListener('click', () => {
            resolve(true);
            bootstrapModal.hide();
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            if (!modal.querySelector('#confirmButton').clicked) {
                resolve(false);
            }
            modal.remove();
        });
        
        modal.querySelector('#confirmButton').addEventListener('click', function() {
            this.clicked = true;
        });
    });
}

/**
 * Export functions for global use
 */
window.RestaurantMS = {
    showToast,
    confirmDialog,
    formatCurrency,
    formatDate,
    refreshPageData
};

// Order management specific functions
if (window.location.pathname.includes('/orders/')) {
    
    /**
     * Update order status via AJAX
     */
    window.updateOrderStatus = function(orderId, newStatus) {
        fetch(`/orders/ajax/${orderId}/status/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `status=${newStatus}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast(data.message, 'success');
                // Update UI
                const statusElement = document.querySelector(`[data-order-id="${orderId}"] .order-status`);
                if (statusElement) {
                    statusElement.textContent = newStatus;
                    statusElement.className = `badge bg-${getStatusColor(newStatus)}`;
                }
            } else {
                showToast(data.message || 'Error updating order status', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error updating order status', 'error');
        });
    };
    
    /**
     * Get status color for badges
     */
    function getStatusColor(status) {
        const colors = {
            'pending': 'warning',
            'confirmed': 'info',
            'preparing': 'primary',
            'ready': 'success',
            'delivered': 'success',
            'cancelled': 'danger'
        };
        return colors[status] || 'secondary';
    }
}

console.log('Restaurant Management System JavaScript loaded successfully');