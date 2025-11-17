// Authentication Form Handling
// Use global functions from auth.js
// Check if showAuthForm is already defined (e.g., by index.html for embedded forms)
if (typeof window.showAuthForm !== 'function') {
    window.showAuthForm = function() {
        console.log('showAuthForm() called from services.js');
        const authContainer = document.getElementById('auth-container');
        if (!authContainer) {
            // Create auth container if it doesn't exist
            const container = document.createElement('div');
            container.id = 'auth-container';
            container.className = 'auth-container';
            document.body.appendChild(container);
        }
        
        // Check if form is already embedded (has .login-form inside)
        const hasEmbeddedForm = authContainer.querySelector('.login-form');
        
        if (hasEmbeddedForm) {
            // Form is already embedded, just show it
            console.log('services.js - Form is embedded, showing container');
            // Use requestAnimationFrame to ensure this runs after any other style changes
            requestAnimationFrame(function() {
                authContainer.style.setProperty('display', 'flex', 'important');
                authContainer.classList.add('active', 'show');
                document.body.style.overflow = 'hidden';
                console.log('services.js - Container display set to flex, computed:', window.getComputedStyle(authContainer).display);
                
                // Attach MutationObserver to prevent display: block (but allow display: none)
                if (!authContainer._displayObserver) {
                    const observer = new MutationObserver(function(mutations) {
                        mutations.forEach(function(mutation) {
                            if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                                const currentDisplay = authContainer.style.display;
                                // Only prevent display: block, allow display: none for closing
                                if (currentDisplay === 'block') {
                                    console.log('services.js MutationObserver: Preventing display:block, forcing display:flex');
                                    authContainer.style.setProperty('display', 'flex', 'important');
                                } else if (currentDisplay === 'none') {
                                    // Allow display: none (for closing) - don't interfere
                                    console.log('services.js MutationObserver: Allowing display:none (closing)');
                                }
                            }
                        });
                    });
                    observer.observe(authContainer, { attributes: true, attributeFilter: ['style'] });
                    authContainer._displayObserver = observer;
                    console.log('services.js - MutationObserver attached');
                }
            });
            // Initialize the auth form handlers
            if (typeof window.initializeAuthForm === 'function') {
                window.initializeAuthForm();
            }
        } else {
            // Form not embedded, load it dynamically
            authContainer.style.setProperty('display', 'flex', 'important');
            authContainer.classList.add('active', 'show');
            document.body.style.overflow = 'hidden';
            
            // Load auth form content
            fetch('/static/auth-form.html')
                .then(response => response.text())
                .then(html => {
                    authContainer.innerHTML = html;
                    // Initialize the auth form
                    if (typeof window.initializeAuthForm === 'function') {
                        window.initializeAuthForm();
                    }
                    // Show login form by default
                    const loginForm = document.querySelector('.login-form');
                    const registerForm = document.querySelector('.register-form');
                    const loginToggle = document.querySelector('.login-toggle');
                    const registerToggle = document.querySelector('.register-toggle');
                    
                    if (loginForm && registerForm && loginToggle && registerToggle) {
                        loginForm.classList.add('active');
                        registerForm.classList.remove('active');
                        loginToggle.classList.add('active');
                        registerToggle.classList.remove('active');
                    }
                })
                .catch(error => console.error('Error loading auth form:', error));
        }
    };
}

// Check if closeAuthForm is already defined
if (typeof window.closeAuthForm !== 'function') {
    window.closeAuthForm = function() {
        console.log('=== closeAuthForm() called from services.js ===');
        const authContainer = document.getElementById('auth-container') || document.querySelector('.auth-container');
        console.log('closeAuthForm - Container found:', !!authContainer);
        if (authContainer) {
            console.log('closeAuthForm - Current display:', window.getComputedStyle(authContainer).display);
            
            // Disconnect ALL observers if they exist
            if (authContainer._displayObserver) {
                console.log('closeAuthForm - Disconnecting MutationObserver...');
                authContainer._displayObserver.disconnect();
                delete authContainer._displayObserver;
                console.log('closeAuthForm - MutationObserver disconnected');
            }
            
            // Remove all classes
            authContainer.classList.remove('active', 'show');
            console.log('closeAuthForm - Classes removed');
            
            // Force display: none with multiple methods
            authContainer.style.removeProperty('display');
            authContainer.style.setProperty('display', 'none', 'important');
            console.log('closeAuthForm - Display set to none');
            
            // Also set via setAttribute as backup
            authContainer.setAttribute('style', 'display: none !important;');
            console.log('closeAuthForm - Display set via setAttribute');
            
            // Restore body overflow
            document.body.style.overflow = 'auto';
            console.log('closeAuthForm - Body overflow restored');
            
            // Verify it's hidden
            const computedDisplay = window.getComputedStyle(authContainer).display;
            console.log('closeAuthForm - Final computed display:', computedDisplay);
            
            if (computedDisplay !== 'none') {
                console.error('closeAuthForm - WARNING: Container still visible! Forcing again...');
                // Last resort: remove from DOM temporarily
                const parent = authContainer.parentNode;
                if (parent) {
                    parent.removeChild(authContainer);
                    setTimeout(function() {
                        parent.appendChild(authContainer);
                        authContainer.style.setProperty('display', 'none', 'important');
                    }, 10);
                }
            } else {
                console.log('closeAuthForm - ✅ Container successfully hidden');
            }
        } else {
            console.error('closeAuthForm - ❌ Auth container not found!');
        }
        console.log('=== closeAuthForm() completed ===');
    };
}

// Close auth form when clicking outside
document.addEventListener('click', (e) => {
    const authContainer = document.getElementById('auth-container');
    if (authContainer && e.target === authContainer) {
        closeAuthForm();
    }
});

// Smooth Scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Code Example Copying
document.querySelectorAll('.code-examples pre code').forEach(block => {
    const copyButton = document.createElement('button');
    copyButton.className = 'copy-button';
    copyButton.textContent = 'Copy';
    
    copyButton.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(block.textContent);
            copyButton.textContent = 'Copied!';
            setTimeout(() => {
                copyButton.textContent = 'Copy';
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
            copyButton.textContent = 'Failed to copy';
        }
    });
    
    block.parentNode.insertBefore(copyButton, block);
});

// Feature Cards Animation and Navigation
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Handle back button navigation first
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.back-button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const href = this.getAttribute('href');
            if (href) {
                window.location.href = href;
            }
        }, true); // Use capture phase to ensure this runs first
    });
});

// Handle feature card clicks
document.querySelectorAll('.feature-card').forEach(card => {
    observer.observe(card);
    
    card.addEventListener('click', function(e) {
        // Don't navigate if clicking on the link itself
        if (e.target.tagName === 'A') {
            return;
        }
        
        const href = this.getAttribute('data-href');
        if (href) {
            window.location.href = href;
        }
    });
});

// Handle smooth scrolling for anchor links
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

// Mobile Navigation
const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
const mobileNav = document.querySelector('.mobile-nav');

if (mobileNavToggle && mobileNav) {
    mobileNavToggle.addEventListener('click', () => {
        mobileNav.classList.toggle('active');
        mobileNavToggle.setAttribute('aria-expanded', 
            mobileNav.classList.contains('active'));
    });
}

// Form Validation
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('error');
        } else {
            input.classList.remove('error');
        }
    });

    return isValid;
}

// API Integration Example
async function fetchServiceData(serviceId) {
    try {
        const response = await fetch(`/api/services/${serviceId}`);
        if (!response.ok) throw new Error('Failed to fetch service data');
        return await response.json();
    } catch (error) {
        console.error('Error fetching service data:', error);
        return null;
    }
}

// Service Status Check
async function checkServiceStatus() {
    const serviceType = document.body.getAttribute('data-service');
    if (!serviceType) return;

    try {
        const response = await fetch(`/api/services/${serviceType}/status`);
        if (!response.ok) throw new Error('Failed to fetch service status');
        const data = await response.json();
        updateServiceStatus(data);
    } catch (error) {
        console.error('Error checking service status:', error);
    }
}

function updateServiceStatus(data) {
    const statusIndicator = document.querySelector('.service-status');
    if (statusIndicator) {
        statusIndicator.className = `service-status ${data.status}`;
        statusIndicator.setAttribute('aria-label', `Service status: ${data.status}`);
        statusIndicator.textContent = `Status: ${data.status.charAt(0).toUpperCase() + data.status.slice(1)}`;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Add loading state to buttons
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.addEventListener('click', () => {
            if (button.form && validateForm(button.form)) {
                button.classList.add('loading');
            }
        });
    });

    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', (e) => {
            const text = e.target.getAttribute('data-tooltip');
            const tooltipEl = document.createElement('div');
            tooltipEl.className = 'tooltip';
            tooltipEl.textContent = text;
            document.body.appendChild(tooltipEl);

            const rect = e.target.getBoundingClientRect();
            tooltipEl.style.top = `${rect.top - tooltipEl.offsetHeight - 10}px`;
            tooltipEl.style.left = `${rect.left + (rect.width - tooltipEl.offsetWidth) / 2}px`;
        });

        tooltip.addEventListener('mouseleave', () => {
            const tooltipEl = document.querySelector('.tooltip');
            if (tooltipEl) {
                tooltipEl.remove();
            }
        });
    });
});

// Initialize service page
document.addEventListener('DOMContentLoaded', () => {
    // Add loading states to buttons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            button.classList.add('loading');
            setTimeout(() => button.classList.remove('loading'), 1000);
        });
    });

    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });

    // Feature Cards Animation
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card, .use-case-card').forEach(card => {
        observer.observe(card);
    });
});

// Show tooltip
function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = this.getAttribute('data-tooltip');
    document.body.appendChild(tooltip);

    const rect = this.getBoundingClientRect();
    tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
    tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;
}

// Hide tooltip
function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Handle service status check
async function checkServiceStatus() {
    const serviceType = document.body.getAttribute('data-service');
    if (!serviceType) return;

    try {
        const response = await fetch(`/api/services/${serviceType}/status`);
        if (!response.ok) throw new Error('Failed to fetch service status');
        const data = await response.json();
        updateServiceStatus(data);
    } catch (error) {
        console.error('Error checking service status:', error);
    }
}

// Set up feature card animations
function setupFeatureCardAnimations() {
    const featureCards = document.querySelectorAll('.feature-card, .detail-card, .example-card');
    
    // Add animation on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    featureCards.forEach(card => {
        observer.observe(card);
        
        // Enhance click behavior
        card.addEventListener('click', function(e) {
            // Get the URL from the onclick attribute or data attribute
            let url;
            if (this.hasAttribute('onclick')) {
                const onclickAttr = this.getAttribute('onclick');
                const match = onclickAttr.match(/window\.location\.href=['"]([^'"]+)['"]/);
                url = match ? match[1] : null;
            } else if (this.hasAttribute('data-href')) {
                url = this.getAttribute('data-href');
            }
            
            if (url) {
                // Add active state animation
                this.classList.add('active');
                
                // Navigate after a small delay to show the animation
                setTimeout(() => {
                    window.location.href = url;
                }, 150);
                
                e.preventDefault();
            }
        });
    });
    
    // Make cards accessible with keyboard
    featureCards.forEach(card => {
        // Add tabindex if not already present
        if (!card.hasAttribute('tabindex')) {
            card.setAttribute('tabindex', '0');
        }
        
        // Handle keyboard events
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
}

// Define service endpoints for API calls
const SERVICE_ENDPOINTS = {
    'phys-ed': '/services/phys-ed',
    'history': '/services/history',
    'math': '/services/math',
    'collaboration': '/services/collaboration',
    'memory': '/services/memory',
    'study': '/services/study',
    'writing': '/services/writing',
    'language': '/services/language',
    'translation': '/services/translation',
    'document-management': '/services/document-management',
    'lesson-planning': '/services/lesson-planning',
    'resource-management': '/services/resource-management'
};

// Handle service button clicks
document.querySelectorAll('.feature-button').forEach(button => {
    button.addEventListener('click', async (e) => {
        const serviceType = e.currentTarget.dataset.service;
        if (serviceType && SERVICE_ENDPOINTS[serviceType]) {
            window.location.href = SERVICE_ENDPOINTS[serviceType];
        }
    });
});

// Remove all previous navigation handlers and keep only this one
document.addEventListener('DOMContentLoaded', function() {
    // Handle all card clicks
    const cards = document.querySelectorAll('.feature-card, .spec-card, .detail-card, .benefit-card, .example-card');
    
    cards.forEach(card => {
        // Add click handler
        card.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('data-href');
            if (href) {
                // Ensure the path ends with .html
                let finalHref = href.endsWith('.html') ? href : href + '.html';
                console.log('Navigating to:', finalHref);
                window.location.href = finalHref;
            }
        });

        // Add keyboard navigation
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const href = this.getAttribute('data-href');
                if (href) {
                    // Ensure the path ends with .html
                    let finalHref = href.endsWith('.html') ? href : href + '.html';
                    window.location.href = finalHref;
                }
            }
        });
    });

    // Handle smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Setup navigation for feature cards
function setupNavigation() {
    // Handle smooth scrolling for anchor links
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

// URL Hash State Management
function handleHashState() {
    const hash = window.location.hash;
    if (hash === '#additional-services') {
        const additionalServices = document.querySelector('.service-category');
        if (additionalServices) {
            additionalServices.classList.add('active');
        }
    }
}

// Update hash when Additional Services is toggled
function updateHashState(isOpen) {
    if (isOpen) {
        window.location.hash = '#additional-services';
    } else if (window.location.hash === '#additional-services') {
        history.replaceState('', document.title, window.location.pathname);
    }
}

// Initialize hash state on page load
document.addEventListener('DOMContentLoaded', () => {
    handleHashState();
    
    // Add hash state management to Additional Services toggle
    const additionalServicesToggle = document.querySelector('.category-button');
    if (additionalServicesToggle) {
        additionalServicesToggle.addEventListener('click', () => {
            const additionalServices = document.querySelector('.service-category');
            if (additionalServices) {
                const isOpen = additionalServices.classList.contains('active');
                updateHashState(isOpen);
            }
        });
    }
}); 