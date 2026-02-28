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

        await fetchAndAppendResponse(text);
    }

    async function fetchAndAppendResponse(text) {
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
        const formattedText = text.replace(/\n/g, '<br>');

        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="message-avatar">
                    ${avatarIcon}
                </div>
                <div class="message-content">
                    <div class="message-text">${formattedText}</div>
                    <div class="edit-container" style="display: none;">
                        <textarea class="edit-textarea" rows="2"></textarea>
                        <div class="edit-actions">
                            <button class="edit-btn cancel-btn">Cancel</button>
                            <button class="edit-btn submit-btn">Send</button>
                        </div>
                    </div>
                </div>
                <button class="edit-msg-btn" aria-label="Edit message" title="Edit message">
                    <i class="ph ph-pencil-simple"></i>
                </button>
            `;

            const editBtn = messageDiv.querySelector('.edit-msg-btn');
            const messageText = messageDiv.querySelector('.message-text');
            const editContainer = messageDiv.querySelector('.edit-container');
            const textarea = messageDiv.querySelector('.edit-textarea');
            const cancelBtn = messageDiv.querySelector('.cancel-btn');
            const submitBtn = messageDiv.querySelector('.submit-btn');

            let currentText = text;

            editBtn.addEventListener('click', () => {
                messageText.style.display = 'none';
                editBtn.style.display = 'none';
                editContainer.style.display = 'flex';
                textarea.value = currentText;
                textarea.focus();

                textarea.style.height = 'auto';
                textarea.style.height = textarea.scrollHeight + 'px';
            });

            textarea.addEventListener('input', function () {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });

            cancelBtn.addEventListener('click', () => {
                editContainer.style.display = 'none';
                messageText.style.display = 'block';
                editBtn.style.display = 'flex';
            });

            submitBtn.addEventListener('click', () => {
                const newText = textarea.value.trim();
                if (!newText) return;

                currentText = newText;
                messageText.innerHTML = newText.replace(/\n/g, '<br>');

                editContainer.style.display = 'none';
                messageText.style.display = 'block';
                editBtn.style.display = 'flex';

                let nextSibling = messageDiv.nextElementSibling;
                while (nextSibling) {
                    const toRemove = nextSibling;
                    nextSibling = nextSibling.nextElementSibling;
                    toRemove.remove();
                }

                fetchAndAppendResponse(currentText);
            });
        } else {
            messageDiv.innerHTML = `
                <div class="message-avatar">
                    ${avatarIcon}
                </div>
                <div class="message-content">
                    ${formattedText}
                </div>
            `;
        }

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
