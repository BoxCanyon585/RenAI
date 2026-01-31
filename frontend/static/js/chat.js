class ChatManager {
    constructor() {
        this.messagesContainer = document.getElementById('messages');
        this.loadingIndicator = document.getElementById('loading');
        this.errorMessageElement = document.getElementById('error-message');
        this.currentEventSource = null;
        this.currentAssistantMessage = null;
    }

    /**
     * Send a message to the chat API with streaming
     */
    async sendMessage(message, model) {
        console.log('ChatManager.sendMessage called with:', { message, model });

        // Append user message
        this.appendMessage('user', message);

        // Show loading indicator
        this.showLoading();

        // Hide any previous errors
        this.hideError();

        // Prepare request
        const requestBody = {
            message: message,
        };

        if (model) {
            requestBody.model = model;
        }

        console.log('Sending request to /api/chat/stream:', requestBody);

        try {
            // Create EventSource for streaming
            const response = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Read the streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantMessageText = '';

            // Create assistant message element
            this.currentAssistantMessage = this.createMessageElement('assistant', '');

            while (true) {
                const { done, value } = await reader.read();

                if (done) {
                    break;
                }

                // Decode the chunk
                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));

                            if (data.token) {
                                assistantMessageText += data.token;
                                this.updateMessageContent(this.currentAssistantMessage, assistantMessageText);
                            } else if (data.done) {
                                // Stream completed
                                this.hideLoading();
                            } else if (data.error) {
                                throw new Error(data.error);
                            }
                        } catch (e) {
                            // Skip invalid JSON lines
                            if (!line.includes('data: ')) {
                                console.warn('Failed to parse SSE data:', line, e);
                            }
                        }
                    }
                }
            }

            // Hide loading when done
            this.hideLoading();

        } catch (error) {
            console.error('Error sending message:', error);
            this.hideLoading();
            this.showError(`Failed to send message: ${error.message}`);

            // Remove the incomplete assistant message if exists
            if (this.currentAssistantMessage) {
                this.currentAssistantMessage.remove();
                this.currentAssistantMessage = null;
            }
        }
    }

    /**
     * Create a message element
     */
    createMessageElement(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;

        messageDiv.appendChild(contentDiv);
        this.messagesContainer.appendChild(messageDiv);

        // Scroll to bottom
        this.scrollToBottom();

        return messageDiv;
    }

    /**
     * Update message content
     */
    updateMessageContent(messageElement, content) {
        const contentDiv = messageElement.querySelector('.message-content');
        contentDiv.textContent = content;

        // Scroll to bottom
        this.scrollToBottom();
    }

    /**
     * Append a complete message to the chat
     */
    appendMessage(role, content) {
        this.createMessageElement(role, content);
    }

    /**
     * Show loading indicator
     */
    showLoading() {
        this.loadingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        this.loadingIndicator.style.display = 'none';
    }

    /**
     * Show error message
     */
    showError(message) {
        this.errorMessageElement.textContent = message;
        this.errorMessageElement.style.display = 'block';
    }

    /**
     * Hide error message
     */
    hideError() {
        this.errorMessageElement.style.display = 'none';
    }

    /**
     * Scroll chat to bottom
     */
    scrollToBottom() {
        const chatContainer = this.messagesContainer.parentElement;
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    /**
     * Clear all messages
     */
    clearMessages() {
        this.messagesContainer.innerHTML = '';
    }
}
