// Utility functions

function formatTime(dateTimeString) {
    const date = new Date(dateTimeString);
    const now = new Date();
    const diff = now - date;
    
    // If today
    if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    }
    
    // If yesterday
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    if (date.toDateString() === yesterday.toDateString()) {
        return 'Hôm qua';
    }
    
    // Otherwise
    return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function makeWordsClickable(text) {
    // Split text into words and wrap each in a span
    const words = text.split(/(\s+)/);
    return words.map(word => {
        if (word.trim() && /[a-zA-Z]/.test(word)) {
            const cleanWord = word.replace(/[^a-zA-Z]/g, '');
            if (cleanWord) {
                return `<span class="word" onclick="lookupWord('${cleanWord}')">${escapeHtml(word)}</span>`;
            }
        }
        return escapeHtml(word);
    }).join('');
}

function showLoading(container) {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message ai loading-message';
    loadingDiv.innerHTML = `
        <div class="message-bubble">
            <div class="message-loading">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    container.appendChild(loadingDiv);
    scrollToBottom(container);
    return loadingDiv;
}

function removeLoading(loadingElement) {
    if (loadingElement && loadingElement.parentNode) {
        loadingElement.parentNode.removeChild(loadingElement);
    }
}

function scrollToBottom(container) {
    container.scrollTop = container.scrollHeight;
}

function showNotification(message, type = 'info') {
    // Simple notification (you can enhance this)
    alert(message);
}
