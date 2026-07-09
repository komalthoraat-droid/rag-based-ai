document.addEventListener('DOMContentLoaded', () => {
    const queryInput = document.getElementById('query-input');
    const sendBtn = document.getElementById('send-btn');
    const welcomeScreen = document.getElementById('welcome-screen');
    const messagesWrapper = document.getElementById('messages-wrapper');
    const chatContainer = document.getElementById('chat-container');
    
    // Simple session ID persistence
    let sessionId = localStorage.getItem('rag_session_id') || 'sess_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('rag_session_id', sessionId);

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

        // Hide welcome screen
        if (welcomeScreen) welcomeScreen.style.display = 'none';
        messagesWrapper.style.display = 'flex';

        // Add user message to UI
        appendMessage('user', text);
        queryInput.value = '';

        // Choose between standard or streaming (Streaming enabled by default for UX)
        await fetchStreamingResponse(text);
    }

    async function fetchStreamingResponse(text) {
        const messageDiv = createMessageDiv('assistant');
        const contentDiv = messageDiv.querySelector('.message-content');
        messagesWrapper.appendChild(messageDiv);
        scrollToBottom();

        try {
            const response = await fetch('/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, session_id: sessionId })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullText = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const token = line.replace('data: ', '');
                        fullText += token;
                        contentDiv.innerHTML = fullText.replace(/\n/g, '<br>');
                        scrollToBottom();
                    }
                }
            }
        } catch (error) {
            contentDiv.innerHTML = `<span class="error">Connection error. Check backend.</span>`;
            console.error(error);
        }
    }

    function createMessageDiv(sender) {
        const div = document.createElement('div');
        div.className = `message ${sender}`;
        const icon = sender === 'user' ? 'ph-user' : 'ph-brain';
        
        div.innerHTML = `
            <div class="message-content"></div>
            <div class="metadata">
                <i class="ph ${icon}"></i> ${sender === 'user' ? 'You' : 'AI Assistant'}
            </div>
        `;
        return div;
    }

    function appendMessage(sender, text) {
        const div = createMessageDiv(sender);
        div.querySelector('.message-content').innerText = text;
        messagesWrapper.appendChild(div);
        scrollToBottom();
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});
