// Dashboard JavaScript
// Main dashboard functionality and API integration

const API_BASE_URL = '/api/v1';
let currentUser = null;
let chatHistory = [];
let activeWidgets = [];
let isVoiceActive = false;
let recognition = null;
let microphoneStream = null; // Keep track of the microphone stream
let mediaRecorder = null; // For Safari: MediaRecorder instance
let isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent); // Detect Safari
let errorCount = 0; // Track consecutive errors to prevent loops
let logEntries = []; // Store log entries for the log viewer
let originalConsole = {
    log: console.log,
    error: console.error,
    warn: console.warn,
    info: console.info,
    debug: console.debug
};

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (microphoneStream) {
        stopMicrophoneStream();
    }
    if (recognition && isVoiceActive) {
        recognition.stop();
    }
});

// Initialize dashboard
async function initializeDashboard() {
    try {
        // Check authentication
        const token = localStorage.getItem('access_token');
        if (!token) {
            showLoginOverlay();
            return;
        }

        // Load user info (don't fail if this errors - token exists so user is authenticated)
        try {
            await loadUserInfo();
        } catch (userInfoError) {
            console.warn('Could not load user info, but token exists. Using token data:', userInfoError);
            // Extract email from token as fallback
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                const email = payload.email || 'User';
                const userNameEl = document.getElementById('userName');
                if (userNameEl) {
                    userNameEl.textContent = email;
                }
            } catch (e) {
                console.warn('Could not decode token:', e);
            }
        }
        
        // Load dashboard state
        await loadDashboardState();
        
        // Setup event listeners
        setupEventListeners();
        
        // Initialize voice recognition if available
        initializeVoiceRecognition();
        
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        // Only show login overlay if there's no token
        const token = localStorage.getItem('access_token');
        if (!token) {
            showLoginOverlay();
        } else {
            // Token exists but something else failed - show error but don't force login
            showError('Failed to load dashboard. Please try refreshing the page.');
        }
    }
}

// Show login overlay
function showLoginOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'loginOverlay';
    overlay.className = 'login-overlay';
    overlay.innerHTML = `
        <div class="login-overlay-content">
            <h2>Welcome to Faraday AI Dashboard</h2>
            <p>Please log in to access your dashboard</p>
            <div class="login-buttons">
                <button class="btn-primary" onclick="window.location.href='/login'">Go to Login</button>
                <button class="btn-secondary" onclick="hideLoginOverlay()">Continue as Guest (Limited)</button>
            </div>
            <div class="login-back-buttons">
                <a href="/" class="back-nav-btn">← Back to Home</a>
                <a href="/static/services/teacher-admin.html" class="back-nav-btn">← Back to Teachers</a>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
}

// Hide login overlay
function hideLoginOverlay() {
    const overlay = document.getElementById('loginOverlay');
    if (overlay) {
        overlay.remove();
    }
    // Allow limited guest access
    setupEventListeners();
    initializeVoiceRecognition();
    // Show a message that features are limited
    addMessageToChat('ai', 'Welcome! You\'re viewing the dashboard in guest mode. Some features may be limited. Please log in for full access.');
}

// Load user information
async function loadUserInfo() {
    try {
        const token = localStorage.getItem('access_token');
        if (!token) {
            document.getElementById('userName').textContent = 'Guest';
            return;
        }
        
        // Check if token is for a teacher (has type: "teacher" in payload)
        let isTeacher = false;
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            isTeacher = payload.type === 'teacher';
        } catch (e) {
            // If we can't decode, try both endpoints
        }
        
        // Try teacher endpoint first if token indicates teacher, otherwise try both
        let response;
        let endpoint = isTeacher ? `${API_BASE_URL}/auth/teacher/me` : `${API_BASE_URL}/users/me`;
        
        try {
            response = await fetch(endpoint, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            // If teacher endpoint fails and we haven't tried users endpoint, try that
            if (!response.ok && isTeacher) {
                response = await fetch(`${API_BASE_URL}/users/me`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
            }
        } catch (fetchError) {
            // If first attempt fails, try the other endpoint
            if (isTeacher) {
                response = await fetch(`${API_BASE_URL}/users/me`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
            } else {
                response = await fetch(`${API_BASE_URL}/auth/teacher/me`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
            }
        }
        
        if (!response.ok) {
            throw new Error('Failed to load user info');
        }
        
        currentUser = await response.json();
        // Handle both teacher and user response formats
        const email = currentUser.email || currentUser.user?.email;
        const name = currentUser.first_name ? `${currentUser.first_name} ${currentUser.last_name || ''}`.trim() : email;
        document.getElementById('userName').textContent = name || email || 'User';
    } catch (error) {
        console.error('Error loading user info:', error);
        // Fallback to email from token if available
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                const email = payload.email || 'User';
                document.getElementById('userName').textContent = email;
            } catch (e) {
                document.getElementById('userName').textContent = 'Guest';
            }
        } else {
            document.getElementById('userName').textContent = 'Guest';
        }
    }
}

// Load dashboard state
async function loadDashboardState() {
    try {
        const token = localStorage.getItem('access_token');
        
        // Try to load from localStorage first (works for both guest and authenticated)
        if (loadWidgetsFromLocalStorage() && activeWidgets.length > 0) {
            renderWidgets();
        }
        
        if (!token) {
            // Guest mode - if no saved widgets, show empty dashboard
            if (activeWidgets.length === 0) {
                renderWidgets();
            }
            return;
        }
        
        // For authenticated users, try to load from API
        const response = await fetch(`${API_BASE_URL}/dashboard/state`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            // If dashboard not initialized, initialize it
            if (response.status === 404) {
                await initializeDashboardState();
                return;
            }
            // If API fails but we have local widgets, use those
            if (activeWidgets.length > 0) {
                renderWidgets();
                return;
            }
            throw new Error('Failed to load dashboard state');
        }
        
        const state = await response.json();
        
        // Load widgets from API (merge with local if needed)
        if (state.widgets && state.widgets.length > 0) {
            activeWidgets = state.widgets;
            saveWidgetsToLocalStorage();
            renderWidgets();
        } else if (activeWidgets.length === 0) {
            renderWidgets();
        }
        
        // Load chat history if available
        if (state.chat_history) {
            chatHistory = state.chat_history;
            renderChatHistory();
        }
        
    } catch (error) {
        console.error('Error loading dashboard state:', error);
        // If we have local widgets, use those
        if (activeWidgets.length > 0) {
            renderWidgets();
        } else {
            // Initialize default dashboard (only if authenticated)
            const token = localStorage.getItem('access_token');
            if (token) {
                await initializeDashboardState();
            } else {
                renderWidgets();
            }
        }
    }
}

// Initialize dashboard state
async function initializeDashboardState() {
    try {
        const response = await fetch(`${API_BASE_URL}/dashboard/initialize`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to initialize dashboard');
        }
        
        const result = await response.json();
        console.log('Dashboard initialized:', result);
    } catch (error) {
        console.error('Error initializing dashboard:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Chat input
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    chatInput.addEventListener('input', () => {
        // Auto-resize textarea
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });
    
    sendBtn.addEventListener('click', sendMessage);
    
    // Voice toggle
    document.getElementById('voiceToggle').addEventListener('click', toggleVoiceInput);
    
    // Clear chat
    document.getElementById('clearChat').addEventListener('click', clearChat);
    
    // Settings
    document.getElementById('settingsBtn').addEventListener('click', openSettings);
    document.getElementById('closeSettingsModal').addEventListener('click', closeSettings);
    document.getElementById('saveSettings').addEventListener('click', saveSettings);
    document.getElementById('cancelSettings').addEventListener('click', closeSettings);
    
    // Logout
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    // Sidebar toggle
    document.getElementById('toggleSidebar').addEventListener('click', toggleSidebar);
    
    // Floating sidebar toggle (when sidebar is collapsed)
    document.getElementById('floatingSidebarToggle').addEventListener('click', toggleSidebar);
    
    // Widget items
    document.querySelectorAll('.widget-item').forEach(item => {
        item.addEventListener('click', () => {
            const widgetType = item.dataset.widget;
            addWidget(widgetType);
        });
    });
    
    // Widget controls
    document.getElementById('addWidgetBtn').addEventListener('click', () => {
        // Show widget selection
        alert('Click on a widget from the sidebar to add it to your dashboard');
    });
    
    document.getElementById('customizeLayoutBtn').addEventListener('click', () => {
        alert('Layout customization coming soon!');
    });
    
    // Panel resize and collapse functionality
    initializePanelResize();
    initializePanelCollapse();
    
    // Log viewer
    initializeLogViewer();
}

// Initialize log viewer and intercept console
function initializeLogViewer() {
    // Intercept console methods
    console.log = function(...args) {
        originalConsole.log.apply(console, args);
        addLogEntry('info', args);
    };
    
    console.error = function(...args) {
        originalConsole.error.apply(console, args);
        addLogEntry('error', args);
    };
    
    console.warn = function(...args) {
        originalConsole.warn.apply(console, args);
        addLogEntry('warn', args);
    };
    
    console.info = function(...args) {
        originalConsole.info.apply(console, args);
        addLogEntry('info', args);
    };
    
    console.debug = function(...args) {
        originalConsole.debug.apply(console, args);
        addLogEntry('debug', args);
    };
    
    // Log viewer event listeners
    const logViewerBtn = document.getElementById('logViewerBtn');
    const closeLogViewerBtn = document.getElementById('closeLogViewerBtn');
    const clearLogsBtn = document.getElementById('clearLogsBtn');
    const exportLogsBtn = document.getElementById('exportLogsBtn');
    
    if (logViewerBtn) {
        logViewerBtn.addEventListener('click', toggleLogViewer);
    }
    
    if (closeLogViewerBtn) {
        closeLogViewerBtn.addEventListener('click', toggleLogViewer);
    }
    
    if (clearLogsBtn) {
        clearLogsBtn.addEventListener('click', clearLogs);
    }
    
    if (exportLogsBtn) {
        exportLogsBtn.addEventListener('click', exportLogs);
    }
    
    // Filter checkboxes
    const filterCheckboxes = ['filterError', 'filterWarn', 'filterInfo', 'filterDebug'];
    filterCheckboxes.forEach(filterId => {
        const checkbox = document.getElementById(filterId);
        if (checkbox) {
            checkbox.addEventListener('change', renderLogs);
        }
    });
    
    // Add initial log
    addLogEntry('info', ['Log viewer initialized. All console messages will appear here.']);
}

// Add log entry
function addLogEntry(level, args) {
    const timestamp = new Date().toLocaleTimeString();
    const message = args.map(arg => {
        if (typeof arg === 'object') {
            try {
                return JSON.stringify(arg, null, 2);
            } catch (e) {
                return String(arg);
            }
        }
        return String(arg);
    }).join(' ');
    
    logEntries.push({
        timestamp,
        level,
        message,
        raw: args
    });
    
    // Keep only last 1000 entries to prevent memory issues
    if (logEntries.length > 1000) {
        logEntries.shift();
    }
    
    // Render if log viewer is open
    const logViewer = document.getElementById('logViewer');
    if (logViewer && logViewer.classList.contains('active')) {
        renderLogs();
    }
}

// Render logs with filters
function renderLogs() {
    const logViewerContent = document.getElementById('logViewerContent');
    if (!logViewerContent) return;
    
    // Get filter states
    const showError = document.getElementById('filterError')?.checked ?? true;
    const showWarn = document.getElementById('filterWarn')?.checked ?? true;
    const showInfo = document.getElementById('filterInfo')?.checked ?? true;
    const showDebug = document.getElementById('filterDebug')?.checked ?? false;
    
    // Filter logs
    const filteredLogs = logEntries.filter(entry => {
        switch (entry.level) {
            case 'error': return showError;
            case 'warn': return showWarn;
            case 'info': return showInfo;
            case 'debug': return showDebug;
            default: return true;
        }
    });
    
    // Render
    logViewerContent.innerHTML = filteredLogs.map(entry => {
        const message = entry.message.length > 500 
            ? entry.message.substring(0, 500) + '...' 
            : entry.message;
        
        return `
            <div class="log-entry ${entry.level}">
                <span class="log-time">[${entry.timestamp}]</span>
                <span class="log-message">${escapeHtml(message)}</span>
            </div>
        `;
    }).join('');
    
    // Auto-scroll to bottom
    logViewerContent.scrollTop = logViewerContent.scrollHeight;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Toggle log viewer
function toggleLogViewer() {
    const logViewer = document.getElementById('logViewer');
    if (!logViewer) return;
    
    logViewer.classList.toggle('active');
    
    if (logViewer.classList.contains('active')) {
        renderLogs();
    }
}

// Clear logs
function clearLogs() {
    if (confirm('Are you sure you want to clear all logs?')) {
        logEntries = [];
        renderLogs();
    }
}

// Export logs
function exportLogs() {
    const logText = logEntries.map(entry => {
        return `[${entry.timestamp}] [${entry.level.toUpperCase()}] ${entry.message}`;
    }).join('\n');
    
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `faraday-ai-logs-${new Date().toISOString().replace(/[:.]/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Send message
async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat('user', message);
    chatInput.value = '';
    chatInput.style.height = 'auto';
    
    // Update avatar status
    updateAvatarStatus('typing', 'Thinking...');
    
    try {
        const token = localStorage.getItem('access_token');
        
        // Prepare headers - include token if available, but don't require it
        const headers = {
            'Content-Type': 'application/json'
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Prepare context from chat history (limit to last 1 message to avoid token limits)
        // The system prompt is already very comprehensive, so we only need the most recent context
        const context = chatHistory.slice(-1).map(msg => ({
            role: msg.role,
            content: msg.content.length > 300 ? msg.content.substring(0, 300) + '...' : msg.content
        }));
        
        // Send message to AI assistant (works for both authenticated and guest users)
        const response = await fetch(`${API_BASE_URL}/chat/message`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                message: message,
                context: context
            })
        });
        
        if (!response.ok) {
            let errorText = '';
            try {
                errorText = await response.text();
                console.error('❌ Server error response:', errorText);
            } catch (e) {
                errorText = `Status: ${response.status} ${response.statusText}`;
            }
            throw new Error(`Failed to send message (${response.status}): ${errorText}`);
        }
        
        const result = await response.json();
        console.log('✅ Chat response received:', result);
        console.log('📊 Widget data:', result.widget_data);
        
        // Add AI response to chat
        if (result.response) {
            addMessageToChat('ai', result.response);
            
            // Update chat history
            chatHistory.push({ role: 'user', content: message });
            chatHistory.push({ role: 'assistant', content: result.response });
            
            // Check if AI wants to add/update widgets
            if (result.widgets) {
                handleWidgetUpdates(result.widgets);
            }
            
            // Check if the response mentions widget data that should be displayed
            // If the AI returns data for a specific widget type, update that widget
            if (result.widget_data) {
                console.log('🔄 Updating widget with data:', result.widget_data);
                updateWidgetWithData(result.widget_data);
            } else {
                console.log('⚠️ No widget_data in response');
            }
        } else {
            throw new Error('Invalid response format: missing "response" field');
        }
        
        // Update avatar status
        updateAvatarStatus('ready', 'Ready to help');
        
    } catch (error) {
        console.error('❌ Error sending message:', error);
        console.error('Error details:', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        
        let errorMessage = 'I apologize, but I encountered an error. ';
        if (error.message) {
            errorMessage += error.message;
        } else {
            errorMessage += 'Please try again or log in for full functionality.';
        }
        
        addMessageToChat('ai', errorMessage);
        updateAvatarStatus('ready', 'Ready to help');
    }
}

// Add message to chat
function addMessageToChat(role, content) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const avatar = role === 'user' ? '👤' : '🤖';
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <p>${escapeHtml(content)}</p>
            <span class="message-time">${time}</span>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Render chat history
function renderChatHistory() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = '';
    
    chatHistory.forEach(msg => {
        addMessageToChat(msg.role === 'user' ? 'user' : 'ai', msg.content);
    });
}

// Update avatar status
function updateAvatarStatus(status, text) {
    const avatarStatus = document.getElementById('avatarStatus');
    const avatarStatusText = document.getElementById('avatarStatusText');
    
    avatarStatus.className = `avatar-status ${status}`;
    avatarStatusText.textContent = text;
}

// Handle widget updates from AI
function handleWidgetUpdates(widgets) {
    if (!widgets || !Array.isArray(widgets)) return;
    
    widgets.forEach(widget => {
        const existingWidget = activeWidgets.find(w => w.id === widget.id);
        if (existingWidget) {
            // Update existing widget
            updateWidget(existingWidget.id, widget);
        } else {
            // Add new widget
            addWidgetToDashboard(widget);
        }
    });
    
    renderWidgets();
}

// Update widget with data from AI response
function updateWidgetWithData(widgetData) {
    if (!widgetData || !widgetData.type) return;
    
    // Find existing widget of this type
    let widget = activeWidgets.find(w => (w.type || w.widget_type) === widgetData.type);
    
    if (!widget) {
        // Widget doesn't exist - add it automatically
        const newWidget = {
            id: `widget-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            type: widgetData.type,
            name: getWidgetTitle(widgetData.type),
            configuration: {},
            position: null,
            size: { width: 2, height: 2 },
            created_at: new Date().toISOString(),
            is_active: true,
            is_visible: true,
            data: widgetData.data || {}
        };
        addWidgetToDashboard(newWidget);
        saveWidgetsToLocalStorage();
    } else {
        // Update existing widget with new data
        widget.data = widgetData.data || widget.data || {};
        saveWidgetsToLocalStorage();
    }
    
    renderWidgets();
}

// Add widget
async function addWidget(widgetType) {
    try {
        // Check if widget already exists
        const existingWidget = activeWidgets.find(w => w.type === widgetType);
        if (existingWidget) {
            addMessageToChat('ai', `${getWidgetTitle(widgetType)} widget is already on your dashboard.`);
            return;
        }
        
        const token = localStorage.getItem('access_token');
        
        // Create widget locally (works for both guest and authenticated users)
        const widget = {
            id: `widget-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            type: widgetType,
            name: getWidgetTitle(widgetType),
            configuration: {},
            position: null,
            size: { width: 2, height: 2 },
            created_at: new Date().toISOString(),
            is_active: true,
            is_visible: true
        };
        
        addWidgetToDashboard(widget);
        saveWidgetsToLocalStorage();
        renderWidgets();
        
        // Try to save to API for authenticated users (non-blocking)
        if (token) {
            try {
                // Try the simpler dashboard_preferences endpoint
                const dashboardId = await getOrCreateDashboardId();
                if (dashboardId) {
                    const response = await fetch(`${API_BASE_URL}/dashboard-preferences/widgets`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            name: widget.name,
                            widget_type: 'CUSTOM',
                            layout_position: 'CENTER',
                            size: widget.size,
                            configuration: { ...widget.configuration, original_type: widgetType },
                            dashboard_id: dashboardId,
                            is_active: true,
                            is_visible: true
                        })
                    });
                    
                    if (response.ok) {
                        const savedWidget = await response.json();
                        // Update local widget with server ID
                        widget.id = savedWidget.id;
                        saveWidgetsToLocalStorage();
                    }
                }
            } catch (apiError) {
                // API call failed, but widget is already added locally
                console.log('Widget added locally. API sync will be retried later.');
            }
        }
        
        addMessageToChat('ai', `Added ${getWidgetTitle(widgetType)} widget to your dashboard.${!token ? ' Log in to save your widgets permanently.' : ''}`);
        
    } catch (error) {
        console.error('Error adding widget:', error);
        showError('Failed to add widget. Please try again.');
    }
}

// Get or create dashboard ID for authenticated users
async function getOrCreateDashboardId() {
    try {
        const token = localStorage.getItem('access_token');
        if (!token) return null;
        
        // Try to get existing dashboard
        const response = await fetch(`${API_BASE_URL}/dashboard/state`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const state = await response.json();
            return state.dashboard_id || null;
        }
        
        // If no dashboard exists, initialize one
        const initResponse = await fetch(`${API_BASE_URL}/dashboard/initialize`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (initResponse.ok) {
            const result = await initResponse.json();
            return result.dashboard_id || null;
        }
        
        return null;
    } catch (error) {
        console.error('Error getting dashboard ID:', error);
        return null;
    }
}

// Save widgets to localStorage
function saveWidgetsToLocalStorage() {
    try {
        localStorage.setItem('dashboard_widgets', JSON.stringify(activeWidgets));
    } catch (error) {
        console.error('Error saving widgets to localStorage:', error);
    }
}

// Load widgets from localStorage
function loadWidgetsFromLocalStorage() {
    try {
        const saved = localStorage.getItem('dashboard_widgets');
        if (saved) {
            activeWidgets = JSON.parse(saved);
            // Normalize widget sizes: ensure all are valid string sizes
            const validSizes = ['small', 'medium', 'large', 'extra-large'];
            activeWidgets.forEach(widget => {
                if (!widget.size || typeof widget.size !== 'string' || !validSizes.includes(widget.size)) {
                    // Normalize invalid sizes (objects, invalid strings, missing) to 'medium'
                    widget.size = 'medium';
                }
            });
            return true;
        }
    } catch (error) {
        console.error('Error loading widgets from localStorage:', error);
    }
    return false;
}

// Add widget to dashboard
function addWidgetToDashboard(widget) {
    activeWidgets.push(widget);
}

// Update widget
function updateWidget(widgetId, widgetData) {
    const index = activeWidgets.findIndex(w => w.id === widgetId);
    if (index !== -1) {
        activeWidgets[index] = { ...activeWidgets[index], ...widgetData };
    }
}

// Render widgets
function renderWidgets() {
    const widgetsGrid = document.getElementById('widgetsGrid');
    
    if (activeWidgets.length === 0) {
        widgetsGrid.innerHTML = `
            <div class="widget-placeholder">
                <p>👋 Start a conversation with your AI assistant to add widgets to your dashboard</p>
                <p class="hint-text">Try saying: "Show me attendance patterns" or "Display my class insights"</p>
            </div>
        `;
        return;
    }
    
    widgetsGrid.innerHTML = activeWidgets.map(widget => {
        // Check if widget has actual data to print (not just instructions)
        const hasData = widget.data && Object.keys(widget.data).length > 0;
        const dataString = hasData ? JSON.stringify(widget.data) : '';
        const isTextPrompt = hasData && (typeof widget.data === 'string' || 
                            (typeof widget.data === 'object' && 
                             Object.keys(widget.data).length === 1 && 
                             (widget.data.message || widget.data.text || widget.data.prompt || widget.data.description)));
        const hasPrintableData = hasData && !isTextPrompt && dataString.length >= 50 && 
                                !dataString.includes('Try asking') && !dataString.includes('example');
        
        // Get widget size (default to 'medium' if not set)
        const widgetSize = widget.size || 'medium';
        const sizeClass = `widget-size-${widgetSize}`;
        
        return `
        <div class="widget-card ${sizeClass}" data-widget-id="${widget.id}" data-widget-size="${widgetSize}">
            <div class="widget-card-header">
                <h3 class="widget-card-title">${getWidgetTitle(widget.type)}</h3>
                <div class="widget-card-actions">
                    <button class="widget-action-btn widget-resize-btn" onclick="(function(e){e.stopPropagation();e.preventDefault();toggleWidgetSize('${widget.id}');})(event)" title="Resize widget">⛶</button>
                    ${hasPrintableData ? `<button class="widget-action-btn widget-print-btn" onclick="(function(e){e.stopPropagation();e.preventDefault();printWidget('${widget.id}');})(event)" title="Print widget data">🖨️</button>` : ''}
                    ${hasPrintableData ? `<button class="widget-action-btn widget-email-btn" onclick="(function(e){e.stopPropagation();e.preventDefault();emailWidget('${widget.id}');})(event)" title="Email widget data">📧</button>` : ''}
                    ${hasPrintableData ? `<button class="widget-action-btn widget-sms-btn" onclick="(function(e){e.stopPropagation();e.preventDefault();smsWidget('${widget.id}');})(event)" title="Send widget data via SMS">💬</button>` : ''}
                    <button class="widget-action-btn" onclick="(function(e){e.stopPropagation();e.preventDefault();removeWidget('${widget.id}');})(event)" title="Remove widget from dashboard">×</button>
                </div>
            </div>
            <div class="widget-card-content">
                ${renderWidgetContent(widget)}
            </div>
        </div>
    `;
    }).join('');
}

// Get widget title
function getWidgetTitle(widgetType) {
    const titles = {
        'attendance': 'Attendance & Analytics',
        'teams': 'Team Management',
        'adaptive': 'Adaptive PE',
        'performance': 'Performance Analytics',
        'safety': 'Safety & Risk Management',
        'insights': 'Class Insights',
        'fitness': 'Exercise & Fitness',
        'lesson-planning': 'Lesson Planning',
        'video': 'Video & Movement',
        'activities': 'Activity Management',
        'assessment': 'Assessment & Skills',
        'psychology': 'Sports Psychology',
        'parent-comm': 'Parent Communication',
        'collaboration': 'Collaboration',
        'health': 'Health & Nutrition',
        'drivers-ed': "Driver's Education",
        'management': 'Management Tools',
        'calendar': 'Calendar',
        'analytics': 'Analytics',
        'notifications': 'Notifications'
    };
    return titles[widgetType] || widgetType;
}

// Format widget data for display
function formatWidgetData(data, widgetType) {
    if (!data || typeof data !== 'object') {
        return '<div class="widget-data-display"><p>No data available</p></div>';
    }
    
    // Format based on widget type and data structure
    let html = '<div class="widget-data-display">';
    
    // Special handling for fitness widget with workout data
    if (widgetType === 'fitness' && data.exercises && Array.isArray(data.exercises)) {
        html += '<div class="workout-plan">';
        if (data.plan_name) {
            html += `<h4 class="workout-plan-title">${escapeHtml(data.plan_name)}</h4>`;
        }
        html += '<ul class="workout-exercises">';
        data.exercises.forEach((exercise, index) => {
            html += '<li class="workout-exercise">';
            html += `<strong class="exercise-name">${escapeHtml(exercise.name || 'Exercise ' + (index + 1))}</strong>`;
            if (exercise.sets && exercise.reps) {
                html += `<span class="exercise-sets-reps">${exercise.sets} sets × ${exercise.reps} reps</span>`;
            }
            if (exercise.description) {
                html += `<p class="exercise-description">${escapeHtml(exercise.description)}</p>`;
            }
            html += '</li>';
        });
        html += '</ul>';
        if (data.description) {
            html += `<p class="workout-description">${escapeHtml(data.description)}</p>`;
        }
        html += '</div>';
    }
    // Handle arrays
    else if (Array.isArray(data)) {
        if (data.length === 0) {
            html += '<p class="widget-empty">No items found</p>';
        } else {
            html += '<ul class="widget-data-list">';
            data.forEach((item, index) => {
                if (typeof item === 'object') {
                    html += `<li class="widget-data-item">
                        <div class="widget-data-item-content">
                            ${formatDataObject(item)}
                        </div>
                    </li>`;
                } else {
                    html += `<li class="widget-data-item">${escapeHtml(String(item))}</li>`;
                }
            });
            html += '</ul>';
        }
    } 
    // Handle objects with common structures
    else if (data.students || data.attendance || data.teams || data.performance || data.insights) {
        html += formatDataObject(data);
    }
    // Handle simple key-value pairs
    else {
        html += formatDataObject(data);
    }
    
    html += '</div>';
    return html;
}

// Format a data object into HTML
function formatDataObject(obj, depth = 0) {
    if (depth > 3) return '<span class="widget-data-deep">...</span>'; // Prevent infinite recursion
    
    let html = '';
    const keys = Object.keys(obj);
    
    if (keys.length === 0) {
        return '<p class="widget-empty">No data</p>';
    }
    
    // Check if it's a simple key-value display
    if (keys.length <= 5 && keys.every(key => {
        const val = obj[key];
        return typeof val !== 'object' || val === null || Array.isArray(val);
    })) {
        html += '<dl class="widget-data-dl">';
        keys.forEach(key => {
            const value = obj[key];
            html += `<dt class="widget-data-key">${escapeHtml(key)}:</dt>`;
            html += `<dd class="widget-data-value">${formatValue(value, depth + 1)}</dd>`;
        });
        html += '</dl>';
    } else {
        // Complex nested structure - show as formatted JSON
        html += `<pre class="widget-data-json">${escapeHtml(JSON.stringify(obj, null, 2))}</pre>`;
    }
    
    return html;
}

// Format a single value
function formatValue(value, depth = 0) {
    if (value === null || value === undefined) {
        return '<span class="widget-data-null">null</span>';
    }
    
    if (typeof value === 'boolean') {
        return `<span class="widget-data-bool">${value}</span>`;
    }
    
    if (typeof value === 'number') {
        return `<span class="widget-data-number">${value}</span>`;
    }
    
    if (Array.isArray(value)) {
        if (value.length === 0) {
            return '<span class="widget-data-empty">[]</span>';
        }
        if (value.length <= 3 && depth < 2) {
            return `[${value.map(v => formatValue(v, depth + 1)).join(', ')}]`;
        }
        return `<span class="widget-data-array">[${value.length} items]</span>`;
    }
    
    if (typeof value === 'object') {
        if (depth >= 2) {
            return '<span class="widget-data-object">{...}</span>';
        }
        const objKeys = Object.keys(value);
        if (objKeys.length === 0) {
            return '<span class="widget-data-empty">{}</span>';
        }
        if (objKeys.length <= 3) {
            return `{${objKeys.map(k => `${k}: ${formatValue(value[k], depth + 1)}`).join(', ')}}`;
        }
        return `<span class="widget-data-object">{${objKeys.length} keys}</span>`;
    }
    
    // String value
    const str = String(value);
    if (str.length > 100) {
        return `<span class="widget-data-string">${escapeHtml(str.substring(0, 100))}...</span>`;
    }
    return `<span class="widget-data-string">${escapeHtml(str)}</span>`;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Render widget content
function renderWidgetContent(widget) {
    // Customize content based on widget type
    const widgetType = widget.type || widget.widget_type;
    
    const widgetInfo = {
        // 1. Attendance Management
        'attendance': {
            description: 'Track daily attendance, analyze patterns over time, and use ML to predict future absences. Identify at-risk students with declining attendance patterns.',
            examples: ['"Mark attendance for my fourth period class today"', '"Show me attendance patterns for Period 3 this month"', '"Predict which students might be absent next week"', '"Identify students with attendance issues"'],
            icon: '📊'
        },
        // 2. Team & Squad Management
        'teams': {
            description: 'Create balanced teams based on skill level, gender, or random distribution. Support multiple teams and squads within a class for various activities.',
            examples: ['"Create 4 teams for Period 3 for basketball"', '"Make balanced teams for soccer by skill level"', '"Assign Sarah to the Red Team"', '"Show me all team configurations"'],
            icon: '👥'
        },
        // 3. Adaptive PE Support
        'adaptive': {
            description: 'Get personalized accommodation suggestions for students with special needs based on IEPs, medical notes, or activity types. Create modified activities and track progress.',
            examples: ['"What accommodations should I use for Sarah for running?"', '"Create an adaptive activity for a student with a knee injury"', '"Track IEP goals for John"', '"Show adaptive PE options for Period 2"'],
            icon: '♿'
        },
        // 4. Performance Analytics
        'performance': {
            description: 'Analyze student performance trends over time using ML models. Predict future performance, identify students needing intervention, and track skill mastery.',
            examples: ['"Show me performance trends for Period 2 this semester"', '"Predict Sarah\'s performance in long jump next month"', '"Which students are struggling with throwing skills?"', '"Generate a performance report"'],
            icon: '📈'
        },
        // 5. Safety & Risk Management
        'safety': {
            description: 'Identify potential safety risks in activities or environments. Check student medical conditions and allergies, generate safety reports, and access emergency protocols.',
            examples: ['"Identify safety risks for the rock climbing activity"', '"Check medical conditions for Period 3 today"', '"Generate a safety report for the last month"', '"What safety precautions do I need for outdoor activities?"'],
            icon: '🛡️'
        },
        // 6. Comprehensive Class Insights
        'insights': {
            description: 'Get holistic insights by combining data from attendance, performance, health metrics, and engagement. Identify overall class trends and individual student needs.',
            examples: ['"Show me comprehensive class insights for Period 3"', '"Give me an overview of my class\'s progress this quarter"', '"What are the key trends in student engagement?"', '"Identify students who need extra support"'],
            icon: '🎯'
        },
        // 7. Exercise Tracker
        'exercise': {
            description: 'Get personalized exercise recommendations based on student fitness levels and goals. Track exercise performance (reps, sets, duration) and predict progress over time.',
            examples: ['"Recommend exercises for Sarah for strength training"', '"Track John\'s push-up performance"', '"Predict Sarah\'s running endurance improvement"', '"Show exercise progress for Period 2"'],
            icon: '🏋️'
        },
        // 8. Fitness Challenges
        'challenges': {
            description: 'Create and manage various fitness challenges (step count, push-up challenges, etc.). Track student participation and progress, generate leaderboards.',
            examples: ['"Create a 30-day step challenge for Period 4"', '"Show the leaderboard for the push-up challenge"', '"Track participation in the cardio challenge"', '"Which students are leading the fitness challenge?"'],
            icon: '🏆'
        },
        // 9. Heart Rate Zones
        'heart-rate': {
            description: 'Calculate personalized heart rate zones for students based on age and fitness level. Recommend target heart rates for different activities and monitor heart rate data.',
            examples: ['"Calculate heart rate zones for John (age 15, intermediate fitness)"', '"Recommend target heart rate for a high-intensity cardio session"', '"Show heart rate data for Sarah during running"', '"What heart rate zone should Period 3 maintain for basketball?"'],
            icon: '❤️'
        },
        // 10. Nutrition Planning
        'nutrition': {
            description: 'Generate personalized meal plans based on student dietary restrictions, fitness goals, and caloric needs. Analyze nutrition intake and provide healthy eating recommendations.',
            examples: ['"Create a meal plan for John (vegetarian, muscle gain goal)"', '"Analyze Sarah\'s daily caloric intake"', '"Give me healthy snack recommendations for my class"', '"Plan meals for students with food allergies"'],
            icon: '🥗'
        },
        // 11. Parent Communication
        'parent-comm': {
            description: 'Send messages to parents via email and SMS with automatic translation to 100+ languages. Send progress updates, attendance concerns, achievement notifications, and safety alerts.',
            examples: ['"Send a progress update to Sarah\'s parents via email and text, translate to Spanish"', '"Generate an attendance concern message for John\'s parents"', '"Notify all parents about the upcoming field trip - translate for Spanish speakers"', '"Send achievement notification to parents"'],
            icon: '👨‍👩‍👧'
        },
        // 12. Game Predictions
        'game-predictions': {
            description: 'Analyze team matchups, player statistics, and historical data to predict game outcomes. Get strategic insights and probability estimates.',
            examples: ['"Predict the outcome of the Red Team vs. Blue Team basketball game"', '"Analyze player statistics for the upcoming soccer match"', '"What are the key factors for winning this game?"', '"Show me game prediction probabilities"'],
            icon: '🎮'
        },
        // 13. Skill Assessment
        'assessment': {
            description: 'Generate customizable rubrics for skill assessment. Identify individual and class-wide skill gaps, track skill mastery over time.',
            examples: ['"Create a rubric for basketball dribbling skills"', '"Show me skill gaps in Period 3 for throwing"', '"Track Sarah\'s progress in gymnastics skills"', '"Generate a skill assessment for soccer"'],
            icon: '🎓'
        },
        // 14. Sports Psychology
        'psychology': {
            description: 'Access tools for mental health assessment, suggest coping strategies for stress and anxiety, track student well-being, and offer performance psychology insights.',
            examples: ['"Assess mental health risks for students in Period 2"', '"Suggest coping strategies for pre-game anxiety"', '"Track student stress levels"', '"What mental preparation techniques should I use?"'],
            icon: '🧠'
        },
        // 15. Timer Management
        'timer': {
            description: 'Set up optimal timer settings for various activities (circuit training, timed drills). Manage countdowns and provide audio cues.',
            examples: ['"Set up a timer for circuit training (45s work, 15s rest, 3 rounds)"', '"Start a 5-minute countdown for the warm-up"', '"Manage activity timers for Period 3"', '"What timer settings work best for interval training?"'],
            icon: '⏱️'
        },
        // 16. Warmup Routines
        'warmup': {
            description: 'Generate activity-specific warmup routines including dynamic stretches and light cardio. Get modifications for different fitness levels.',
            examples: ['"Create a warmup routine for basketball practice"', '"Generate a dynamic stretching routine for running"', '"Suggest modifications for a beginner warmup"', '"What warmup should I use before soccer?"'],
            icon: '🔥'
        },
        // 17. Weather Recommendations
        'weather': {
            description: 'Analyze current and forecasted weather conditions. Get suggestions for appropriate indoor or outdoor activities and safety warnings for extreme weather.',
            examples: ['"Is it safe to have class outside today?"', '"Suggest indoor alternatives for a rainy day"', '"Provide safety warnings for extreme heat"', '"What activities work best in this weather?"'],
            icon: '🌤️'
        },
        // 18. Lesson Plan Generation
        'lesson-planning': {
            description: 'Generate standards-aligned lesson plans for various PE activities. Include objectives, activities, equipment, and assessment methods. Save and reuse plans.',
            examples: ['"Create a lesson plan on basketball fundamentals for 5th grade"', '"Generate a warmup routine for a soccer lesson"', '"Plan lessons for next week focusing on teamwork"', '"Show me saved lesson plans"'],
            icon: '📋'
        },
        // 19. Video Processing & Movement Analysis
        'video': {
            description: 'Process and analyze video recordings of student movement to assess technique, identify areas for improvement, and provide visual feedback.',
            examples: ['"Analyze movement patterns in this video of Sarah\'s long jump"', '"Assess John\'s throwing technique from the video"', '"Check video quality for movement analysis"', '"What improvements can Sarah make to her form?"'],
            icon: '🎥'
        },
        // 20. Workout Planning
        'fitness': {
            description: 'Create structured workout plans for individuals or groups. Include exercise selection, sets, reps, rest periods, and progression plans for various fitness goals.',
            examples: ['"Create a strength training workout plan for chest and triceps"', '"Design a cardio workout routine for general fitness"', '"Generate a personalized workout plan for Sarah (weight loss goal)"', '"Create workout for chest"'],
            icon: '💪'
        },
        // 21. Routine Management
        'routine': {
            description: 'Create and manage daily or weekly PE routines. Organize activities and ensure smooth transitions between segments.',
            examples: ['"Create a routine for Period 3 focusing on circuit training"', '"Organize activities for the morning PE session"', '"Manage daily routines"', '"Show me the routine schedule"'],
            icon: '📝'
        },
        // 22. Activity Scheduling
        'scheduling': {
            description: 'Schedule and manage various PE activities including class times, locations, and required equipment. Detect and resolve scheduling conflicts.',
            examples: ['"Schedule basketball practice for Period 4 on Tuesday"', '"Show me the activity schedule for next week"', '"Check for scheduling conflicts"', '"Reschedule the soccer activity"'],
            icon: '📅'
        },
        // 23. Activity Tracking
        'activities': {
            description: 'Track student performance metrics during activities, monitor completion rates, and record participation data.',
            examples: ['"Track performance for the running activity in Period 2"', '"Monitor completion of the obstacle course"', '"Record participation data for the team game"', '"Show activity completion rates"'],
            icon: '📊'
        },
        // 24. Fitness Goal Management
        'goals': {
            description: 'Help students set realistic fitness goals, track their progress towards these goals, and provide motivational feedback.',
            examples: ['"Create a fitness goal for Sarah to run a mile in under 8 minutes"', '"Show John\'s progress towards his strength goal"', '"Provide motivational feedback for the fitness challenge"', '"Which students have achieved their goals?"'],
            icon: '🎯'
        },
        // 25. Activity Planning
        'planning': {
            description: 'Plan activities based on student demographics, available equipment, and learning objectives. Get suggestions for variations and modifications.',
            examples: ['"Plan activities for Period 3 focusing on teamwork with limited equipment"', '"Suggest variations for a soccer drill"', '"Modify activity for different skill levels"', '"What activities work best for large classes?"'],
            icon: '📐'
        },
        // 26. Activity Analytics
        'analytics': {
            description: 'Analyze data from various activities to identify trends, measure effectiveness, and generate reports on student engagement and performance.',
            examples: ['"Analyze activity performance for the last month"', '"Calculate average engagement scores for team sports"', '"Generate a report on activity effectiveness"', '"What activities have the highest participation?"'],
            icon: '📈'
        },
        // 27. Activity Recommendations
        'recommendations': {
            description: 'Get personalized activity recommendations for students or classes based on their interests, skill levels, and learning objectives.',
            examples: ['"Recommend activities for Sarah based on her interest in gymnastics"', '"Suggest new activities for Period 3 to improve cardiovascular fitness"', '"Find activities suitable for beginners"', '"What activities match my class\'s skill level?"'],
            icon: '💡'
        },
        // 28. Activity Visualization
        'visualization': {
            description: 'Create interactive charts, graphs, and other visualizations to display activity data, performance trends, and student progress.',
            examples: ['"Create a chart showing performance trends for running"', '"Visualize attendance patterns over the semester"', '"Display student progress in a bar graph"', '"Show me a visualization of fitness data"'],
            icon: '📊'
        },
        // 29. Activity Export
        'export': {
            description: 'Export activity data, reports, and lesson plans in various formats (CSV, PDF, JSON) for sharing or record-keeping.',
            examples: ['"Export activity data for Period 3 to CSV"', '"Generate a PDF report of lesson plans"', '"Export student performance data to JSON"', '"Share this data with administrators"'],
            icon: '💾'
        },
        // 30. Collaboration System
        'collaboration': {
            description: 'Facilitate real-time collaboration among teachers. Share lesson plans and resources, support co-teaching initiatives.',
            examples: ['"Create a collaboration session for the PE department"', '"Share this lesson plan with John Smith"', '"Coordinate co-teaching activities for Period 2"', '"Who can I collaborate with on this project?"'],
            icon: '🤝'
        },
        // 31. Notification System
        'notifications': {
            description: 'Send automated notifications and alerts to students, parents, and teachers regarding important updates, deadlines, or safety concerns.',
            examples: ['"Send a notification to all students about the upcoming field trip"', '"Set up an alert for low equipment inventory"', '"Show notification history"', '"Notify parents about schedule changes"'],
            icon: '🔔'
        },
        // 32. Progress Tracking
        'progress': {
            description: 'Track student progress across multiple metrics (fitness, skills, academic). Visualize individual growth and identify areas needing improvement.',
            examples: ['"Track Sarah\'s overall progress this semester"', '"Show John\'s progress in basketball skills"', '"Identify areas where students need improvement"', '"Generate a progress report for Period 3"'],
            icon: '📊'
        },
        // 33. Health & Fitness Service
        'health': {
            description: 'Comprehensive service to manage all health and fitness-related data including metrics, workout plans, and nutrition.',
            examples: ['"Record daily health metrics for Sarah"', '"Show overall fitness data for Period 3"', '"Manage health and fitness profiles"', '"What health trends are emerging?"'],
            icon: '🏥'
        },
        // 34. Class Management
        'class-management': {
            description: 'Create, organize, and manage PE classes including student enrollment, scheduling, and grade-level assignments.',
            examples: ['"Create a new PE class for 6th grade"', '"Enroll John in Period 3"', '"Organize classes by grade level"', '"Show me all my classes"'],
            icon: '👨‍🏫'
        },
        // 35. Student Management
        'student-management': {
            description: 'Manage individual student profiles including personal information, medical history, emergency contacts, and academic records.',
            examples: ['"Create a student profile for new student Emily"', '"Update Sarah\'s medical information"', '"View John\'s contact details"', '"Show all student records"'],
            icon: '👤'
        },
        // 36. Health Metrics Management
        'health-metrics': {
            description: 'Track and analyze various health metrics such as heart rate, blood pressure, BMI, and sleep patterns. Identify trends and potential health concerns.',
            examples: ['"Record Sarah\'s heart rate after exercise"', '"Show average BMI for Period 3"', '"Analyze sleep patterns for students"', '"What health trends should I be concerned about?"'],
            icon: '📊'
        },
        // 37. Activity Engagement
        'engagement': {
            description: 'Measure student engagement levels during activities using various metrics (participation, effort, focus). Identify factors influencing engagement.',
            examples: ['"Track engagement for the team sport activity"', '"Calculate engagement scores for Period 2"', '"Identify factors affecting student focus"', '"Which activities have the highest engagement?"'],
            icon: '🎯'
        },
        // 38. Safety Report Generation
        'safety-reports': {
            description: 'Generate detailed safety reports for incidents, near-misses, or general safety audits. Track safety compliance and recommendations.',
            examples: ['"Generate a safety report for the recent incident"', '"Audit safety compliance for the gym"', '"Track safety recommendations"', '"Show me safety statistics for this month"'],
            icon: '🛡️'
        },
        // 39. Movement Analysis
        'movement': {
            description: 'Advanced analysis of student movement patterns using video or sensor data. Assess biomechanics, efficiency, and injury risk.',
            examples: ['"Perform a biomechanical analysis of John\'s running form"', '"Assess movement efficiency for Sarah\'s gymnastics routine"', '"Identify injury risks in student movements"', '"What movement corrections should I suggest?"'],
            icon: '🏃'
        }
    };
    
    const info = widgetInfo[widgetType] || {
        description: 'This widget is controlled through conversation with your AI assistant.',
        examples: ['"Show me data for this widget"', '"Update this widget"'],
        icon: '📦'
    };
    
    // Check if widget has data to display
    const hasData = widget.data && Object.keys(widget.data).length > 0;
    
    if (hasData) {
        // Check if data is actually structured data (not just text/prompts)
        const dataString = JSON.stringify(widget.data);
        const isTextPrompt = typeof widget.data === 'string' || 
                            (typeof widget.data === 'object' && 
                             Object.keys(widget.data).length === 1 && 
                             (widget.data.message || widget.data.text || widget.data.prompt || widget.data.description));
        
        // If it looks like a prompt/instruction text, don't show it as data
        if (isTextPrompt || dataString.length < 50 || dataString.includes('Try asking') || dataString.includes('example')) {
            // This looks like instructions/prompts, show the default instructions instead
            return `
                <div class="widget-instructions">
                    <div class="widget-icon-large">${info.icon}</div>
                    <p class="widget-description">${info.description}</p>
                    <div class="widget-examples">
                        <p class="examples-title">Try asking your AI assistant:</p>
                        <ul class="examples-list">
                            ${info.examples.map(ex => `<li>${ex}</li>`).join('')}
                        </ul>
                    </div>
                    <button class="widget-try-btn" onclick="tryWidgetExample('${widgetType}')">Try Example Command</button>
                </div>
            `;
        }
        
        // Widget has structured data - display it nicely
        return formatWidgetData(widget.data, widgetType);
    } else {
        // Widget is empty - show instructions
        return `
            <div class="widget-instructions">
                <div class="widget-icon-large">${info.icon}</div>
                <p class="widget-description">${info.description}</p>
                <div class="widget-examples">
                    <p class="examples-title">Try asking your AI assistant:</p>
                    <ul class="examples-list">
                        ${info.examples.map(ex => `<li>${ex}</li>`).join('')}
                    </ul>
                </div>
                <button class="widget-try-btn" onclick="tryWidgetExample('${widgetType}')">Try Example Command</button>
            </div>
        `;
    }
}

// Try widget example command
function tryWidgetExample(widgetType) {
    const examples = {
        'attendance': 'Mark attendance for my fourth period class today',
        'teams': 'Create 4 teams for Period 3 for basketball',
        'adaptive': 'What accommodations should I use for Sarah for running?',
        'performance': 'Show me performance trends for Period 2 this semester',
        'safety': 'Check medical conditions for Period 3 today',
        'insights': 'Show me comprehensive class insights for Period 3',
        'exercise': 'Recommend exercises for Sarah for strength training',
        'challenges': 'Create a 30-day step challenge for Period 4',
        'heart-rate': 'Calculate heart rate zones for John (age 15, intermediate fitness)',
        'nutrition': 'Create a meal plan for John (vegetarian, muscle gain goal)',
        'parent-comm': 'Send a progress update to Sarah\'s parents via email and text, translate to Spanish',
        'game-predictions': 'Predict the outcome of the Red Team vs. Blue Team basketball game',
        'assessment': 'Create a rubric for basketball dribbling skills',
        'psychology': 'Assess mental health risks for students in Period 2',
        'timer': 'Set up a timer for circuit training (45s work, 15s rest, 3 rounds)',
        'warmup': 'Create a warmup routine for basketball practice',
        'weather': 'Is it safe to have class outside today?',
        'lesson-planning': 'Create a lesson plan on basketball fundamentals for 5th grade',
        'video': 'Analyze movement patterns in this video of Sarah\'s long jump',
        'fitness': 'Create a strength training workout plan for chest and triceps',
        'routine': 'Create a routine for Period 3 focusing on circuit training',
        'scheduling': 'Schedule basketball practice for Period 4 on Tuesday',
        'activities': 'Track performance for the running activity in Period 2',
        'goals': 'Create a fitness goal for Sarah to run a mile in under 8 minutes',
        'planning': 'Plan activities for Period 3 focusing on teamwork with limited equipment',
        'analytics': 'Analyze activity performance for the last month',
        'recommendations': 'Recommend activities for Sarah based on her interest in gymnastics',
        'visualization': 'Create a chart showing performance trends for running',
        'export': 'Export activity data for Period 3 to CSV',
        'collaboration': 'Create a collaboration session for the PE department',
        'notifications': 'Send a notification to all students about the upcoming field trip',
        'progress': 'Track Sarah\'s overall progress this semester',
        'health': 'Record daily health metrics for Sarah',
        'class-management': 'Create a new PE class for 6th grade',
        'student-management': 'Create a student profile for new student Emily',
        'health-metrics': 'Record Sarah\'s heart rate after exercise',
        'engagement': 'Track engagement for the team sport activity',
        'safety-reports': 'Generate a safety report for the recent incident',
        'movement': 'Perform a biomechanical analysis of John\'s running form'
    };
    
    const exampleCommand = examples[widgetType] || 'Show me data for this widget';
    const chatInput = document.getElementById('chatInput');
    chatInput.value = exampleCommand;
    chatInput.focus();
    // Auto-resize textarea
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
}

// SMS widget data
function smsWidget(widgetId) {
    try {
        const widget = activeWidgets.find(w => w.id === widgetId);
        if (!widget) {
            console.error('Widget not found:', widgetId);
            return;
        }
        
        // Get widget title
        const widgetTitle = getWidgetTitle(widget.type);
        
        // Get the formatted data for SMS (concise format due to character limits)
        let smsBody = '';
        
        if (widget.data && Object.keys(widget.data).length > 0) {
            // Format data for SMS (keep it concise - SMS has 160 char limit per message)
            smsBody = formatWidgetDataForSMS(widget.data, widget.type, widgetTitle);
        } else {
            smsBody = `${widgetTitle}: No data available.`;
        }
        
        // Check if SMS protocol is supported (works on mobile devices)
        // For desktop, we'll prompt for phone number and use the backend SMS service
        if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
            // Mobile device - use sms: protocol
            const phoneNumber = prompt('Enter phone number (E.164 format, e.g., +1234567890):');
            if (phoneNumber) {
                const smsLink = `sms:${phoneNumber}?body=${encodeURIComponent(smsBody)}`;
                window.location.href = smsLink;
            }
        } else {
            // Desktop - prompt for phone number and offer to use backend SMS service
            const phoneNumber = prompt('Enter phone number to send SMS to (E.164 format, e.g., +1234567890):');
            if (phoneNumber) {
                // Validate phone number format (basic E.164 check)
                if (!/^\+[1-9]\d{1,14}$/.test(phoneNumber)) {
                    alert('Please enter a valid phone number in E.164 format (e.g., +1234567890)');
                    return;
                }
                
                // Ask if user wants to send via backend SMS service
                const useBackend = confirm('Would you like to send this SMS via the Faraday AI SMS service?\n\nClick OK to send via backend, or Cancel to copy the message to clipboard.');
                
                if (useBackend) {
                    // Send via backend SMS service
                    sendSMSViaBackend(phoneNumber, smsBody);
                } else {
                    // Copy to clipboard as fallback
                    navigator.clipboard.writeText(smsBody).then(() => {
                        alert('Message copied to clipboard! You can paste it into your SMS app.\n\nPhone number: ' + phoneNumber);
                    }).catch(() => {
                        // Fallback if clipboard API fails
                        const textArea = document.createElement('textarea');
                        textArea.value = smsBody;
                        document.body.appendChild(textArea);
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
                        alert('Message copied to clipboard! You can paste it into your SMS app.\n\nPhone number: ' + phoneNumber);
                    });
                }
            }
        }
        
    } catch (error) {
        console.error('Error sending SMS widget:', error);
        alert('Failed to send SMS. Please try again.');
    }
}

// Send SMS via backend service
async function sendSMSViaBackend(phoneNumber, message) {
    try {
        const token = localStorage.getItem('access_token');
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Check if send_sms function is available via the chat endpoint
        // We'll use the chat endpoint to send SMS since it has access to the send_sms function
        const response = await fetch(`${API_BASE_URL}/chat/message`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                message: `Send an SMS to ${phoneNumber} with the following message: ${message}`,
                context: []
            })
        });
        
        if (!response.ok) {
            throw new Error(`SMS send failed: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.response && result.response.toLowerCase().includes('sent') || 
            result.response && result.response.toLowerCase().includes('success')) {
            alert('SMS sent successfully!');
        } else {
            // If the AI didn't send it, show the response and offer to copy
            alert('SMS may not have been sent. Response: ' + (result.response || 'Unknown error'));
        }
        
    } catch (error) {
        console.error('Error sending SMS via backend:', error);
        alert('Failed to send SMS via backend service. Error: ' + error.message);
    }
}

// Format widget data for SMS (concise format)
function formatWidgetDataForSMS(data, widgetType, widgetTitle) {
    // SMS has character limits, so keep it concise
    let smsText = `${widgetTitle}\n`;
    
    if (!data || typeof data !== 'object') {
        smsText += 'No data';
        return smsText;
    }
    
    // Special handling for fitness widget with workout data
    if (widgetType === 'fitness' && data.exercises && Array.isArray(data.exercises)) {
        if (data.plan_name) {
            smsText += `${data.plan_name}\n`;
        }
        data.exercises.slice(0, 5).forEach((exercise, index) => {
            smsText += `${index + 1}. ${exercise.name || 'Exercise'}`;
            if (exercise.sets && exercise.reps) {
                smsText += ` (${exercise.sets}x${exercise.reps})`;
            }
            smsText += '\n';
        });
        if (data.exercises.length > 5) {
            smsText += `...and ${data.exercises.length - 5} more`;
        }
    }
    // Handle arrays - show first few items
    else if (Array.isArray(data)) {
        if (data.length === 0) {
            smsText += 'No items';
        } else {
            data.slice(0, 3).forEach((item, index) => {
                if (typeof item === 'object') {
                    smsText += `${index + 1}. ${JSON.stringify(item).substring(0, 50)}...\n`;
                } else {
                    smsText += `${index + 1}. ${String(item).substring(0, 100)}\n`;
                }
            });
            if (data.length > 3) {
                smsText += `...${data.length - 3} more items`;
            }
        }
    }
    // Handle objects - show key summary
    else {
        const keys = Object.keys(data);
        keys.slice(0, 5).forEach(key => {
            const value = data[key];
            let valueStr = '';
            if (typeof value === 'object' && value !== null) {
                valueStr = JSON.stringify(value).substring(0, 30) + '...';
            } else {
                valueStr = String(value).substring(0, 50);
            }
            smsText += `${key}: ${valueStr}\n`;
        });
        if (keys.length > 5) {
            smsText += `...${keys.length - 5} more fields`;
        }
    }
    
    // Truncate if too long (SMS limit is ~160 chars per message, but we'll allow up to 500 for multi-part)
    const maxLength = 500;
    if (smsText.length > maxLength) {
        smsText = smsText.substring(0, maxLength - 3) + '...';
    }
    
    return smsText;
}

// Email widget data
function emailWidget(widgetId) {
    try {
        const widget = activeWidgets.find(w => w.id === widgetId);
        if (!widget) {
            console.error('Widget not found:', widgetId);
            return;
        }
        
        // Get widget title
        const widgetTitle = getWidgetTitle(widget.type);
        
        // Get the formatted data for email
        let emailBody = '';
        let emailSubject = `${widgetTitle} - Widget Data`;
        
        if (widget.data && Object.keys(widget.data).length > 0) {
            // Format data for email
            emailBody = formatWidgetDataForEmail(widget.data, widget.type, widgetTitle);
        } else {
            emailBody = `Widget: ${widgetTitle}\n\nNo data available.`;
        }
        
        // Create mailto link
        const subject = encodeURIComponent(emailSubject);
        const body = encodeURIComponent(emailBody);
        const mailtoLink = `mailto:?subject=${subject}&body=${body}`;
        
        // Open email client
        window.location.href = mailtoLink;
        
    } catch (error) {
        console.error('Error emailing widget:', error);
        alert('Failed to open email client. Please try again.');
    }
}

// Format widget data for email
function formatWidgetDataForEmail(data, widgetType, widgetTitle) {
    let emailText = `${widgetTitle}\n`;
    emailText += `${'='.repeat(widgetTitle.length)}\n\n`;
    emailText += `Generated on: ${new Date().toLocaleString()}\n\n`;
    emailText += `${'-'.repeat(50)}\n\n`;
    
    if (!data || typeof data !== 'object') {
        emailText += 'No data available\n';
        return emailText;
    }
    
    // Special handling for fitness widget with workout data
    if (widgetType === 'fitness' && data.exercises && Array.isArray(data.exercises)) {
        if (data.plan_name) {
            emailText += `Workout Plan: ${data.plan_name}\n\n`;
        }
        emailText += 'Exercises:\n';
        emailText += `${'-'.repeat(50)}\n`;
        data.exercises.forEach((exercise, index) => {
            emailText += `\n${index + 1}. ${exercise.name || 'Exercise ' + (index + 1)}\n`;
            if (exercise.sets && exercise.reps) {
                emailText += `   Sets: ${exercise.sets} × Reps: ${exercise.reps}\n`;
            }
            if (exercise.description) {
                emailText += `   ${exercise.description}\n`;
            }
        });
        if (data.description) {
            emailText += `\n${'-'.repeat(50)}\n`;
            emailText += `Description: ${data.description}\n`;
        }
    }
    // Handle arrays
    else if (Array.isArray(data)) {
        if (data.length === 0) {
            emailText += 'No items found\n';
        } else {
            emailText += 'Items:\n';
            emailText += `${'-'.repeat(50)}\n`;
            data.forEach((item, index) => {
                emailText += `\n${index + 1}. `;
                if (typeof item === 'object') {
                    emailText += formatDataObjectForEmail(item, 1);
                } else {
                    emailText += String(item) + '\n';
                }
            });
        }
    }
    // Handle objects
    else {
        emailText += formatDataObjectForEmail(data, 0);
    }
    
    emailText += `\n${'-'.repeat(50)}\n`;
    emailText += `\nThis data was generated from the Faraday AI dashboard.\n`;
    
    return emailText;
}

// Format a data object for email
function formatDataObjectForEmail(obj, depth = 0) {
    if (depth > 3) return '...\n';
    
    let text = '';
    const keys = Object.keys(obj);
    
    if (keys.length === 0) {
        return 'No data\n';
    }
    
    keys.forEach(key => {
        const value = obj[key];
        const indent = '  '.repeat(depth);
        
        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
            text += `${indent}${key}:\n`;
            text += formatDataObjectForEmail(value, depth + 1);
        } else if (Array.isArray(value)) {
            text += `${indent}${key}: [${value.length} items]\n`;
            if (value.length <= 5 && depth < 2) {
                value.forEach((item, index) => {
                    if (typeof item === 'object') {
                        text += `${indent}  ${index + 1}. `;
                        text += formatDataObjectForEmail(item, depth + 1);
                    } else {
                        text += `${indent}  ${index + 1}. ${String(item)}\n`;
                    }
                });
            }
        } else {
            text += `${indent}${key}: ${formatValueForEmail(value)}\n`;
        }
    });
    
    return text;
}

// Format a single value for email
function formatValueForEmail(value) {
    if (value === null || value === undefined) {
        return 'null';
    }
    
    if (typeof value === 'boolean' || typeof value === 'number') {
        return String(value);
    }
    
    if (Array.isArray(value)) {
        if (value.length === 0) {
            return '[]';
        }
        if (value.length <= 3) {
            return `[${value.map(v => formatValueForEmail(v)).join(', ')}]`;
        }
        return `[${value.length} items]`;
    }
    
    if (typeof value === 'object') {
        const objKeys = Object.keys(value);
        if (objKeys.length === 0) {
            return '{}';
        }
        if (objKeys.length <= 3) {
            return `{${objKeys.map(k => `${k}: ${formatValueForEmail(value[k])}`).join(', ')}}`;
        }
        return `{${objKeys.length} keys}`;
    }
    
    return String(value);
}

// Print widget data
function printWidget(widgetId) {
    try {
        const widget = activeWidgets.find(w => w.id === widgetId);
        if (!widget) {
            console.error('Widget not found:', widgetId);
            return;
        }
        
        // Get widget title
        const widgetTitle = getWidgetTitle(widget.type);
        
        // Get widget content element
        const widgetCard = document.querySelector(`[data-widget-id="${widgetId}"]`);
        if (!widgetCard) {
            console.error('Widget card element not found');
            return;
        }
        
        const widgetContent = widgetCard.querySelector('.widget-card-content');
        if (!widgetContent) {
            console.error('Widget content element not found');
            return;
        }
        
        // Create a new window for printing
        const printWindow = window.open('', '_blank', 'width=800,height=600');
        if (!printWindow) {
            alert('Please allow pop-ups to print widget data.');
            return;
        }
        
        // Get the formatted data
        let printContent = '';
        
        if (widget.data && Object.keys(widget.data).length > 0) {
            // Format data for printing
            printContent = formatWidgetDataForPrint(widget.data, widget.type, widgetTitle);
        } else {
            printContent = `
                <h1>${escapeHtml(widgetTitle)}</h1>
                <p>No data available to print.</p>
            `;
        }
        
        // Write the print document
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>${escapeHtml(widgetTitle)} - Print</title>
                <style>
                    @media print {
                        @page {
                            margin: 1in;
                        }
                        body {
                            margin: 0;
                            padding: 0;
                        }
                    }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                    }
                    h1 {
                        color: #2c3e50;
                        border-bottom: 3px solid #3498db;
                        padding-bottom: 10px;
                        margin-bottom: 20px;
                    }
                    h2 {
                        color: #34495e;
                        margin-top: 25px;
                        margin-bottom: 15px;
                    }
                    h3 {
                        color: #555;
                        margin-top: 20px;
                        margin-bottom: 10px;
                    }
                    h4 {
                        color: #666;
                        margin-top: 15px;
                        margin-bottom: 8px;
                    }
                    .workout-plan {
                        margin: 20px 0;
                    }
                    .workout-plan-title {
                        font-size: 1.3em;
                        font-weight: bold;
                        margin-bottom: 15px;
                        color: #2c3e50;
                    }
                    .workout-exercises {
                        list-style: none;
                        padding: 0;
                        margin: 0;
                    }
                    .workout-exercise {
                        margin: 15px 0;
                        padding: 15px;
                        background: #f8f9fa;
                        border-left: 4px solid #3498db;
                        border-radius: 4px;
                    }
                    .exercise-name {
                        display: block;
                        font-size: 1.1em;
                        font-weight: bold;
                        color: #2c3e50;
                        margin-bottom: 8px;
                    }
                    .exercise-sets-reps {
                        display: block;
                        color: #7f8c8d;
                        margin-bottom: 8px;
                        font-weight: 600;
                    }
                    .exercise-description {
                        margin: 8px 0 0 0;
                        color: #555;
                    }
                    .workout-description {
                        margin-top: 15px;
                        padding: 10px;
                        background: #ecf0f1;
                        border-radius: 4px;
                        color: #555;
                    }
                    ul, ol {
                        margin: 10px 0;
                        padding-left: 30px;
                    }
                    li {
                        margin: 8px 0;
                    }
                    dl {
                        margin: 15px 0;
                    }
                    dt {
                        font-weight: bold;
                        color: #2c3e50;
                        margin-top: 10px;
                    }
                    dd {
                        margin-left: 20px;
                        margin-bottom: 8px;
                        color: #555;
                    }
                    pre {
                        background: #f4f4f4;
                        padding: 15px;
                        border-radius: 4px;
                        overflow-x: auto;
                        font-size: 0.9em;
                        line-height: 1.5;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin: 15px 0;
                    }
                    th, td {
                        border: 1px solid #ddd;
                        padding: 10px;
                        text-align: left;
                    }
                    th {
                        background-color: #3498db;
                        color: white;
                        font-weight: bold;
                    }
                    tr:nth-child(even) {
                        background-color: #f8f9fa;
                    }
                    .print-date {
                        color: #7f8c8d;
                        font-size: 0.9em;
                        margin-bottom: 20px;
                    }
                    .no-data {
                        color: #95a5a6;
                        font-style: italic;
                        text-align: center;
                        padding: 40px;
                    }
                </style>
            </head>
            <body>
                ${printContent}
                <div class="print-date" style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd;">
                    Printed on ${new Date().toLocaleString()}
                </div>
            </body>
            </html>
        `);
        
        printWindow.document.close();
        
        // Wait for content to load, then print
        printWindow.onload = function() {
            setTimeout(() => {
                printWindow.print();
            }, 250);
        };
        
    } catch (error) {
        console.error('Error printing widget:', error);
        alert('Failed to print widget. Please try again.');
    }
}

// Format widget data for printing
function formatWidgetDataForPrint(data, widgetType, widgetTitle) {
    let html = `<h1>${escapeHtml(widgetTitle)}</h1>`;
    
    if (!data || typeof data !== 'object') {
        html += '<p class="no-data">No data available</p>';
        return html;
    }
    
    // Special handling for fitness widget with workout data
    if (widgetType === 'fitness' && data.exercises && Array.isArray(data.exercises)) {
        html += '<div class="workout-plan">';
        if (data.plan_name) {
            html += `<h2 class="workout-plan-title">${escapeHtml(data.plan_name)}</h2>`;
        }
        html += '<ul class="workout-exercises">';
        data.exercises.forEach((exercise, index) => {
            html += '<li class="workout-exercise">';
            html += `<span class="exercise-name">${index + 1}. ${escapeHtml(exercise.name || 'Exercise ' + (index + 1))}</span>`;
            if (exercise.sets && exercise.reps) {
                html += `<span class="exercise-sets-reps">${exercise.sets} sets × ${exercise.reps} reps</span>`;
            }
            if (exercise.description) {
                html += `<p class="exercise-description">${escapeHtml(exercise.description)}</p>`;
            }
            html += '</li>';
        });
        html += '</ul>';
        if (data.description) {
            html += `<p class="workout-description">${escapeHtml(data.description)}</p>`;
        }
        html += '</div>';
    }
    // Handle arrays
    else if (Array.isArray(data)) {
        if (data.length === 0) {
            html += '<p class="no-data">No items found</p>';
        } else {
            html += '<ul>';
            data.forEach((item, index) => {
                if (typeof item === 'object') {
                    html += `<li><strong>Item ${index + 1}:</strong><br>${formatDataObjectForPrint(item)}</li>`;
                } else {
                    html += `<li>${escapeHtml(String(item))}</li>`;
                }
            });
            html += '</ul>';
        }
    }
    // Handle objects
    else {
        html += formatDataObjectForPrint(data);
    }
    
    return html;
}

// Format a data object for printing
function formatDataObjectForPrint(obj, depth = 0) {
    if (depth > 3) return '<span>...</span>';
    
    let html = '';
    const keys = Object.keys(obj);
    
    if (keys.length === 0) {
        return '<p class="no-data">No data</p>';
    }
    
    // Check if it's a simple key-value display
    if (keys.length <= 10 && keys.every(key => {
        const val = obj[key];
        return typeof val !== 'object' || val === null || Array.isArray(val);
    })) {
        html += '<dl>';
        keys.forEach(key => {
            const value = obj[key];
            html += `<dt>${escapeHtml(key)}:</dt>`;
            html += `<dd>${formatValueForPrint(value, depth + 1)}</dd>`;
        });
        html += '</dl>';
    } else {
        // Complex nested structure - show as formatted JSON
        html += `<pre>${escapeHtml(JSON.stringify(obj, null, 2))}</pre>`;
    }
    
    return html;
}

// Format a single value for printing
function formatValueForPrint(value, depth = 0) {
    if (value === null || value === undefined) {
        return '<span style="color: #95a5a6;">null</span>';
    }
    
    if (typeof value === 'boolean') {
        return `<strong>${value}</strong>`;
    }
    
    if (typeof value === 'number') {
        return `<strong>${value}</strong>`;
    }
    
    if (Array.isArray(value)) {
        if (value.length === 0) {
            return '<span style="color: #95a5a6;">[]</span>';
        }
        if (value.length <= 5 && depth < 2) {
            return `[${value.map(v => formatValueForPrint(v, depth + 1)).join(', ')}]`;
        }
        return `<span>[${value.length} items]</span>`;
    }
    
    if (typeof value === 'object') {
        if (depth >= 2) {
            return '<span>{...}</span>';
        }
        const objKeys = Object.keys(value);
        if (objKeys.length === 0) {
            return '<span style="color: #95a5a6;">{}</span>';
        }
        if (objKeys.length <= 3) {
            return `{${objKeys.map(k => `${k}: ${formatValueForPrint(value[k], depth + 1)}`).join(', ')}}`;
        }
        return `<span>{${objKeys.length} keys}</span>`;
    }
    
    // String value
    return escapeHtml(String(value));
}

// Toggle widget size (small -> medium -> large -> extra-large -> small)
function toggleWidgetSize(widgetId) {
    console.log('🔧 toggleWidgetSize called with widgetId:', widgetId);
    try {
        const widget = activeWidgets.find(w => w.id === widgetId);
        if (!widget) {
            console.error('❌ Widget not found:', widgetId, 'Available widgets:', activeWidgets.map(w => w.id));
            alert('Widget not found. Please refresh the page.');
            return;
        }
        
        console.log('✅ Widget found:', widget);
        
        const sizes = ['small', 'medium', 'large', 'extra-large'];
        // Handle both string sizes and old object format ({ width, height })
        let currentSize = widget.size || 'medium';
        console.log('🔍 Raw widget.size:', widget.size, 'Type:', typeof widget.size);
        if (typeof currentSize !== 'string' || !sizes.includes(currentSize)) {
            // Normalize invalid sizes (objects, invalid strings) to 'medium'
            console.log('⚠️ Normalizing invalid size to medium');
            currentSize = 'medium';
            widget.size = 'medium';
        }
        const currentIndex = sizes.indexOf(currentSize);
        const nextIndex = (currentIndex + 1) % sizes.length;
        const nextSize = sizes[nextIndex];
        
        console.log(`📏 Current size: ${currentSize}, Current index: ${currentIndex}, Next index: ${nextIndex}, Next size: ${nextSize}`);
        
        // Update widget size
        widget.size = nextSize;
        
        // Save to localStorage
        saveWidgetsToLocalStorage();
        console.log('💾 Widget size saved to localStorage');
        
        // Update the widget element directly (faster and more reliable than re-rendering)
        const widgetElement = document.querySelector(`[data-widget-id="${widgetId}"]`);
        if (widgetElement) {
            // Remove all size classes
            widgetElement.classList.remove('widget-size-small', 'widget-size-medium', 'widget-size-large', 'widget-size-extra-large');
            // Add the new size class
            widgetElement.classList.add(`widget-size-${nextSize}`);
            // Update the data attribute
            widgetElement.setAttribute('data-widget-size', nextSize);
            
            // Map sizes to grid column spans
            const sizeToSpan = {
                'small': 3,
                'medium': 6,
                'large': 9,
                'extra-large': 12
            };
            const spanValue = sizeToSpan[nextSize];
            
            // Also set grid-column directly as a fallback (in case CSS isn't working)
            widgetElement.style.gridColumn = `span ${spanValue}`;
            
            console.log('✅ Widget element updated directly with class:', `widget-size-${nextSize}`);
            console.log('✅ Grid column set to:', `span ${spanValue}`);
            
            // Force a reflow to ensure CSS is applied
            void widgetElement.offsetHeight;
        } else {
            console.warn('⚠️ Widget element not found, falling back to full re-render');
            // Fallback: re-render all widgets
            renderWidgets();
        }
        
        // Show feedback
        const sizeLabels = {
            'small': 'Small (1 column)',
            'medium': 'Medium (2 columns)',
            'large': 'Large (3 columns)',
            'extra-large': 'Extra Large (4 columns)'
        };
        console.log(`✅ Widget resized to: ${sizeLabels[nextSize]}`);
        
    } catch (error) {
        console.error('❌ Error resizing widget:', error);
        console.error('Error stack:', error.stack);
        alert('Failed to resize widget: ' + error.message);
        showError('Failed to resize widget. Please try again.');
    }
}

// Remove widget
async function removeWidget(widgetId) {
    try {
        const token = localStorage.getItem('access_token');
        
        // Remove locally first
        activeWidgets = activeWidgets.filter(w => w.id !== widgetId);
        saveWidgetsToLocalStorage();
        renderWidgets();
        
        // Try to delete from API for authenticated users (non-blocking)
        if (token && !widgetId.startsWith('guest-') && !widgetId.startsWith('widget-')) {
            try {
                await fetch(`${API_BASE_URL}/dashboard/widgets/${widgetId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
            } catch (apiError) {
                console.log('Widget removed locally. API sync will be retried later.');
            }
        }
        
        addMessageToChat('ai', 'Widget removed from your dashboard.');
        
    } catch (error) {
        console.error('Error removing widget:', error);
        showError('Failed to remove widget. Please try again.');
    }
}

// Initialize voice recognition
function initializeVoiceRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        // Check Safari version and Web Speech API support
        if (isSafari) {
            const safariVersion = navigator.userAgent.match(/Version\/(\d+)/);
            const version = safariVersion ? parseInt(safariVersion[1]) : 0;
            console.log('Safari detected', { version, userAgent: navigator.userAgent });
            
            // Safari 14.1+ has Web Speech API support, but it may have issues
            if (version < 14) {
                console.warn('Safari version may not fully support Web Speech API. Version:', version);
            }
            
            // Show a warning about Safari's limitations
            console.warn('⚠️ Safari Web Speech API has known limitations. Voice input may not work reliably. Consider using Chrome or Firefox for better voice input support.');
            
            // Add a user-visible warning (non-blocking)
            setTimeout(() => {
                const warningMsg = 'Voice input in Safari may not work reliably due to browser limitations. For best results, please use Chrome or Firefox.';
                addMessageToChat('ai', warningMsg);
            }, 2000);
        }
        
        recognition = new SpeechRecognition();
        
        // Safari-specific settings - try different configurations
        if (isSafari) {
            // Try continuous mode for Safari - sometimes it works better
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            // Safari sometimes needs maxAlternatives set
            recognition.maxAlternatives = 1;
        } else {
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
        }
        
        console.log('Initialized speech recognition', { 
            isSafari, 
            continuous: recognition.continuous,
            hasWebkitSpeechRecognition: 'webkitSpeechRecognition' in window,
            hasSpeechRecognition: 'SpeechRecognition' in window
        });
        
        recognition.onresult = (event) => {
            console.log('🎤 Speech recognition result received!', {
                resultIndex: event.resultIndex,
                resultsLength: event.results.length,
                results: Array.from(event.results).map((r, i) => ({
                    index: i,
                    isFinal: r.isFinal,
                    transcript: r[0].transcript,
                    confidence: r[0].confidence
                }))
            });
            
            const chatInput = document.getElementById('chatInput');
            let interimTranscript = '';
            let finalTranscript = '';
            
            // Process all results
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }
            
            console.log('Processed transcripts:', { interimTranscript, finalTranscript });
            
            // Update input field with what we've heard so far
            if (finalTranscript) {
                chatInput.value = finalTranscript.trim();
                console.log('✅ Updated chat input with final transcript:', finalTranscript.trim());
            } else if (interimTranscript) {
                chatInput.value = interimTranscript;
                console.log('✅ Updated chat input with interim transcript:', interimTranscript);
            }
            
            // If we have final results, send the message
            if (finalTranscript.trim()) {
                console.log('📤 Final transcript received, sending message:', finalTranscript.trim());
                recognition.stop();
                isVoiceActive = false;
                updateVoiceButton();
                updateAvatarStatus('processing', 'Processing your message...');
                sendMessage();
            }
        };
        
        // Add additional event listeners for Safari debugging
        recognition.onaudiostart = () => {
            console.log('🎤 Audio capture started');
        };
        
        recognition.onaudioend = () => {
            console.log('🎤 Audio capture ended');
        };
        
        recognition.onsoundstart = () => {
            console.log('🔊 Sound detected');
        };
        
        recognition.onsoundend = () => {
            console.log('🔊 Sound ended');
        };
        
        recognition.onspeechstart = () => {
            console.log('🗣️ Speech detected');
        };
        
        recognition.onspeechend = () => {
            console.log('🗣️ Speech ended');
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error, event);
            const chatInput = document.getElementById('chatInput');
            
            // Prevent error loops - if we get too many errors, stop trying
            // Don't count 'no-speech', 'aborted', or 'audio-capture' as loop-causing errors
            if (event.error !== 'no-speech' && event.error !== 'aborted' && event.error !== 'audio-capture') {
                errorCount++;
                if (errorCount >= 3) {
                    console.error('Too many consecutive errors, stopping voice recognition');
                    isVoiceActive = false;
                    updateVoiceButton();
                    stopMicrophoneStream();
                    updateAvatarStatus('ready', 'Voice recognition disabled due to errors. Please refresh the page.');
                    return;
                }
            } else {
                // Reset error count on non-critical errors
                errorCount = 0;
            }
            
            // Handle specific errors
            if (event.error === 'no-speech') {
                console.log('No speech detected');
                updateAvatarStatus('ready', 'No speech detected. Try speaking again.');
                // Don't show alert for no-speech, just update status
            } else if (event.error === 'audio-capture') {
                console.error('Audio capture error - microphone may not be accessible', {
                    isSafari,
                    userAgent: navigator.userAgent,
                    mediaDevices: !!navigator.mediaDevices,
                    getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
                });
                
                // For Safari, try fallback approaches when audio-capture error occurs
                // Only try fallback once to prevent infinite loops
                if (isSafari && errorCount === 0 && !microphoneStream) {
                    console.log('Safari audio-capture error - trying fallback approach (getUserMedia + recognition)');
                    
                    // Stop current recognition attempt
                    try {
                        recognition.stop();
                    } catch (e) {
                        // Ignore errors stopping
                    }
                    
                    isVoiceActive = false;
                    updateVoiceButton();
                    
                    // Try fallback: Keep getUserMedia stream active WHILE recognition runs
                    setTimeout(() => {
                        console.log('Fallback: Requesting getUserMedia stream to keep active during recognition');
                        navigator.mediaDevices.getUserMedia({ audio: true })
                            .then(stream => {
                                console.log('Fallback: Got getUserMedia stream, keeping it active during recognition');
                                
                                // Store the stream so we can stop it later
                                microphoneStream = stream;
                                
                                // Monitor stream state
                                stream.getTracks().forEach(track => {
                                    track.addEventListener('ended', () => {
                                        console.warn('Fallback stream track ended unexpectedly');
                                    });
                                    console.log('Stream track state:', { id: track.id, label: track.label, readyState: track.readyState });
                                });
                                
                                // Keep stream active and start recognition
                                setTimeout(() => {
                                    try {
                                        console.log('Fallback: Starting recognition with active getUserMedia stream');
                                        recognition.start();
                                        // Note: onstart handler will log stream state
                                    } catch (fallbackError) {
                                        console.error('Fallback recognition start failed:', fallbackError);
                                        stream.getTracks().forEach(track => track.stop());
                                        microphoneStream = null;
                                        updateAvatarStatus('ready', 'Voice input not available in Safari');
                                        
                                        const useChrome = confirm(
                                            'Safari\'s Web Speech API cannot access the microphone.\n\n' +
                                            'For voice input to work, please use Chrome or Firefox instead.\n\n' +
                                            'Would you like to see troubleshooting steps?\n\n' +
                                            '(Click OK for troubleshooting, Cancel to dismiss)'
                                        );
                                        
                                        if (useChrome) {
                                            alert('Safari Web Speech API Troubleshooting:\n\n' +
                                                  '1. System Settings → Privacy & Security → Microphone:\n' +
                                                  '   - Ensure Safari is checked/enabled\n\n' +
                                                  '2. Safari Settings:\n' +
                                                  '   - Safari → Settings → Websites → Microphone\n' +
                                                  '   - Ensure this site is set to "Allow"\n\n' +
                                                  '3. Restart Safari after changing permissions\n\n' +
                                                  '⚠️ Even with correct permissions, Safari\'s Web Speech API may still not work.\n' +
                                                  'For reliable voice input, please use Chrome or Firefox.');
                                        }
                                    }
                                }, 300);
                            })
                            .catch(mediaError => {
                                console.error('Fallback getUserMedia failed:', mediaError);
                                updateAvatarStatus('ready', 'Microphone access denied');
                            });
                    }, 500);
                    
                    return; // Don't show alert yet, let fallback try first
                } else if (isSafari && microphoneStream) {
                    // Fallback already tried, still getting errors
                    console.warn('Safari fallback already attempted, still getting audio-capture error');
                    // Don't try again, just show the error message below
                }
                
                // For Safari, provide specific troubleshooting (if fallback didn't work)
                if (isSafari) {
                    // Only show alert once to prevent spam
                    if (errorCount === 0) {
                        const useChrome = confirm(
                            'Safari\'s Web Speech API has known limitations and cannot reliably access the microphone.\n\n' +
                            'For voice input to work, please use Chrome or Firefox instead.\n\n' +
                            'Would you like to see instructions for checking system permissions in Safari?\n\n' +
                            '(Click OK for Safari troubleshooting, Cancel to dismiss)'
                        );
                        
                        if (useChrome) {
                            alert('Safari Web Speech API Troubleshooting:\n\n' +
                                  '1. System Settings → Privacy & Security → Microphone:\n' +
                                  '   - Ensure Safari is checked/enabled\n' +
                                  '   - If Safari is not listed, you may need to use Safari first\n\n' +
                                  '2. Safari Settings:\n' +
                                  '   - Safari → Settings → Websites → Microphone\n' +
                                  '   - Ensure this site is set to "Allow"\n\n' +
                                  '3. Restart Safari after changing permissions\n\n' +
                                  '⚠️ Even with correct permissions, Safari\'s Web Speech API may still not work.\n' +
                                  'For reliable voice input, please use Chrome or Firefox.');
                        }
                    }
                } else {
                    // For other browsers
                    if (errorCount === 0) {
                        alert('Microphone access issue detected. Please:\n\n' +
                              '1. Check browser permissions:\n' +
                              '   - Click the lock icon (🔒) in your browser address bar\n' +
                              '   - Ensure microphone is set to "Allow"\n\n' +
                              '2. Check system settings:\n' +
                              '   - Ensure microphone is enabled in system settings\n' +
                              '   - Check that no other app is using the microphone\n\n' +
                              '3. Try refreshing the page after granting permission');
                    }
                }
                updateAvatarStatus('ready', 'Microphone access issue. Check permissions and try again.');
                // Don't increment errorCount for audio-capture - allow retry after permission fix
            } else if (event.error === 'not-allowed') {
                console.error('Microphone permission denied');
                errorCount = 0; // Reset on permission error
                alert('Microphone permission denied. Please:\n\n' +
                      '1. Click the lock icon (🔒) in your browser address bar\n' +
                      '2. Change microphone setting to "Allow"\n' +
                      '3. Refresh the page and try again');
            } else if (event.error === 'aborted') {
                console.log('Speech recognition aborted');
                // User stopped it, no need to alert
                updateAvatarStatus('ready', 'Voice input stopped');
            } else if (event.error === 'network') {
                console.error('Network error during speech recognition');
                alert('Network error. Please check your internet connection and try again.');
            } else {
                console.error('Speech recognition error:', event.error);
                updateAvatarStatus('ready', `Error: ${event.error}. Please try again.`);
            }
            
            isVoiceActive = false;
            updateVoiceButton();
            stopMicrophoneStream(); // Stop stream on error
            // Only update status if we haven't already set a specific message
            if (event.error !== 'no-speech' && event.error !== 'aborted') {
                setTimeout(() => {
                    updateAvatarStatus('ready', 'Ready to help');
                }, 3000);
            }
        };
        
        recognition.onstart = () => {
            console.log('Speech recognition started successfully', {
                hasMicrophoneStream: !!microphoneStream,
                streamTracks: microphoneStream ? microphoneStream.getTracks().length : 0,
                streamTrackStates: microphoneStream ? microphoneStream.getTracks().map(t => ({
                    id: t.id,
                    label: t.label,
                    readyState: t.readyState
                })) : []
            });
            errorCount = 0; // Reset error count on successful start
            isVoiceActive = true;
            updateVoiceButton();
            updateAvatarStatus('listening', 'Listening... Speak now');
        };
        
        recognition.onend = () => {
            console.log('Speech recognition ended');
            const chatInput = document.getElementById('chatInput');
            
            // If we have text in the input but it wasn't sent, keep it
            if (chatInput.value.trim() && !chatInput.value.includes('...')) {
                // Text was captured, it should have been sent in onresult
                // But if not, we'll keep it for the user to send manually
            } else {
                // Clear if it was just interim results
                chatInput.value = '';
            }
            
            isVoiceActive = false;
            updateVoiceButton();
            
            // Only stop microphone stream if we're not restarting
            // (continuous mode might restart automatically)
            if (!isVoiceActive) {
                stopMicrophoneStream();
            }
            
            updateAvatarStatus('ready', 'Ready to help');
        };
    } else {
        console.warn('Speech recognition not supported in this browser');
    }
}

// Request microphone permission and keep stream active
async function requestMicrophonePermission() {
    try {
        // Check if getUserMedia is available
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            // Stop any existing stream first
            if (microphoneStream) {
                microphoneStream.getTracks().forEach(track => track.stop());
                microphoneStream = null;
            }
            
            // Request new stream and keep it active
            // For Safari, we keep the stream active during recognition
            // For other browsers, we can stop it after getting permission
            microphoneStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            // Add event listeners to track stream state (only for non-Safari)
            if (!isSafari) {
                microphoneStream.getTracks().forEach(track => {
                    track.addEventListener('ended', () => {
                        console.warn('Microphone track ended - this should not happen during recognition');
                    });
                });
            }
            
            console.log('Microphone permission granted, stream active', {
                tracks: microphoneStream.getTracks().length,
                trackStates: microphoneStream.getTracks().map(t => ({ id: t.id, label: t.label, readyState: t.readyState }))
            });
            
            // For Safari, don't stop the stream - keep it active
            // For other browsers, we can stop it after permission is granted
            if (!isSafari) {
                // For non-Safari browsers, we can stop the stream after getting permission
                // The Web Speech API will request its own stream
                setTimeout(() => {
                    if (microphoneStream && !isVoiceActive) {
                        console.log('Stopping permission stream (non-Safari)');
                        stopMicrophoneStream();
                    }
                }, 1000);
            }
            
            return true;
        } else {
            console.warn('getUserMedia not supported');
            return false;
        }
    } catch (error) {
        console.error('Microphone permission error:', error);
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            alert('Microphone permission denied. Please:\n1. Click the lock icon in your browser address bar\n2. Allow microphone access\n3. Refresh the page and try again');
            return false;
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
            alert('No microphone found. Please:\n1. Check that your microphone is connected\n2. Check system settings that microphone is enabled\n3. Try refreshing the page');
            return false;
        } else {
            console.error('Unexpected microphone error:', error);
            return false;
        }
    }
}

// Stop microphone stream
function stopMicrophoneStream() {
    if (microphoneStream) {
        console.log('Stopping microphone stream');
        microphoneStream.getTracks().forEach(track => {
            track.stop();
            console.log('Microphone track stopped:', track.label);
        });
        microphoneStream = null;
    }
}

// Toggle voice input
async function toggleVoiceInput() {
    // For Safari, we don't need recognition object
    if (!isSafari && !recognition) {
        alert('Voice recognition is not available in your browser.');
        return;
    }
    
    if (isVoiceActive) {
        // Stop recognition or recording
        if (isSafari && mediaRecorder && microphoneStream) {
            // For Safari, stop MediaRecorder first
            console.log('🛑 User clicked to stop Safari audio recording');
            
            // Check recording state
            if (mediaRecorder.state === 'recording') {
                console.log('Stopping MediaRecorder...');
                // Request any remaining data before stopping
                try {
                    mediaRecorder.requestData();
                } catch (e) {
                    console.warn('Could not request data:', e);
                }
                // Small delay to ensure data is collected
                setTimeout(() => {
                    if (mediaRecorder.state === 'recording') {
                        mediaRecorder.stop(); // This will trigger onstop handler
                    }
                }, 100);
                // Don't clean up here - let onstop handler do it after transcription
            } else if (mediaRecorder.state === 'inactive') {
                console.log('MediaRecorder already stopped');
                // Clean up if already stopped
                microphoneStream.getTracks().forEach(track => track.stop());
                microphoneStream = null;
                mediaRecorder = null;
                isVoiceActive = false;
                updateVoiceButton();
                updateAvatarStatus('ready', 'Ready to help');
            } else {
                console.log('MediaRecorder state:', mediaRecorder.state);
                // Try to stop anyway
                try {
                    mediaRecorder.stop();
                } catch (e) {
                    console.error('Error stopping MediaRecorder:', e);
                    // Force cleanup
                    microphoneStream.getTracks().forEach(track => track.stop());
                    microphoneStream = null;
                    mediaRecorder = null;
                    isVoiceActive = false;
                    updateVoiceButton();
                    updateAvatarStatus('ready', 'Ready to help');
                }
            }
            
            // Don't send message here - wait for transcription to complete
        } else if (recognition) {
            // For other browsers, stop Web Speech API
            recognition.stop();
            isVoiceActive = false;
            updateVoiceButton();
            stopMicrophoneStream();
            updateAvatarStatus('ready', 'Ready to help');
            
            // If there's text in the input, send it
            const chatInput = document.getElementById('chatInput');
            if (chatInput.value.trim()) {
                sendMessage();
            }
        }
    } else {
        // Reset error count when user manually starts
        errorCount = 0;
        
        // For Safari, use getUserMedia + backend transcription (Safari doesn't support Web Speech API)
        if (isSafari) {
            console.log('Safari detected - using getUserMedia + backend transcription');
            
            // Check if we're on localhost and provide guidance
            if (window.location.protocol === 'http:' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
                console.warn('⚠️ Safari on localhost: Microphone access may require special settings');
                // Don't show warning immediately - let's try first and see if it works
            }
            
            // Clear input field before starting
            const chatInput = document.getElementById('chatInput');
            chatInput.value = '';
            
            updateAvatarStatus('processing', 'Requesting microphone access...');
            
            // Use getUserMedia to capture audio, then send to backend for transcription
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    }
                });
                
                console.log('Safari: Got microphone stream, starting audio capture');
                console.log('Stream details:', {
                    id: stream.id,
                    active: stream.active,
                    tracks: stream.getTracks().length,
                    trackDetails: stream.getTracks().map(t => ({
                        id: t.id,
                        kind: t.kind,
                        label: t.label,
                        enabled: t.enabled,
                        muted: t.muted,
                        readyState: t.readyState
                    }))
                });
                
                // Safari workaround: Create AudioContext and connect stream to activate audio pipeline
                // This ensures Safari actually processes the audio
                let audioContext = null;
                let audioSource = null;
                let audioDestination = null;
                
                // Store original stream for cleanup
                microphoneStream = stream;
                
                try {
                    console.log('🔧 Attempting to create AudioContext for Safari audio processing...');
                    audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    console.log('✅ AudioContext created, state:', audioContext.state);
                    
                    // Resume AudioContext if suspended (Safari sometimes starts suspended)
                    if (audioContext.state === 'suspended') {
                        console.log('⏸️ AudioContext suspended, resuming...');
                        await audioContext.resume();
                        console.log('✅ AudioContext resumed, state:', audioContext.state);
                    }
                    
                    audioSource = audioContext.createMediaStreamSource(stream);
                    audioDestination = audioContext.createMediaStreamDestination();
                    
                    // Connect source to destination to keep audio pipeline active
                    audioSource.connect(audioDestination);
                    console.log('✅ Audio nodes connected');
                    
                    // Use the destination stream for MediaRecorder (this ensures audio is processed)
                    const processedStream = audioDestination.stream;
                    console.log('✅ AudioContext created and stream connected');
                    console.log('Processed stream details:', {
                        id: processedStream.id,
                        active: processedStream.active,
                        tracks: processedStream.getTracks().length,
                        trackStates: processedStream.getTracks().map(t => ({
                            kind: t.kind,
                            enabled: t.enabled,
                            muted: t.muted,
                            readyState: t.readyState
                        }))
                    });
                    
                    // Use the processed stream for recording
                    stream = processedStream;
                    console.log('✅ Using processed stream from AudioContext for MediaRecorder');
                } catch (audioContextError) {
                    console.error('❌ Could not create AudioContext, using original stream:', audioContextError);
                    // Keep using original stream - AudioContext failed
                    audioContext = null; // Make sure it's null if creation failed
                }
                
                isVoiceActive = true;
                updateVoiceButton();
                updateAvatarStatus('listening', 'Listening... Speak now');
                
                // Use MediaRecorder to capture audio
                // Safari supports different formats - try to find the best one
                let mimeType = null;
                const supportedTypes = [
                    'audio/webm;codecs=opus',
                    'audio/webm',
                    'audio/mp4',
                    'audio/mpeg',
                    'audio/wav'
                ];
                
                for (const type of supportedTypes) {
                    if (MediaRecorder.isTypeSupported(type)) {
                        mimeType = type;
                        console.log('✅ Using MediaRecorder type:', mimeType);
                        break;
                    }
                }
                
                if (!mimeType) {
                    // Fallback: let browser choose
                    console.warn('⚠️ No specific type supported, using browser default');
                    mimeType = '';
                }
                
                // Use the stream (either processed from AudioContext or original)
                const streamToRecord = stream;
                
                const recorderOptions = mimeType ? { mimeType: mimeType } : {};
                mediaRecorder = new MediaRecorder(streamToRecord, recorderOptions);
                
                console.log('MediaRecorder created:', {
                    state: mediaRecorder.state,
                    mimeType: mediaRecorder.mimeType || 'browser default',
                    audioBitsPerSecond: mediaRecorder.audioBitsPerSecond || 'default'
                });
                
                // Store audio chunks in a variable that persists across the recording session
                const audioChunks = [];
                let recordingStartTime = Date.now();
                const MIN_RECORDING_TIME = 1000; // Minimum 1 second of recording
                
                // Clear any previous chunks
                audioChunks.length = 0;
                
                mediaRecorder.ondataavailable = (event) => {
                    console.log('📦 ondataavailable fired:', {
                        size: event.data?.size || 0,
                        type: event.data?.type || 'unknown',
                        state: mediaRecorder.state,
                        streamActive: stream.active,
                        tracksActive: stream.getTracks().filter(t => t.readyState === 'live').length
                    });
                    
                    if (event.data && event.data.size > 0) {
                        audioChunks.push(event.data);
                        console.log('✅ Audio chunk received:', event.data.size, 'bytes, total chunks:', audioChunks.length);
                    } else {
                        console.warn('⚠️ Empty or invalid audio chunk received');
                        console.warn('Stream state:', {
                            active: stream.active,
                            tracks: stream.getTracks().map(t => ({
                                kind: t.kind,
                                enabled: t.enabled,
                                muted: t.muted,
                                readyState: t.readyState
                            }))
                        });
                    }
                };
                
                mediaRecorder.onstop = async () => {
                    const recordingDuration = Date.now() - recordingStartTime;
                    console.log(`🛑 Recording stopped after ${recordingDuration}ms`);
                    console.log(`📊 Total chunks collected: ${audioChunks.length}`);
                    
                    // Log chunk details
                    audioChunks.forEach((chunk, index) => {
                        console.log(`  Chunk ${index + 1}: ${chunk.size} bytes, type: ${chunk.type}`);
                    });
                    
                    // Restore placeholder
                    chatInput.placeholder = 'Type your message or use voice input...';
                    
                    // Clean up AudioContext first
                    if (audioContext) {
                        try {
                            audioContext.close();
                            console.log('✅ AudioContext closed');
                        } catch (e) {
                            console.warn('Error closing AudioContext:', e);
                        }
                    }
                    
                    // Check if recording was too short
                    if (recordingDuration < MIN_RECORDING_TIME) {
                        console.warn(`⚠️ Recording was too short (${recordingDuration}ms < ${MIN_RECORDING_TIME}ms)`);
                        updateAvatarStatus('ready', 'Recording too short. Please speak for at least 1 second.');
                        if (microphoneStream) {
                            microphoneStream.getTracks().forEach(track => track.stop());
                        }
                        microphoneStream = null;
                        mediaRecorder = null;
                        isVoiceActive = false;
                        updateVoiceButton();
                        return;
                    }
                    
                    // Check if we have any chunks
                    if (audioChunks.length === 0) {
                        console.error('❌ No audio chunks collected!');
                        updateAvatarStatus('ready', 'No audio captured. Please try again and speak clearly.');
                        if (microphoneStream) {
                            microphoneStream.getTracks().forEach(track => track.stop());
                        }
                        microphoneStream = null;
                        mediaRecorder = null;
                        isVoiceActive = false;
                        updateVoiceButton();
                        return;
                    }
                    
                    updateAvatarStatus('processing', 'Transcribing...');
                    
                    // Combine audio chunks - make sure we're using the correct type
                    const actualMimeType = mediaRecorder.mimeType || mimeType || 'audio/webm';
                    const audioBlob = new Blob(audioChunks, { type: actualMimeType });
                    console.log('📦 Audio blob created:', audioBlob.size, 'bytes from', audioChunks.length, 'chunks, type:', actualMimeType);
                    
                    // Allow any audio data through - let the backend validate
                    // Safari sometimes produces small files that might still work
                    const MIN_AUDIO_SIZE = 1; // Allow any non-empty audio
                    if (audioBlob.size < MIN_AUDIO_SIZE) {
                        console.warn(`⚠️ Audio blob is empty (${audioBlob.size} bytes)`);
                        updateAvatarStatus('ready', 'No audio captured. Please try again and speak clearly.');
                        if (microphoneStream) {
                            microphoneStream.getTracks().forEach(track => track.stop());
                        }
                        microphoneStream = null;
                        mediaRecorder = null;
                        isVoiceActive = false;
                        updateVoiceButton();
                        return;
                    }
                    
                    // Log warning if file is very small but still try to send it
                    if (audioBlob.size < 100) {
                        console.warn(`⚠️ Audio blob is very small (${audioBlob.size} bytes) - may not contain actual audio, but sending anyway`);
                    }
                    
                    // Send to backend for transcription
                    try {
                        const formData = new FormData();
                        formData.append('audio', audioBlob, `recording.${mimeType.split('/')[1].split(';')[0]}`);
                        formData.append('language', 'en');
                        
                        const token = localStorage.getItem('access_token');
                        const headers = {};
                        if (token) {
                            headers['Authorization'] = `Bearer ${token}`;
                        }
                        
                        const response = await fetch(`${API_BASE_URL}/speech-to-text`, {
                            method: 'POST',
                            headers: headers,
                            body: formData
                        });
                        
                        if (!response.ok) {
                            let errorText = '';
                            try {
                                errorText = await response.text();
                                console.error('❌ Server error response:', errorText);
                            } catch (e) {
                                errorText = `Status: ${response.status} ${response.statusText}`;
                            }
                            throw new Error(`Transcription failed (${response.status}): ${errorText}`);
                        }
                        
                        const result = await response.json();
                        console.log('✅ Transcription result:', result);
                        
                        if (!result || !result.text) {
                            throw new Error('Invalid response from server: ' + JSON.stringify(result));
                        }
                        
                        if (result.text && result.text.trim()) {
                            chatInput.value = result.text.trim();
                            updateAvatarStatus('ready', 'Ready to help');
                            sendMessage();
                        } else {
                            updateAvatarStatus('ready', 'No speech detected. Try again.');
                        }
                    } catch (transcriptionError) {
                        console.error('❌ Transcription error:', transcriptionError);
                        console.error('Error details:', {
                            name: transcriptionError.name,
                            message: transcriptionError.message,
                            stack: transcriptionError.stack
                        });
                        
                        let errorMessage = 'Failed to transcribe audio. ';
                        if (transcriptionError.message) {
                            errorMessage += transcriptionError.message;
                        } else {
                            errorMessage += 'Please check your OpenAI API key configuration.';
                        }
                        
                        updateAvatarStatus('ready', 'Transcription failed. Please try again.');
                        alert(errorMessage);
                    }
                    
                    // Clean up
                    if (microphoneStream) {
                        microphoneStream.getTracks().forEach(track => track.stop());
                    }
                    if (audioContext) {
                        try {
                            audioContext.close();
                        } catch (e) {
                            console.warn('Error closing AudioContext:', e);
                        }
                    }
                    microphoneStream = null;
                    mediaRecorder = null;
                    isVoiceActive = false;
                    updateVoiceButton();
                    
                    // Restore placeholder
                    chatInput.placeholder = 'Type your message or use voice input...';
                };
                
                mediaRecorder.onerror = (event) => {
                    console.error('MediaRecorder error:', event.error);
                    updateAvatarStatus('ready', 'Recording error. Please try again.');
                };
                
                // Start recording with a small timeslice to ensure we get chunks
                // Safari needs timeslice to fire ondataavailable events
                try {
                    // Wait a moment for stream to stabilize
                    await new Promise(resolve => setTimeout(resolve, 100));
                    
                    // Check stream state before starting
                    const activeTracks = stream.getTracks().filter(t => t.readyState === 'live');
                    console.log('Stream state before recording:', {
                        active: stream.active,
                        activeTracks: activeTracks.length,
                        trackStates: stream.getTracks().map(t => ({
                            kind: t.kind,
                            enabled: t.enabled,
                            muted: t.muted,
                            readyState: t.readyState
                        }))
                    });
                    
                    if (activeTracks.length === 0) {
                        throw new Error('No active audio tracks in stream');
                    }
                    
                    // Start with timeslice - Safari needs this to fire ondataavailable
                    mediaRecorder.start(250); // Fire every 250ms
                    console.log('✅ MediaRecorder started with 250ms timeslice');
                    console.log('💡 Speak now, then click the microphone button again when you finish');
                    
                    // Show a visual indicator that recording is active
                    const chatInput = document.getElementById('chatInput');
                    chatInput.placeholder = '🎤 Recording... Click microphone again to stop';
                    
                    // Monitor stream health
                    stream.getTracks().forEach(track => {
                        track.onended = () => {
                            console.error('❌ Audio track ended unexpectedly!');
                            updateAvatarStatus('ready', 'Microphone disconnected. Please try again.');
                        };
                        
                        track.onmute = () => {
                            console.warn('⚠️ Audio track muted');
                        };
                        
                        track.onunmute = () => {
                            console.log('✅ Audio track unmuted');
                        };
                    });
                } catch (startError) {
                    console.error('Error starting MediaRecorder:', startError);
                    throw startError;
                }
                
            } catch (error) {
                console.error('Safari microphone access error:', error);
                isVoiceActive = false;
                updateVoiceButton();
                updateAvatarStatus('ready', 'Microphone access denied');
                
                if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
                    let errorMsg = 'Microphone permission denied. Please try:\n\n';
                    errorMsg += '1. System Settings → Privacy & Security → Microphone\n';
                    errorMsg += '   - Ensure Safari is enabled\n\n';
                    errorMsg += '2. Safari Settings:\n';
                    errorMsg += '   - Safari → Settings → Websites → Microphone\n';
                    errorMsg += '   - Ensure this site is set to "Allow"\n\n';
                    
                    // Only mention "Allow Insecure Localhost" if on localhost
                    if (window.location.protocol === 'http:' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
                        errorMsg += '3. For localhost (if available in your Safari version):\n';
                        errorMsg += '   - Safari → Develop → Allow Insecure Localhost\n';
                        errorMsg += '   - OR try using https://localhost:8000 instead\n\n';
                    }
                    
                    errorMsg += '4. Refresh the page and try again';
                    alert(errorMsg);
                } else if (error.name === 'NotFoundError') {
                    alert('No microphone found. Please check your microphone settings.');
                } else {
                    alert('Failed to access microphone. Please try again.');
                }
            }
        } else {
            // For other browsers, request permission first
            updateAvatarStatus('processing', 'Requesting microphone access...');
            const hasPermission = await requestMicrophonePermission();
            
            if (!hasPermission) {
                updateAvatarStatus('ready', 'Microphone access required');
                return;
            }
            
            // Small delay to ensure stream is ready
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Clear input field before starting
            const chatInput = document.getElementById('chatInput');
            chatInput.value = '';
            
            // Start recognition
            try {
                console.log('Starting speech recognition with active microphone stream');
                recognition.start();
                // isVoiceActive will be set to true in onstart handler
            } catch (error) {
                console.error('Error starting voice recognition:', error);
                stopMicrophoneStream(); // Clean up stream on error
                if (error.name === 'InvalidStateError') {
                    // Recognition is already running, try to stop and restart
                    recognition.stop();
                    setTimeout(() => {
                        try {
                            recognition.start();
                        } catch (retryError) {
                            console.error('Error restarting recognition:', retryError);
                            updateAvatarStatus('ready', 'Error starting voice recognition');
                        }
                    }, 100);
                } else {
                    updateAvatarStatus('ready', 'Failed to start voice recognition');
                    alert('Failed to start voice recognition. Please try again or check your browser console for details.');
                }
            }
        }
    }
}

// Update voice button
function updateVoiceButton() {
    const voiceBtn = document.getElementById('voiceToggle');
    if (isVoiceActive) {
        voiceBtn.classList.add('active');
    } else {
        voiceBtn.classList.remove('active');
    }
}

// Clear chat
function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        chatHistory = [];
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = `
            <div class="message ai-message">
                <div class="message-avatar">👤</div>
                <div class="message-content">
                    <p>Chat cleared. How can I help you today?</p>
                    <span class="message-time">Just now</span>
                </div>
            </div>
        `;
    }
}

// Open settings
function openSettings() {
    document.getElementById('settingsModal').classList.add('active');
}

// Close settings
function closeSettings() {
    document.getElementById('settingsModal').classList.remove('active');
}

// Save settings
function saveSettings() {
    const theme = document.querySelector('input[name="theme"]:checked').value;
    const enableNotifications = document.getElementById('enableNotifications').checked;
    const enableSounds = document.getElementById('enableSounds').checked;
    const enableVoiceInput = document.getElementById('enableVoiceInput').checked;
    
    // Save to localStorage
    localStorage.setItem('dashboard_theme', theme);
    localStorage.setItem('enable_notifications', enableNotifications);
    localStorage.setItem('enable_sounds', enableSounds);
    localStorage.setItem('enable_voice_input', enableVoiceInput);
    
    // Apply theme
    if (theme === 'light') {
        document.body.classList.add('light-theme');
    } else {
        document.body.classList.remove('light-theme');
    }
    
    closeSettings();
    showSuccess('Settings saved successfully!');
}

// Toggle sidebar
function toggleSidebar() {
    const sidebar = document.querySelector('.widgets-sidebar');
    const floatingToggle = document.getElementById('floatingSidebarToggle');
    
    sidebar.classList.toggle('collapsed');
    
    const toggleBtn = document.getElementById('toggleSidebar');
    const icon = toggleBtn.querySelector('.icon');
    const isCollapsed = sidebar.classList.contains('collapsed');
    
    icon.textContent = isCollapsed ? '→' : '←';
    
    // Show/hide floating toggle button
    if (isCollapsed) {
        floatingToggle.style.display = 'flex';
    } else {
        floatingToggle.style.display = 'none';
    }
}

// Logout
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        // Clear all auth data from localStorage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('teacher_id');
        localStorage.removeItem('user_email');
        window.location.href = '/';
    }
}

// Show error message
function showError(message) {
    // Simple error display - can be enhanced with a toast notification system
    alert('Error: ' + message);
}

// Show success message
function showSuccess(message) {
    // Simple success display - can be enhanced with a toast notification system
    console.log('Success: ' + message);
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize panel resize functionality
function initializePanelResize() {
    console.log('🔧 Initializing panel resize functionality...');
    
    // Restore saved sizes
    const savedSidebarWidth = localStorage.getItem('sidebarWidth');
    const savedChatHeight = localStorage.getItem('chatHeight');
    
    const sidebar = document.getElementById('widgetsSidebar');
    const chatSection = document.getElementById('chatSection');
    
    if (!sidebar || !chatSection) {
        console.error('❌ Could not find sidebar or chatSection elements');
        return;
    }
    
    if (savedSidebarWidth && !sidebar.classList.contains('collapsed')) {
        sidebar.style.width = savedSidebarWidth + 'px';
        console.log('✅ Restored sidebar width:', savedSidebarWidth);
    }
    
    if (savedChatHeight && !chatSection.classList.contains('collapsed')) {
        chatSection.style.height = savedChatHeight + 'px';
        console.log('✅ Restored chat height:', savedChatHeight);
    }
    
    // Sidebar resize
    const sidebarResizeHandle = document.getElementById('sidebarResizeHandle');
    
    if (sidebarResizeHandle && sidebar) {
        console.log('✅ Sidebar resize handle found');
        let isResizing = false;
        let startX = 0;
        let startWidth = 0;
        
        sidebarResizeHandle.addEventListener('mousedown', (e) => {
            if (sidebar.classList.contains('collapsed')) return;
            isResizing = true;
            startX = e.clientX;
            startWidth = sidebar.offsetWidth;
            sidebarResizeHandle.classList.add('resizing');
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;
            const diff = e.clientX - startX; // Positive when dragging right
            const newWidth = Math.max(200, Math.min(600, startWidth + diff));
            sidebar.style.width = newWidth + 'px';
            sidebar.style.transition = 'none'; // Disable transition during resize
            localStorage.setItem('sidebarWidth', newWidth);
        });
        
        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                sidebarResizeHandle.classList.remove('resizing');
                sidebar.style.transition = 'width 0.2s ease'; // Re-enable transition
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        });
    }
    
    // Chat section resize
    const chatResizeHandle = document.getElementById('chatResizeHandle');
    
    if (chatResizeHandle && chatSection) {
        console.log('✅ Chat resize handle found');
        let isResizing = false;
        let startY = 0;
        let startHeight = 0;
        
        chatResizeHandle.addEventListener('mousedown', (e) => {
            if (chatSection.classList.contains('collapsed')) return;
            isResizing = true;
            startY = e.clientY;
            startHeight = chatSection.offsetHeight;
            chatResizeHandle.classList.add('resizing');
            document.body.style.cursor = 'row-resize';
            document.body.style.userSelect = 'none';
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;
            const diff = e.clientY - startY;
            const newHeight = Math.max(200, Math.min(window.innerHeight * 0.8, startHeight + diff));
            chatSection.style.height = newHeight + 'px';
            chatSection.style.transition = 'none'; // Disable transition during resize
            localStorage.setItem('chatHeight', newHeight);
        });
        
        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                chatResizeHandle.classList.remove('resizing');
                chatSection.style.transition = 'height 0.2s ease'; // Re-enable transition
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        });
    }
}

// Initialize panel collapse functionality
function initializePanelCollapse() {
    console.log('🔧 Initializing panel collapse functionality...');
    
    const collapseChatBtn = document.getElementById('collapseChatBtn');
    const chatSection = document.getElementById('chatSection');
    const collapseChatIcon = document.getElementById('collapseChatIcon');
    
    if (collapseChatBtn && chatSection && collapseChatIcon) {
        console.log('✅ Chat collapse button found');
        collapseChatBtn.addEventListener('click', () => {
            const isCollapsed = chatSection.classList.toggle('collapsed');
            collapseChatIcon.textContent = isCollapsed ? '▲' : '▼';
            
            // Save collapsed state
            localStorage.setItem('chatCollapsed', isCollapsed);
            
            // Restore height when expanding
            if (!isCollapsed) {
                const savedHeight = localStorage.getItem('chatHeight');
                if (savedHeight) {
                    chatSection.style.height = savedHeight + 'px';
                } else {
                    chatSection.style.height = '400px';
                }
            }
        });
        
        // Restore collapsed state on load
        const wasCollapsed = localStorage.getItem('chatCollapsed') === 'true';
        if (wasCollapsed) {
            chatSection.classList.add('collapsed');
            collapseChatIcon.textContent = '▲';
        }
    }
}

// Make functions available globally for onclick handlers
window.removeWidget = removeWidget;
window.toggleWidgetSize = toggleWidgetSize;
window.printWidget = printWidget;
window.emailWidget = emailWidget;
window.smsWidget = smsWidget;
window.hideLoginOverlay = hideLoginOverlay;
window.tryWidgetExample = tryWidgetExample;

