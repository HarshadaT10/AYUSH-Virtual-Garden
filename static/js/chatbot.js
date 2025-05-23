document.addEventListener('DOMContentLoaded', function() {
    const bubble = document.getElementById('chatbot-bubble');
    const windowEl = document.getElementById('chatbot-window');
    const closeBtn = document.getElementById('chatbot-close');
    const form = document.getElementById('chatbot-form');
    const input = document.getElementById('chatbot-input');
    const messages = document.getElementById('chatbot-messages');

    // Open chat window
    bubble.addEventListener('click', () => {
        windowEl.classList.add('active');
        input.focus();
    });

    // Close chat window
    closeBtn.addEventListener('click', () => {
        windowEl.classList.remove('active');
    });

    // Send message
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const userMsg = input.value.trim();
        if (!userMsg) return;
        appendMessage(userMsg, 'user');
        input.value = '';
        messages.scrollTop = messages.scrollHeight;

        // Show loading
        appendMessage('...', 'bot', true);

        fetch('/chatbot', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: userMsg})
        })
        .then(res => res.json())
        .then(data => {
            removeLoading();
            appendMessage(data.response, 'bot');
            messages.scrollTop = messages.scrollHeight;
        })
        .catch(() => {
            removeLoading();
            appendMessage("Sorry, there was an error. Please try again.", 'bot');
        });
    });

    function appendMessage(text, sender, loading=false) {
        const msg = document.createElement('div');
        msg.className = 'chatbot-message ' + sender + (loading ? ' loading' : '');
        msg.textContent = text;
        messages.appendChild(msg);
        messages.scrollTop = messages.scrollHeight;
    }

    function removeLoading() {
        const loadingMsg = messages.querySelector('.chatbot-message.bot.loading');
        if (loadingMsg) loadingMsg.remove();
    }
});
