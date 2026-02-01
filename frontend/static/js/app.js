// Initialize managers
const chatManager = new ChatManager();
const audioManager = new AudioManager();

// DOM elements
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const modelSelect = document.getElementById('model-select');
const micButton = document.getElementById('mic-button');
const settingsButton = document.getElementById('settings-button');
const settingsModal = document.getElementById('settings-modal');
const closeSettings = document.getElementById('close-settings');
const autoTtsToggle = document.getElementById('auto-tts-toggle');

// Settings (loaded from localStorage)
let settings = {
    autoTts: localStorage.getItem('autoTts') === 'true',
    whisperModel: localStorage.getItem('whisperModel') || 'base.en'
};

// Apply saved settings
autoTtsToggle.checked = settings.autoTts;

/**
 * Load available models from the API
 */
async function loadModels() {
    try {
        const response = await fetch('/api/models');

        if (!response.ok) {
            throw new Error('Failed to fetch models');
        }

        const models = await response.json();

        // Clear existing options
        modelSelect.innerHTML = '';

        if (models.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No models available';
            modelSelect.appendChild(option);
            return;
        }

        // Add model options
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.name;
            option.textContent = model.name;
            modelSelect.appendChild(option);
        });

        // Select first model by default
        if (models.length > 0) {
            modelSelect.value = models[0].name;
        }

    } catch (error) {
        console.error('Error loading models:', error);
        modelSelect.innerHTML = '<option value="">Error loading models</option>';
    }
}

/**
 * Handle form submission
 */
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    console.log('Form submitted');

    const message = messageInput.value.trim();
    console.log('Message:', message);

    if (!message) {
        console.log('Empty message, returning');
        return;
    }

    // Disable input while sending
    messageInput.disabled = true;
    sendButton.disabled = true;

    // Get selected model
    const selectedModel = modelSelect.value;
    console.log('Selected model:', selectedModel);

    try {
        // Send message
        await chatManager.sendMessage(message, selectedModel);
    } catch (error) {
        console.error('Error in form submission:', error);
    }

    // Clear input and re-enable
    messageInput.value = '';
    messageInput.disabled = false;
    sendButton.disabled = false;

    // Focus input
    messageInput.focus();
});

/**
 * Handle Enter key (Shift+Enter for new line)
 */
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.requestSubmit();
    }
});

/**
 * Auto-resize textarea
 */
messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
});

/**
 * Handle microphone button click
 */
micButton.addEventListener('click', async () => {
    if (audioManager.isRecording) {
        // Stop recording and transcribe
        micButton.classList.remove('recording');
        micButton.disabled = true;

        try {
            const audioBlob = await audioManager.stopRecording();
            chatManager.showError('Transcribing...', 'info');

            const transcription = await audioManager.transcribeAudio(audioBlob);

            if (transcription) {
                messageInput.value = transcription;
                messageInput.focus();
                chatManager.showError(''); // Clear info message
            } else {
                chatManager.showError('No speech detected. Please try again.');
            }
        } catch (error) {
            console.error('Transcription error:', error);
            chatManager.showError(`Transcription failed: ${error.message}`);
        } finally {
            micButton.disabled = false;
        }
    } else {
        // Start recording
        try {
            await audioManager.startRecording();
            micButton.classList.add('recording');
            chatManager.showError('Recording... Click again to stop', 'info');
        } catch (error) {
            console.error('Recording error:', error);
            chatManager.showError(error.message);
        }
    }
});

/**
 * Handle settings button
 */
settingsButton.addEventListener('click', () => {
    settingsModal.style.display = 'flex';
});

closeSettings.addEventListener('click', () => {
    settingsModal.style.display = 'none';
});

// Close modal when clicking outside
settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        settingsModal.style.display = 'none';
    }
});

/**
 * Handle auto-TTS toggle
 */
autoTtsToggle.addEventListener('change', () => {
    settings.autoTts = autoTtsToggle.checked;
    localStorage.setItem('autoTts', settings.autoTts);
});

/**
 * Add speaker button to messages
 */
function addSpeakerButton(messageElement, text) {
    const speakerBtn = document.createElement('button');
    speakerBtn.className = 'speaker-button';
    speakerBtn.title = 'Play as speech';
    speakerBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
        </svg>
    `;

    speakerBtn.addEventListener('click', async () => {
        try {
            speakerBtn.disabled = true;
            await audioManager.playTextAsSpeech(text);
        } catch (error) {
            console.error('TTS error:', error);
            chatManager.showError(`Failed to play speech: ${error.message}`);
        } finally {
            speakerBtn.disabled = false;
        }
    });

    messageElement.appendChild(speakerBtn);
}

/**
 * Override chat manager's message display to add speaker buttons
 */
const originalAddMessage = chatManager.addMessage;
chatManager.addMessage = function(content, role) {
    const messageElement = originalAddMessage.call(this, content, role);

    // Add speaker button to assistant messages
    if (role === 'assistant' && content) {
        addSpeakerButton(messageElement, content);

        // Auto-play if enabled
        if (settings.autoTts) {
            setTimeout(() => {
                audioManager.playTextAsSpeech(content).catch(err => {
                    console.error('Auto-TTS error:', err);
                });
            }, 500); // Small delay to ensure message is fully rendered
        }
    }

    return messageElement;
};

/**
 * Initialize app
 */
async function init() {
    // Load available models
    await loadModels();

    // Focus input
    messageInput.focus();

    // Check backend health
    try {
        const response = await fetch('/health');
        const health = await response.json();

        if (health.ollama !== 'connected') {
            chatManager.showError('Warning: Ollama is not connected. Please ensure Ollama is running.');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        chatManager.showError('Warning: Could not connect to backend.');
    }
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
