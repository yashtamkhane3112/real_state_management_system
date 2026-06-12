/**
 * Real Estate Marketplace - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize property filters
    initializePropertyFilters();
    
    // Initialize favorites toggle
    initializeFavoritesToggle();
});

/**
 * Initialize Bootstrap components
 */
function initializeBootstrapComponents() {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[novalidate]');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Initialize property filters
 */
function initializePropertyFilters() {
    const filterForm = document.getElementById('propertyFilterForm');
    
    if (filterForm) {
        const inputs = filterForm.querySelectorAll('input, select');
        
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                // Auto-submit form on filter change
                // filterForm.submit();
            });
        });
    }
}

/**
 * Initialize favorites toggle
 */
function initializeFavoritesToggle() {
    const favoriteButtons = document.querySelectorAll('[data-toggle="favorite"]');
    
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const propertyId = this.dataset.propertyId;
            const isFavorite = this.classList.contains('favorited');
            
            // Toggle visual state
            this.classList.toggle('favorited');
            
            // Update icon
            const icon = this.querySelector('i');
            if (isFavorite) {
                icon.classList.remove('fas');
                icon.classList.add('far');
            } else {
                icon.classList.remove('far');
                icon.classList.add('fas');
            }
        });
    });
}

/**
 * Utility: Format price
 */
function formatPrice(price) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(price);
}

/**
 * Utility: Format date
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-IN', options);
}

/**
 * Utility: Show alert
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container:first-of-type');
    if (container) {
        container.insertAdjacentElement('afterbegin', alertDiv);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

/**
 * Utility: Confirm action
 */
function confirmAction(message = 'Are you sure?') {
    return confirm(message);
}

/**
 * Utility: Disable form submission
 */
function disableFormSubmission(formId) {
    const form = document.getElementById(formId);
    if (form) {
        const button = form.querySelector('button[type="submit"]');
        if (button) {
            button.disabled = true;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
        }
    }
}

/**
 * Property card carousel
 */
function initializeCarousels() {
    const carousels = document.querySelectorAll('[data-carousel]');
    
    carousels.forEach(carousel => {
        let currentIndex = 0;
        const slides = carousel.querySelectorAll('[data-slide]');
        const prevBtn = carousel.querySelector('[data-prev]');
        const nextBtn = carousel.querySelector('[data-next]');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                currentIndex = (currentIndex - 1 + slides.length) % slides.length;
                updateCarousel(carousel, currentIndex);
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                currentIndex = (currentIndex + 1) % slides.length;
                updateCarousel(carousel, currentIndex);
            });
        }
    });
}

function updateCarousel(carousel, index) {
    const slides = carousel.querySelectorAll('[data-slide]');
    slides.forEach((slide, i) => {
        slide.style.display = i === index ? 'block' : 'none';
    });
}

/**
 * Search functionality
 */
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value;
            
            if (query.length > 2) {
                // Perform search
                performSearch(query);
            }
        });
    }
}

function performSearch(query) {
    // This would typically make an AJAX call to the server
    console.log('Searching for:', query);
}

/**
 * Lazy load images
 */
function lazyLoadImages() {
    if ('IntersectionObserver' in window) {
        const imageElements = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });
        
        imageElements.forEach(img => imageObserver.observe(img));
    }
}

/**
 * Document ready check
 */
function isDocumentReady() {
    return document.readyState === 'complete' || document.readyState === 'interactive';
}

/**
 * Export functions for global use
 */
window.RealEstate = {
    formatPrice,
    formatDate,
    showAlert,
    confirmAction,
    disableFormSubmission
};
