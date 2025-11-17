// Auth container styles
document.addEventListener('DOMContentLoaded', function() {
    // Add auth container styles
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        /* Auth Form Styles */
        .auth-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .auth-form {
            background: #fff;
            padding: 2rem;
            border-radius: 10px;
            width: 90%;
            max-width: 400px;
            position: relative;
        }

        .auth-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .auth-close-button {
            position: absolute;
            right: -20px;
            background: none;
            border: none;
            color: #1a73e8;
            font-size: 0.9em;
            cursor: pointer;
            padding: 2px;
            opacity: 0.7;
            transition: opacity 0.3s ease;
            z-index: 1001;
        }

        .auth-close-button:hover {
            opacity: 1;
        }

        .auth-tabs {
            display: flex;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid #ddd;
        }

        .auth-tab {
            padding: 0.5rem 1rem;
            border: none;
            background: none;
            cursor: pointer;
            color: #666;
        }

        .auth-tab.active {
            color: #1a73e8;
            border-bottom: 2px solid #1a73e8;
        }

        .form-group {
            margin-bottom: 1rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
        }

        .form-group input {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        .login-button,
        .register-button {
            width: 100%;
            padding: 0.75rem;
            background: #1a73e8;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 1rem;
        }

        .login-button:hover,
        .register-button:hover {
            background: #1557b0;
        }

        /* Error and Success Message Styles */
        .login-email-error,
        .login-password-error,
        .register-name-error,
        .register-email-error,
        .register-password-error,
        .register-confirm-password-error {
            color: #dc3545;
            font-size: 0.875rem;
            margin-top: 0.25rem;
            display: none;
        }

        .login-success,
        .register-success {
            color: #28a745;
            font-size: 0.875rem;
            margin-top: 0.25rem;
            display: none;
            text-align: center;
            padding: 0.5rem;
            background-color: rgba(40, 167, 69, 0.1);
            border-radius: 4px;
        }

        .login-loading,
        .register-loading {
            display: none;
            width: 20px;
            height: 20px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #1a73e8;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 1rem auto;
        }

        .login-loading.active,
        .register-loading.active {
            display: block;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .login-form,
        .register-form {
            display: none;
        }

        .login-form.active,
        .register-form.active {
            display: block;
        }

        .auth-button-container {
            position: fixed;
            top: 8px;
            right: 8px;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .auth-button {
            padding: 4px 8px;
            font-size: 0.7em;
            background-color: transparent;
            color: #1a73e8;
            border: 1px solid #1a73e8;
            border-radius: 4px;
            cursor: pointer;
            max-width: 100px;
            transition: all 0.3s ease;
        }

        .auth-button:hover {
            background-color: rgba(26, 115, 232, 0.1);
        }

        @media (max-width: 767px) {
            .auth-container {
                padding: 10px;
            }

            .auth-form {
                width: 100%;
                padding: 1rem;
            }

            .auth-close-button {
                position: absolute;
                right: -20px;
                background: none;
                border: none;
                color: #1a73e8;
                font-size: 0.9em;
                cursor: pointer;
                padding: 2px;
                opacity: 0.7;
                transition: opacity 0.3s ease;
                z-index: 1001;
            }

            .auth-close-button:hover {
                opacity: 1;
            }

            .auth-button-container {
                position: fixed;
                top: 8px;
                right: 8px;
                z-index: 1000;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .auth-button {
                padding: 4px 8px;
                font-size: 0.7em;
                background-color: transparent;
                color: #1a73e8;
                border: 1px solid #1a73e8;
                border-radius: 4px;
                cursor: pointer;
                max-width: 100px;
                transition: all 0.3s ease;
            }

            .auth-button:hover {
                background-color: rgba(26, 115, 232, 0.1);
            }
        }
    `;
    document.head.appendChild(styleElement);
});

// Make toggleForms globally accessible
window.toggleForms = function() {
    const loginForm = document.querySelector('.login-form');
    const registerForm = document.querySelector('.register-form');
    const loginToggle = document.querySelector('.login-toggle');
    const registerToggle = document.querySelector('.register-toggle');

    if (loginForm && registerForm && loginToggle && registerToggle) {
        loginForm.classList.toggle('active');
        registerForm.classList.toggle('active');
        loginToggle.classList.toggle('active');
        registerToggle.classList.toggle('active');
    }
};

// Auth form functionality
window.initializeAuthForm = function() {
    console.log('=== initializeAuthForm() called ===');
    try {
        
        // Form Validation
        function showError(element, message) {
            if (!element) {
                console.error('showError called with null element, message:', message);
                return;
            }
            element.textContent = message;
            element.style.setProperty('display', 'block', 'important');
        }

        function hideError(element) {
            if (!element) return;
            element.textContent = '';
            element.style.setProperty('display', 'none', 'important');
        }

        function showSuccess(element, message) {
            if (!element) {
                console.error('showSuccess called with null element, message:', message);
                return;
            }
            element.textContent = message;
            element.style.setProperty('display', 'block', 'important');
        }

        function hideSuccess(element) {
            if (!element) return;
            element.textContent = '';
            element.style.setProperty('display', 'none', 'important');
        }

        function showLoading(element) {
            element.classList.add('active');
        }

        function hideLoading(element) {
            element.classList.remove('active');
        }

        // Login Form Handler
        console.log('Looking for login form...');
        const loginFormElement = document.querySelector('.login-form');
        console.log('Login form element found:', loginFormElement);
        if (loginFormElement) {
            console.log('Found login form, attaching handler...');
            console.log('Form parent:', loginFormElement.parentNode);
            console.log('Form HTML:', loginFormElement.outerHTML.substring(0, 200));
            // Remove any existing event listeners by cloning the form
            const newLoginForm = loginFormElement.cloneNode(true);
            // Ensure onsubmit prevents default submission
            newLoginForm.setAttribute('onsubmit', 'return false;');
            newLoginForm.setAttribute('action', 'javascript:void(0);');
            newLoginForm.setAttribute('method', 'post');
            loginFormElement.parentNode.replaceChild(newLoginForm, loginFormElement);
            
            // Add handler BEFORE any potential submission
            const submitHandler = async (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                console.log('Login form submitted - handler is working!');
                
                const email = document.getElementById('login-email')?.value;
                const password = document.getElementById('login-password')?.value;
                const loginButton = document.querySelector('.login-button');
                const loginLoading = document.querySelector('.login-loading');
                const loginSuccess = document.querySelector('.login-success');
                const loginEmailError = document.querySelector('.login-email-error');
                const loginPasswordError = document.querySelector('.login-password-error');

                // Reset errors and success messages
                hideError(loginEmailError);
                hideError(loginPasswordError);
                hideSuccess(loginSuccess);

                // Basic validation
                if (!email || !password) {
                    if (!email) showError(loginEmailError, 'Email is required');
                    if (!password) showError(loginPasswordError, 'Password is required');
                    return;
                }

                // Show loading state
                loginButton.disabled = true;
                showLoading(loginLoading);

                // Login with API
                try {
                    const response = await fetch('/api/v1/auth/teacher/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            email: email,
                            password: password
                        })
                    });

                    // Check if response is JSON
                    const contentType = response.headers.get('content-type');
                    let data;
                    
                    if (contentType && contentType.includes('application/json')) {
                        data = await response.json();
                    } else {
                        // Response is not JSON, get text instead
                        const text = await response.text();
                        console.error('Non-JSON response from login API:', text);
                        hideLoading(loginLoading);
                        loginButton.disabled = false;
                        showError(loginEmailError, 'Server error. Please try again later.');
                        return;
                    }

                    console.log('Login API response:', { 
                        status: response.status, 
                        ok: response.ok,
                        data: data,
                        hasAccessToken: !!data.access_token,
                        hasSuccess: !!data.success
                    });

                    if (response.ok && (data.success || data.access_token)) {
                        console.log('Login successful! Storing tokens and redirecting...');
                        hideLoading(loginLoading);
                        
                        // Store tokens and user data
                        if (data.access_token) {
                            localStorage.setItem('access_token', data.access_token);
                            console.log('Access token stored');
                        }
                        if (data.refresh_token) {
                            localStorage.setItem('refresh_token', data.refresh_token);
                        }
                        if (data.teacher_id) {
                            localStorage.setItem('teacher_id', data.teacher_id);
                        }
                        if (data.email) {
                            localStorage.setItem('user_email', data.email);
                        }
                        
                        showSuccess(loginSuccess, data.message || 'Login successful! Redirecting...');
                        
                        // Clear form
                        const emailInput = document.getElementById('login-email');
                        const passwordInput = document.getElementById('login-password');
                        if (emailInput) emailInput.value = '';
                        if (passwordInput) passwordInput.value = '';
                        
                        // Update auth button to show logout
                        updateAuthButton();
                        
                        // Redirect to dashboard after a short delay
                        console.log('Scheduling redirect to dashboard...');
                        setTimeout(() => {
                            console.log('Redirecting to dashboard now...');
                            closeAuthForm();
                            // Force redirect - use replace to prevent back button issues
                            window.location.replace('/dashboard');
                        }, 1500);
                    } else {
                        console.error('Login failed - response not ok or missing token:', {
                            ok: response.ok,
                            status: response.status,
                            hasAccessToken: !!data.access_token,
                            hasSuccess: !!data.success,
                            data: data
                        });
                        hideLoading(loginLoading);
                        loginButton.disabled = false;
                        const errorMsg = data.detail || data.message || 'Login failed. Please check your credentials and try again.';
                        console.error('Login failed:', errorMsg);
                        
                        // Ensure error elements exist
                        if (!loginEmailError) {
                            console.error('loginEmailError element not found!');
                        }
                        if (!loginPasswordError) {
                            console.error('loginPasswordError element not found!');
                        }
                        
                        if (errorMsg.toLowerCase().includes('email') || errorMsg.toLowerCase().includes('not verified')) {
                            showError(loginEmailError, errorMsg);
                        } else if (errorMsg.toLowerCase().includes('password')) {
                            showError(loginPasswordError, errorMsg);
                        } else {
                            showError(loginEmailError, errorMsg);
                        }
                    }
                } catch (error) {
                    hideLoading(loginLoading);
                    loginButton.disabled = false;
                    console.error('Login error:', error);
                    showError(loginEmailError, 'Network error. Please check your connection and try again.');
                }
            };
            
            // Attach the handler
            newLoginForm.addEventListener('submit', submitHandler);
            console.log('Login form submit handler attached successfully');
            
            // Also prevent submission via button click (defensive)
            const loginButton = newLoginForm.querySelector('.login-button');
            if (loginButton) {
                loginButton.addEventListener('click', function(e) {
                    // Don't prevent default here - let the form submit event handle it
                    // But log to verify button click is working
                    console.log('Login button clicked');
                });
            }
        } else {
            console.error('Login form element not found!');
        }

        // Registration Form Handler
        const registerFormElement = document.querySelector('.register-form');
        if (registerFormElement) {
            // Remove any existing event listeners by cloning the form
            const newRegisterForm = registerFormElement.cloneNode(true);
            // Ensure onsubmit prevents default submission
            newRegisterForm.setAttribute('onsubmit', 'return false;');
            registerFormElement.parentNode.replaceChild(newRegisterForm, registerFormElement);
            
            newRegisterForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const name = document.getElementById('register-name').value;
                const email = document.getElementById('register-email').value;
                const password = document.getElementById('register-password').value;
                const confirmPassword = document.getElementById('register-confirm-password').value;
                
                const registerButton = document.querySelector('.register-button');
                const registerLoading = document.querySelector('.register-loading');
                const registerSuccess = document.querySelector('.register-success');
                const registerNameError = document.querySelector('.register-name-error');
                const registerEmailError = document.querySelector('.register-email-error');
                const registerPasswordError = document.querySelector('.register-password-error');
                const registerConfirmPasswordError = document.querySelector('.register-confirm-password-error');

                // Reset errors and success messages
                hideError(registerNameError);
                hideError(registerEmailError);
                hideError(registerPasswordError);
                hideError(registerConfirmPasswordError);
                hideSuccess(registerSuccess);

                // Basic validation
                if (!name || !email || !password || !confirmPassword) {
                    if (!name) showError(registerNameError, 'Name is required');
                    if (!email) showError(registerEmailError, 'Email is required');
                    if (!password) showError(registerPasswordError, 'Password is required');
                    if (!confirmPassword) showError(registerConfirmPasswordError, 'Please confirm your password');
                    return;
                }

                if (password !== confirmPassword) {
                    showError(registerConfirmPasswordError, 'Passwords do not match');
                    return;
                }

                // Parse name into first and last name
                const nameParts = name.trim().split(/\s+/);
                const firstName = nameParts[0] || '';
                const lastName = nameParts.slice(1).join(' ') || '';

                // Show loading state
                registerButton.disabled = true;
                showLoading(registerLoading);

                // Register with API
                try {
                    const response = await fetch('/api/v1/auth/teacher/register', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            email: email,
                            password: password,
                            first_name: firstName,
                            last_name: lastName
                        })
                    });

                    const data = await response.json();

                    if (response.ok) {
                        hideLoading(registerLoading);
                        showSuccess(registerSuccess, data.message || 'Registration successful! Please check your email to verify your account.');
                        // Clear form
                        document.getElementById('register-name').value = '';
                        document.getElementById('register-email').value = '';
                        document.getElementById('register-password').value = '';
                        document.getElementById('register-confirm-password').value = '';
                        
                        // Switch to login form after a short delay
                        setTimeout(() => {
                            // Switch to login tab
                            const loginToggle = document.querySelector('.login-toggle');
                            const registerToggle = document.querySelector('.register-toggle');
                            const loginForm = document.querySelector('.login-form');
                            const registerForm = document.querySelector('.register-form');
                            
                            if (loginToggle && registerToggle && loginForm && registerForm) {
                                loginForm.classList.add('active');
                                registerForm.classList.remove('active');
                                loginToggle.classList.add('active');
                                registerToggle.classList.remove('active');
                            }
                            
                            // Pre-fill email in login form
                            const loginEmailInput = document.getElementById('login-email');
                            if (loginEmailInput) {
                                loginEmailInput.value = email;
                            }
                        }, 2000);
                    } else {
                        hideLoading(registerLoading);
                        registerButton.disabled = false;
                        const errorMsg = data.detail || data.message || 'Registration failed. Please try again.';
                        if (errorMsg.toLowerCase().includes('email')) {
                            showError(registerEmailError, errorMsg);
                        } else if (errorMsg.toLowerCase().includes('password')) {
                            showError(registerPasswordError, errorMsg);
                        } else {
                            showError(registerNameError, errorMsg);
                        }
                    }
                } catch (error) {
                    hideLoading(registerLoading);
                    registerButton.disabled = false;
                    showError(registerNameError, 'Network error. Please check your connection and try again.');
                    console.error('Registration error:', error);
                }
            });
        }

        // Add click outside to close
        document.addEventListener('click', (e) => {
            const authContainer = document.getElementById('auth-container');
            if (e.target === authContainer) {
                closeAuthForm();
            }
        });
        
        // Ensure close button works (add event listener after form is cloned)
        // Use setTimeout to ensure this runs after all DOM manipulation
        setTimeout(function() {
            const closeButton = document.querySelector('.auth-close-button');
            if (closeButton) {
                console.log('Close button found, attaching handlers...');
                // Remove existing onclick and all event listeners by cloning
                const newCloseButton = closeButton.cloneNode(true);
                closeButton.parentNode.replaceChild(newCloseButton, closeButton);
                
                // Add multiple event listeners to ensure it works
                const closeHandler = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Close button clicked!');
                    if (typeof window.closeAuthForm === 'function') {
                        window.closeAuthForm();
                    } else {
                        console.error('closeAuthForm function not available!');
                        // Fallback: hide the container directly
                        const container = document.getElementById('auth-container') || document.querySelector('.auth-container');
                        if (container) {
                            // Disconnect observer if exists
                            if (container._displayObserver) {
                                container._displayObserver.disconnect();
                                delete container._displayObserver;
                            }
                            container.style.setProperty('display', 'none', 'important');
                            container.classList.remove('active', 'show');
                            document.body.style.overflow = 'auto';
                        }
                    }
                    return false;
                };
                
                // Add click listener with capture phase
                newCloseButton.addEventListener('click', closeHandler, true);
                // Add click listener with bubble phase
                newCloseButton.addEventListener('click', closeHandler, false);
                // Add mousedown as backup
                newCloseButton.addEventListener('mousedown', closeHandler, true);
                // Set onclick as final fallback
                newCloseButton.setAttribute('onclick', 'event.preventDefault(); event.stopPropagation(); if(typeof window.closeAuthForm === "function") { window.closeAuthForm(); } else { const c = document.getElementById("auth-container") || document.querySelector(".auth-container"); if(c) { if(c._displayObserver) { c._displayObserver.disconnect(); delete c._displayObserver; } c.style.setProperty("display", "none", "important"); c.classList.remove("active", "show"); document.body.style.overflow = "auto"; } } return false;');
                
                console.log('Close button handlers attached (multiple methods)');
            } else {
                console.error('Close button not found after DOM manipulation!');
            }
        }, 150);
        
        console.log('=== initializeAuthForm() completed successfully ===');
    } catch (error) {
        console.error('ERROR in initializeAuthForm():', error);
        console.error('Error stack:', error.stack);
    }
};

// Show auth form - only define if not already defined (e.g., by index.html)
if (typeof window.showAuthForm !== 'function') {
    window.showAuthForm = function() {
        console.log('showAuthForm() called from auth.js');
        const authContainer = document.getElementById('auth-container');
        if (authContainer) {
            // Check if form is already embedded
            const hasEmbeddedForm = authContainer.querySelector('.login-form');
            
            if (hasEmbeddedForm) {
                // Form is already embedded, just show it
                console.log('auth.js - Form is embedded, showing container');
                requestAnimationFrame(function() {
                    authContainer.style.setProperty('display', 'flex', 'important');
                    authContainer.classList.add('active', 'show');
                    document.body.style.overflow = 'hidden';
                    console.log('auth.js - Container display set to flex, computed:', window.getComputedStyle(authContainer).display);
                    
                    // Attach MutationObserver to prevent display: block
                    if (!authContainer._displayObserver) {
                        const observer = new MutationObserver(function(mutations) {
                            mutations.forEach(function(mutation) {
                                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                                    const currentDisplay = authContainer.style.display;
                                    if (currentDisplay === 'block') {
                                        console.log('auth.js MutationObserver: Preventing display:block, forcing display:flex');
                                        authContainer.style.setProperty('display', 'flex', 'important');
                                    }
                                }
                            });
                        });
                        observer.observe(authContainer, { attributes: true, attributeFilter: ['style'] });
                        authContainer._displayObserver = observer;
                        console.log('auth.js - MutationObserver attached');
                    }
                    
                    // Initialize the auth form handlers
                    if (typeof window.initializeAuthForm === 'function') {
                        window.initializeAuthForm();
                    }
                });
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
                        if (typeof window.initializeAuthForm === 'function') {
                            window.initializeAuthForm();
                        }
                    })
                    .catch(error => console.error('Error loading auth form:', error));
            }
        }
    };
}

// Close auth form - only define if not already defined (e.g., by index.html)
if (typeof window.closeAuthForm !== 'function') {
    window.closeAuthForm = function() {
        console.log('=== closeAuthForm() called ===');
        const authContainer = document.getElementById('auth-container') || document.querySelector('.auth-container');
        console.log('closeAuthForm - Container found:', !!authContainer);
        if (authContainer) {
            console.log('closeAuthForm - Current display:', window.getComputedStyle(authContainer).display);
            console.log('closeAuthForm - Current classes:', authContainer.className);
            
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

// Check if user is logged in
function isLoggedIn() {
    return !!localStorage.getItem('access_token');
}

// Update auth button based on login status
function updateAuthButton() {
    const authButton = document.querySelector('.auth-button');
    if (!authButton) return;
    
    if (isLoggedIn()) {
        authButton.textContent = 'Logout';
        authButton.onclick = logout;
    } else {
        authButton.textContent = 'Login / Register';
        authButton.onclick = showAuthForm;
    }
}

// Logout function
window.logout = function() {
    // Clear all auth data from localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('teacher_id');
    localStorage.removeItem('user_email');
    
    // Update auth button
    updateAuthButton();
    
    // If on dashboard, redirect to homepage
    if (window.location.pathname === '/dashboard' || window.location.pathname.startsWith('/dashboard/')) {
        window.location.href = '/';
    }
};

// Initialize auth button on page load
document.addEventListener('DOMContentLoaded', function() {
    updateAuthButton();
}); 