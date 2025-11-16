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
    // Form Validation
    function showError(element, message) {
        element.textContent = message;
        element.style.display = 'block';
    }

    function hideError(element) {
        element.textContent = '';
        element.style.display = 'none';
    }

    function showSuccess(element, message) {
        element.textContent = message;
        element.style.display = 'block';
    }

    function hideSuccess(element) {
        element.textContent = '';
        element.style.display = 'none';
    }

    function showLoading(element) {
        element.classList.add('active');
    }

    function hideLoading(element) {
        element.classList.remove('active');
    }

    // Login Form Handler
    const loginFormElement = document.querySelector('.login-form');
    if (loginFormElement) {
        loginFormElement.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;
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

                const data = await response.json();

                if (response.ok && (data.success || data.access_token)) {
                    hideLoading(loginLoading);
                    
                    // Store tokens and user data
                    if (data.access_token) {
                        localStorage.setItem('access_token', data.access_token);
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
                    document.getElementById('login-email').value = '';
                    document.getElementById('login-password').value = '';
                    
                    // Update auth button to show logout
                    updateAuthButton();
                    
                    // Redirect to dashboard after a short delay
                    setTimeout(() => {
                        closeAuthForm();
                        // Force redirect - use replace to prevent back button issues
                        window.location.replace('/dashboard');
                    }, 1500);
                } else {
                    hideLoading(loginLoading);
                    loginButton.disabled = false;
                    const errorMsg = data.detail || data.message || 'Login failed. Please check your credentials and try again.';
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
                showError(loginEmailError, 'Network error. Please check your connection and try again.');
                console.error('Login error:', error);
            }
        });
    }

    // Registration Form Handler
    const registerFormElement = document.querySelector('.register-form');
    if (registerFormElement) {
        registerFormElement.addEventListener('submit', async (e) => {
            e.preventDefault();
            
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
};

// Show auth form
window.showAuthForm = function() {
    const authContainer = document.getElementById('auth-container');
    authContainer.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Load auth form content
    fetch('/static/auth-form.html')
        .then(response => response.text())
        .then(html => {
            authContainer.innerHTML = html;
            initializeAuthForm();
        })
        .catch(error => console.error('Error loading auth form:', error));
};

// Close auth form
window.closeAuthForm = function() {
    const authContainer = document.getElementById('auth-container');
    authContainer.style.display = 'none';
    document.body.style.overflow = 'auto';
};

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