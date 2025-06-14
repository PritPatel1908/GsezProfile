// Global Profile Premium JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Initialize animations
    initAnimations();

    // Initialize form enhancements
    enhanceForms();

    // Initialize tooltips and popovers
    initTooltips();

    // Add smooth scrolling
    initSmoothScroll();

    // Initialize profile card effects
    initProfileCardEffects();

    // Initialize stat counter animations
    initStatCounters();

    // Add active class to current nav item
    highlightCurrentNavItem();

    // Initialize alert auto-dismiss
    initAlertAutoDismiss();
});

// Initialize animations for elements
function initAnimations() {
    const animatedElements = document.querySelectorAll('.animate-fade-in');

    // Create an observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    // Observe each element
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(element);
    });

    // Add animation to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        card.style.transitionDelay = `${index * 0.1}s`;

        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 300);
    });
}

// Enhance form elements
function enhanceForms() {
    // Add floating labels
    const formControls = document.querySelectorAll('.form-control');

    formControls.forEach(control => {
        control.addEventListener('focus', () => {
            control.parentElement.classList.add('focused');
        });

        control.addEventListener('blur', () => {
            if (control.value === '') {
                control.parentElement.classList.remove('focused');
            }
        });

        // Check if the input already has a value
        if (control.value !== '') {
            control.parentElement.classList.add('focused');
        }
    });

    // Add file input preview for image uploads
    const fileInputs = document.querySelectorAll('input[type="file"]');

    fileInputs.forEach(input => {
        input.addEventListener('change', function () {
            const preview = document.createElement('div');
            preview.className = 'file-preview mt-2';

            if (this.files && this.files[0]) {
                const reader = new FileReader();

                reader.onload = function (e) {
                    preview.innerHTML = `
                        <div class="file-preview-item">
                            <img src="${e.target.result}" alt="Preview" class="img-fluid rounded">
                        </div>
                    `;

                    // Add preview after the input
                    if (!input.nextElementSibling || !input.nextElementSibling.classList.contains('file-preview')) {
                        input.parentNode.insertBefore(preview, input.nextSibling);
                    } else {
                        input.parentNode.replaceChild(preview, input.nextElementSibling);
                    }
                }

                reader.readAsDataURL(this.files[0]);
            }
        });
    });
}

// Initialize Bootstrap tooltips and popovers
function initTooltips() {
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
}

// Add smooth scrolling to all links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const target = document.querySelector(targetId);
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Initialize profile card hover effects
function initProfileCardEffects() {
    const profileCards = document.querySelectorAll('.profile-card');

    profileCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            const img = card.querySelector('.profile-img');
            if (img) {
                img.style.transform = 'scale(1.05)';
            }
        });

        card.addEventListener('mouseleave', () => {
            const img = card.querySelector('.profile-img');
            if (img) {
                img.style.transform = 'scale(1)';
            }
        });
    });
}

// Initialize stat counter animations
function initStatCounters() {
    const statValues = document.querySelectorAll('.stat-value');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const targetValue = parseInt(target.getAttribute('data-target'), 10);

                if (!target.classList.contains('counted') && !isNaN(targetValue)) {
                    let currentValue = 0;
                    const duration = 1500;
                    const increment = Math.ceil(targetValue / (duration / 16));

                    const counter = setInterval(() => {
                        currentValue += increment;

                        if (currentValue >= targetValue) {
                            target.textContent = targetValue.toLocaleString();
                            target.classList.add('counted');
                            clearInterval(counter);
                        } else {
                            target.textContent = currentValue.toLocaleString();
                        }
                    }, 16);

                    observer.unobserve(target);
                }
            }
        });
    }, { threshold: 0.5 });

    statValues.forEach(value => {
        if (value.textContent) {
            value.setAttribute('data-target', value.textContent.replace(/,/g, ''));
            value.textContent = '0';
            observer.observe(value);
        }
    });
}

// Highlight current nav item based on URL
function highlightCurrentNavItem() {
    const currentPath = window.location.pathname;

    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        const linkPath = link.getAttribute('href');

        if (linkPath === currentPath ||
            (linkPath !== '/' && currentPath.startsWith(linkPath)) ||
            (linkPath === '/' && currentPath === '/')) {
            link.classList.add('active');
        }
    });
}

// Auto dismiss alerts after 5 seconds
function initAlertAutoDismiss() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');

    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
} 