/**
 * Chandran AI Chatbot System
 * Features: Product Suggestions, Cart Status, Real-time Interaction
 */
(function () {
    const chatTrigger = document.getElementById('chat-trigger');
    const chatWindow = document.getElementById('chat-window');
    const closeChat = document.getElementById('close-chat');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    // Toggle Chat
    if (chatTrigger) {
        chatTrigger.addEventListener('click', () => {
            chatWindow.classList.toggle('active');
            if (chatWindow.classList.contains('active')) {
                chatInput.focus();
            }
        });
    }

    if (closeChat) {
        closeChat.addEventListener('click', () => {
            chatWindow.classList.remove('active');
        });
    }

    // Handle Form Submission
    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const msg = chatInput.value.trim();
            if (!msg) return;

            addMessage(msg, 'user');
            chatInput.value = '';

            // Show typing indicator
            const typing = addTypingIndicator();

            // Send to Backend
            fetch('/chatbot/response/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ message: msg })
            })
                .then(res => res.json())
                .then(data => {
                    typing.remove();
                    if (data.response) {
                        addMessage(data.response, 'bot');
                        // Check if AI suggested an action (optional enhancement)
                        handleBotAction(data.action);
                    }
                })
                .catch(err => {
                    typing.remove();
                    addMessage("System Error: Could not connect to the Matrix. Check your uplink.", 'bot');
                });
        });
    }

    function addMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender} animate-in`;

        // Improved Markdown Parsing (Links and Bold)
        let formattedText = text
            .replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" class="chat-link">$1</a>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
        
        msgDiv.innerHTML = formattedText;

        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Auto-handle redirects if the response contains a link and seems like a command
        if (sender === 'bot' && text.includes('(/payment/)') && text.length < 100) {
            setTimeout(() => {
                 window.location.href = '/payment/';
            }, 2000);
        }
    }

    function addTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'typing-indicator';
        div.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return div;
    }

    function getCsrfToken() {
        return document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
    }

    function handleBotAction(action) {
        if (!action) return;
        // Example: if action is 'refresh_cart', we could trigger a UI update
        if (action === 'refresh_cart') {
            // Trigger cart count update or similar
        }
    }

})();
