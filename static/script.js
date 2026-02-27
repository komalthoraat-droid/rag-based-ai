document.addEventListener('DOMContentLoaded', () => {
    const queryInput = document.getElementById('query-input');
    const sendBtn = document.getElementById('send-btn');
    const welcomeScreen = document.getElementById('welcome-screen');
    const messagesWrapper = document.getElementById('messages-wrapper');
    const chatContainer = document.getElementById('chat-container');

    // Make suggestion buttons work
    window.setQuery = function (text) {
        queryInput.value = text;
        sendMessage();
    };

    // Send message on Enter key
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Send message on button click
    sendBtn.addEventListener('click', sendMessage);

    async function sendMessage() {
        const text = queryInput.value.trim();
        if (!text) return;

        // Hide welcome screen and show messages list if first time
        if (welcomeScreen.style.display !== 'none') {
            welcomeScreen.style.display = 'none';
            messagesWrapper.style.display = 'flex';
        }

        // Add user message to UI
        appendMessage('user', text);
        queryInput.value = '';

        // Add loading indicator for AI
        const loadingId = appendLoadingIndicator();
        scrollToBottom();

        try {
            // Send API Request
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();

            // Remove loading indicator
            removeElement(loadingId);

            if (response.ok) {
                appendMessage('ai', data.response);
            } else {
                appendMessage('ai', `Error: ${data.error || 'Something went wrong.'}`);
            }

        } catch (error) {
            removeElement(loadingId);
            appendMessage('ai', `Connection error: Ensure the backend is running and Ollama is accessible.`);
            console.error(error);
        }

        scrollToBottom();
    }

    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const avatarIcon = sender === 'ai' ? '<i class="ph ph-brain"></i>' : '<i class="ph ph-user"></i>';

        // Format link/newlines nicely if needed. RAG returns raw text so we can just use innerText or simple markdown replacement.
        const formattedText = text.replace(/\n/g, '<br>');

        messageDiv.innerHTML = `
            <div class="message-avatar">
                ${avatarIcon}
            </div>
            <div class="message-content">
                ${formattedText}
            </div>
        `;

        messagesWrapper.appendChild(messageDiv);
    }

    function appendLoadingIndicator() {
        const id = 'loading-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai';
        messageDiv.id = id;

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="ph ph-brain"></i>
            </div>
            <div class="message-content typing-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        `;

        messagesWrapper.appendChild(messageDiv);
        return id;
    }

    function removeElement(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});
