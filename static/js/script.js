// Chatbot functionality
document.addEventListener('DOMContentLoaded', function() {
    const chatbot = document.getElementById('chatbot');
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotBtn = document.getElementById('chatbot-btn');
    const chatbotClose = document.getElementById('chatbot-close');
    const messages = document.getElementById('chatbot-messages');
    const input = document.getElementById('chatbot-input');
    const sendBtn = document.getElementById('chatbot-send');

    // Toggle chatbot
    chatbotBtn.addEventListener('click', function() {
        chatbot.style.display = chatbot.style.display === 'none' ? 'flex' : 'none';
    });

    chatbotClose.addEventListener('click', function() {
        chatbot.style.display = 'none';
    });

    // Function to add message to chat
    function addMessage(text, isUser = false) {
        const msgDiv = document.createElement('div');
        msgDiv.textContent = text;
        msgDiv.className = isUser ? 'user' : 'bot';
        messages.appendChild(msgDiv);
        messages.scrollTop = messages.scrollHeight;
    }

    // Send message function
    function sendMessage() {
        const message = input.value.trim();
        if (message) {
            addMessage(message, true);
            input.value = '';

            // Fetch response from API
            fetch(`/api/chatbot?message=${encodeURIComponent(message)}`)
                .then(response => response.json())
                .then(data => {
                    addMessage(data.response);
                })
                .catch(error => {
                    addMessage('Sorry, something went wrong.');
                    console.error('Error:', error);
                });
        }
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});