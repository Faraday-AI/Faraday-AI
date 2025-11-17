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

        // Load user info
        await loadUserInfo();
        
        // Load dashboard state
        await loadDashboardState();
        
        // Setup event listeners
        setupEventListeners();
        
        // Initialize voice recognition if available
        initializeVoiceRecognition();
        
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        // If auth fails, show login overlay
        if (error.message && error.message.includes('401')) {
            showLoginOverlay();
        } else {
            showError('Failed to load dashboard. Please try again.');
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
                <button class="btn-primary" onclick="window.location.href='/static/auth-form.html'">Go to Login</button>
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
        
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load user info');
        }
        
        currentUser = await response.json();
        document.getElementById('userName').textContent = currentUser.email || 'User';
    } catch (error) {
        console.error('Error loading user info:', error);
        // Fallback to email from token if available
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                document.getElementById('userName').textContent = payload.email || 'User';
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
        
        // Prepare context from chat history
        const context = chatHistory.slice(-5).map(msg => ({
            role: msg.role,
            content: msg.content
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
                updateWidgetWithData(result.widget_data);
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
    
    widgetsGrid.innerHTML = activeWidgets.map(widget => `
        <div class="widget-card" data-widget-id="${widget.id}">
            <div class="widget-card-header">
                <h3 class="widget-card-title">${getWidgetTitle(widget.type)}</h3>
                <div class="widget-card-actions">
                    <button class="widget-action-btn" onclick="removeWidget('${widget.id}')" title="Remove">×</button>
                </div>
            </div>
            <div class="widget-card-content">
                ${renderWidgetContent(widget)}
            </div>
        </div>
    `).join('');
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

// Render widget content
function renderWidgetContent(widget) {
    // Customize content based on widget type
    const widgetType = widget.type || widget.widget_type;
    
    const widgetInfo = {
        'attendance': {
            description: 'Track attendance patterns, predict absences, and identify at-risk students.',
            examples: ['"Show me attendance for Period 3"', '"Which students are frequently absent?"', '"Predict absences for next week"'],
            icon: '📊'
        },
        'teams': {
            description: 'Create balanced teams and manage squads for activities.',
            examples: ['"Create teams for basketball in Period 3"', '"Show me team configurations"', '"Balance teams by skill level"'],
            icon: '👥'
        },
        'adaptive': {
            description: 'Suggest accommodations and create adaptive activities for students with special needs.',
            examples: ['"What accommodations should I use for Sarah?"', '"Create adaptive activity for knee injury"', '"Show adaptive PE options"'],
            icon: '♿'
        },
        'performance': {
            description: 'View performance analytics, trends, and predictions for student progress.',
            examples: ['"Show me performance trends"', '"Predict student outcomes"', '"Which students need intervention?"'],
            icon: '📈'
        },
        'safety': {
            description: 'Monitor safety risks, check medical conditions, and generate safety reports.',
            examples: ['"Show me safety risks for Period 2"', '"Generate a safety report"', '"Check medical conditions for today"'],
            icon: '🛡️'
        },
        'insights': {
            description: 'Get comprehensive class insights combining attendance, performance, health, and more.',
            examples: ['"Show me class insights for Period 3"', '"What are the key trends?"', '"Give me a class summary"'],
            icon: '🎯'
        },
        'fitness': {
            description: 'Track fitness metrics, create workout plans, and monitor heart rate zones.',
            examples: ['"Show me fitness data"', '"Create a workout plan"', '"Track heart rate zones"'],
            icon: '💪'
        },
        'lesson-planning': {
            description: 'Generate standards-aligned lesson plans, warmup routines, and curriculum materials.',
            examples: ['"Create a lesson plan on basketball"', '"Generate warmup routines"', '"Plan lessons for next week"'],
            icon: '📋'
        },
        'video': {
            description: 'Analyze movement patterns, assess technique, and process video data.',
            examples: ['"Analyze this video"', '"Show movement analysis"', '"Assess student technique"'],
            icon: '🎥'
        },
        'activities': {
            description: 'Manage activities, track progress, and get activity recommendations.',
            examples: ['"Show me activity data"', '"Track activity progress"', '"Recommend activities for Period 2"'],
            icon: '📅'
        },
        'assessment': {
            description: 'Create assessments, track skills, and identify knowledge gaps.',
            examples: ['"Generate an assessment"', '"Show skill gaps"', '"Create a rubric"'],
            icon: '🎓'
        },
        'psychology': {
            description: 'Access sports psychology tools, mental health support, and performance psychology.',
            examples: ['"Show mental health insights"', '"Suggest coping strategies"', '"Analyze game predictions"'],
            icon: '🧠'
        },
        'parent-comm': {
            description: 'Manage parent communication, send updates, and track communication history.',
            examples: ['"Send parent update"', '"Show communication history"', '"Generate parent message"'],
            icon: '👨‍👩‍👧'
        },
        'collaboration': {
            description: 'Access collaboration features, share documents, and coordinate with team members.',
            examples: ['"Show collaboration sessions"', '"Share this lesson plan"', '"Who\'s in the collaboration?"'],
            icon: '👥'
        },
        'health': {
            description: 'Track health metrics, plan nutrition, and analyze health trends.',
            examples: ['"Show health data"', '"Create nutrition plan"', '"Track health trends"'],
            icon: '🏥'
        },
        'drivers-ed': {
            description: 'Manage driver\'s education curriculum, track progress, and handle safety incidents.',
            examples: ['"Show driver\'s ed data"', '"Track driving hours"', '"Generate safety report"'],
            icon: '🚗'
        },
        'management': {
            description: 'Access management tools, equipment tracking, and administrative utilities.',
            examples: ['"Show management dashboard"', '"Track equipment"', '"Manage classes"'],
            icon: '⚙️'
        },
        'calendar': {
            description: 'View and manage calendar events, schedule meetings, and track important dates.',
            examples: ['"Show my calendar"', '"Schedule an event"', '"What\'s on my calendar tomorrow?"'],
            icon: '📅'
        },
        'analytics': {
            description: 'View comprehensive analytics, reports, and data visualizations.',
            examples: ['"Show analytics dashboard"', '"Generate a report"', '"Show data trends"'],
            icon: '📊'
        },
        'notifications': {
            description: 'View notifications, alerts, and important updates.',
            examples: ['"Show notifications"', '"What are my alerts?"', '"Check for updates"'],
            icon: '🔔'
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
        // Widget has data - display it
        return `
            <div class="widget-data-display">
                ${JSON.stringify(widget.data, null, 2)}
            </div>
        `;
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
        'attendance': 'Show me attendance for Period 3',
        'teams': 'Create teams for basketball in Period 3',
        'adaptive': 'What accommodations should I use for Sarah?',
        'performance': 'Show me performance trends',
        'safety': 'Show me safety risks for Period 2',
        'insights': 'Show me class insights for Period 3',
        'fitness': 'Show me fitness data',
        'lesson-planning': 'Create a lesson plan on basketball',
        'video': 'Show movement analysis',
        'activities': 'Show me activity data',
        'assessment': 'Generate an assessment',
        'psychology': 'Show mental health insights',
        'parent-comm': 'Send parent update',
        'collaboration': 'Show collaboration sessions',
        'health': 'Show health data',
        'drivers-ed': 'Show driver\'s ed data',
        'management': 'Show management dashboard',
        'calendar': 'Show my calendar',
        'analytics': 'Show analytics dashboard',
        'notifications': 'Show notifications'
    };
    
    const exampleCommand = examples[widgetType] || 'Show me data for this widget';
    const chatInput = document.getElementById('chatInput');
    chatInput.value = exampleCommand;
    chatInput.focus();
    // Auto-resize textarea
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
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
window.hideLoginOverlay = hideLoginOverlay;
window.tryWidgetExample = tryWidgetExample;

