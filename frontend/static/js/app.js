// Initialize chat manager
const chatManager = new ChatManager();

// DOM elements
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const modelSelect = document.getElementById('model-select');

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
