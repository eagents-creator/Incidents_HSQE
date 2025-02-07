// Form Validation
document.addEventListener('DOMContentLoaded', function() {
    // Password confirmation validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const password = form.querySelector('input[type="password"][id$="password"]');
        const confirmPassword = form.querySelector('input[type="password"][id$="confirm_password"]');
        
        if (password && confirmPassword) {
            form.addEventListener('submit', function(event) {
                if (password.value !== confirmPassword.value) {
                    event.preventDefault();
                    alert('Passwords do not match!');
                }
            });
        }
    });

    // Date input validation and initialization
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        const today = new Date().toISOString().split('T')[0];
        if (input.id === 'due_date') {
            input.min = today;
        }
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Chart Configuration Defaults
if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = "'Segoe UI', 'Helvetica Neue', 'Arial', sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.plugins.legend.position = 'bottom';
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    Chart.defaults.plugins.tooltip.titleColor = '#ffffff';
    Chart.defaults.plugins.tooltip.bodyColor = '#ffffff';
    Chart.defaults.plugins.tooltip.borderColor = 'rgba(0, 0, 0, 0.1)';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.displayColors = true;
    Chart.defaults.plugins.tooltip.boxPadding = 3;
}

// Dynamic Form Updates
function updateSubcategories(categorySelect, subcategorySelect, subcategories) {
    if (!categorySelect || !subcategorySelect || !subcategories) return;

    const category = categorySelect.value;
    subcategorySelect.innerHTML = '<option value="">Select Subcategory</option>';
    
    if (category && subcategories[category]) {
        subcategories[category].forEach(sub => {
            const option = document.createElement('option');
            option.value = sub;
            option.textContent = sub;
            subcategorySelect.appendChild(option);
        });
    }
}

// Status Updates
function updateStatus(type, id, status, url) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = url;
    
    const statusInput = document.createElement('input');
    statusInput.type = 'hidden';
    statusInput.name = 'status';
    statusInput.value = status;
    
    form.appendChild(statusInput);
    document.body.appendChild(form);
    form.submit();
}

// Table Search and Filter
function initializeTableSearch(tableId, inputId) {
    const searchInput = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!searchInput || !table) return;
    
    searchInput.addEventListener('keyup', function() {
        const searchText = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchText) ? '' : 'none';
        });
    });
}

// Modal Handlers
function initializeModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            if (!button) return;
            
            // Handle dynamic content loading
            const contentUrl = button.getAttribute('data-content-url');
            if (contentUrl) {
                const modalBody = this.querySelector('.modal-body');
                fetch(contentUrl)
                    .then(response => response.text())
                    .then(html => {
                        modalBody.innerHTML = html;
                    })
                    .catch(error => {
                        console.error('Error loading modal content:', error);
                        modalBody.innerHTML = '<div class="alert alert-danger">Error loading content</div>';
                    });
            }
        });
    });
}

// Alert Auto-dismiss
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    });
}

// Form Reset Handler
function initializeFormResets() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const resetButtons = form.querySelectorAll('[type="reset"]');
        resetButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                if (confirm('Are you sure you want to reset the form?')) {
                    form.reset();
                }
            });
        });
    });
}

// Initialize all components
document.addEventListener('DOMContentLoaded', function() {
    initializeModals();
    initializeAlerts();
    initializeFormResets();
    
    // Initialize table search if elements exist
    initializeTableSearch('incidentsTable', 'incidentSearch');
    initializeTableSearch('actionsTable', 'actionSearch');
    initializeTableSearch('metricsTable', 'metricSearch');
});
