// Main JavaScript file for POS System

$(document).ready(function() {
    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-bs-theme', savedTheme);
    updateThemeIcon(savedTheme);

    themeToggle.addEventListener('click', function() {
        const currentTheme = htmlElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        htmlElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });

    function updateThemeIcon(theme) {
        const icon = themeToggle.querySelector('i');
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }

    // Sidebar toggle for mobile
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            if (!sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
                sidebar.classList.remove('show');
            }
        });
    }

    // Flash message auto-hide
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            const alert = new bootstrap.Alert(message);
            alert.close();
        }, 5000); // Auto-hide after 5 seconds
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Number input enhancement
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            // Prevent negative values for price/quantity
            if (this.min === '0' && parseFloat(this.value) < 0) {
                this.value = 0;
            }
        });
    });

    // Search functionality
    const searchInputs = document.querySelectorAll('input[type="search"], input[placeholder*="search" i]');
    searchInputs.forEach(function(input) {
        let timeout;
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(function() {
                // Trigger search event
                const event = new CustomEvent('search', { detail: { query: input.value } });
                input.dispatchEvent(event);
            }, 300); // Debounce search
        });
    });

    // Table sorting
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    sortableHeaders.forEach(function(header) {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const table = header.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const column = header.dataset.sort;
            const direction = header.dataset.direction || 'asc';

            rows.sort(function(a, b) {
                const aValue = a.querySelector(`td[data-${column}]`)?.textContent || '';
                const bValue = b.querySelector(`td[data-${column}]`)?.textContent || '';

                if (direction === 'asc') {
                    return aValue.localeCompare(bValue);
                } else {
                    return bValue.localeCompare(aValue);
                }
            });

            // Update direction
            header.dataset.direction = direction === 'asc' ? 'desc' : 'asc';

            // Re-append sorted rows
            rows.forEach(function(row) {
                tbody.appendChild(row);
            });

            // Update sort indicators
            sortableHeaders.forEach(function(h) {
                h.querySelector('.sort-indicator')?.remove();
            });

            const indicator = document.createElement('i');
            indicator.className = 'fas fa-sort-' + (direction === 'asc' ? 'up' : 'down') + ' ms-1 sort-indicator';
            header.appendChild(indicator);
        });
    });

    // Modal enhancements
    const modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        modal.addEventListener('shown.bs.modal', function() {
            // Focus on first input
            const firstInput = modal.querySelector('input, select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });

    // Print functionality
    window.printContent = function(selector) {
        const printContent = document.querySelector(selector);
        if (printContent) {
            const originalContent = document.body.innerHTML;
            document.body.innerHTML = printContent.innerHTML;
            window.print();
            document.body.innerHTML = originalContent;
            // Re-initialize Bootstrap components
            initBootstrapComponents();
        }
    };

    // Copy to clipboard
    window.copyToClipboard = function(text) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copied to clipboard!', 'success');
        }).catch(function() {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showToast('Copied to clipboard!', 'success');
        });
    };

    // Toast notifications
    function showToast(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container') || createToastContainer();
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Auto remove after hide
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }

    function createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    // Loading states
    window.showLoading = function(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
        button.disabled = true;

        return function() {
            button.innerHTML = originalText;
            button.disabled = false;
        };
    };

    // Confirm dialog
    window.confirmAction = function(message, callback) {
        if (window.confirm(message)) {
            callback();
        }
    };

    // Auto-save functionality for forms
    const autoSaveForms = document.querySelectorAll('form[data-auto-save]');
    autoSaveForms.forEach(function(form) {
        let timeout;
        const inputs = form.querySelectorAll('input, select, textarea');

        inputs.forEach(function(input) {
            input.addEventListener('input', function() {
                clearTimeout(timeout);
                timeout = setTimeout(function() {
                    // Auto-save logic here
                    console.log('Auto-saving form data...');
                }, 2000);
            });
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + S to save
        if ((event.ctrlKey || event.metaKey) && event.key === 's') {
            event.preventDefault();
            const saveButton = document.querySelector('button[type="submit"], .btn-save');
            if (saveButton && !saveButton.disabled) {
                saveButton.click();
            }
        }

        // Escape to close modals
        if (event.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const bsModal = bootstrap.Modal.getInstance(openModal);
                if (bsModal) {
                    bsModal.hide();
                }
            }
        }

        // Ctrl/Cmd + N for new item
        if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
            event.preventDefault();
            const newButton = document.querySelector('.btn-add, .btn-new');
            if (newButton) {
                newButton.click();
            }
        }
    });

    // Re-initialize Bootstrap components after dynamic content changes
    function initBootstrapComponents() {
        // Re-initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Re-initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    // Initialize components on page load
    initBootstrapComponents();

    // Handle AJAX errors globally
    $(document).ajaxError(function(event, xhr, settings, thrownError) {
        console.error('AJAX Error:', thrownError);
        showToast('An error occurred. Please try again.', 'danger');
    });

    // Handle successful AJAX requests
    $(document).ajaxSuccess(function(event, xhr, settings) {
        // You can add global success handling here
    });

    // Page visibility API for performance
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // Page is hidden, pause non-essential operations
            console.log('Page hidden');
        } else {
            // Page is visible again, resume operations
            console.log('Page visible');
        }
    });

    // Service Worker registration for PWA features
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            // Register service worker for offline functionality
            // navigator.serviceWorker.register('/sw.js');
        });
    }

    // Performance monitoring
    if ('performance' in window && 'getEntriesByType' in performance) {
        window.addEventListener('load', function() {
            // Log page load performance
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
        });
    }

    // Touch device optimizations
    if ('ontouchstart' in window) {
        // Add touch-specific styles or behaviors
        document.body.classList.add('touch-device');

        // Prevent double-tap zoom on buttons
        const buttons = document.querySelectorAll('button, .btn');
        buttons.forEach(function(button) {
            button.addEventListener('touchstart', function() {
                // Prevent default touch behavior
            });
        });
    }

    console.log('POS System initialized successfully');
});