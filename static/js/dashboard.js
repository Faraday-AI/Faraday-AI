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

// Apply theme from localStorage
function applyTheme() {
    const theme = localStorage.getItem('dashboard_theme') || 'dark';
    if (theme === 'light') {
        document.body.classList.add('light-theme');
    } else {
        document.body.classList.remove('light-theme');
    }
    // Update theme toggle button icon
    updateThemeIcon();
}

// Update theme toggle button icon based on current theme
function updateThemeIcon() {
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        const theme = localStorage.getItem('dashboard_theme') || 'dark';
        themeIcon.textContent = theme === 'light' ? '🌙' : '☀️';
    }
}

// Toggle theme between light and dark
function toggleTheme() {
    const currentTheme = localStorage.getItem('dashboard_theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('dashboard_theme', newTheme);
    applyTheme();
    
    // Also update the radio button in settings modal if it's open
    const themeRadio = document.querySelector(`input[name="theme"][value="${newTheme}"]`);
    if (themeRadio) {
        themeRadio.checked = true;
    }
}

async function initializeDashboard() {
    try {
        // Apply theme immediately on page load
        applyTheme();
        
        // Check authentication first
        const token = localStorage.getItem('access_token');
        
        // Check for new session (both guest and authenticated users)
        // Use a timestamp-based approach: if last session was more than 1 hour ago, clear widgets
        // This handles both tab closes and long breaks
        const lastSessionTime = localStorage.getItem('dashboard_last_session_time');
        const currentTime = Date.now();
        const oneHour = 60 * 60 * 1000; // 1 hour in milliseconds
        
        // Check if this is a completely new browser session (sessionStorage cleared)
        const sessionId = sessionStorage.getItem('dashboard_session_id');
        const isNewBrowserSession = !sessionId;
        
        // Check if user changed (different token means different user)
        const lastUserId = localStorage.getItem('dashboard_last_user_id');
        let currentUserId = 'guest';
        if (token) {
            // Try to extract user ID from token payload
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                currentUserId = payload.sub || payload.user_id || payload.teacher_id || payload.email || 'user';
            } catch (e) {
                // Fallback to localStorage values
                currentUserId = localStorage.getItem('teacher_id') || localStorage.getItem('user_email') || 'user';
            }
        }
        const userChanged = lastUserId && lastUserId !== currentUserId;
        
        // Clear widgets if:
        // 1. New browser session (sessionStorage cleared)
        // 2. User changed (different user logged in)
        // 3. More than 1 hour since last session (for guest users only, authenticated users persist)
        const shouldClearWidgets = isNewBrowserSession || userChanged || (!token && (!lastSessionTime || (currentTime - parseInt(lastSessionTime)) > oneHour));
        
        if (shouldClearWidgets) {
            console.log('🔄 New session detected - clearing widgets', {
                isNewBrowserSession,
                userChanged,
                isGuest: !token,
                timeElapsed: lastSessionTime ? (currentTime - parseInt(lastSessionTime)) : 'N/A'
            });
            activeWidgets = [];
            localStorage.removeItem('dashboard_widgets'); // Remove from localStorage
            saveWidgetsToLocalStorage(); // Ensure it's cleared
            // Set flag to prevent reloading from API
            sessionStorage.setItem('widgets_cleared_for_session', 'true');
            localStorage.setItem('dashboard_widgets_cleared', 'true');
            // Clear opening prompt flag so it can play again for new session
            sessionStorage.removeItem('opening_prompt_played');
        }
        
        // Update last session time, session ID, and user ID
        localStorage.setItem('dashboard_last_session_time', currentTime.toString());
        localStorage.setItem('dashboard_last_user_id', currentUserId);
        if (isNewBrowserSession) {
            sessionStorage.setItem('dashboard_session_id', currentTime.toString());
        }
        
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
        
        // Load and display avatar if one is selected
        const selectedAvatarId = localStorage.getItem('selected_avatar_id');
        if (selectedAvatarId) {
            // First load avatars and voices (needed for avatar lookup)
            await loadAvatarsAndVoices(selectedAvatarId, localStorage.getItem('selected_voice_id') || '7');
            // Then display the avatar
            await loadAndDisplayAvatar(selectedAvatarId);
        }
        
        // Setup event listeners
        setupEventListeners();
        
        // Initialize voice recognition if available
        initializeVoiceRecognition();
        
        // Setup opening prompt (plays on first click anywhere)
        // Delay slightly to ensure DOM is fully ready
        setTimeout(() => setupOpeningPrompt(), 100);
        
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

// Update opening prompt for authenticated users with their name
function updateOpeningPromptForAuthenticatedUser(firstName) {
    if (!firstName) {
        return; // No name available, keep guest version
    }
    
    const openingPromptContent = document.getElementById('openingPromptContent');
    if (!openingPromptContent) {
        return; // Opening prompt not found
    }
    
    // Create personalized greeting
    const personalizedGreeting = `<p>Hello ${firstName}, I'm Jasper, your comprehensive AI assistant for Physical Education, what can I do for you today?</p>
                                
                                <p style="margin-top: 0.75rem;"><strong>Try these examples:</strong></p>
                                <ul style="margin-top: 0.5rem; padding-left: 1.5rem; text-align: left;">
                                    <li>"Create a lesson plan on basketball fundamentals"</li>
                                    <li>"Show me attendance patterns for my fourth period class"</li>
                                    <li>"Create balanced teams for Period 3"</li>
                                    <li>"Send a progress update to Sarah's parents - translate to Spanish"</li>
                                </ul>
                                
                                <p style="margin-top: 0.75rem;">The more comprehensive your request is, the more detailed my responses will be. All responses can be modified or enhanced further with more explicit details through our continued conversation.</p>
                                
                                <p style="margin-top: 0.5rem;"><strong>Try this comprehensive example:</strong></p>
                                <p style="margin-top: 0.5rem; font-style: italic; padding-left: 1rem; border-left: 3px solid #4CAF50;">"Create a comprehensive lesson plan for a 6th grade basketball unit that includes detailed learning objectives aligned with state standards, step-by-step activities for a 45-minute class, assessment rubrics, differentiation strategies for students with varying skill levels, safety considerations, and homework assignments. Also include Costa's Levels of Questioning examples and Danielson Framework alignment."</p>
                                
                                <span class="message-time">Just now</span>`;
    
    openingPromptContent.innerHTML = personalizedGreeting;
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
    
    // Setup opening prompt autoplay for guest users
    // Delay slightly to ensure DOM is fully ready and the welcome message is rendered
    setTimeout(() => setupOpeningPrompt(), 500);
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
        
        // Update opening prompt with personalized greeting if user has a name
        const firstName = currentUser.first_name || (name ? name.split(' ')[0] : null);
        updateOpeningPromptForAuthenticatedUser(firstName);
    } catch (error) {
        console.error('Error loading user info:', error);
        // Fallback to email from token if available
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                const email = payload.email || 'User';
                document.getElementById('userName').textContent = email;
                // Try to extract first name from email (before @) or use email as fallback
                const emailName = email.split('@')[0].split('.')[0]; // Get part before @ and before first dot
                updateOpeningPromptForAuthenticatedUser(emailName || null);
            } catch (e) {
                document.getElementById('userName').textContent = 'Guest';
                // Keep guest version of opening prompt
            }
        } else {
            document.getElementById('userName').textContent = 'Guest';
            // Keep guest version of opening prompt
        }
    }
}

// Load dashboard state
async function loadDashboardState() {
    try {
        const token = localStorage.getItem('access_token');
        
        // For authenticated users, try to load from localStorage first
        // For guest users, only load if we have widgets (they were cleared on new session if needed)
        if (token) {
            // Authenticated user - load from localStorage
            if (loadWidgetsFromLocalStorage() && activeWidgets.length > 0) {
                renderWidgets();
            }
        } else {
            // Guest user - widgets should have been cleared in initializeDashboard if needed
            // Just load what's in localStorage (should be empty if it was a new session)
            if (loadWidgetsFromLocalStorage() && activeWidgets.length > 0) {
                renderWidgets();
            } else if (activeWidgets.length === 0) {
                renderWidgets();
            }
        }
        
        if (!token) {
            // Guest mode - if no saved widgets, show empty dashboard
            if (activeWidgets.length === 0) {
                renderWidgets();
            }
            return;
        }
        
        // For authenticated users, try to load from API
        // BUT: If widgets were cleared for this session, don't load from API
        const widgetsWereCleared = sessionStorage.getItem('widgets_cleared_for_session') === 'true' || 
                                   localStorage.getItem('dashboard_widgets_cleared') === 'true';
        
        if (widgetsWereCleared) {
            console.log('🔄 Widgets were cleared for this session - skipping API load');
            // Clear the flag
            sessionStorage.removeItem('widgets_cleared_for_session');
            localStorage.removeItem('dashboard_widgets_cleared');
            // Use empty widgets (already cleared)
            renderWidgets();
            return;
        }
        
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
            // If API fails (401/500 for guest users is expected), use local widgets
            if (activeWidgets.length > 0) {
                renderWidgets();
                return;
            }
            // Only throw error if we have no local widgets and it's not an auth error
            if (response.status !== 401 && response.status !== 500) {
                throw new Error('Failed to load dashboard state');
            }
            // For 401/500, just use empty dashboard (guest mode)
            renderWidgets();
            return;
        }
        
        const state = await response.json();
        
        // Load widgets from API (merge with local if needed)
        if (state.widgets && state.widgets.length > 0) {
            activeWidgets = state.widgets;
            // Normalize widget sizes: ensure all are valid string sizes
            const validSizes = ['small', 'medium', 'large', 'extra-large'];
            activeWidgets.forEach(widget => {
                if (!widget.size || typeof widget.size !== 'string' || !validSizes.includes(widget.size)) {
                    // Normalize invalid sizes (objects, invalid strings, missing) to 'medium'
                    widget.size = 'medium';
                }
            });
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
        // Only log unexpected errors (not auth/network errors for guest users)
        if (!error.message.includes('Failed to load') && !error.message.includes('401') && !error.message.includes('500')) {
            console.error('Error loading dashboard state:', error);
        }
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
            // Don't throw for auth errors (expected for guest users)
            if (response.status === 401 || response.status === 500) {
                return; // Silently fail for guest users
            }
            throw new Error('Failed to initialize dashboard');
        }
        
        const result = await response.json();
        console.log('Dashboard initialized:', result);
    } catch (error) {
        // Only log unexpected errors (not auth/network errors for guest users)
        if (!error.message.includes('Failed to initialize') && !error.message.includes('401') && !error.message.includes('500')) {
            console.error('Error initializing dashboard:', error);
        }
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
    
    // File upload
    const fileUploadBtn = document.getElementById('fileUploadBtn');
    const fileInput = document.getElementById('fileInput');
    if (fileUploadBtn && fileInput) {
        fileUploadBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileUpload);
    }
    
    // Photo upload
    const photoUploadBtn = document.getElementById('photoUploadBtn');
    const photoInput = document.getElementById('photoInput');
    if (photoUploadBtn && photoInput) {
        photoUploadBtn.addEventListener('click', () => photoInput.click());
        photoInput.addEventListener('change', handlePhotoUpload);
    }
    
    // Settings
    document.getElementById('settingsBtn').addEventListener('click', openSettings);
    document.getElementById('closeSettingsModal').addEventListener('click', closeSettings);
    document.getElementById('saveSettings').addEventListener('click', saveSettings);
    document.getElementById('cancelSettings').addEventListener('click', closeSettings);
    
    // Logout
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    // Theme toggle
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }
    
    // Sidebar toggle
    const toggleSidebarBtn = document.getElementById('toggleSidebar');
    if (toggleSidebarBtn) {
        toggleSidebarBtn.addEventListener('click', toggleSidebar);
    } else {
        console.error('❌ toggleSidebar button not found');
    }
    
    // Floating sidebar toggle (when sidebar is collapsed)
    const floatingSidebarToggle = document.getElementById('floatingSidebarToggle');
    if (floatingSidebarToggle) {
        floatingSidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    // Restore sidebar collapsed state
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (sidebarCollapsed) {
        const sidebar = document.querySelector('.widgets-sidebar') || document.getElementById('widgetsSidebar');
        if (sidebar) {
            sidebar.classList.add('collapsed');
            if (toggleSidebarBtn) {
                const icon = toggleSidebarBtn.querySelector('.icon');
                if (icon) {
                    icon.textContent = '→';
                }
            }
            if (floatingSidebarToggle) {
                floatingSidebarToggle.style.display = 'flex';
            }
        }
    }
    
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
    
    document.getElementById('customizeLayoutBtn').addEventListener('click', openLayoutCustomization);
    document.getElementById('closeLayoutModal').addEventListener('click', closeLayoutCustomization);
    document.getElementById('saveLayoutBtn').addEventListener('click', saveLayoutCustomization);
    document.getElementById('cancelLayoutBtn').addEventListener('click', closeLayoutCustomization);
    document.getElementById('resetLayoutBtn').addEventListener('click', resetLayoutToDefault);
    
    // Panel resize and collapse functionality
    initializePanelResize();
    initializePanelCollapse();
    
    // Log viewer
    initializeLogViewer();
}

// Setup opening prompt - plays welcome message on first click anywhere
function setupOpeningPrompt() {
    originalConsole.log('🎯 setupOpeningPrompt called');
    
    // Check if opening prompt autoplay is disabled in settings
    const enableOpeningPromptAutoplay = localStorage.getItem('enable_opening_prompt_autoplay') !== 'false';
    if (!enableOpeningPromptAutoplay) {
        originalConsole.log('⏭️ Opening prompt autoplay is disabled in settings, skipping');
        return; // Autoplay is disabled, don't set up
    }
    
    // For guest users, always allow opening prompt to play (clear flag if it exists)
    // For authenticated users, check if it was already played this session
    const token = localStorage.getItem('access_token');
    const isGuest = !token;
    
    if (isGuest) {
        // Guest users: clear the flag so opening prompt can play on every page load
        sessionStorage.removeItem('opening_prompt_played');
        originalConsole.log('👤 Guest user detected - clearing opening prompt flag to allow playback');
    } else {
        // Authenticated users: check if opening prompt has already been played this session
        const openingPromptPlayed = sessionStorage.getItem('opening_prompt_played');
        if (openingPromptPlayed === 'true') {
            originalConsole.log('⏭️ Opening prompt already played this session, skipping');
            return; // Already played, don't set up again
        }
    }
    
    // Extract the opening prompt text from the dashboard
    // Find the first AI message in the chat (the opening prompt)
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) {
        originalConsole.warn('⚠️ Chat messages container not found, retrying in 500ms...');
        // Retry after a short delay in case DOM isn't ready yet
        setTimeout(() => setupOpeningPrompt(), 500);
        return;
    }
    
    const firstAIMessage = chatMessages.querySelector('.message.ai-message');
    if (!firstAIMessage) {
        originalConsole.warn('⚠️ Opening prompt message not found, retrying in 500ms...');
        // Retry after a short delay in case DOM isn't ready yet
        setTimeout(() => setupOpeningPrompt(), 500);
        return;
    }
    
    const messageContent = firstAIMessage.querySelector('.message-content');
    if (!messageContent) {
        originalConsole.warn('⚠️ Message content not found');
        return;
    }
    
    originalConsole.log('✅ Found opening prompt message, extracting text...');
    
    // Extract all text content, preserving structure but removing HTML tags
    // Clone the element to avoid modifying the original
    const contentClone = messageContent.cloneNode(true);
    
    // Remove the message-time span if it exists
    const timeSpan = contentClone.querySelector('.message-time');
    if (timeSpan) {
        timeSpan.remove();
    }
    
    // Convert to plain text, preserving line breaks
    // Replace <p> tags with line breaks
    contentClone.querySelectorAll('p').forEach(p => {
        p.innerHTML = p.textContent + '\n\n';
    });
    
    // Replace <li> tags with bullet points and line breaks
    contentClone.querySelectorAll('li').forEach(li => {
        li.innerHTML = '• ' + li.textContent + '\n';
    });
    
    // Replace <strong> tags with emphasis markers
    contentClone.querySelectorAll('strong').forEach(strong => {
        strong.innerHTML = strong.textContent; // Keep text but remove bold formatting for TTS
    });
    
    // Get the final text content
    let welcomeMessage = contentClone.textContent || contentClone.innerText;
    
    // Clean up extra whitespace and normalize line breaks
    welcomeMessage = welcomeMessage
        .replace(/\n{3,}/g, '\n\n') // Replace 3+ newlines with 2
        .replace(/[ \t]+/g, ' ') // Replace multiple spaces/tabs with single space
        .trim();
    
    // If we couldn't extract text, use a fallback
    if (!welcomeMessage || welcomeMessage.length < 50) {
        welcomeMessage = "Hello! I'm your comprehensive AI assistant for Physical Education. I have access to an extensive suite of capabilities designed to help you manage every aspect of your PE program. You can ask me to do anything - I handle all features whether widgets are on your dashboard or not.";
        originalConsole.warn('⚠️ Using fallback opening prompt');
    }
    
    // Create a temporary button element for speakMessage (it needs a button parameter)
    const tempButton = document.createElement('button');
    tempButton.style.display = 'none';
    document.body.appendChild(tempButton);
    
    // OPTIMIZATION: Pre-generate audio for opening prompt to make autoplay instant
    // Fetch audio in the background so it's ready when user clicks
    let preGeneratedAudio = null;
    let preGeneratedAudioUrl = null;
    
    // For opening prompt, use the FULL text (up to 5000 chars) to ensure complete message
    // Since this is pre-fetched in background, we can use more text without blocking
    // The opening prompt is important and should be read completely
    const openingPromptText = welcomeMessage.length > 5000 ? welcomeMessage.substring(0, 5000) : welcomeMessage;
    originalConsole.log(`📝 Opening prompt text length: ${welcomeMessage.length} chars, using: ${openingPromptText.length} chars for pre-fetch`);
    
    // Pre-fetch audio in background (non-blocking)
    const preFetchAudio = async () => {
        try {
            originalConsole.log('🎵 Pre-fetching opening prompt audio...');
            const voiceSpeed = parseFloat(localStorage.getItem('voice_speed') || '1');
            const voicePitch = parseFloat(localStorage.getItem('voice_pitch') || '1');
            const voiceLanguage = localStorage.getItem('voice_language') || 'en-US';
            const selectedVoiceId = localStorage.getItem('selected_voice_id') || '7';
            
            // Use voice-sample endpoint for faster response (it's optimized)
            const token = localStorage.getItem('access_token');
            const headers = {
                'Content-Type': 'application/json'
            };
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            
            const params = new URLSearchParams({
                voice_id: selectedVoiceId,
                text: openingPromptText,
                rate: voiceSpeed.toString(),
                pitch: ((voicePitch - 1) * 50).toString(),
            });
            
            const response = await fetch(`${API_BASE_URL}/text-to-speech/voice-sample?${params.toString()}`, {
                method: 'POST',
                headers: headers
            });
            
            if (response.ok) {
                const audioBlob = await response.blob();
                preGeneratedAudioUrl = URL.createObjectURL(audioBlob);
                preGeneratedAudio = new Audio(preGeneratedAudioUrl);
                preGeneratedAudio.preload = 'auto';
                // Pre-load the audio
                await new Promise((resolve, reject) => {
                    preGeneratedAudio.addEventListener('canplaythrough', resolve, { once: true });
                    preGeneratedAudio.addEventListener('error', reject, { once: true });
                    preGeneratedAudio.load();
                });
                originalConsole.log('✅ Opening prompt audio pre-fetched and ready');
            } else {
                originalConsole.warn('⚠️ Failed to pre-fetch opening prompt audio, will generate on click');
            }
        } catch (error) {
            originalConsole.warn('⚠️ Error pre-fetching opening prompt audio:', error);
            // Fallback: will generate on click
        }
    };
    
    // Start pre-fetching immediately (non-blocking)
    preFetchAudio();
    
    // One-time click listener for the entire document
    const handleFirstClick = async (event) => {
        // Remove the listener immediately so it only fires once
        document.removeEventListener('click', handleFirstClick, true);
        document.removeEventListener('touchstart', handleFirstClick, true);
        
        // Mark as played in sessionStorage
        sessionStorage.setItem('opening_prompt_played', 'true');
        
        originalConsole.log('🎵 User clicked - playing opening prompt...');
        
        // If audio is pre-generated, play it immediately (FAST PATH)
        if (preGeneratedAudio && preGeneratedAudioUrl) {
            try {
                originalConsole.log('⚡ Using pre-generated audio (instant playback)');
                
                // Stop any existing audio
                if (window.audioManager && window.audioManager.currentAudio) {
                    window.audioManager.currentAudio.pause();
                }
                
                // Set up audio manager
                window.audioManager.currentAudio = preGeneratedAudio;
                window.audioManager.currentButton = tempButton;
                window.audioManager.currentAudioUrl = preGeneratedAudioUrl;
                
                // Set up event handlers
                const handleEnded = () => {
                    tempButton.classList.remove('playing');
                    tempButton.textContent = '🔊';
                    tempButton.disabled = false;
                    setTimeout(() => {
                        if (window.audioManager.currentAudioUrl === preGeneratedAudioUrl) {
                            URL.revokeObjectURL(preGeneratedAudioUrl);
                            window.audioManager.currentAudioUrl = null;
                        }
                    }, 100);
                    if (window.audioManager.currentAudio === preGeneratedAudio) {
                        window.audioManager.currentAudio = null;
                    }
                };
                
                preGeneratedAudio.onended = handleEnded;
                preGeneratedAudio.onerror = (e) => {
                    console.error('Error playing pre-generated audio:', e);
                    handleEnded();
                };
                
                // Play immediately - audio is already loaded
                const playPromise = preGeneratedAudio.play();
                if (playPromise) {
                    playPromise.then(() => {
                        originalConsole.log('✅ Opening prompt playing (pre-generated)');
                        tempButton.classList.add('playing');
                        tempButton.textContent = '⏸️';
                    }).catch((error) => {
                        originalConsole.warn('⚠️ Autoplay blocked for pre-generated audio:', error);
                        tempButton.textContent = '🔊';
                    });
                }
                return; // Success - exit early
            } catch (error) {
                originalConsole.warn('⚠️ Error playing pre-generated audio, falling back to on-demand generation:', error);
                // Fall through to on-demand generation
            }
        }
        
        // FALLBACK: Generate audio on-demand (slower but works if pre-fetch failed)
        originalConsole.log('🔄 Generating opening prompt audio on-demand...');
        try {
            // Use the FULL welcome message (not truncated) to ensure complete message
            // speakMessage will handle truncation based on useFullText parameter
            await speakMessage(tempButton, welcomeMessage, true, true); // Use full text for opening prompt
            originalConsole.log('✅ Opening prompt played successfully (on-demand)');
        } catch (error) {
            // If autoplay fails, that's okay - user can click speaker button later
            originalConsole.log('⚠️ Opening prompt autoplay blocked, but audio is ready. Error:', error);
        }
        
        // Clean up temp button after a delay
        setTimeout(() => {
            if (tempButton.parentNode) {
                document.body.removeChild(tempButton);
            }
        }, 1000);
    };
    
    // Add listeners for both click and touch (mobile support)
    // Use capture phase to catch clicks anywhere
    document.addEventListener('click', handleFirstClick, true);
    document.addEventListener('touchstart', handleFirstClick, true);
    
    originalConsole.log('🎯 Opening prompt listener set up - will play on first click anywhere');
    originalConsole.log('📝 Extracted opening prompt length:', welcomeMessage.length, 'characters');
    originalConsole.log('📝 First 100 chars:', welcomeMessage.substring(0, 100));
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

// Handle file upload
function handleFileUpload(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    const chatInput = document.getElementById('chatInput');
    const fileNames = Array.from(files).map(file => file.name).join(', ');
    
    // Add file names to the input
    if (chatInput.value.trim()) {
        chatInput.value += `\n[Files: ${fileNames}]`;
    } else {
        chatInput.value = `[Files: ${fileNames}]`;
    }
    
    // Auto-resize textarea
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    
    // Store files for sending with message
    chatInput._attachedFiles = files;
    
    // Reset input to allow selecting same file again
    event.target.value = '';
    
    console.log('📎 Files selected:', fileNames);
}

// Handle photo upload
function handlePhotoUpload(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    const chatInput = document.getElementById('chatInput');
    const photoNames = Array.from(files).map(file => file.name).join(', ');
    
    // Add photo names to the input
    if (chatInput.value.trim()) {
        chatInput.value += `\n[Photos: ${photoNames}]`;
    } else {
        chatInput.value = `[Photos: ${photoNames}]`;
    }
    
    // Auto-resize textarea
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    
    // Store photos for sending with message
    chatInput._attachedPhotos = files;
    
    // Reset input to allow selecting same file again
    event.target.value = '';
    
    console.log('📷 Photos selected:', photoNames);
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
        const isAuthenticated = !!token;
        
        // Prepare headers
        const headers = {
            'Content-Type': 'application/json'
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Route authenticated users to advanced AI Assistant endpoint
        // Guest users use the simple guest chat endpoint
        let response;
        if (isAuthenticated) {
            // Advanced endpoint for authenticated/paying users
            // Uses conversation management, message history, analytics
            response = await fetch(`${API_BASE_URL}/ai-assistant/chat`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    message: message,
                    conversation_id: null, // Will create new or use existing
                    conversation_type: 'general_chat',
                    metadata: {
                        context: chatHistory.slice(-1).map(msg => ({
                            role: msg.role,
                            content: msg.content.length > 300 ? msg.content.substring(0, 300) + '...' : msg.content
                        }))
                    }
                })
            });
        } else {
            // Simple endpoint for guest/free trial users
            const context = chatHistory.slice(-1).map(msg => ({
                role: msg.role,
                content: msg.content.length > 300 ? msg.content.substring(0, 300) + '...' : msg.content
            }));
            
            // Try to extract user's name from the message if not already stored
            let guestName = sessionStorage.getItem('guest_name');
            if (!guestName) {
                // Try to extract name from message (simple patterns)
                // Updated patterns to handle lowercase names and be more flexible
                const trimmedMessage = message.trim();
                const namePatterns = [
                    // Patterns with phrases before the name
                    /(?:my name is|i'm|i am|call me|it's|it is|i go by|people call me)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)/i,
                    /(?:name is|name's|name:)\s+([a-zA-Z]+)/i,
                    /(?:i'm|i am)\s+([a-zA-Z]+)/i, // "i'm mike" or "i am mike"
                    // Just a name by itself (must be a single word or two words, all letters)
                    /^([a-zA-Z]{2,20})(?:\s+[a-zA-Z]{2,20})?$/ // Matches "mike" or "mike smith" but not "mike123"
                ];
                
                for (const pattern of namePatterns) {
                    const match = trimmedMessage.match(pattern);
                    if (match && match[1]) {
                        guestName = match[1].trim();
                        // Extract first name only (first word)
                        guestName = guestName.split(' ')[0];
                        // Validate it's a reasonable name (2-20 chars, only letters, no numbers/special chars)
                        if (guestName.length >= 2 && guestName.length <= 20 && /^[a-zA-Z]+$/.test(guestName)) {
                            // Capitalize first letter, lowercase the rest
                            guestName = guestName.charAt(0).toUpperCase() + guestName.slice(1).toLowerCase();
                            sessionStorage.setItem('guest_name', guestName);
                            console.log(`✅ Extracted and stored guest name: ${guestName} from message: "${message}"`);
                            break;
                        }
                    }
                }
                
                // If no pattern matched, check if the entire message is just a name (very simple case)
                if (!guestName && trimmedMessage.length >= 2 && trimmedMessage.length <= 20) {
                    // Check if message is just letters (no spaces, no special chars, no numbers)
                    if (/^[a-zA-Z]+$/.test(trimmedMessage)) {
                        guestName = trimmedMessage.charAt(0).toUpperCase() + trimmedMessage.slice(1).toLowerCase();
                        sessionStorage.setItem('guest_name', guestName);
                        console.log(`✅ Extracted and stored guest name (simple match): ${guestName} from message: "${message}"`);
                    }
                }
            }
            
            // Add guest name to headers if available
            if (guestName) {
                headers['X-Guest-Name'] = guestName;
            }
            
            response = await fetch(`${API_BASE_URL}/chat/message`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    message: message,
                    context: context
                })
            });
        }
        
        if (!response.ok) {
            let errorText = '';
            let errorDetail = '';
            try {
                errorText = await response.text();
                console.error('❌ Server error response:', errorText);
                // Try to parse JSON error detail
                try {
                    const errorJson = JSON.parse(errorText);
                    errorDetail = errorJson.detail || errorText;
                } catch {
                    errorDetail = errorText;
                }
            } catch (e) {
                errorText = `Status: ${response.status} ${response.statusText}`;
                errorDetail = errorText;
            }
            
            // Check for quota/billing errors
            if (response.status === 503 || errorDetail.toLowerCase().includes('quota') || 
                errorDetail.toLowerCase().includes('billing') || 
                errorDetail.toLowerCase().includes('insufficient_quota')) {
                throw new Error('AI service quota exceeded. Please check your OpenAI account billing or try again later.');
            }
            
            throw new Error(`Failed to send message (${response.status}): ${errorDetail}`);
        }
        
        const result = await response.json();
        console.log('✅ Chat response received:', result);
        console.log('📊 Widget data:', result.widget_data);
        
        // For guest users, try to extract name from AI response if not already stored
        if (!isAuthenticated && !sessionStorage.getItem('guest_name') && result.response) {
            // Look for patterns where AI confirms or uses the name
            const nameConfirmationPatterns = [
                /(?:nice to meet you|hello|hi|great|thanks),?\s+([A-Z][a-z]+)/i,
                /(?:hello|hi),?\s+([A-Z][a-z]+),/i,
                /(?:call you|your name is|you're)\s+([A-Z][a-z]+)/i
            ];
            
            for (const pattern of nameConfirmationPatterns) {
                const match = result.response.match(pattern);
                if (match && match[1]) {
                    let extractedName = match[1].trim();
                    // Extract first name only
                    extractedName = extractedName.split(' ')[0];
                    // Capitalize first letter
                    extractedName = extractedName.charAt(0).toUpperCase() + extractedName.slice(1).toLowerCase();
                    if (extractedName.length >= 2 && extractedName.length <= 20) {
                        sessionStorage.setItem('guest_name', extractedName);
                        console.log(`✅ Extracted guest name from AI response: ${extractedName}`);
                        break;
                    }
                }
            }
        }
        
        // Add AI response to chat
        if (result.response) {
            // CRITICAL: Add message to chat and start autoplay FIRST
            // This must happen immediately within the user interaction context
            // Widget updates will happen AFTER autoplay starts
            console.log('🔊 About to call addMessageToChat with autoplay=true');
            addMessageToChat('ai', result.response, true); // Pass true to auto-speak
            console.log('🔊 addMessageToChat called, checking if autoplay was triggered...');
            
            // Update chat history
            chatHistory.push({ role: 'user', content: message });
            chatHistory.push({ role: 'assistant', content: result.response });
            
            // Store widget data temporarily - we'll update widgets AFTER autoplay starts
            const pendingWidgetData = result.widget_data;
            const pendingWidgets = result.widgets;
            
            // Find the message div to get the audio play promise
            const chatMessages = document.getElementById('chatMessages');
            const lastMessage = chatMessages?.lastElementChild;
            const audioPlayPromise = lastMessage?._audioPlayPromise;
            
            // CRITICAL: Wait for audio play() call to be initiated (not completed)
            // Once play() is called, Safari has queued it and we can safely update widgets
            // The play() call itself must happen synchronously within user interaction context
            const updateWidgets = () => {
                // Check if AI wants to add/update multiple widgets
                if (pendingWidgets && Array.isArray(pendingWidgets) && pendingWidgets.length > 0) {
                    console.log(`🔄 Processing ${pendingWidgets.length} widgets from widgets array`);
                    // Process each widget in the array
                    pendingWidgets.forEach((widget, index) => {
                        if (widget && widget.type && widget.data) {
                            console.log(`🔄 Updating widget ${index + 1}/${pendingWidgets.length}: ${widget.type}`);
                            updateWidgetWithData(widget);
                        }
                    });
                }
                // Also check widget_data for backward compatibility (single widget)
                else if (pendingWidgetData) {
                    console.log('🔄 Updating widget with data:', pendingWidgetData);
                    updateWidgetWithData(pendingWidgetData);
                } else {
                    console.log('⚠️ No widget_data or widgets in response');
                }
            };
            
            if (audioPlayPromise) {
                // CRITICAL: Wait for audio blob to be received AND play() to be called
                // Widget updates break Safari's interaction context, so we must wait
                // The audio fetch is async and takes ~5-8 seconds, but we need to wait for it
                console.log('🔊 Audio fetch started - deferring widget updates to preserve interaction context');
                
                // Wait for the audio blob to be received and play() to be called
                // The promise resolves when play() is called (not when it completes)
                audioPlayPromise.then(() => {
                    console.log('✅ Audio play() called successfully - now safe to update widgets');
                    // Now that play() has been called, we can safely update widgets
                    // Use a small delay to ensure play() is fully queued by Safari
                    setTimeout(updateWidgets, 100);
                }).catch((error) => {
                    console.log('⚠️ Audio play() blocked or failed:', error.name);
                    // Even if autoplay failed, update widgets after a delay
                    // The audio is still ready for manual play
                    setTimeout(updateWidgets, 500);
                });
            } else {
                // No audio play promise (autoplay disabled or button not found)
                // Update widgets immediately
                setTimeout(updateWidgets, 50);
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
            // Check for specific error types and provide user-friendly messages
            if (error.message.includes('quota') || error.message.includes('billing')) {
                errorMessage = 'I\'m sorry, but the AI service is currently unavailable due to quota limits. Please check your OpenAI account billing settings or try again later. If you\'re the administrator, you may need to add credits to your OpenAI account.';
            } else if (error.message.includes('timeout') || error.message.includes('Load failed') || error.message.includes('network') || error.message.includes('connection')) {
                errorMessage = 'The request took too long to process or the connection was lost. This can happen with complex requests like lesson plans. Please try again - the system is working on your request.';
            } else if (error.message.includes('authentication') || error.message.includes('API key')) {
                errorMessage = 'There was an authentication error with the AI service. Please contact support.';
            } else {
                errorMessage += error.message;
            }
        } else {
            errorMessage += 'Please try again or log in for full functionality.';
        }
        
        addMessageToChat('ai', errorMessage, true); // Enable autoplay for error messages too
        updateAvatarStatus('ready', 'Ready to help');
    }
}

// Add message to chat
function addMessageToChat(role, content, autoSpeak = false, widgetData = null) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const avatar = role === 'user' ? '👤' : '🤖';
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Add speaker button for AI messages
    let speakerButton = '';
    if (role === 'ai') {
        // Store message content in a data attribute to avoid escaping issues
        const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        messageDiv.setAttribute('data-message-id', messageId);
        window[`msg_${messageId}`] = content; // Store content globally temporarily
        
        speakerButton = `
        <button class="message-speaker-btn" onclick="speakMessageFromId('${messageId}')" 
                aria-label="Speak message" title="Play audio">
            🔊
        </button>
    `;
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem;">
                <p style="flex: 1; margin: 0;">${escapeHtml(content)}</p>
                ${speakerButton}
            </div>
            <span class="message-time">${time}</span>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Auto-speak AI messages if enabled
    console.log('🔊 addMessageToChat autoplay check:', { role, autoSpeak, isAI: role === 'ai', willAttemptAutoplay: role === 'ai' && autoSpeak });
    if (role === 'ai' && autoSpeak) {
        const enableAIVoice = localStorage.getItem('enable_ai_voice') !== 'false'; // Default to true
        console.log('🔊 Auto-speak check:', { enableAIVoice, autoSpeak, role });
        if (enableAIVoice) {
            // Start fetching audio IMMEDIATELY and SYNCHRONOUSLY to preserve user interaction context
            // The user just sent a message, so we're still in their interaction context
            // DO NOT use requestAnimationFrame or setTimeout - they break the interaction chain
            // Use a small synchronous delay to ensure DOM is ready, then find button
            let speakerBtn = null;
            // Try to find button immediately
            speakerBtn = messageDiv.querySelector('.message-speaker-btn');
            // If not found, try again synchronously (DOM might not be ready yet)
            if (!speakerBtn) {
                // Force a synchronous DOM update by accessing offsetHeight
                messageDiv.offsetHeight; // Force reflow
                speakerBtn = messageDiv.querySelector('.message-speaker-btn');
            }
            console.log('🔊 Auto-speak: speaker button found?', !!speakerBtn, 'messageDiv:', messageDiv, 'innerHTML length:', messageDiv.innerHTML.length);
            if (speakerBtn) {
                // Stop any existing audio before auto-speaking
                // But don't clear everything - just pause to preserve context
                if (window.audioManager && window.audioManager.currentAudio) {
                    try {
                        const audio = window.audioManager.currentAudio;
                        audio.pause();
                        audio.currentTime = 0;
                        // Don't clear src immediately - wait until new audio is ready
                    } catch (e) {
                        console.warn('Error pausing audio:', e);
                    }
                }
                // Start fetching audio immediately - call directly, no delays
                console.log('🔊 Auto-speak: Starting audio fetch immediately (synchronous call)...');
                // CRITICAL: Call speakMessage IMMEDIATELY and synchronously to preserve user interaction context
                // Do NOT await it - let it run in the background
                // The play() call inside speakMessage must happen synchronously when blob is received
                // For longer responses (like lesson plans), use more text for autoplay
                // Check if response is long or contains lesson plan keywords
                // Lower threshold (1500) to catch guest responses that might be shorter
                const isLongResponse = content.length > 1500;
                const contentLower = content.toLowerCase();
                // More comprehensive lesson plan detection - check for multiple indicators
                const hasLessonKeywords = contentLower.includes('lesson plan') || 
                                        contentLower.includes('learning objectives') ||
                                        contentLower.includes('curriculum standards') ||
                                        contentLower.includes('danielson framework') ||
                                        contentLower.includes("costa's levels") ||
                                        contentLower.includes('exit ticket') ||
                                        contentLower.includes('worksheet') ||
                                        contentLower.includes('rubric');
                const hasEducationKeywords = (contentLower.includes('grade level') || contentLower.includes('grade')) && 
                                           (contentLower.includes('subject') || contentLower.includes('students will') || contentLower.includes('objectives'));
                const isLessonPlan = hasLessonKeywords || hasEducationKeywords;
                // For any response over 2000 chars OR containing lesson plan keywords, use more text
                const useFullTextForAutoplay = isLongResponse || isLessonPlan;
                console.log('🔊 Autoplay text length decision:', { 
                    contentLength: content.length, 
                    isLongResponse, 
                    hasLessonKeywords,
                    hasEducationKeywords,
                    isLessonPlan, 
                    useFullTextForAutoplay,
                    maxChars: useFullTextForAutoplay ? 5000 : 1000,
                    preview: content.substring(0, 100) + '...'
                });
                const audioPlayPromise = speakMessage(speakerBtn, content, true, useFullTextForAutoplay);
                
                // Store promise on message div so widget updates can wait for play() to be called
                messageDiv._audioPlayPromise = audioPlayPromise;
                
                // Handle the promise asynchronously (don't block)
                audioPlayPromise.then(() => {
                    console.log('✅ Auto-speak: play() called successfully');
                    // Now that new audio is ready, clean up old audio
                    if (window.audioManager && window.audioManager.currentAudioUrl) {
                        const oldUrl = window.audioManager.currentAudioUrl;
                        // Check if this is the old URL (not the new one)
                        const newBtn = messageDiv.querySelector('.message-speaker-btn');
                        const newUrl = newBtn?.getAttribute('data-audio-url');
                        if (oldUrl !== newUrl) {
                            // Old URL - revoke it
                            try {
                                URL.revokeObjectURL(oldUrl);
                            } catch (e) {
                                console.warn('Error revoking old URL:', e);
                            }
                        }
                    }
                }).catch(error => {
                    console.log('⚠️ Auto-speak error:', error.name, error.message);
                    // If autoplay is blocked, that's okay - user can click the button
                    if (error.name === 'NotAllowedError' || error.name === 'NotSupportedError') {
                        console.log('ℹ️ Autoplay blocked (expected on some browsers). User can click speaker button.');
                    } else if (error.message && (
                        error.message.includes('Load failed') || 
                        error.message.includes('network') || 
                        error.message.includes('fetch') ||
                        error.message.includes('502') ||
                        error.message.includes('503') ||
                        error.message.includes('504') ||
                        error.message.includes('TTS request failed: 5')
                    )) {
                        console.warn('⚠️ Network/server error during autoplay (retries exhausted). User can click speaker button to retry.');
                    } else {
                        console.error('Error in auto-speak:', error);
                    }
                });
            } else {
                // If button not found yet, try multiple times synchronously
                // Force DOM reflow to ensure button is available
                messageDiv.offsetHeight; // Force reflow
                let btn = messageDiv.querySelector('.message-speaker-btn');
                
                // Try one more time after a micro-delay (using Promise.resolve to queue it)
                if (!btn) {
                    // Use a synchronous microtask to check again
                    Promise.resolve().then(() => {
                        btn = messageDiv.querySelector('.message-speaker-btn');
                        if (btn) {
                            if (window.audioManager && window.audioManager.currentAudio) {
                                try {
                                    const audio = window.audioManager.currentAudio;
                                    audio.pause();
                                    audio.currentTime = 0;
                                } catch (e) {
                                    console.warn('Error pausing audio:', e);
                                }
                            }
                            console.log('🔊 Auto-speak: Starting audio fetch (button found on retry)...');
                            speakMessage(btn, content, true).catch(error => {
                                if (error.name !== 'NotAllowedError' && error.name !== 'NotSupportedError') {
                                    console.error('Error in auto-speak:', error);
                                }
                            });
                        } else {
                            console.warn('⚠️ Auto-speak: Speaker button not found in message after retries');
                            console.warn('⚠️ Message div HTML:', messageDiv.innerHTML.substring(0, 200));
                        }
                    });
                } else {
                    // Button found on retry - proceed with autoplay
                    if (window.audioManager && window.audioManager.currentAudio) {
                        try {
                            const audio = window.audioManager.currentAudio;
                            audio.pause();
                            audio.currentTime = 0;
                        } catch (e) {
                            console.warn('Error pausing audio:', e);
                        }
                    }
                    console.log('🔊 Auto-speak: Starting audio fetch (button found on retry)...');
                    speakMessage(btn, content, true).catch(error => {
                        if (error.name !== 'NotAllowedError' && error.name !== 'NotSupportedError') {
                            console.error('Error in auto-speak:', error);
                        }
                    });
                }
            }
        } else {
            console.log('🔇 Auto-speak disabled in settings');
        }
    }
    
    // Clean up stored message after a delay (to allow auto-speak to work)
    if (role === 'ai' && messageDiv.getAttribute('data-message-id')) {
        const messageId = messageDiv.getAttribute('data-message-id');
        setTimeout(() => {
            // Keep message in memory for 5 minutes, then clean up
            setTimeout(() => {
                if (window[`msg_${messageId}`]) {
                    delete window[`msg_${messageId}`];
                }
            }, 5 * 60 * 1000);
        }, 1000);
    }
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
    
    // CRITICAL: Don't update widgets if voice recording is active
    // This prevents DOM manipulation from breaking Safari's interaction context
    if (isVoiceActive) {
        console.log('⚠️ Voice recording active - deferring widget updates');
        // Defer widget updates until voice recording is done
        setTimeout(() => {
            if (!isVoiceActive) {
                handleWidgetUpdates(widgets);
            } else {
                // Still recording - try again later
                setTimeout(() => handleWidgetUpdates(widgets), 1000);
            }
        }, 500);
        return;
    }
    
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
    if (!widgetData || !widgetData.type) {
        console.warn('⚠️ Invalid widget data:', widgetData);
        return;
    }
    
    // CRITICAL: Don't update widgets if voice recording is active
    // This prevents DOM manipulation from breaking Safari's interaction context
    if (isVoiceActive) {
        console.log('⚠️ Voice recording active - deferring widget update');
        // Defer widget update until voice recording is done
        setTimeout(() => {
            if (!isVoiceActive) {
                updateWidgetWithData(widgetData);
            } else {
                // Still recording - try again later
                setTimeout(() => updateWidgetWithData(widgetData), 1000);
            }
        }, 500);
        return;
    }
    
    try {
        // Find existing widget of this type
        let widget = activeWidgets.find(w => (w.type || w.widget_type) === widgetData.type);
        
        if (!widget) {
            // Widget doesn't exist - add it automatically
            // Ensure is_preview is NOT set for authenticated users
            const widgetDataCopy = { ...widgetData };
            if (widgetDataCopy.data) {
                widgetDataCopy.data = { ...widgetDataCopy.data };
                // Remove any preview flags for authenticated users
                delete widgetDataCopy.data.is_preview;
                delete widgetDataCopy.data.preview_message;
            }
            
            const newWidget = {
                id: `widget-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                type: widgetDataCopy.type,
                name: getWidgetTitle(widgetDataCopy.type),
                configuration: {},
                position: null,
                size: 'medium', // String, not object: 'small', 'medium', 'large', 'extra-large'
                created_at: new Date().toISOString(),
                is_active: true,
                is_visible: true,
                data: widgetDataCopy.data || {}
            };
            addWidgetToDashboard(newWidget);
            saveWidgetsToLocalStorage();
        } else {
            // Update existing widget with new data
            // Ensure is_preview is NOT set for authenticated users
            const updatedData = { ...(widgetData.data || widget.data || {}) };
            delete updatedData.is_preview;
            delete updatedData.preview_message;
            widget.data = updatedData;
            saveWidgetsToLocalStorage();
        }
        
        renderWidgets();
    } catch (error) {
        console.error('❌ Error updating widget with data:', error);
        console.error('Widget data:', widgetData);
        if (typeof showError === 'function') {
            showError('Failed to load widget. Please try again.');
        }
    }
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
            size: 'medium', // String, not object: 'small', 'medium', 'large', 'extra-large'
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
        // Normalize widget sizes before saving to ensure consistency
        const validSizes = ['small', 'medium', 'large', 'extra-large'];
        const normalizedWidgets = activeWidgets.map(widget => {
            const normalizedWidget = { ...widget };
            if (!normalizedWidget.size || typeof normalizedWidget.size !== 'string' || !validSizes.includes(normalizedWidget.size)) {
                // Normalize invalid sizes (objects, invalid strings, missing) to 'medium'
                normalizedWidget.size = 'medium';
            }
            return normalizedWidget;
        });
        localStorage.setItem('dashboard_widgets', JSON.stringify(normalizedWidgets));
        // Update activeWidgets with normalized sizes to keep them in sync
        activeWidgets = normalizedWidgets;
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
    
    if (!widgetsGrid) {
        console.error('❌ Widgets grid not found');
        return;
    }
    
    if (activeWidgets.length === 0) {
        widgetsGrid.innerHTML = `
            <div class="widget-placeholder">
                <p>👋 Start a conversation with your AI assistant to add widgets to your dashboard</p>
                <p class="hint-text">Try saying: "Show me attendance patterns" or "Display my class insights"</p>
            </div>
        `;
        return;
    }
    
    try {
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
        // Normalize size: if it's an object, convert to 'medium'; if invalid string, default to 'medium'
        let widgetSize = widget.size || 'medium';
        if (typeof widgetSize !== 'string') {
            // If size is an object (old format like {width: 2, height: 2}), convert to 'medium'
            widgetSize = 'medium';
        }
        const validSizes = ['small', 'medium', 'large', 'extra-large'];
        if (!validSizes.includes(widgetSize)) {
            widgetSize = 'medium';
        }
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
    } catch (error) {
        console.error('❌ Error rendering widgets:', error);
        console.error('Active widgets:', activeWidgets);
        widgetsGrid.innerHTML = `
            <div class="widget-placeholder">
                <p>⚠️ Error loading widgets. Please refresh the page.</p>
            </div>
        `;
    }
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
    try {
        if (!data || typeof data !== 'object') {
            return '<div class="widget-data-display"><p>No data available</p></div>';
        }
        
        // Check if this is a preview/teaser widget for guest users (applies to ALL widget types)
        // For authenticated users, NEVER show preview (even if flag is set)
        const isAuthenticated = !!localStorage.getItem('access_token');
        const isPreview = !isAuthenticated && data.is_preview === true;
        
        // Format based on widget type and data structure
        let html = '<div class="widget-data-display' + (isPreview ? ' widget-preview' : '') + '">';
        
        // Show preview banner for guest users (generic, works for all widget types)
        if (isPreview) {
            html += '<div class="widget-preview-banner">';
            html += '<div class="preview-banner-content">';
            html += '<span class="preview-badge">👁️ PREVIEW</span>';
            html += '<p class="preview-message">' + (data.preview_message || 'This is a preview of what a complete widget would include. <strong>Sign up for a premium account</strong> to generate full, professional-grade content with advanced features.') + '</p>';
            html += '</div>';
            html += '</div>';
        }
    
    // Special handling for lesson plan widget
    // Check for lesson plan data - be more lenient to catch all lesson plan widgets
    if (widgetType === 'lesson-planning' && data && (data.title || data.description || data.objectives || data.introduction || data.activities || data.materials || data.danielson_framework || data.costas_questioning || data.curriculum_standards || data.exit_ticket || data.worksheets || data.assessments || data.rubrics)) {
        console.log('📋 Rendering lesson-planning widget with data:', {
            hasTitle: !!data.title,
            hasDescription: !!data.description,
            hasObjectives: !!data.objectives,
            objectivesLength: Array.isArray(data.objectives) ? data.objectives.length : 'not array',
            hasActivities: !!data.activities,
            activitiesLength: Array.isArray(data.activities) ? data.activities.length : 'not array',
            dataKeys: Object.keys(data)
        });
        
        // Check if this is a preview/teaser widget for guest users
        // For authenticated users, NEVER show preview (even if flag is set)
        const isAuthenticated = !!localStorage.getItem('access_token');
        const isPreview = !isAuthenticated && data.is_preview === true;
        
        html += '<div class="lesson-plan' + (isPreview ? ' lesson-plan-preview' : '') + '">';
        
        // Preview banner is now shown at the top level for all widgets
        
        if (data.title) {
            html += `<h4 class="lesson-plan-title">${escapeHtml(data.title)}</h4>`;
        }
        if (data.description) {
            html += `<div class="lesson-section"><h5>📋 Lesson Description</h5><p>${escapeHtml(data.description)}</p></div>`;
        }
        if (data.subject || data.grade_level) {
            html += '<div class="lesson-plan-meta">';
            if (data.subject) {
                html += `<span class="lesson-subject">${escapeHtml(data.subject)}</span>`;
            }
            if (data.grade_level) {
                html += `<span class="lesson-grade">Grade ${escapeHtml(data.grade_level)}</span>`;
            }
            html += '</div>';
        }
        if (data.introduction) {
            html += `<div class="lesson-section"><h5>Introduction</h5><p>${escapeHtml(data.introduction)}</p></div>`;
        }
        if (data.objectives && Array.isArray(data.objectives) && data.objectives.length > 0) {
            html += '<div class="lesson-section"><h5>Learning Objectives</h5><ul class="lesson-objectives">';
            data.objectives.forEach((objective, index) => {
                html += `<li>${escapeHtml(objective)}</li>`;
            });
            html += '</ul></div>';
        }
        if (data.activities && Array.isArray(data.activities) && data.activities.length > 0) {
            html += '<div class="lesson-section"><h5>Activities</h5><ul class="lesson-activities">';
            data.activities.forEach((activity, index) => {
                html += `<li>${escapeHtml(activity)}</li>`;
            });
            html += '</ul></div>';
        }
        if (data.curriculum_standards) {
            html += `<div class="lesson-section"><h5>Curriculum Standards</h5><p>${escapeHtml(data.curriculum_standards)}</p></div>`;
        }
        if (data.materials && Array.isArray(data.materials) && data.materials.length > 0) {
            html += '<div class="lesson-section"><h5>Materials Needed</h5><ul class="lesson-materials">';
            data.materials.forEach((material, index) => {
                html += `<li>${escapeHtml(material)}</li>`;
            });
            html += '</ul></div>';
        }
        if (data.danielson_framework) {
            html += `<div class="lesson-section"><h5>Danielson Framework Alignment</h5><p>${escapeHtml(data.danielson_framework)}</p></div>`;
        }
        if (data.costas_questioning) {
            html += `<div class="lesson-section"><h5>Costa's Levels of Questioning</h5><p>${escapeHtml(data.costas_questioning)}</p></div>`;
        }
        if (data.worksheets) {
            // Format worksheets with better structure - preserve line breaks and formatting
            let worksheetsHtml = escapeHtml(data.worksheets);
            // Convert double newlines to paragraph breaks
            const paragraphs = worksheetsHtml.split('\n\n').filter(p => p.trim());
            if (paragraphs.length > 1) {
                worksheetsHtml = paragraphs.map(para => {
                    // Check if paragraph starts with a number or letter (numbered list or question)
                    if (para.match(/^\d+[\.\)]\s/) || para.match(/^[A-Z][a-z]+:/)) {
                        return `<p class="worksheet-item">${para.replace(/\n/g, '<br>')}</p>`;
                    }
                    return `<p>${para.replace(/\n/g, '<br>')}</p>`;
                }).join('');
            } else {
                // If no double newlines, just preserve single newlines
                worksheetsHtml = worksheetsHtml.replace(/\n/g, '<br>');
            }
            html += `<div class="lesson-section worksheet-section"><h5>📄 Worksheets</h5><div class="worksheet-content">${worksheetsHtml}</div></div>`;
        }
        if (data.rubrics) {
            // Format rubrics with better structure - preserve line breaks and formatting
            let rubricsHtml = escapeHtml(data.rubrics);
            // Convert double newlines to paragraph breaks
            const paragraphs = rubricsHtml.split('\n\n').filter(p => p.trim());
            if (paragraphs.length > 1) {
                rubricsHtml = paragraphs.map(para => {
                    // Check if paragraph starts with a number, letter, or performance level (numbered list, criteria, or level)
                    if (para.match(/^\d+[\.\)]\s/) || para.match(/^[A-Z][a-z]+:/) || para.match(/^(excellent|proficient|developing|beginning|advanced|novice|criteria)/i)) {
                        return `<p class="rubric-item">${para.replace(/\n/g, '<br>')}</p>`;
                    }
                    return `<p>${para.replace(/\n/g, '<br>')}</p>`;
                }).join('');
            } else {
                // If no double newlines, just preserve single newlines
                rubricsHtml = rubricsHtml.replace(/\n/g, '<br>');
            }
            html += `<div class="lesson-section rubric-section"><h5>📋 Rubrics</h5><div class="rubric-content">${rubricsHtml}</div></div>`;
        }
        if (data.assessments) {
            html += `<div class="lesson-section"><h5>Assessments</h5><p>${escapeHtml(data.assessments)}</p></div>`;
        }
        if (data.assessment) {
            html += `<div class="lesson-section"><h5>Assessment</h5><p>${escapeHtml(data.assessment)}</p></div>`;
        }
        if (data.exit_ticket) {
            html += `<div class="lesson-section"><h5>Exit Ticket</h5><p>${escapeHtml(data.exit_ticket)}</p></div>`;
        }
        html += '</div>'; // Close lesson-plan div
        html += '</div>'; // Close widget-data-display div
        console.log('✅ Lesson plan HTML generated, length:', html.length);
        return html;
    }
    // Special handling for fitness widget FIRST (before health) to avoid misclassification
    // Check fitness widget BEFORE health to prevent fitness widgets with meal data from being misclassified
    if (widgetType === 'fitness' && (data.exercises || data.strength_training || data.cardio)) {
        console.log('💪 Rendering fitness/workout widget with data:', {
            hasExercises: !!data.exercises,
            hasStrengthTraining: !!data.strength_training,
            hasCardio: !!data.cardio,
            exercisesCount: data.exercises ? data.exercises.length : 0,
            dataKeys: Object.keys(data)
        });
        // Check if this is a preview/teaser widget for guest users
        // For authenticated users, NEVER show preview (even if flag is set)
        const isAuthenticated = !!localStorage.getItem('access_token');
        const isPreview = !isAuthenticated && data.is_preview === true;
        
        html += '<div class="workout-plan' + (isPreview ? ' workout-plan-preview' : '') + '">';
        
        // Preview banner is now shown at the top level for all widgets
        
        if (data.plan_name) {
            html += `<h4 class="workout-plan-title">${escapeHtml(data.plan_name)}</h4>`;
        }
        
        // Render Strength Training section if available
        if (data.strength_training && Array.isArray(data.strength_training) && data.strength_training.length > 0) {
            html += '<div class="workout-section"><h5 class="workout-section-title">💪 Strength Training</h5><ul class="workout-exercises">';
            data.strength_training.forEach((exercise, index) => {
                html += '<li class="workout-exercise">';
                html += `<strong class="exercise-name">${escapeHtml(exercise.name || 'Exercise ' + (index + 1))}</strong>`;
                if (exercise.sets && exercise.reps) {
                    html += `<span class="exercise-sets-reps">${exercise.sets} sets × ${exercise.reps} reps</span>`;
                }
                if (exercise.duration) {
                    html += `<span class="exercise-duration">${escapeHtml(exercise.duration)}</span>`;
                }
                if (exercise.calories_burned) {
                    html += `<span class="exercise-calories">Burns ${escapeHtml(exercise.calories_burned)} calories</span>`;
                }
                if (exercise.description) {
                    html += `<p class="exercise-description">${escapeHtml(exercise.description)}</p>`;
                }
                html += '</li>';
            });
            html += '</ul></div>';
        }
        
        // Render Cardio section if available
        if (data.cardio && Array.isArray(data.cardio) && data.cardio.length > 0) {
            html += '<div class="workout-section"><h5 class="workout-section-title">🏃 Cardio</h5><ul class="workout-exercises">';
            data.cardio.forEach((exercise, index) => {
                html += '<li class="workout-exercise">';
                html += `<strong class="exercise-name">${escapeHtml(exercise.name || 'Exercise ' + (index + 1))}</strong>`;
                if (exercise.sets && exercise.reps) {
                    html += `<span class="exercise-sets-reps">${exercise.sets} sets × ${exercise.reps} reps</span>`;
                }
                if (exercise.duration) {
                    html += `<span class="exercise-duration">${escapeHtml(exercise.duration)}</span>`;
                }
                if (exercise.calories_burned) {
                    html += `<span class="exercise-calories">Burns ${escapeHtml(exercise.calories_burned)} calories</span>`;
                }
                if (exercise.description) {
                    html += `<p class="exercise-description">${escapeHtml(exercise.description)}</p>`;
                }
                html += '</li>';
            });
            html += '</ul></div>';
        }
        
        // Fallback to general exercises list if no sections (backward compatibility)
        if ((!data.strength_training || data.strength_training.length === 0) && 
            (!data.cardio || data.cardio.length === 0) && 
            data.exercises && Array.isArray(data.exercises) && data.exercises.length > 0) {
            html += '<ul class="workout-exercises">';
            data.exercises.forEach((exercise, index) => {
                html += '<li class="workout-exercise">';
                html += `<strong class="exercise-name">${escapeHtml(exercise.name || 'Exercise ' + (index + 1))}</strong>`;
                if (exercise.exercise_type) {
                    html += `<span class="exercise-type">${escapeHtml(exercise.exercise_type)}</span>`;
                }
                if (exercise.sets && exercise.reps) {
                    html += `<span class="exercise-sets-reps">${exercise.sets} sets × ${exercise.reps} reps</span>`;
                }
                if (exercise.duration) {
                    html += `<span class="exercise-duration">${escapeHtml(exercise.duration)}</span>`;
                }
                if (exercise.calories_burned) {
                    html += `<span class="exercise-calories">Burns ${escapeHtml(exercise.calories_burned)} calories</span>`;
                }
                if (exercise.description) {
                    html += `<p class="exercise-description">${escapeHtml(exercise.description)}</p>`;
                }
                html += '</li>';
            });
            html += '</ul>';
        }
        
        if (data.description) {
            html += `<p class="workout-description">${escapeHtml(data.description)}</p>`;
        }
        html += '</div>';
    }
    // Special handling for health/nutrition widget with meal plan data
    else if (widgetType === 'health' && (data.meals || data.daily_calories || data.macros || data.days)) {
        console.log('🍎 Rendering health/nutrition widget with data:', {
            hasMeals: !!data.meals,
            hasCalories: !!data.daily_calories,
            hasMacros: !!data.macros,
            hasDays: !!data.days,
            dataKeys: Object.keys(data)
        });
        
        html += '<div class="health-plan' + (isPreview ? ' health-plan-preview' : '') + '">';
        
        if (data.title) {
            html += `<h4 class="health-plan-title">${escapeHtml(data.title)}</h4>`;
        }
        if (data.description) {
            html += `<div class="health-section"><h5>📋 Description</h5><p>${escapeHtml(data.description)}</p></div>`;
        }
        if (data.daily_calories) {
            html += `<div class="health-section"><h5>🔥 Daily Calories</h5><p class="health-calories">${escapeHtml(data.daily_calories)}</p></div>`;
        }
        if (data.macros && typeof data.macros === 'object') {
            html += '<div class="health-section"><h5>📊 Macronutrients</h5><ul class="health-macros">';
            if (data.macros.protein) {
                html += `<li><strong>Protein:</strong> ${escapeHtml(data.macros.protein)}</li>`;
            }
            if (data.macros.carbs) {
                html += `<li><strong>Carbs:</strong> ${escapeHtml(data.macros.carbs)}</li>`;
            }
            if (data.macros.fat) {
                html += `<li><strong>Fat:</strong> ${escapeHtml(data.macros.fat)}</li>`;
            }
            html += '</ul></div>';
        }
        // Check for multi-day meal plan first
        if (data.days && Array.isArray(data.days) && data.days.length > 0) {
            html += '<div class="health-section"><h5>🍽️ Meal Plan</h5>';
            data.days.forEach((dayData, dayIndex) => {
                html += `<div class="health-day-plan">`;
                html += `<h6 class="health-day-title">📅 ${escapeHtml(dayData.day)}</h6>`;
                html += '<ul class="health-meals">';
                if (dayData.meals && Array.isArray(dayData.meals)) {
                    dayData.meals.forEach((meal, mealIndex) => {
                        if (typeof meal === 'object' && meal.meal && meal.foods) {
                            const caloriesText = meal.calories ? ` <span class="meal-calories">(${escapeHtml(meal.calories)})</span>` : '';
                            html += `<li class="health-meal-item"><strong>${escapeHtml(meal.meal)}${caloriesText}:</strong> ${escapeHtml(meal.foods)}</li>`;
                        } else if (typeof meal === 'string') {
                            html += `<li class="health-meal-item">${escapeHtml(meal)}</li>`;
                        }
                    });
                }
                html += '</ul>';
                html += '</div>';
            });
            html += '</div>';
        } else if (data.meals && Array.isArray(data.meals) && data.meals.length > 0) {
            // Single day format (backward compatibility)
            html += '<div class="health-section"><h5>🍽️ Meals</h5><ul class="health-meals">';
            data.meals.forEach((meal, index) => {
                if (typeof meal === 'object' && meal.meal && meal.foods) {
                    const caloriesText = meal.calories ? ` <span class="meal-calories">(${escapeHtml(meal.calories)})</span>` : '';
                    html += `<li class="health-meal-item"><strong>${escapeHtml(meal.meal)}${caloriesText}:</strong> ${escapeHtml(meal.foods)}</li>`;
                } else if (typeof meal === 'string') {
                    html += `<li class="health-meal-item">${escapeHtml(meal)}</li>`;
                }
            });
            html += '</ul></div>';
        }
        if (data.exercise_calories) {
            html += `<div class="health-section"><h5>🔥 Exercise Calories</h5><p class="health-exercise-calories">Aim to burn ${escapeHtml(data.exercise_calories)} calories per day through exercise</p></div>`;
        }
        if (data.exercise_plan && data.exercise_plan.exercises && Array.isArray(data.exercise_plan.exercises) && data.exercise_plan.exercises.length > 0) {
            html += '<div class="health-section"><h5>💪 Exercise Plan</h5><ul class="health-exercises">';
            data.exercise_plan.exercises.forEach((exercise, index) => {
                html += '<li class="health-exercise-item">';
                html += `<strong class="exercise-name">${escapeHtml(exercise.name || 'Exercise ' + (index + 1))}</strong>`;
                if (exercise.sets && exercise.reps) {
                    html += `<span class="exercise-sets-reps">${exercise.sets} sets × ${exercise.reps} reps</span>`;
                }
                if (exercise.calories_burned) {
                    html += `<span class="exercise-calories">Burns ${escapeHtml(exercise.calories_burned)} calories</span>`;
                }
                if (exercise.duration) {
                    html += `<span class="exercise-duration">${escapeHtml(exercise.duration)}</span>`;
                }
                if (exercise.description) {
                    html += `<p class="exercise-description">${escapeHtml(exercise.description)}</p>`;
                }
                html += '</li>';
            });
            html += '</ul></div>';
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
    } catch (error) {
        console.error('❌ Error formatting widget data:', error);
        console.error('Widget type:', widgetType);
        console.error('Data:', data);
        return '<div class="widget-data-display"><p class="widget-error">⚠️ Error displaying widget data. Please try again.</p></div>';
    }
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
            
            // Safari Web Speech API initialization
            console.warn('⚠️ Safari Web Speech API has known limitations. Voice input may not work reliably. Consider using Chrome or Firefox for better voice input support.');
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
                // CRITICAL for Safari: Request data multiple times before stopping
                // Safari sometimes doesn't fire ondataavailable events properly
                try {
                    mediaRecorder.requestData(); // Request current data
                } catch (e) {
                    console.warn('Could not request data:', e);
                }
                // Request data again after a short delay to ensure we get all chunks
                setTimeout(() => {
                    try {
                        if (mediaRecorder.state === 'recording') {
                            mediaRecorder.requestData();
                        }
                    } catch (e) {
                        console.warn('Could not request data (second attempt):', e);
                    }
                }, 50);
                // Small delay to ensure data is collected before stopping
                setTimeout(() => {
                    if (mediaRecorder.state === 'recording') {
                        mediaRecorder.stop(); // This will trigger onstop handler
                    }
                }, 150);
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
                const originalStream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    }
                });
                
                console.log('Safari: Got microphone stream, starting audio capture');
                console.log('Stream details:', {
                    id: originalStream.id,
                    active: originalStream.active,
                    tracks: originalStream.getTracks().length,
                    trackDetails: originalStream.getTracks().map(t => ({
                        id: t.id,
                        kind: t.kind,
                        label: t.label,
                        enabled: t.enabled,
                        muted: t.muted,
                        readyState: t.readyState
                    }))
                });
                
                // Store original stream for cleanup
                microphoneStream = originalStream;
                
                // CRITICAL for Safari: Use the original stream directly - don't process through AudioContext
                // Safari's MediaRecorder has issues with processed streams and can cause tracks to end
                // The error "A MediaStreamTrack ended due to a capture failure" happens when we use processed streams
                let audioContext = null;
                let audioSource = null;
                let audioDestination = null;
                const streamToRecord = originalStream; // Always use original stream for Safari
                
                console.log('ℹ️ Using original stream directly for Safari MediaRecorder compatibility');
                
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
                // streamToRecord is already set above
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
                        streamActive: streamToRecord.active,
                        tracksActive: streamToRecord.getTracks().filter(t => t.readyState === 'live').length
                    });
                    
                    if (event.data && event.data.size > 0) {
                        audioChunks.push(event.data);
                        console.log('✅ Audio chunk received:', event.data.size, 'bytes, total chunks:', audioChunks.length);
                    } else {
                        console.warn('⚠️ Empty or invalid audio chunk received');
                        console.warn('Stream state:', {
                            active: streamToRecord.active,
                            tracks: streamToRecord.getTracks().map(t => ({
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
                    
                    // Check if file is too small - Safari sometimes produces empty files
                    if (audioBlob.size < 100) {
                        console.warn(`⚠️ Audio blob is very small (${audioBlob.size} bytes) - Safari MediaRecorder may not be capturing audio properly`);
                        updateAvatarStatus('ready', 'Audio capture failed. Safari voice input may not work. Please type your message instead.');
                        if (microphoneStream) {
                            microphoneStream.getTracks().forEach(track => track.stop());
                        }
                        microphoneStream = null;
                        mediaRecorder = null;
                        isVoiceActive = false;
                        updateVoiceButton();
                        alert('Safari voice input is not working properly. The audio file is too small (likely empty). Please type your message instead, or try using Chrome or Firefox for voice input.');
                        return;
                    }
                    
                    // Send to backend for transcription
                    try {
                        const formData = new FormData();
                        // Ensure proper file extension for Whisper API
                        // Extract format from mimeType (e.g., "audio/webm;codecs=opus" -> "webm")
                        const format = mimeType.split('/')[1].split(';')[0];
                        const filename = `recording.${format}`;
                        formData.append('audio', audioBlob, filename);
                        formData.append('language', 'en');
                        
                        console.log(`📤 Sending audio for transcription: ${audioBlob.size} bytes, format: ${format}, filename: ${filename}`);
                        
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
                    const activeTracks = streamToRecord.getTracks().filter(t => t.readyState === 'live');
                    console.log('Stream state before recording:', {
                        active: streamToRecord.active,
                        activeTracks: activeTracks.length,
                        trackStates: streamToRecord.getTracks().map(t => ({
                            kind: t.kind,
                            enabled: t.enabled,
                            muted: t.muted,
                            readyState: t.readyState
                        }))
                    });
                    
                    if (activeTracks.length === 0) {
                        throw new Error('No active audio tracks in stream');
                    }
                    
                    // CRITICAL: Safari MediaRecorder needs timeslice to fire ondataavailable events
                    // Without timeslice, Safari may not fire any events until stop() is called
                    // Use a small timeslice (100ms) to ensure we get chunks frequently
                    try {
                        // Start with timeslice - Safari needs this to fire ondataavailable
                        mediaRecorder.start(100); // Fire every 100ms for better Safari compatibility
                        console.log('✅ MediaRecorder started with 100ms timeslice');
                    } catch (timesliceError) {
                        console.warn('⚠️ Timeslice not supported, trying without timeslice:', timesliceError);
                        try {
                            // Fallback: start without timeslice (may not work well in Safari)
                            mediaRecorder.start();
                            console.log('✅ MediaRecorder started without timeslice (may not get chunks in Safari)');
                        } catch (noTimesliceError) {
                            console.error('❌ Failed to start MediaRecorder with or without timeslice:', noTimesliceError);
                            throw new Error(`MediaRecorder failed to start: ${noTimesliceError.message || noTimesliceError}`);
                        }
                    }
                    
                    console.log('💡 Speak now, then click the microphone button again when you finish');
                    
                    // Show a visual indicator that recording is active
                    const chatInput = document.getElementById('chatInput');
                    chatInput.placeholder = '🎤 Recording... Click microphone again to stop';
                    
                    // Monitor stream health
                    streamToRecord.getTracks().forEach(track => {
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
                    // Clean up on error
                    if (microphoneStream) {
                        microphoneStream.getTracks().forEach(track => track.stop());
                        microphoneStream = null;
                    }
                    if (mediaRecorder) {
                        mediaRecorder = null;
                    }
                    throw startError;
                }
                
            } catch (error) {
                console.error('Safari microphone access error:', error);
                console.error('Error details:', {
                    name: error.name,
                    message: error.message,
                    stack: error.stack,
                    toString: error.toString()
                });
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
                    // Provide more specific error message
                    const errorMessage = error.message || error.toString() || 'Unknown error';
                    alert(`Failed to access microphone: ${errorMessage}\n\nSafari voice input may not be fully supported. Please try typing your message instead, or use Chrome or Firefox for voice input.`);
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

// Open settings and load existing preferences
async function openSettings() {
    const settingsModal = document.getElementById('settingsModal');
    settingsModal.classList.add('active');
    
    // Scroll to top of modal content when opening
    const modalBody = settingsModal.querySelector('.modal-body');
    if (modalBody) {
        modalBody.scrollTop = 0;
    }
    
    // Load existing settings from localStorage
    const theme = localStorage.getItem('dashboard_theme') || 'dark';
    document.querySelector(`input[name="theme"][value="${theme}"]`).checked = true;
    
    // Theme & Display
    document.getElementById('fontSize').value = localStorage.getItem('font_size') || 'medium';
    document.getElementById('fontFamily').value = localStorage.getItem('font_family') || 'system';
    document.getElementById('accentColor').value = localStorage.getItem('accent_color') || '#4a90e2';
    document.getElementById('highContrast').checked = localStorage.getItem('high_contrast') === 'true';
    
    // Notifications
    document.getElementById('enableNotifications').checked = localStorage.getItem('enable_notifications') !== 'false';
    document.getElementById('pushNotifications').checked = localStorage.getItem('push_notifications') !== 'false';
    document.getElementById('inAppNotifications').checked = localStorage.getItem('in_app_notifications') !== 'false';
    document.getElementById('smsNotifications').checked = localStorage.getItem('sms_notifications') === 'true';
    document.getElementById('enableSounds').checked = localStorage.getItem('enable_sounds') !== 'false';
    document.getElementById('quietHoursStart').value = localStorage.getItem('quiet_hours_start') || '';
    document.getElementById('quietHoursEnd').value = localStorage.getItem('quiet_hours_end') || '';
    
    // Voice Input
    document.getElementById('enableVoiceInput').checked = localStorage.getItem('enable_voice_input') !== 'false';
    
    // Avatar preferences
    const avatarScale = parseFloat(localStorage.getItem('avatar_scale') || '1.0');
    const avatarOpacity = parseInt(localStorage.getItem('avatar_opacity') || '100');
    const avatarColor = localStorage.getItem('avatar_color') || '#ffffff';
    document.getElementById('avatarScale').value = avatarScale;
    document.getElementById('avatarScaleValue').textContent = avatarScale.toFixed(1);
    document.getElementById('avatarOpacity').value = avatarOpacity;
    document.getElementById('avatarOpacityValue').textContent = avatarOpacity + '%';
    document.getElementById('avatarColor').value = avatarColor;
    
    // AI voice preferences
    document.getElementById('enableAIVoice').checked = localStorage.getItem('enable_ai_voice') !== 'false';
    document.getElementById('enableOpeningPromptAutoplay').checked = localStorage.getItem('enable_opening_prompt_autoplay') !== 'false';
    const voiceSpeed = parseInt(localStorage.getItem('voice_speed') || '1');
    const voicePitch = parseInt(localStorage.getItem('voice_pitch') || '100');
    const voiceLanguage = localStorage.getItem('voice_language') || 'en-US';
    document.getElementById('voiceSpeed').value = voiceSpeed;
    document.getElementById('voiceSpeedValue').textContent = voiceSpeed + '%';
    document.getElementById('voicePitch').value = voicePitch;
    document.getElementById('voicePitchValue').textContent = voicePitch + '%';
    document.getElementById('voiceLanguage').value = voiceLanguage;
    
    // Language & Regional
    document.getElementById('language').value = localStorage.getItem('language') || 'en';
    document.getElementById('timezone').value = localStorage.getItem('timezone') || 'UTC';
    document.getElementById('dateFormat').value = localStorage.getItem('date_format') || 'YYYY-MM-DD';
    document.getElementById('timeFormat').value = localStorage.getItem('time_format') || '24h';
    
    // Accessibility
    document.getElementById('reducedMotion').checked = localStorage.getItem('reduced_motion') === 'true';
    document.getElementById('screenReader').checked = localStorage.getItem('screen_reader') === 'true';
    
    // Layout
    document.getElementById('sidebarPosition').value = localStorage.getItem('sidebar_position') || 'left';
    document.getElementById('gridView').checked = localStorage.getItem('grid_view') !== 'false';
    
    // Performance
    document.getElementById('autoRefresh').checked = localStorage.getItem('auto_refresh') !== 'false';
    document.getElementById('refreshInterval').value = parseInt(localStorage.getItem('refresh_interval') || '60');
    
    // Privacy
    document.getElementById('analyticsOptIn').checked = localStorage.getItem('analytics_opt_in') !== 'false';
    document.getElementById('dataSharing').checked = localStorage.getItem('data_sharing') === 'true';
    
    // Load selected avatar and voice
    const selectedAvatarId = localStorage.getItem('selected_avatar_id') || '';
    const selectedVoiceId = localStorage.getItem('selected_voice_id') || '7';
    
    // Load avatars and voices from API
    await loadAvatarsAndVoices(selectedAvatarId, selectedVoiceId);
    
    // Load and display the selected avatar in the chat interface
    if (selectedAvatarId) {
        await loadAndDisplayAvatar(selectedAvatarId);
    }
    
    // Try to load from backend API (for authenticated users)
    const token = localStorage.getItem('access_token');
    if (token) {
        try {
            // Use 'ai-assistant' as the default tool_id for the AI assistant
            const response = await fetch('/api/v1/dashboard/tools/ai-assistant/avatar', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const avatarData = await response.json();
                if (avatarData.customization) {
                    const custom = avatarData.customization;
                    if (custom.scale !== undefined) {
                        document.getElementById('avatarScale').value = custom.scale;
                        document.getElementById('avatarScaleValue').textContent = custom.scale.toFixed(1);
                    }
                    if (custom.opacity !== undefined) {
                        const opacityPercent = Math.round(custom.opacity * 100);
                        document.getElementById('avatarOpacity').value = opacityPercent;
                        document.getElementById('avatarOpacityValue').textContent = opacityPercent + '%';
                    }
                    if (custom.color) {
                        document.getElementById('avatarColor').value = custom.color;
                    }
                }
                if (avatarData.voice_preferences) {
                    const voice = avatarData.voice_preferences;
                    if (voice.speed !== undefined) {
                        document.getElementById('voiceSpeed').value = voice.speed;
                        document.getElementById('voiceSpeedValue').textContent = voice.speed + '%';
                    }
                    if (voice.pitch !== undefined) {
                        document.getElementById('voicePitch').value = voice.pitch;
                        document.getElementById('voicePitchValue').textContent = voice.pitch + '%';
                    }
                    if (voice.language) {
                        document.getElementById('voiceLanguage').value = voice.language;
                    }
                }
            }
        } catch (error) {
            console.error('Error loading avatar preferences from backend:', error);
            // Continue with localStorage values if API fails
        }
    }
    
    // Setup slider value displays
    setupSettingsSliders();
    
    // Setup voice search
    setupVoiceSearch();
}

// Close settings
function closeSettings() {
    document.getElementById('settingsModal').classList.remove('active');
}

// Load avatars and voices from API
let availableAvatars = [];
let availableVoices = [];
let filteredVoices = [];

async function loadAvatarsAndVoices(selectedAvatarId = '', selectedVoiceId = '') {
    const token = localStorage.getItem('access_token');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    // Load avatars
    try {
        console.log('🖼️ Fetching avatars from /api/v1/beta/avatars');
        const avatarsResponse = await fetch('/api/v1/beta/avatars', { headers });
        console.log('🖼️ Avatars response status:', avatarsResponse.status, avatarsResponse.statusText);
        
        if (avatarsResponse.ok) {
            availableAvatars = await avatarsResponse.json();
            console.log('✅ Loaded avatars:', availableAvatars.length, 'avatars');
            populateAvatarSelect(selectedAvatarId);
        } else {
            const errorText = await avatarsResponse.text();
            console.error('❌ Failed to load avatars:', avatarsResponse.status, errorText);
            const select = document.getElementById('selectedAvatar');
            if (select) {
                select.innerHTML = `<option value="">Failed to load avatars (${avatarsResponse.status}). Check console.</option>`;
            }
        }
    } catch (error) {
        console.error('❌ Error loading avatars:', error);
        console.error('❌ Error details:', error.message, error.stack);
        const select = document.getElementById('selectedAvatar');
        if (select) {
            select.innerHTML = '<option value="">Error loading avatars. Check console for details.</option>';
        }
    }
    
    // Load voices
    try {
        console.log('🔊 Fetching voices from /api/v1/beta/voices?limit=500');
        const voicesResponse = await fetch('/api/v1/beta/voices?limit=500', { headers });
        console.log('🔊 Voices response status:', voicesResponse.status, voicesResponse.statusText);
        
        if (voicesResponse.ok) {
            availableVoices = await voicesResponse.json();
            console.log('✅ Loaded voices:', availableVoices.length, 'voices');
            console.log('🔊 First 3 voices:', availableVoices.slice(0, 3));
            // Log detailed info about first few voices for debugging
            if (availableVoices.length > 0) {
                console.log('🔊 First voice details:', JSON.stringify(availableVoices[0], null, 2));
                if (availableVoices.length > 1) {
                    console.log('🔊 Second voice details:', JSON.stringify(availableVoices[1], null, 2));
                }
                // Log the last two voices (teacher/student)
                if (availableVoices.length >= 2) {
                    console.log('🔊 Second to last voice:', JSON.stringify(availableVoices[availableVoices.length - 2], null, 2));
                    console.log('🔊 Last voice:', JSON.stringify(availableVoices[availableVoices.length - 1], null, 2));
                }
            }
            filteredVoices = [...availableVoices];
            
            if (availableVoices.length === 0) {
                console.warn('⚠️ No voices returned from API');
                const select = document.getElementById('selectedVoice');
                if (select) {
                    select.innerHTML = '<option value="">No voices available. Using fallback voices...</option>';
                }
            } else {
                console.log('🔊 Calling populateVoiceSelect with', selectedVoiceId);
                populateVoiceSelect(selectedVoiceId);
            }
        } else {
            const errorText = await voicesResponse.text();
            console.error('❌ Failed to load voices:', voicesResponse.status, errorText);
            const select = document.getElementById('selectedVoice');
            if (select) {
                select.innerHTML = `<option value="">Failed to load voices (${voicesResponse.status}). Check console.</option>`;
            }
        }
    } catch (error) {
        console.error('❌ Error loading voices:', error);
        console.error('❌ Error details:', error.message, error.stack);
        const select = document.getElementById('selectedVoice');
        if (select) {
            select.innerHTML = '<option value="">Error loading voices. Check console for details.</option>';
        }
    }
}

function populateAvatarSelect(selectedId = '') {
    const select = document.getElementById('selectedAvatar');
    if (!select) return;
    
    select.innerHTML = '<option value="">Select an avatar...</option>';
    
    // Remove existing change listener to avoid duplicates
    const newSelect = select.cloneNode(true);
    select.parentNode.replaceChild(newSelect, select);
    
    availableAvatars.forEach((avatar, index) => {
        const option = document.createElement('option');
        option.value = avatar.id;
        // Use avatar_name if available, otherwise generate a name
        const displayName = avatar.avatar_name || 
                           avatar.name || 
                           (avatar.avatar_type ? `${avatar.avatar_type} Avatar ${index + 1}` : `Avatar ${index + 1}`);
        option.textContent = displayName;
        if (avatar.id === selectedId || selectedId === avatar.id) {
            option.selected = true;
            showAvatarPreview(avatar);
        }
        newSelect.appendChild(option);
    });
    
    // Add change listener
    newSelect.addEventListener('change', (e) => {
        const avatarId = e.target.value;
        const avatar = availableAvatars.find(a => a.id === avatarId);
        if (avatar) {
            showAvatarPreview(avatar);
        } else {
            hideAvatarPreview();
        }
    });
}

function showAvatarPreview(avatar) {
    const preview = document.getElementById('avatarPreview');
    const previewImage = document.getElementById('avatarPreviewImage');
    const previewDescription = document.getElementById('avatarPreviewDescription');
    
    if (!preview || !previewImage || !previewDescription) return;
    
    // Set image if available
    const imageUrl = avatar.image_url || 
                     avatar.avatar_config?.url || 
                     avatar.avatar_config?.image_url ||
                     '/static/avatars/default.png';
    
    if (imageUrl && imageUrl !== '/static/avatars/default.png') {
        previewImage.src = imageUrl;
        previewImage.style.display = 'block';
        previewImage.onerror = function() {
            // If image fails to load, hide it
            previewImage.style.display = 'none';
        };
    } else {
        previewImage.style.display = 'none';
    }
    
    // Set description
    const description = avatar.description || 
                       `${avatar.avatar_type || 'Avatar'} - ${avatar.avatar_name || 'Preview'}`;
    previewDescription.textContent = description;
    preview.style.display = 'block';
}

function hideAvatarPreview() {
    document.getElementById('avatarPreview').style.display = 'none';
}

// Load and display the selected avatar in the chat interface
async function loadAndDisplayAvatar(avatarId) {
    console.log('🖼️ loadAndDisplayAvatar called with avatarId:', avatarId);
    const aiAvatar = document.getElementById('aiAvatar');
    if (!aiAvatar) {
        console.warn('⚠️ aiAvatar element not found');
        return;
    }
    
    console.log('✅ aiAvatar element found, availableAvatars count:', availableAvatars?.length || 0);
    
    // Find the avatar in available avatars
    const avatar = availableAvatars.find(a => a.id === avatarId || a.id === String(avatarId));
    console.log('🔍 Found avatar:', avatar ? 'Yes' : 'No', avatar);
    
    if (!avatar) {
        console.warn('Avatar not found in available avatars, trying to fetch...');
        // Try to fetch avatar details from API
        const token = localStorage.getItem('access_token');
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        
        try {
            const response = await fetch(`/api/v1/beta/avatars`, { headers });
            if (response.ok) {
                const avatars = await response.json();
                const foundAvatar = avatars.find(a => a.id === avatarId || a.id === String(avatarId));
                if (foundAvatar) {
                    renderAvatarInChat(foundAvatar);
                    return;
                }
            }
        } catch (error) {
            console.error('Error fetching avatar:', error);
        }
        
        // Fallback to default
        renderAvatarInChat(null);
        return;
    }
    
    renderAvatarInChat(avatar);
}

function renderAvatarInChat(avatar) {
    const aiAvatar = document.getElementById('aiAvatar');
    const avatarFace = aiAvatar?.querySelector('.avatar-face');
    
    console.log('🎨 renderAvatarInChat called with avatar:', avatar);
    
    if (!aiAvatar || !avatarFace) {
        console.warn('⚠️ aiAvatar or avatarFace not found');
        return;
    }
    
    // Get avatar customization settings from localStorage
    const avatarScale = parseFloat(localStorage.getItem('avatar_scale') || '1.0');
    const avatarOpacity = parseInt(localStorage.getItem('avatar_opacity') || '100');
    const avatarColor = localStorage.getItem('avatar_color') || '#ffffff';
    
    // Apply opacity (scale is handled by CSS animation for animated avatars)
    aiAvatar.style.opacity = avatarOpacity / 100;
    
    if (!avatar) {
        // Default placeholder
        avatarFace.textContent = '👤';
        avatarFace.style.backgroundImage = '';
        avatarFace.style.backgroundSize = '';
        avatarFace.style.backgroundPosition = '';
        return;
    }
    
    // Handle different avatar types
    const avatarType = avatar.avatar_type || avatar.type || 'STATIC';
    
    // Only apply scale transform for static avatars (animated ones use CSS animations)
    if (avatarType === 'STATIC') {
        aiAvatar.style.transform = `scale(${avatarScale})`;
    } else {
        // For animated/3D avatars, store scale in CSS variable so animation can use it
        aiAvatar.style.setProperty('--avatar-scale', avatarScale);
        // Remove inline transform to let CSS animation handle it
        aiAvatar.style.transform = '';
    }
    
    // Add animation classes based on avatar type
    aiAvatar.classList.remove('animated', 'three-d');
    if (avatarType === 'ANIMATED') {
        aiAvatar.classList.add('animated');
    } else if (avatarType === 'THREE_D') {
        aiAvatar.classList.add('three-d');
    }
    
    // Try multiple sources for image URL
    let imageUrl = avatar.image_url || 
                   avatar.avatar_config?.url || 
                   avatar.avatar_config?.image_url ||
                   avatar.avatar_config?.preview_url ||
                   avatar.avatar_config?.preview_image ||
                   avatar.url ||
                   avatar.preview_url ||
                   avatar.preview_image;
    
    // If avatar_config is a string, try to parse it
    if (!imageUrl && avatar.avatar_config) {
        try {
            const config = typeof avatar.avatar_config === 'string' 
                ? JSON.parse(avatar.avatar_config) 
                : avatar.avatar_config;
            imageUrl = config?.url || config?.image_url || config?.preview_url || config?.preview_image;
        } catch (e) {
            console.warn('Could not parse avatar_config:', e);
        }
    }
    
    console.log('🖼️ Avatar rendering:', {
        type: avatarType,
        hasImageUrl: !!imageUrl,
        imageUrl: imageUrl,
        avatarConfig: avatar.avatar_config,
        avatarName: avatar.avatar_name || avatar.name
    });
    
    // Helper function to handle image load errors
    const handleImageError = (imgUrl, avatarName, avatarType) => {
        console.warn(`⚠️ Failed to load avatar image: ${imgUrl}`);
        avatarFace.style.backgroundImage = '';
        const fallbackEmoji = avatarType === 'THREE_D' ? '🎭' : 
                             avatarType === 'ANIMATED' ? '🎬' : 
                             getAvatarEmoji(avatarName) || '👤';
        avatarFace.textContent = fallbackEmoji;
    };
    
    if (avatarType === 'ANIMATED' || avatarType === 'THREE_D') {
        // For animated/3D avatars, try to show preview image or use animated emoji
        if (imageUrl) {
            // Create an image element to test if the URL is valid
            const testImg = new Image();
            let imageLoaded = false;
            
            // Set a timeout to handle cases where the image never loads
            const loadTimeout = setTimeout(() => {
                if (!imageLoaded) {
                    console.warn(`⏱️ Image load timeout for: ${imageUrl}`);
                    const avatarName = avatar.avatar_name || avatar.name || '';
                    handleImageError(imageUrl, avatarName, avatarType);
                }
            }, 3000); // 3 second timeout
            
            testImg.onload = () => {
                imageLoaded = true;
                clearTimeout(loadTimeout);
                // Verify the image actually loaded by checking its dimensions
                if (testImg.width === 0 && testImg.height === 0) {
                    console.warn(`⚠️ Image loaded but has 0 dimensions: ${imageUrl}`);
                    const avatarName = avatar.avatar_name || avatar.name || '';
                    handleImageError(imageUrl, avatarName, avatarType);
                    return;
                }
                // Image loaded successfully
                avatarFace.textContent = '';
                avatarFace.style.backgroundImage = `url(${imageUrl})`;
                avatarFace.style.backgroundSize = 'cover';
                avatarFace.style.backgroundPosition = 'center';
                avatarFace.style.width = '100%';
                avatarFace.style.height = '100%';
                console.log('✅ Set animated avatar image:', imageUrl, `(${testImg.width}x${testImg.height})`);
            };
            testImg.onerror = (e) => {
                imageLoaded = true; // Mark as handled
                clearTimeout(loadTimeout);
                // Image failed to load, use fallback
                const avatarName = avatar.avatar_name || avatar.name || '';
                console.error('❌ Image load error:', e, imageUrl);
                handleImageError(imageUrl, avatarName, avatarType);
            };
            // Set src last to trigger load
            testImg.src = imageUrl;
        } else {
            // For animated avatars without image, use a more prominent animated indicator
            const avatarName = avatar.avatar_name || avatar.name || '';
            if (avatarType === 'THREE_D') {
                avatarFace.textContent = '🎭';
            } else if (avatarName.toLowerCase().includes('animated')) {
                avatarFace.textContent = '🎬';
            } else {
                avatarFace.textContent = getAvatarEmoji(avatarName) || '🎬';
            }
            avatarFace.style.backgroundImage = '';
            console.warn('⚠️ Animated avatar has no image_url, using emoji fallback');
        }
    } else {
        // STATIC avatar - use image
        if (imageUrl) {
            // Create an image element to test if the URL is valid
            const testImg = new Image();
            let imageLoaded = false;
            
            // Set a timeout to handle cases where the image never loads
            const loadTimeout = setTimeout(() => {
                if (!imageLoaded) {
                    console.warn(`⏱️ Image load timeout for: ${imageUrl}`);
                    const avatarName = avatar.avatar_name || avatar.name || 'Avatar';
                    handleImageError(imageUrl, avatarName, 'STATIC');
                }
            }, 3000); // 3 second timeout
            
            testImg.onload = () => {
                imageLoaded = true;
                clearTimeout(loadTimeout);
                // Verify the image actually loaded by checking its dimensions
                if (testImg.width === 0 && testImg.height === 0) {
                    console.warn(`⚠️ Image loaded but has 0 dimensions: ${imageUrl}`);
                    const avatarName = avatar.avatar_name || avatar.name || 'Avatar';
                    handleImageError(imageUrl, avatarName, 'STATIC');
                    return;
                }
                // Image loaded successfully
                avatarFace.textContent = '';
                avatarFace.style.backgroundImage = `url(${imageUrl})`;
                avatarFace.style.backgroundSize = 'cover';
                avatarFace.style.backgroundPosition = 'center';
                avatarFace.style.width = '100%';
                avatarFace.style.height = '100%';
                console.log('✅ Set static avatar image:', imageUrl, `(${testImg.width}x${testImg.height})`);
            };
            testImg.onerror = (e) => {
                imageLoaded = true; // Mark as handled
                clearTimeout(loadTimeout);
                // Image failed to load, use fallback
                const avatarName = avatar.avatar_name || avatar.name || 'Avatar';
                console.error('❌ Image load error:', e, imageUrl);
                handleImageError(imageUrl, avatarName, 'STATIC');
            };
            // Set src last to trigger load
            testImg.src = imageUrl;
        } else {
            // Fallback to emoji or avatar name
            const avatarName = avatar.avatar_name || avatar.name || 'Avatar';
            avatarFace.textContent = getAvatarEmoji(avatarName);
            avatarFace.style.backgroundImage = '';
            console.warn('⚠️ Static avatar has no image_url, using emoji fallback:', avatarName);
        }
    }
}

function getAvatarEmoji(name) {
    // Map avatar names to emojis
    const nameLower = name.toLowerCase();
    if (nameLower.includes('teacher') || nameLower.includes('educator')) return '👨‍🏫';
    if (nameLower.includes('student') || nameLower.includes('learner')) return '👨‍🎓';
    if (nameLower.includes('robot') || nameLower.includes('ai')) return '🤖';
    if (nameLower.includes('assistant')) return '👤';
    if (nameLower.includes('animated')) return '🎬';
    if (nameLower.includes('3d') || nameLower.includes('three')) return '🎭';
    return '👤';
}

function populateVoiceSelect(selectedId = '7') {
    const select = document.getElementById('selectedVoice');
    if (!select) {
        console.error('❌ Voice select element not found');
        return;
    }
    
    console.log('🔊 populateVoiceSelect called with selectedId:', selectedId);
    console.log('🔊 filteredVoices length:', filteredVoices?.length || 0);
    
    // Clear existing options
    select.innerHTML = '';
    
    if (!filteredVoices || filteredVoices.length === 0) {
        console.warn('⚠️ No voices to populate');
        select.innerHTML = '<option value="">No voices available</option>';
        return;
    }
    
    console.log('🔊 Populating voice select with', filteredVoices.length, 'voices');
    
    // Remove any existing change listeners by cloning (simpler approach)
    const hasExistingListener = select.hasAttribute('data-listener-attached');
    
    // Add all options
    filteredVoices.forEach((voice, index) => {
        const option = document.createElement('option');
        const voiceId = voice.id || voice.voice_id || `voice_${index}`;
        option.value = voiceId;
        
        // Create a display name - build it step by step
        let displayName = '';
        
        // Check if name exists and is not generic
        const name = voice.name || voice.template_name || '';
        const isGenericName = name.toLowerCase().includes('default') || 
                             name.toLowerCase() === 'default voice' ||
                             (name.toLowerCase().includes('voice') && name.toLowerCase().trim() === 'voice') ||
                             (name.toLowerCase().startsWith('voice ') && /^voice \d+$/.test(name.toLowerCase())) ||
                             name.toLowerCase().includes('system voice');
        
        // Extract metadata and settings
        const metadata = voice.metadata || {};
        const settings = voice.settings || voice.template_settings || {};
        const provider = metadata.provider || metadata.service || settings.provider || '';
        const language = metadata.language || metadata.locale || settings.language || '';
        const voiceName = metadata.name || metadata.voice_name || settings.name || '';
        const role = metadata.role || settings.role || '';
        const category = metadata.category || settings.category || '';
        const gender = metadata.gender || settings.gender || '';
        const accent = metadata.accent || settings.accent || '';
        const style = metadata.style || settings.style || '';
        
        // Skip "system" as a provider name - it's too generic
        const validProvider = provider && provider.toLowerCase() !== 'system' ? provider : '';
        
        if (name && !isGenericName) {
            displayName = name;
            // Only add provider if it's not "system" and not already in the name
            if (validProvider && !name.toLowerCase().includes(validProvider.toLowerCase())) {
                displayName += ` (${validProvider})`;
            }
            // Add language if available and not already in name
            if (language && !name.toLowerCase().includes(language.toLowerCase())) {
                displayName += ` - ${language}`;
            }
        } else {
            // Build name from metadata
            const nameParts = [];
            
            // Try to get name from metadata (skip if it's generic)
            if (voiceName && !voiceName.toLowerCase().includes('default') && !voiceName.toLowerCase().includes('system')) {
                nameParts.push(voiceName);
            }
            // Try role (e.g., "teacher", "student")
            else if (role) {
                nameParts.push(`${role.charAt(0).toUpperCase() + role.slice(1)} Voice`);
            }
            // Try category
            else if (category) {
                nameParts.push(`${category.charAt(0).toUpperCase() + category.slice(1)} Voice`);
            }
            
            // Add provider (skip "system")
            if (validProvider) {
                if (nameParts.length > 0) {
                    nameParts.push(`(${validProvider})`);
                } else {
                    // Capitalize first letter
                    const providerName = validProvider.charAt(0).toUpperCase() + validProvider.slice(1);
                    nameParts.push(`${providerName} Voice`);
                }
            }
            
            // Add language
            if (language) {
                if (nameParts.length > 0) {
                    nameParts.push(`- ${language}`);
                } else {
                    nameParts.push(`Voice (${language})`);
                }
            }
            
            // Try to extract more info from settings or metadata
            if (nameParts.length === 0) {
                // Try gender or accent
                if (gender) {
                    nameParts.push(`${gender.charAt(0).toUpperCase() + gender.slice(1)} Voice`);
                } else if (accent) {
                    nameParts.push(`${accent.charAt(0).toUpperCase() + accent.slice(1)} Voice`);
                } else if (style) {
                    nameParts.push(`${style.charAt(0).toUpperCase() + style.slice(1)} Voice`);
                }
                // Check if there's a voice type that's meaningful
                else {
                    const voiceType = voice.voice_type || '';
                    if (voiceType && voiceType.toLowerCase() !== 'tts' && voiceType.toLowerCase() !== 'system' && voiceType.toLowerCase() !== 'default') {
                        nameParts.push(`${voiceType} Voice`);
                    } else if (voice.description && !voice.description.toLowerCase().includes('default') && !voice.description.toLowerCase().includes('default voice')) {
                        // Use description if available and not generic
                        nameParts.push(voice.description);
                    } else {
                        // Try to create a unique name based on available info
                        const parts = [];
                        if (language) parts.push(language);
                        if (validProvider) parts.push(validProvider);
                        // Check metadata quality or other fields
                        if (metadata.quality && metadata.quality !== 'high') {
                            parts.push(metadata.quality);
                        }
                        if (parts.length > 0) {
                            nameParts.push(`${parts.join(' ')} Voice`);
                        } else {
                            // For voices with no distinguishing features, use a more descriptive name
                            // Try to use template_id or voice_id to create unique names
                            const voiceNum = voice.template_id || voice.voice_id || voice.id || index + 1;
                            // Use a format like "Voice #1" or "Standard Voice 1"
                            if (metadata.quality === 'high') {
                                nameParts.push(`Standard Voice ${voiceNum}`);
                            } else {
                                nameParts.push(`Voice ${voiceNum}`);
                            }
                        }
                    }
                }
            }
            
            displayName = nameParts.join(' ');
        }
        
        // Final fallback if still empty
        if (!displayName || displayName.trim() === '') {
            displayName = `Voice ${index + 1}`;
        }
        
        // Log for first few voices to debug
        if (index < 3) {
            console.log(`🔊 Voice ${index} name generation:`, {
                originalName: name,
                metadata: metadata,
                finalName: displayName
            });
        }
        
        option.textContent = displayName;
        
        if ((voice.id === selectedId || voice.voice_id === selectedId || voiceId === selectedId) && selectedId) {
            option.selected = true;
            showVoicePreview(voice);
            // Reset scroll to top immediately after selecting (prevents auto-scroll to selected item)
            select.scrollTop = 0;
        }
        select.appendChild(option);
    });
    
    // Ensure the select is visible and properly sized
    select.style.display = 'block';
    select.style.visibility = 'visible';
    select.style.height = '200px';
    select.style.minHeight = '200px';
    select.style.maxHeight = '300px';
    select.style.overflowY = 'auto';
    select.style.width = '100%';
    
    // Only add change listener if not already attached
    if (!hasExistingListener) {
        select.setAttribute('data-listener-attached', 'true');
        select.addEventListener('change', (e) => {
            const voiceId = e.target.value;
            console.log('🔊 Voice selected:', voiceId);
            const voice = filteredVoices.find(v => {
                const vId = v.id || v.voice_id;
                return vId === voiceId || v.id === voiceId || v.voice_id === voiceId;
            });
            if (voice) {
                console.log('🔊 Showing preview for voice:', voice.name || voice.id);
                showVoicePreview(voice);
            } else {
                console.warn('⚠️ Voice not found for ID:', voiceId);
                hideVoicePreview();
            }
        });
    }
    
    // Reset scroll position to top (after selected option might have scrolled it)
    // Use multiple methods to ensure this happens after browser's auto-scroll
    setTimeout(() => {
        select.scrollTop = 0;
        // Also use requestAnimationFrame as a backup
        requestAnimationFrame(() => {
            select.scrollTop = 0;
        });
    }, 0);
    
    // Log for debugging
    console.log('✅ Voice select populated with', select.options.length, 'options');
    console.log('🔊 First 5 options:', Array.from(select.options).slice(0, 5).map(opt => ({ value: opt.value, text: opt.textContent })));
    console.log('🔊 Select element visible:', select.offsetHeight > 0, 'Height:', select.offsetHeight);
    
    // Force a reflow to ensure the select is visible
    void select.offsetHeight;
    
    // Verify the select is in the DOM and visible
    const computedStyle = window.getComputedStyle(select);
    const selectInfo = {
        inDOM: document.body.contains(select),
        display: computedStyle.display,
        visibility: computedStyle.visibility,
        height: computedStyle.height,
        width: computedStyle.width,
        opacity: computedStyle.opacity,
        zIndex: computedStyle.zIndex,
        optionsCount: select.options.length,
        size: select.getAttribute('size'),
        clientHeight: select.clientHeight,
        offsetHeight: select.offsetHeight,
        scrollHeight: select.scrollHeight
    };
    console.log('🔊 Select element details:', selectInfo);
    
    // If the select has no height, force it
    if (parseInt(computedStyle.height) === 0 || computedStyle.height === 'auto') {
        console.warn('⚠️ Select has no height, setting explicit height');
        select.style.height = '200px';
        select.style.minHeight = '200px';
    }
    
    // Ensure parent is visible
    const parent = select.parentElement;
    if (parent) {
        const parentStyle = window.getComputedStyle(parent);
        const parentInfo = {
            display: parentStyle.display,
            visibility: parentStyle.visibility,
            overflow: parentStyle.overflow,
            overflowY: parentStyle.overflowY,
            height: parentStyle.height,
            maxHeight: parentStyle.maxHeight,
            clientHeight: parent.clientHeight,
            scrollHeight: parent.scrollHeight
        };
        console.log('Parent element:', parentInfo);
        
        // If parent has max-height and content is taller, ensure it's scrollable
        if (parentInfo.maxHeight && parentInfo.maxHeight !== 'none') {
            const maxHeightValue = parseInt(parentInfo.maxHeight);
            if (parent.scrollHeight > maxHeightValue) {
                console.log('Parent content exceeds max-height, ensuring scrollable');
                parent.style.overflowY = 'auto';
            }
        }
    }
    
    // Add a visible border to help debug visibility
    select.style.border = '2px solid #4a90e2';
    select.style.backgroundColor = 'var(--bg-secondary)';
    
    // Log the actual rendered dimensions
    setTimeout(() => {
        const rect = select.getBoundingClientRect();
        console.log('🔊 Select bounding rect:', {
            top: rect.top,
            left: rect.left,
            width: rect.width,
            height: rect.height,
            visible: rect.width > 0 && rect.height > 0
        });
        
        // If height is 0, there's a rendering issue
        if (rect.height === 0) {
            console.error('⚠️ Select has 0 height! This is a rendering issue.');
            // Try forcing a different display mode
            select.style.display = 'block';
            select.style.position = 'relative';
            select.style.height = '200px';
        }
        
        // Don't scroll into view or focus on initial load - this causes the modal to jump to the voice section
        // Only focus/scroll when user actively interacts with the voice select
    }, 100);
}

function showVoicePreview(voice) {
    const preview = document.getElementById('voicePreview');
    const previewName = document.getElementById('voicePreviewName');
    const previewDescription = document.getElementById('voicePreviewDescription');
    const previewPlayButton = document.getElementById('voicePreviewPlayButton');
    
    previewName.textContent = voice.name || `Voice ${voice.id}`;
    previewDescription.textContent = voice.description || `${voice.voice_type} voice${voice.metadata?.provider ? ` (${voice.metadata.provider})` : ''}${voice.metadata?.language ? ` - ${voice.metadata.language}` : ''}`;
    preview.style.display = 'block';
    
    // Store the voice for playback
    if (previewPlayButton) {
        previewPlayButton.dataset.voiceId = voice.id || voice.voice_id;
        previewPlayButton.dataset.voiceData = JSON.stringify(voice);
    }
}

// Helper function to get message text from stored ID
function speakMessageFromId(messageId) {
    const text = window[`msg_${messageId}`];
    if (!text) {
        console.error('Message not found:', messageId);
        return;
    }
    // Find the button that was clicked
    const messageDiv = document.querySelector(`[data-message-id="${messageId}"]`);
    const button = messageDiv?.querySelector('.message-speaker-btn');
    if (button) {
        speakMessage(button, text);
    }
}

// Global audio manager to prevent overlapping audio
if (!window.audioManager) {
    window.audioManager = {
        currentAudio: null,
        currentButton: null,
        currentUtterance: null,
        currentAudioUrl: null,
        stopAll: function() {
            // Stop any playing audio
            if (this.currentAudio) {
                try {
                    // Remove all event listeners to prevent restart
                    const audio = this.currentAudio;
                    // Remove handlers
                    if (audio._handleEnded) {
                        audio.onended = null;
                        audio._handleEnded = null;
                    }
                    if (audio._handleError) {
                        audio.onerror = null;
                        audio._handleError = null;
                    }
                    audio.onplay = null;
                    audio.onpause = null;
                    // Pause and reset
                    audio.pause();
                    audio.currentTime = 0;
                    // Load empty source to fully stop and prevent any events
                    audio.src = '';
                    audio.load(); // Force reload with empty source
                } catch (e) {
                    console.warn('Error stopping audio:', e);
                }
                this.currentAudio = null;
            }
            // Revoke audio URL if exists
            if (this.currentAudioUrl) {
                try {
                    URL.revokeObjectURL(this.currentAudioUrl);
                } catch (e) {
                    console.warn('Error revoking audio URL:', e);
                }
                this.currentAudioUrl = null;
            }
            // Stop browser TTS
            if ('speechSynthesis' in window) {
                try {
                    window.speechSynthesis.cancel();
                } catch (e) {
                    console.warn('Error canceling speech synthesis:', e);
                }
            }
            if (this.currentUtterance) {
                this.currentUtterance = null;
            }
            // Reset button states
            if (this.currentButton) {
                const originalText = this.currentButton.getAttribute('data-original-text') || '🔊';
                this.currentButton.classList.remove('playing');
                this.currentButton.textContent = originalText;
                // Clear stored audio URL from button
                this.currentButton.removeAttribute('data-audio-url');
                this.currentButton = null;
            }
            // Reset all playing buttons
            document.querySelectorAll('.message-speaker-btn.playing').forEach(btn => {
                const originalText = btn.getAttribute('data-original-text') || '🔊';
                btn.classList.remove('playing');
                btn.textContent = originalText;
                btn.removeAttribute('data-audio-url');
            });
        }
    };
}

// Speak an AI message using Azure TTS
// Clean markdown formatting from text before TTS (remove **, *, _, etc.)
function cleanTextForTTS(text) {
    if (!text) return text;
    // Remove markdown bold markers (**text** or *text*)
    let cleaned = text.replace(/\*\*([^*]+)\*\*/g, '$1'); // Remove **bold**
    cleaned = cleaned.replace(/\*([^*]+)\*/g, '$1'); // Remove *italic* (but not **bold** which was already removed)
    // Remove markdown italic markers (_text_)
    cleaned = cleaned.replace(/_([^_]+)_/g, '$1'); // Remove _italic_
    // Remove markdown headers (# ## ###)
    cleaned = cleaned.replace(/^#{1,6}\s+/gm, ''); // Remove # headers at start of line
    // Remove markdown links [text](url) but keep the text
    cleaned = cleaned.replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1'); // Keep link text, remove URL
    // Remove markdown code blocks ```code``` but keep the code
    cleaned = cleaned.replace(/```[\s\S]*?```/g, ''); // Remove code blocks
    cleaned = cleaned.replace(/`([^`]+)`/g, '$1'); // Remove inline code markers
    // Remove any remaining standalone markdown markers
    cleaned = cleaned.replace(/\*\*/g, ''); // Remove any remaining **
    cleaned = cleaned.replace(/\*/g, ''); // Remove any remaining *
    cleaned = cleaned.replace(/__/g, ''); // Remove any remaining __
    cleaned = cleaned.replace(/_/g, ''); // Remove any remaining _
    // Clean up extra whitespace
    cleaned = cleaned.replace(/\s+/g, ' ').trim();
    return cleaned;
}

async function speakMessage(button, text, autoplay = false, useFullText = false) {
    if (!text || !text.trim()) {
        console.warn('No text to speak');
        return;
    }
    
    // Clean markdown formatting from text before sending to TTS
    text = cleanTextForTTS(text);
    
    // Stop any currently playing audio first
    window.audioManager.stopAll();
    
    // Update button state
    const originalText = button.textContent.trim();
    button.setAttribute('data-original-text', originalText);
    const isPlaying = button.classList.contains('playing');
    
    // If this button is already playing, pause/stop it
    if (isPlaying && window.audioManager.currentButton === button) {
        // Fully stop the audio
        if (window.audioManager.currentAudio) {
            try {
                const audio = window.audioManager.currentAudio;
                // Remove event listeners to prevent auto-restart
                if (audio._handleEnded) {
                    audio.onended = null;
                    audio._handleEnded = null;
                }
                if (audio._handleError) {
                    audio.onerror = null;
                    audio._handleError = null;
                }
                audio.onplay = null;
                audio.pause();
                audio.currentTime = 0;
                // Clear source to fully stop
                audio.src = '';
                audio.load(); // Force reload with empty source
            } catch (e) {
                console.warn('Error pausing audio:', e);
            }
        }
        window.audioManager.stopAll();
        return;
    }
    
    // Check if there's a stored audio for this button (from a previous autoplay failure)
    const storedAudioUrl = button.getAttribute('data-audio-url');
    if (storedAudioUrl && window.audioManager.currentAudio) {
        // Check if this is the same button that had autoplay blocked
        const storedButton = window.audioManager.currentButton;
        if (storedButton === button || (storedButton && storedButton.getAttribute('data-audio-url') === storedAudioUrl)) {
            // Try to play the stored audio (user clicked after autoplay was blocked)
            const audio = window.audioManager.currentAudio;
            if (audio && (audio.readyState >= 2 || audio.readyState === 0)) { // HAVE_CURRENT_DATA or HAVE_NOTHING
                // Mark this button as the current one
                window.audioManager.currentButton = button;
                button.classList.add('playing');
                button.textContent = '⏸️';
                button.disabled = false;
                
                audio.play().then(() => {
                    // Success - audio is playing
                    console.log('✅ Playing stored audio after user click');
                }).catch(err => {
                    console.error('Error playing stored audio:', err);
                    // Clear stored audio and continue with normal flow to fetch new
                    button.removeAttribute('data-audio-url');
                    if (window.audioManager.currentAudio === audio) {
                        window.audioManager.currentAudio = null;
                    }
                    if (window.audioManager.currentButton === button) {
                        window.audioManager.currentButton = null;
                    }
                    // Continue with normal flow below to fetch new audio
                    // Reset button state first
                    const originalText = button.getAttribute('data-original-text') || '🔊';
                    button.classList.remove('playing');
                    button.textContent = originalText;
                });
                // If audio is ready, try to play it and return
                if (audio.readyState >= 2 || audio.readyState === 0) {
                    return;
                }
            } else {
                // Audio not ready, clear it and fetch new
                button.removeAttribute('data-audio-url');
                if (window.audioManager.currentAudio === audio) {
                    window.audioManager.currentAudio = null;
                }
            }
        }
    }
    
    // Mark this button as the current one
    window.audioManager.currentButton = button;
    button.classList.add('playing');
    button.textContent = '⏸️';
    button.disabled = true;
    
    // CRITICAL: Create audio element IMMEDIATELY (synchronously) to preserve user interaction context
    // This must happen before any async operations
    const audio = new Audio();
    window.audioManager.currentAudio = audio;
    
    try {
        // Get voice settings from localStorage
        const selectedVoiceId = localStorage.getItem('selected_voice_id') || '7';
        // Convert frontend speed (1-100%) to backend rate (0.2-2.0, which is 20%-200% in Azure TTS)
        // Simple linear mapping: 1% → 0.2 rate (20%), 100% → 2.0 rate (200%)
        // Formula: rate = 0.2 + (speed_percent - 1) * 1.8 / 99
        const speedPercent = parseFloat(localStorage.getItem('voice_speed') || '1');
        // Clamp speed to valid range (1-100)
        const clampedSpeed = Math.max(1, Math.min(100, speedPercent));
        const voiceSpeed = 0.2 + (clampedSpeed - 1) * 1.8 / 99; // Map 1-100% to 0.2-2.0 rate (20%-200%)
        const voicePitch = parseFloat(localStorage.getItem('voice_pitch') || '100') / 100; // Convert percentage to pitch
        const voiceLanguage = localStorage.getItem('voice_language') || 'en-US';
        
        console.log('🔊 Speaking message with voice settings:', {
            voice_id: selectedVoiceId,
            speed: voiceSpeed,
            pitch: voicePitch,
            language: voiceLanguage
        });
        
        // Audio element already created above - configure it now
        audio.preload = 'auto';
        // Try to "prime" the audio element by calling load() within interaction context
        // This might help Safari preserve the interaction context for later play()
        try {
            audio.load(); // Prime the audio element
        } catch (e) {
            // Ignore errors - load() might fail if no src is set yet
        }
        
        // Get token for authentication
        const token = localStorage.getItem('access_token');
        const headers = {
            'Content-Type': 'application/json'
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Use Azure TTS synthesize endpoint
        // If we have a voice_id, use the voice-sample endpoint which maps to the correct Azure voice
        // Add retry logic for 5xx errors (502, 503, 504, etc.) which are often temporary
        const maxRetries = 2; // Retry up to 2 times (3 total attempts)
        let lastError = null;
        let response = null;
        
        for (let attempt = 0; attempt <= maxRetries; attempt++) {
            try {
                if (selectedVoiceId) {
                    // Use voice-sample endpoint which handles voice_id mapping
                    // Pass user's saved preferences to override database settings
                    // For autoplay, use shorter text to speed up fetch (preserve user interaction context)
                    // Use first 1000 chars for autoplay to make fetch very fast, full 10000 for manual playback or opening prompt
                    // Exception: if useFullText is true (e.g., for opening prompt or lesson plans), use more text (up to 5000 chars for autoplay, 10000 for manual)
                    const isAutoplay = autoplay === true;
                    // For autoplay: 1000 chars (fast), 5000 chars if useFullText (for lesson plans), 10000 for manual playback
                    const maxTextLength = (isAutoplay && !useFullText) ? 1000 : (isAutoplay && useFullText) ? 5000 : 10000;
                    const params = new URLSearchParams({
                        voice_id: selectedVoiceId,
                        text: text.substring(0, maxTextLength), // Shorter text for faster autoplay
                        rate: voiceSpeed.toString(), // User's saved speed preference
                        pitch: ((voicePitch - 1) * 50).toString() // Convert percentage to semitones (-50 to +50)
                    });
                    response = await fetch(`${API_BASE_URL}/text-to-speech/voice-sample?${params.toString()}`, {
                        method: 'POST',
                        headers: headers
                    });
                } else {
                    // For autoplay, use shorter text to speed up fetch
                    // Exception: if useFullText is true (e.g., for opening prompt or lesson plans), use more text (up to 5000 chars for autoplay, 10000 for manual)
                    const isAutoplay = autoplay === true;
                    // For autoplay: 1000 chars (fast), 5000 chars if useFullText (for lesson plans), 10000 for manual playback
                    const maxTextLength = (isAutoplay && !useFullText) ? 1000 : (isAutoplay && useFullText) ? 5000 : 10000;
                    // Use synthesize endpoint with direct parameters
                    const params = new URLSearchParams({
                        text: text.substring(0, maxTextLength), // Shorter text for faster autoplay
                        rate: voiceSpeed.toString(),
                        pitch: ((voicePitch - 1) * 50).toString(), // Convert to semitones (-50 to +50)
                        language: voiceLanguage
                    });
                    response = await fetch(`${API_BASE_URL}/text-to-speech/synthesize?${params.toString()}`, {
                        method: 'POST',
                        headers: headers
                    });
                }
                
                if (!response.ok) {
                    // Check if it's a retryable error (5xx server errors)
                    const isRetryable = response.status >= 500 && response.status < 600;
                    
                    // Try to get error details from response
                    // CRITICAL: Clone the response before reading body to avoid "Body is disturbed or locked" error
                    let errorDetail = `TTS request failed: ${response.status}`;
                    try {
                        // Clone response to read body without locking it
                        const clonedResponse = response.clone();
                        const errorData = await clonedResponse.json();
                        errorDetail = errorData.detail || errorData.message || errorDetail;
                        console.error('❌ TTS Error Response:', errorData);
                    } catch (e) {
                        // If JSON parsing fails, try text (but only if we haven't already read the body)
                        try {
                            const errorText = await response.text();
                            console.error('❌ TTS Error Response (text):', errorText);
                            errorDetail = errorText || errorDetail;
                        } catch (textError) {
                            // Body already read or other error
                            console.error('❌ TTS Error (could not read response body):', textError);
                        }
                    }
                    
                    // If it's a retryable error and we have retries left, retry
                    if (isRetryable && attempt < maxRetries) {
                        const delay = (attempt + 1) * 500; // Exponential backoff: 500ms, 1000ms
                        console.warn(`⚠️ TTS server error ${response.status}, retrying in ${delay}ms (attempt ${attempt + 1}/${maxRetries})...`);
                        await new Promise(resolve => setTimeout(resolve, delay));
                        lastError = new Error(errorDetail);
                        continue; // Retry the fetch
                    } else {
                        // Not retryable or out of retries - throw error
                        throw new Error(errorDetail);
                    }
                } else {
                    // Success - break out of retry loop
                    break;
                }
            } catch (error) {
                // Network errors or other fetch failures
                const isNetworkError = error.message && (
                    error.message.includes('fetch') || 
                    error.message.includes('network') || 
                    error.message.includes('Failed to fetch') ||
                    error.name === 'TypeError'
                );
                
                if (isNetworkError && attempt < maxRetries) {
                    const delay = (attempt + 1) * 500; // Exponential backoff: 500ms, 1000ms
                    console.warn(`⚠️ TTS network error, retrying in ${delay}ms (attempt ${attempt + 1}/${maxRetries})...`);
                    lastError = error;
                    await new Promise(resolve => setTimeout(resolve, delay));
                    continue; // Retry the fetch
                } else {
                    // Not a network error or out of retries - throw error
                    throw error;
                }
            }
        }
        
        // If we exhausted all retries, throw the last error
        if (!response || !response.ok) {
            throw lastError || new Error('TTS request failed after retries');
        }
        
        // Get audio blob
        const audioBlob = await response.blob();
        const blobSize = audioBlob.size;
        const blobSizeKB = (blobSize / 1024).toFixed(2);
        console.log(`🔊 Audio blob received: ${blobSizeKB} KB (${blobSize} bytes) for ${text.substring(0, 50)}...`);
        
        // Check if blob seems too small (might be truncated)
        // MP3 audio at 16kHz 64kbps: ~8 KB per second of audio
        // For 5000 chars at slow rate (0.2x), expect ~60-90 seconds = ~480-720 KB
        // For 5000 chars at normal rate (1.0x), expect ~12-15 seconds = ~96-120 KB
        const expectedMinSize = Math.max(10, (text.length / 100) * 8); // Rough estimate: 8 KB per 100 chars
        if (blobSize < expectedMinSize) {
            console.warn(`⚠️ Audio blob seems small (${blobSizeKB} KB) for ${text.length} characters. Expected at least ~${(expectedMinSize/1024).toFixed(2)} KB. May be truncated.`);
        }
        
        const audioUrl = URL.createObjectURL(audioBlob);
        window.audioManager.currentAudioUrl = audioUrl; // Store URL to revoke later
        
        // CRITICAL: Explicitly set playbackRate to 1.0 to ensure consistent playback speed across ALL browsers
        // Different browsers (Chrome, Safari, Firefox, Edge) may have different default playback rates
        // The rate is already set in the Azure TTS generation, so we want 1.0x playback (no browser adjustment)
        audio.playbackRate = 1.0;
        
        // CRITICAL: Set audio source and call play() IMMEDIATELY in the same synchronous operation
        // Safari requires play() to be called synchronously within user interaction context
        // We must do this in one synchronous block - no async operations, no load(), no delays
        // Set up event handlers FIRST (before setting src) to preserve context
        const handleEnded = () => {
            // Check if audio was manually stopped (src cleared)
            if (!audio.src || audio.src === '' || audio.src === window.location.href) {
                return; // Audio was stopped, don't process ended event
            }
            
            // Log audio completion info
            const duration = audio.duration || 0;
            const currentTime = audio.currentTime || 0;
            console.log(`✅ Audio playback completed: duration=${duration.toFixed(2)}s, currentTime=${currentTime.toFixed(2)}s`);
            
            // Check if audio ended prematurely (duration is much longer than currentTime)
            if (duration > 0 && currentTime > 0 && (duration - currentTime) > 1) {
                console.warn(`⚠️ Audio may have ended prematurely: duration=${duration.toFixed(2)}s but stopped at ${currentTime.toFixed(2)}s`);
            }
            
            const originalText = button.getAttribute('data-original-text') || '🔊';
            button.classList.remove('playing');
            button.textContent = originalText;
            button.disabled = false;
            // Revoke URL after a delay to ensure audio is fully done
            setTimeout(() => {
                if (window.audioManager.currentAudioUrl === audioUrl) {
                    URL.revokeObjectURL(audioUrl);
                    window.audioManager.currentAudioUrl = null;
                }
            }, 100);
            // Clear manager state
            if (window.audioManager.currentAudio === audio) {
                window.audioManager.currentAudio = null;
            }
            if (window.audioManager.currentButton === button) {
                window.audioManager.currentButton = null;
            }
        };
        
        const handleError = (e) => {
            // Check if audio was manually stopped
            if (!audio.src || audio.src === '' || audio.src === window.location.href) {
                return; // Audio was stopped, don't process error
            }
            console.error('Error playing audio:', e);
            const originalText = button.getAttribute('data-original-text') || '🔊';
            button.classList.remove('playing');
            button.textContent = originalText;
            button.disabled = false;
            // Revoke URL after a delay
            setTimeout(() => {
                if (window.audioManager.currentAudioUrl === audioUrl) {
                    URL.revokeObjectURL(audioUrl);
                    window.audioManager.currentAudioUrl = null;
                }
            }, 100);
            // Clear manager state
            if (window.audioManager.currentAudio === audio) {
                window.audioManager.currentAudio = null;
            }
            if (window.audioManager.currentButton === button) {
                window.audioManager.currentButton = null;
            }
            // Only show alert for actual errors, not autoplay restrictions
            if (e.error && e.error.code !== 20) { // 20 is MEDIA_ERR_ABORTED
                console.error('Audio playback error:', e.error);
            }
        };
        
        // Store handlers BEFORE setting src to preserve interaction context
        audio.onended = handleEnded;
        audio.onerror = handleError;
        audio._handleEnded = handleEnded;
        audio._handleError = handleError;
        
        button.disabled = false;
        
        // CRITICAL: Set src and call play() IMMEDIATELY in one synchronous block
        // NO delays, NO load(), NO async operations between these two lines
        // Safari requires play() to be called synchronously within user interaction context
        audio.src = audioUrl;
        
        console.log('🔊 Attempting to play audio immediately (within user interaction context)...', {
            audioReadyState: audio.readyState,
            audioSrc: audio.src.substring(0, 50) + '...',
            hasUserInteraction: true
        });
        
        // CRITICAL: Call play() IMMEDIATELY after setting src - no delays whatsoever
        // Safari will queue the play() call and execute it when the audio is ready
        // This MUST happen synchronously - even though blob fetch was async, we call play() NOW
        let playPromise;
        try {
            // Call play() immediately - Safari will queue this if audio isn't ready yet
            // This MUST happen synchronously - no await, no setTimeout, no delays
            playPromise = audio.play();
            
            if (playPromise !== undefined) {
                // Handle the promise asynchronously - don't await it
                // Safari will resolve it when audio is ready, or reject if autoplay is blocked
                playPromise.then(() => {
                    console.log('✅ Audio playback started successfully');
                    // Success - store audio URL in button
                    button.setAttribute('data-audio-url', audioUrl);
                }).catch((playError) => {
                    console.error('❌ Audio play error:', {
                        name: playError.name,
                        message: playError.message
                    });
                    
                    // Check if it's an autoplay restriction
                    if (playError.name === 'NotAllowedError' || playError.name === 'NotSupportedError') {
                        console.log('⚠️ Autoplay blocked - user interaction may have expired. Audio ready for manual play.');
                        // Don't show error - just reset button state but keep audio ready
                        const originalText = button.getAttribute('data-original-text') || '🔊';
                        button.classList.remove('playing');
                        button.textContent = originalText;
                        button.disabled = false;
                        // Store audio URL in button so user can click to play
                        button.setAttribute('data-audio-url', audioUrl);
                        // Keep audio and URL in manager for when user clicks
                        // Don't revoke URL yet - user might click to play
                    } else {
                        // Other errors - log and reset
                        console.error('Error playing audio:', playError);
                        const originalText = button.getAttribute('data-original-text') || '🔊';
                        button.classList.remove('playing');
                        button.textContent = originalText;
                        button.disabled = false;
                        if (window.audioManager.currentAudio === audio) {
                            window.audioManager.currentAudio = null;
                        }
                        if (window.audioManager.currentButton === button) {
                            window.audioManager.currentButton = null;
                        }
                        setTimeout(() => {
                            if (window.audioManager.currentAudioUrl === audioUrl) {
                                URL.revokeObjectURL(audioUrl);
                                window.audioManager.currentAudioUrl = null;
                            }
                        }, 100);
                    }
                });
            } else {
                // Play promise is undefined (older browser), audio should be playing
                console.log('✅ Audio playback started (no promise)');
                button.setAttribute('data-audio-url', audioUrl);
                // Create a resolved promise for consistency
                playPromise = Promise.resolve();
            }
        } catch (playError) {
            // Synchronous error (shouldn't happen with modern browsers, but handle it)
            console.error('❌ Synchronous audio play error:', {
                name: playError.name,
                message: playError.message
            });
            
            // Check if it's an autoplay restriction
            if (playError.name === 'NotAllowedError' || playError.name === 'NotSupportedError') {
                console.log('⚠️ Autoplay blocked - user interaction may have expired. Audio ready for manual play.');
                const originalText = button.getAttribute('data-original-text') || '🔊';
                button.classList.remove('playing');
                button.textContent = originalText;
                button.disabled = false;
                button.setAttribute('data-audio-url', audioUrl);
                // Create a rejected promise so widget updates can proceed
                playPromise = Promise.reject(playError);
            } else {
                // Other errors - log and reset
                const originalText = button.getAttribute('data-original-text') || '🔊';
                button.classList.remove('playing');
                button.textContent = originalText;
                button.disabled = false;
                if (window.audioManager.currentAudio === audio) {
                    window.audioManager.currentAudio = null;
                }
                if (window.audioManager.currentButton === button) {
                    window.audioManager.currentButton = null;
                }
                setTimeout(() => {
                    if (window.audioManager.currentAudioUrl === audioUrl) {
                        URL.revokeObjectURL(audioUrl);
                        window.audioManager.currentAudioUrl = null;
                    }
                }, 100);
                // Create a rejected promise so widget updates can proceed
                playPromise = Promise.reject(playError);
            }
        }
        
        // CRITICAL: Return the play promise immediately
        // This allows widget updates to wait for the play() call to complete
        // The promise resolves/rejects when play() is called, not when audio finishes loading
        // Ensure playPromise is always defined before returning
        if (!playPromise) {
            playPromise = Promise.resolve(); // Fallback if somehow undefined
        }
        return playPromise;
        
    } catch (error) {
        console.error('Error speaking message:', error);
        const originalText = button.getAttribute('data-original-text') || '🔊';
        button.classList.remove('playing');
        button.textContent = originalText;
        button.disabled = false;
        // Clear manager state
        if (window.audioManager.currentButton === button) {
            window.audioManager.currentButton = null;
        }
        
        // Return a rejected promise so widget updates can proceed
        // Note: Fallback to browser TTS removed - widget updates need to proceed immediately
        return Promise.reject(error);
    }
}

async function playVoiceSample(voice) {
    const playButton = document.getElementById('voicePreviewPlayButton');
    
    // Update button state
    if (playButton) {
        playButton.disabled = true;
        playButton.textContent = 'Loading...';
    }
    
    try {
        // Get voice ID
        const voiceId = voice.id || voice.voice_id || '';
        if (!voiceId) {
            throw new Error('Voice ID is required');
        }
        
        // Get token for authentication
        const token = localStorage.getItem('access_token');
        const headers = {
            'Content-Type': 'application/json'
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Use same default speed as autoplay voice (from user's saved preference)
        // Convert frontend speed (1-100%) to backend rate (0.2-2.0, which is 20%-200% in Azure TTS)
        // Simple linear mapping: 1% → 0.2 rate (20%), 100% → 2.0 rate (200%)
        // Formula: rate = 0.2 + (speed_percent - 1) * 1.8 / 99
        const speedPercent = parseFloat(localStorage.getItem('voice_speed') || '1');
        // Clamp speed to valid range (1-100)
        const clampedSpeed = Math.max(1, Math.min(100, speedPercent));
        const voiceSpeed = 0.2 + (clampedSpeed - 1) * 1.8 / 99; // Map 1-100% to 0.2-2.0 rate (20%-200%)
        
        // Call backend Azure TTS endpoint with user's saved speed preference
        const params = new URLSearchParams({
            voice_id: voiceId,
            rate: voiceSpeed.toString()
        });
        const response = await fetch(`/api/v1/text-to-speech/voice-sample?${params.toString()}`, {
            method: 'POST',
            headers: headers
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Failed to generate voice sample: ${response.status} ${errorText}`);
        }
        
        // Get audio blob
        const audioBlob = await response.blob();
        
        // Create audio element and play
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        // CRITICAL: Explicitly set playbackRate to 1.0 to ensure consistent playback speed across ALL browsers
        // Different browsers (Chrome, Safari, Firefox, Edge) may have different default playback rates
        // The rate is already set in the Azure TTS generation, so we want 1.0x playback (no browser adjustment)
        audio.playbackRate = 1.0;
        
        if (playButton) {
            playButton.textContent = 'Playing...';
        }
        
        audio.onended = () => {
            URL.revokeObjectURL(audioUrl);
            if (playButton) {
                playButton.disabled = false;
                playButton.textContent = '▶ Play Sample';
            }
        };
        
        audio.onerror = (event) => {
            console.error('Audio playback error:', event);
            URL.revokeObjectURL(audioUrl);
            if (playButton) {
                playButton.disabled = false;
                playButton.textContent = '▶ Play Sample';
            }
            alert('Error playing voice sample. Please try again.');
        };
        
        // Play audio
        await audio.play();
        
    } catch (error) {
        console.error('Error playing voice sample:', error);
        if (playButton) {
            playButton.disabled = false;
            playButton.textContent = '▶ Play Sample';
        }
        
        // Fallback to browser TTS if Azure TTS fails
        console.log('Falling back to browser TTS...');
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance();
            utterance.text = "Hello, this is a sample of my voice. I can help you with your questions.";
            utterance.volume = voice.settings?.volume || voice.template_settings?.volume || 0.8;
            utterance.rate = voice.settings?.speed || voice.template_settings?.speed || 1.0;
            utterance.pitch = voice.settings?.pitch || voice.template_settings?.pitch || 1.0;
            
            utterance.onend = () => {
                if (playButton) {
                    playButton.disabled = false;
                    playButton.textContent = '▶ Play Sample';
                }
            };
            
            utterance.onerror = () => {
                if (playButton) {
                    playButton.disabled = false;
                    playButton.textContent = '▶ Play Sample';
                }
                alert('Error playing voice sample. Please check your Azure TTS configuration.');
            };
            
            window.speechSynthesis.speak(utterance);
        } else {
            alert('Text-to-speech is not supported in your browser, and Azure TTS is not available.');
        }
    }
}

function hideVoicePreview() {
    document.getElementById('voicePreview').style.display = 'none';
}

function setupVoiceSearch() {
    const searchInput = document.getElementById('voiceSearch');
    const clearButton = document.getElementById('clearVoiceSearch');
    const voiceSelect = document.getElementById('selectedVoice');
    
    if (!searchInput || !clearButton || !voiceSelect) return;
    
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase().trim();
        
        if (searchTerm === '') {
            filteredVoices = [...availableVoices];
        } else {
            filteredVoices = availableVoices.filter(voice => {
                const name = (voice.name || '').toLowerCase();
                const description = (voice.description || '').toLowerCase();
                const provider = (voice.metadata?.provider || '').toLowerCase();
                const language = (voice.metadata?.language || '').toLowerCase();
                const voiceType = (voice.voice_type || '').toLowerCase();
                
                return name.includes(searchTerm) ||
                       description.includes(searchTerm) ||
                       provider.includes(searchTerm) ||
                       language.includes(searchTerm) ||
                       voiceType.includes(searchTerm);
            });
        }
        
        // Save current selection if any
        const currentSelection = voiceSelect.value;
        populateVoiceSelect(currentSelection);
    });
    
    clearButton.addEventListener('click', () => {
        searchInput.value = '';
        filteredVoices = [...availableVoices];
        const currentSelection = voiceSelect.value;
        populateVoiceSelect(currentSelection);
    });
}

// Setup slider value displays
function setupSettingsSliders() {
    // Avatar scale slider
    const avatarScaleSlider = document.getElementById('avatarScale');
    const avatarScaleValue = document.getElementById('avatarScaleValue');
    if (avatarScaleSlider && avatarScaleValue) {
        avatarScaleSlider.addEventListener('input', (e) => {
            avatarScaleValue.textContent = parseFloat(e.target.value).toFixed(1);
        });
    }
    
    // Avatar opacity slider
    const avatarOpacitySlider = document.getElementById('avatarOpacity');
    const avatarOpacityValue = document.getElementById('avatarOpacityValue');
    if (avatarOpacitySlider && avatarOpacityValue) {
        avatarOpacitySlider.addEventListener('input', (e) => {
            avatarOpacityValue.textContent = e.target.value + '%';
        });
    }
    
    // Voice speed slider
    const voiceSpeedSlider = document.getElementById('voiceSpeed');
    const voiceSpeedValue = document.getElementById('voiceSpeedValue');
    if (voiceSpeedSlider && voiceSpeedValue) {
        voiceSpeedSlider.addEventListener('input', (e) => {
            voiceSpeedValue.textContent = e.target.value + '%';
        });
    }
    
    // Voice pitch slider
    const voicePitchSlider = document.getElementById('voicePitch');
    const voicePitchValue = document.getElementById('voicePitchValue');
    if (voicePitchSlider && voicePitchValue) {
        voicePitchSlider.addEventListener('input', (e) => {
            voicePitchValue.textContent = e.target.value + '%';
        });
    }
}

// Save settings
async function saveSettings() {
    // Theme & Display
    const theme = document.querySelector('input[name="theme"]:checked').value;
    const fontSize = document.getElementById('fontSize').value;
    const fontFamily = document.getElementById('fontFamily').value;
    const accentColor = document.getElementById('accentColor').value;
    const highContrast = document.getElementById('highContrast').checked;
    
    // Notifications
    const enableNotifications = document.getElementById('enableNotifications').checked;
    const pushNotifications = document.getElementById('pushNotifications').checked;
    const inAppNotifications = document.getElementById('inAppNotifications').checked;
    const smsNotifications = document.getElementById('smsNotifications').checked;
    const enableSounds = document.getElementById('enableSounds').checked;
    const quietHoursStart = document.getElementById('quietHoursStart').value;
    const quietHoursEnd = document.getElementById('quietHoursEnd').value;
    
    // Voice Input
    const enableVoiceInput = document.getElementById('enableVoiceInput').checked;
    
    // Get selected avatar and voice
    const selectedAvatarId = document.getElementById('selectedAvatar').value;
    const selectedVoiceId = document.getElementById('selectedVoice').value;
    
    // Avatar preferences
    const avatarScale = parseFloat(document.getElementById('avatarScale').value);
    const avatarOpacity = parseInt(document.getElementById('avatarOpacity').value) / 100; // Convert to 0-1 range
    const avatarColor = document.getElementById('avatarColor').value;
    
    // AI voice preferences
    const enableAIVoice = document.getElementById('enableAIVoice').checked;
    const enableOpeningPromptAutoplay = document.getElementById('enableOpeningPromptAutoplay').checked;
    const voiceSpeed = parseInt(document.getElementById('voiceSpeed').value);
    const voicePitch = parseInt(document.getElementById('voicePitch').value);
    const voiceLanguage = document.getElementById('voiceLanguage').value;
    
    // Language & Regional
    const language = document.getElementById('language').value;
    const timezone = document.getElementById('timezone').value;
    const dateFormat = document.getElementById('dateFormat').value;
    const timeFormat = document.getElementById('timeFormat').value;
    
    // Accessibility
    const reducedMotion = document.getElementById('reducedMotion').checked;
    const screenReader = document.getElementById('screenReader').checked;
    
    // Layout
    const sidebarPosition = document.getElementById('sidebarPosition').value;
    const gridView = document.getElementById('gridView').checked;
    
    // Performance
    const autoRefresh = document.getElementById('autoRefresh').checked;
    const refreshInterval = parseInt(document.getElementById('refreshInterval').value);
    
    // Privacy
    const analyticsOptIn = document.getElementById('analyticsOptIn').checked;
    const dataSharing = document.getElementById('dataSharing').checked;
    
    // Save to localStorage
    localStorage.setItem('dashboard_theme', theme);
    localStorage.setItem('font_size', fontSize);
    localStorage.setItem('font_family', fontFamily);
    localStorage.setItem('accent_color', accentColor);
    localStorage.setItem('high_contrast', highContrast);
    localStorage.setItem('enable_notifications', enableNotifications);
    localStorage.setItem('push_notifications', pushNotifications);
    localStorage.setItem('in_app_notifications', inAppNotifications);
    localStorage.setItem('sms_notifications', smsNotifications);
    localStorage.setItem('enable_sounds', enableSounds);
    localStorage.setItem('quiet_hours_start', quietHoursStart);
    localStorage.setItem('quiet_hours_end', quietHoursEnd);
    localStorage.setItem('enable_voice_input', enableVoiceInput);
    localStorage.setItem('selected_avatar_id', selectedAvatarId);
    localStorage.setItem('selected_voice_id', selectedVoiceId);
    localStorage.setItem('avatar_scale', avatarScale);
    localStorage.setItem('avatar_opacity', Math.round(avatarOpacity * 100));
    localStorage.setItem('avatar_color', avatarColor);
    localStorage.setItem('enable_ai_voice', enableAIVoice);
    localStorage.setItem('enable_opening_prompt_autoplay', enableOpeningPromptAutoplay);
    localStorage.setItem('voice_speed', voiceSpeed);
    localStorage.setItem('voice_pitch', voicePitch);
    localStorage.setItem('voice_language', voiceLanguage);
    localStorage.setItem('language', language);
    localStorage.setItem('timezone', timezone);
    localStorage.setItem('date_format', dateFormat);
    localStorage.setItem('time_format', timeFormat);
    localStorage.setItem('reduced_motion', reducedMotion);
    localStorage.setItem('screen_reader', screenReader);
    localStorage.setItem('sidebar_position', sidebarPosition);
    localStorage.setItem('grid_view', gridView);
    localStorage.setItem('auto_refresh', autoRefresh);
    localStorage.setItem('refresh_interval', refreshInterval);
    localStorage.setItem('analytics_opt_in', analyticsOptIn);
    localStorage.setItem('data_sharing', dataSharing);
    
    // Apply theme
    applyTheme();
    
    // Apply font size
    document.documentElement.style.setProperty('--base-font-size', 
        fontSize === 'small' ? '14px' : fontSize === 'large' ? '18px' : '16px');
    
    // Apply font family
    if (fontFamily !== 'system') {
        document.body.style.fontFamily = fontFamily;
    } else {
        document.body.style.fontFamily = '';
    }
    
    // Apply accent color
    document.documentElement.style.setProperty('--primary-color', accentColor);
    
    // Apply high contrast
    if (highContrast) {
        document.body.classList.add('high-contrast');
    } else {
        document.body.classList.remove('high-contrast');
    }
    
    // Apply reduced motion
    if (reducedMotion) {
        document.documentElement.style.setProperty('--transition', 'none');
    } else {
        document.documentElement.style.setProperty('--transition', 'all 0.3s ease');
    }
    
    // Apply sidebar position
    const sidebar = document.querySelector('.widgets-sidebar');
    if (sidebar) {
        if (sidebarPosition === 'right') {
            sidebar.style.order = '2';
        } else {
            sidebar.style.order = '0';
        }
    }
    
    // Save to backend API (for authenticated users)
    const token = localStorage.getItem('access_token');
    if (token) {
        try {
            const preferences = {
                avatar_id: selectedAvatarId,
                voice_id: selectedVoiceId,
                avatar_customization: {
                    scale: avatarScale,
                    opacity: avatarOpacity,
                    color: avatarColor
                },
                voice_preferences: {
                    voice_id: selectedVoiceId,
                    speed: voiceSpeed,
                    pitch: voicePitch,
                    language: voiceLanguage,
                    enabled: enableAIVoice
                }
            };
            
            const response = await fetch('/api/v1/dashboard/tools/ai-assistant/avatar/preferences', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(preferences)
            });
            
            if (!response.ok) {
                console.warn('Failed to save avatar preferences to backend, but saved to localStorage');
            }
        } catch (error) {
            console.error('Error saving avatar preferences to backend:', error);
            // Continue - at least localStorage is saved
        }
    }
    
    closeSettings();
    showSuccess('Settings saved successfully!');
    
    // Update the avatar display in the chat interface
    if (selectedAvatarId) {
        await loadAndDisplayAvatar(selectedAvatarId);
    }
}

// Toggle sidebar
function toggleSidebar(event) {
    // Prevent event propagation if event is provided
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    console.log('🔧 toggleSidebar called');
    
    // Try multiple selectors to find the sidebar
    let sidebar = document.querySelector('.widgets-sidebar');
    if (!sidebar) {
        sidebar = document.getElementById('widgetsSidebar');
    }
    if (!sidebar) {
        console.error('❌ Could not find sidebar element');
        return;
    }
    
    const floatingToggle = document.getElementById('floatingSidebarToggle');
    const toggleBtn = document.getElementById('toggleSidebar');
    
    if (!toggleBtn) {
        console.error('❌ Could not find toggleSidebar button');
        return;
    }
    
    const isCurrentlyCollapsed = sidebar.classList.contains('collapsed');
    console.log('🔧 Sidebar currently collapsed:', isCurrentlyCollapsed);
    
    // Toggle the collapsed class
    sidebar.classList.toggle('collapsed');
    const isCollapsed = sidebar.classList.contains('collapsed');
    console.log('🔧 Sidebar now collapsed:', isCollapsed);
    
    // When collapsing, clear inline width style to let CSS take over
    // When expanding, restore saved width or use default
    if (isCollapsed) {
        sidebar.style.width = '';
        sidebar.style.minWidth = '';
        sidebar.style.maxWidth = '';
    } else {
        // Restore saved width or use default
        const savedWidth = localStorage.getItem('sidebarWidth');
        if (savedWidth) {
            sidebar.style.width = savedWidth + 'px';
        } else {
            sidebar.style.width = '';
        }
        sidebar.style.minWidth = '';
        sidebar.style.maxWidth = '';
    }
    
    const icon = toggleBtn.querySelector('.icon');
    if (icon) {
        icon.textContent = isCollapsed ? '→' : '←';
        console.log('🔧 Icon updated to:', icon.textContent);
    }
    
    // Show/hide floating toggle button
    if (floatingToggle) {
        if (isCollapsed) {
            floatingToggle.style.display = 'flex';
        } else {
            floatingToggle.style.display = 'none';
        }
    }
    
    // Save sidebar state
    localStorage.setItem('sidebarCollapsed', isCollapsed);
    console.log('✅ Sidebar state saved:', isCollapsed);
}

// Logout
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        // Clear all auth data from localStorage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('teacher_id');
        localStorage.removeItem('user_email');
        
        // Clear widgets and dashboard state
        activeWidgets = [];
        localStorage.removeItem('dashboard_widgets');
        localStorage.removeItem('dashboard_last_session_time');
        sessionStorage.removeItem('dashboard_session_id');
        sessionStorage.removeItem('widgets_cleared_for_session');
        sessionStorage.removeItem('guest_name'); // Clear guest name on logout
        
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
    
    // Check if sidebar should be collapsed
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (sidebarCollapsed) {
        // Sidebar should be collapsed, ensure it is
        sidebar.classList.add('collapsed');
        sidebar.style.width = '';
        sidebar.style.minWidth = '';
        sidebar.style.maxWidth = '';
    } else if (savedSidebarWidth) {
        // Restore saved width if not collapsed
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

// Layout Customization Functions
let originalWidgetOrder = [];

// Open layout customization modal
function openLayoutCustomization() {
    console.log('🔧 Opening layout customization. Active widgets:', activeWidgets.length, activeWidgets);
    
    // Make sure we have the latest widgets from the DOM or localStorage
    if (activeWidgets.length === 0) {
        // Try to reload from localStorage
        loadWidgetsFromLocalStorage();
        console.log('🔧 Reloaded from localStorage. Active widgets:', activeWidgets.length);
    }
    
    // Store original order
    originalWidgetOrder = [...activeWidgets];
    
    // Show modal
    document.getElementById('layoutModal').classList.add('active');
    
    // Populate widgets list
    populateLayoutWidgetsList();
    
    // Initialize drag and drop
    initializeLayoutDragAndDrop();
}

// Close layout customization modal
function closeLayoutCustomization() {
    document.getElementById('layoutModal').classList.remove('active');
    // Restore original order if cancelled
    if (originalWidgetOrder.length > 0) {
        activeWidgets = [...originalWidgetOrder];
    }
}

// Populate the layout widgets list
function populateLayoutWidgetsList() {
    const listContainer = document.getElementById('layoutWidgetsList');
    if (!listContainer) {
        console.error('❌ Layout widgets list container not found!');
        return;
    }
    
    listContainer.innerHTML = '';
    
    console.log('🔧 Populating layout list. Active widgets count:', activeWidgets.length);
    console.log('🔧 Active widgets:', activeWidgets);
    
    if (activeWidgets.length === 0) {
        listContainer.innerHTML = '<p class="no-widgets-message">No widgets on your dashboard yet. Add widgets from the sidebar.</p>';
        return;
    }
    
    // Also try to get widgets from the DOM as a fallback
    const domWidgets = document.querySelectorAll('[data-widget-id]');
    console.log('🔧 Found widgets in DOM:', domWidgets.length);
    
    // If we have widgets in DOM but not in activeWidgets, try to sync
    if (domWidgets.length > activeWidgets.length) {
        console.log('⚠️ More widgets in DOM than in activeWidgets. Syncing...');
        const domWidgetIds = Array.from(domWidgets).map(el => el.dataset.widgetId);
        const missingWidgets = activeWidgets.filter(w => !domWidgetIds.includes(w.id));
        console.log('🔧 Missing widgets:', missingWidgets);
    }
    
    activeWidgets.forEach((widget, index) => {
        if (!widget || !widget.id) {
            console.warn('⚠️ Invalid widget at index', index, widget);
            return;
        }
        
        const widgetItem = document.createElement('div');
        widgetItem.className = 'layout-widget-item';
        widgetItem.draggable = true;
        widgetItem.dataset.widgetId = widget.id;
        widgetItem.dataset.index = index;
        
        const widgetName = widget.name || getWidgetTitle(widget.type) || 'Unknown Widget';
        const widgetType = getWidgetTitle(widget.type) || widget.type || 'Unknown';
        const widgetSize = widget.size || 'medium';
        
        widgetItem.innerHTML = `
            <div class="layout-widget-drag-handle">☰</div>
            <div class="layout-widget-info">
                <div class="layout-widget-name">${widgetName}</div>
                <div class="layout-widget-type">${widgetType}</div>
            </div>
            <div class="layout-widget-size">
                <span class="size-badge size-${widgetSize}">${widgetSize.toUpperCase()}</span>
            </div>
        `;
        
        // Add drag event listeners
        widgetItem.addEventListener('dragstart', handleDragStart);
        widgetItem.addEventListener('dragover', handleDragOver);
        widgetItem.addEventListener('drop', handleDrop);
        widgetItem.addEventListener('dragend', handleDragEnd);
        widgetItem.addEventListener('dragenter', handleDragEnter);
        
        listContainer.appendChild(widgetItem);
        console.log('✅ Added widget to layout list:', widgetName, widget.id);
    });
    
    console.log('✅ Layout list populated. Total items:', listContainer.children.length);
}

// Initialize drag and drop
function initializeLayoutDragAndDrop() {
    const listContainer = document.getElementById('layoutWidgetsList');
    if (!listContainer) return;
    
    // Add container-level drag events
    listContainer.addEventListener('dragover', handleContainerDragOver);
    listContainer.addEventListener('drop', handleContainerDrop);
    
    const items = document.querySelectorAll('.layout-widget-item');
    items.forEach(item => {
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragend', handleDragEnd);
    });
}

// Drag and drop handlers
let draggedElement = null;
let draggedIndex = null;

function handleDragStart(e) {
    draggedElement = this;
    draggedIndex = parseInt(this.dataset.index);
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', this.dataset.widgetId);
    // Allow dragging
    e.dataTransfer.dropEffect = 'move';
}

function handleDragEnter(e) {
    e.preventDefault();
    if (this !== draggedElement) {
        this.classList.add('drag-over');
    }
}

function handleContainerDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = 'move';
    
    const listContainer = e.currentTarget;
    const afterElement = getDragAfterElement(listContainer, e.clientY);
    const dragging = document.querySelector('.dragging');
    
    if (!dragging) return;
    
    // Remove drag-over class from all items
    listContainer.querySelectorAll('.layout-widget-item').forEach(item => {
        item.classList.remove('drag-over');
    });
    
    // Move the dragging element
    if (afterElement == null) {
        listContainer.appendChild(dragging);
    } else {
        listContainer.insertBefore(dragging, afterElement);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = 'move';
    
    if (this !== draggedElement) {
        this.classList.add('drag-over');
    }
}

function handleContainerDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    
    const listContainer = e.currentTarget;
    
    // Remove drag-over classes
    listContainer.querySelectorAll('.layout-widget-item').forEach(item => {
        item.classList.remove('drag-over');
    });
    
    // Update activeWidgets array based on new DOM order
    const items = Array.from(listContainer.querySelectorAll('.layout-widget-item'));
    const newOrder = items.map((item, index) => {
        const widgetId = item.dataset.widgetId;
        const widget = activeWidgets.find(w => w.id === widgetId);
        if (widget) {
            // Update the index in dataset
            item.dataset.index = index;
        }
        return widget;
    }).filter(w => w !== undefined);
    
    if (newOrder.length === activeWidgets.length) {
        activeWidgets = newOrder;
        console.log('✅ Widgets reordered:', activeWidgets.map(w => w.name || w.type));
    }
    
    return false;
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    return false;
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    this.classList.remove('drag-over');
    
    // Remove drag-over from all items
    const listContainer = document.getElementById('layoutWidgetsList');
    if (listContainer) {
        listContainer.querySelectorAll('.layout-widget-item').forEach(item => {
            item.classList.remove('drag-over');
        });
    }
    
    draggedElement = null;
    draggedIndex = null;
}

// Helper function to determine drop position
function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.layout-widget-item:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

// Save layout customization
function saveLayoutCustomization() {
    // Save to localStorage
    saveWidgetsToLocalStorage();
    
    // Re-render widgets with new order
    renderWidgets();
    
    // Close modal
    closeLayoutCustomization();
    
    // Show success message
    showSuccess('Layout saved successfully!');
    
    // Save to backend if authenticated
    const token = localStorage.getItem('access_token');
    if (token) {
        // TODO: Save layout to backend API
        console.log('Layout saved to localStorage. Backend sync can be implemented here.');
    }
}

// Reset layout to default
function resetLayoutToDefault() {
    if (confirm('Are you sure you want to reset the layout to default? This will restore the original widget order.')) {
        // Reset to original order
        if (originalWidgetOrder.length > 0) {
            activeWidgets = [...originalWidgetOrder];
        } else {
            // If no original order, sort by creation date
            activeWidgets.sort((a, b) => {
                const dateA = new Date(a.created_at || 0);
                const dateB = new Date(b.created_at || 0);
                return dateA - dateB;
            });
        }
        
        // Save and re-render
        saveWidgetsToLocalStorage();
        renderWidgets();
        populateLayoutWidgetsList();
        
        showSuccess('Layout reset to default!');
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

