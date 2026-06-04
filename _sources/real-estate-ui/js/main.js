// RealEstate Pro - Main JavaScript

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize smooth scrolling
    initSmoothScroll();

    // Initialize form validation
    initFormValidation();

    // Initialize favorites functionality
    initFavorites();

    // Initialize search filters
    initSearchFilters();
});

/**
 * Smooth scroll functionality
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Get form fields
            const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('is-invalid');
                    showToast('Please fill in all required fields', 'warning');
                } else {
                    input.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Favorites functionality
 */
function initFavorites() {
    const favoriteButtons = document.querySelectorAll('[data-favorite]');
    
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const isFavorited = this.classList.toggle('is-favorited');
            const icon = this.querySelector('i');
            
            if (isFavorited) {
                this.style.color = '#dc3545';
                icon.classList.remove('far');
                icon.classList.add('fas');
                showToast('Added to favorites', 'success');
            } else {
                this.style.color = '#999';
                icon.classList.remove('fas');
                icon.classList.add('far');
                showToast('Removed from favorites', 'info');
            }
        });
    });
}

/**
 * Search filters functionality
 */
function initSearchFilters() {
    const filterButtons = document.querySelectorAll('[data-filter]');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            filterProperties(filter);
        });
    });
}

/**
 * Filter properties based on criteria
 */
function filterProperties(filter) {
    const properties = document.querySelectorAll('.property-card');
    
    properties.forEach(property => {
        if (filter === 'all' || property.getAttribute('data-type') === filter) {
            property.style.display = 'block';
            setTimeout(() => property.classList.add('show'), 10);
        } else {
            property.classList.remove('show');
            setTimeout(() => property.style.display = 'none', 300);
        }
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toastHtml = `
        <div class="alert alert-${type} alert-dismissible fade show position-fixed" 
             role="alert" 
             style="top: 80px; right: 20px; min-width: 300px; z-index: 9999;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const toastContainer = document.createElement('div');
    toastContainer.innerHTML = toastHtml;
    document.body.appendChild(toastContainer);
    
    const alert = toastContainer.querySelector('.alert');
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

/**
 * Format price as currency
 */
function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0
    }).format(price);
}

/**
 * Handle property search
 */
function searchProperties(query) {
    const properties = document.querySelectorAll('[data-property-name]');
    
    properties.forEach(property => {
        const name = property.getAttribute('data-property-name').toLowerCase();
        if (name.includes(query.toLowerCase())) {
            property.style.display = 'block';
        } else {
            property.style.display = 'none';
        }
    });
}

/**
 * Schedule a tour
 */
function scheduleTour(propertyId) {
    const modal = new bootstrap.Modal(document.getElementById('tourModal'));
    modal.show();
}

/**
 * Contact agent
 */
function contactAgent(agentId) {
    showToast('Opening message with agent...', 'info');
    // Redirect to messages page
    setTimeout(() => {
        window.location.href = 'messages.html';
    }, 1000);
}

/**
 * Toggle property comparison
 */
function toggleComparison(propertyId) {
    const checkbox = document.querySelector(`[data-compare="${propertyId}"]`);
    const isChecked = checkbox.checked;
    
    if (isChecked) {
        addToComparison(propertyId);
    } else {
        removeFromComparison(propertyId);
    }
}

/**
 * Add property to comparison
 */
function addToComparison(propertyId) {
    showToast('Property added to comparison', 'success');
}

/**
 * Remove property from comparison
 */
function removeFromComparison(propertyId) {
    showToast('Property removed from comparison', 'info');
}

/**
 * Format date to readable format
 */
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

/**
 * Validate email
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate phone
 */
function validatePhone(phone) {
    const re = /^\d{10}$/;
    return re.test(phone.replace(/\D/g, ''));
}

/**
 * Export table to CSV
 */
function exportToCSV(tableId) {
    const table = document.getElementById(tableId);
    const csv = [];
    
    // Get headers
    const headers = [];
    table.querySelectorAll('thead th').forEach(th => {
        headers.push(th.textContent.trim());
    });
    csv.push(headers.join(','));
    
    // Get rows
    table.querySelectorAll('tbody tr').forEach(tr => {
        const row = [];
        tr.querySelectorAll('td').forEach(td => {
            row.push('"' + td.textContent.trim().replace(/"/g, '""') + '"');
        });
        csv.push(row.join(','));
    });
    
    // Create and download file
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'export.csv';
    a.click();
}

/**
 * Print page
 */
function printPage() {
    window.print();
}

/**
 * Share property
 */
function shareProperty(propertyName) {
    if (navigator.share) {
        navigator.share({
            title: propertyName,
            text: 'Check out this property!',
            url: window.location.href
        });
    } else {
        showToast('Share functionality not supported', 'warning');
    }
}

/**
 * Lazy load images
 */
function initLazyLoad() {
    const images = document.querySelectorAll('img[data-lazy]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.getAttribute('data-lazy');
                img.removeAttribute('data-lazy');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

/**
 * Dark mode toggle
 */
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Initialize dark mode from localStorage
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}
