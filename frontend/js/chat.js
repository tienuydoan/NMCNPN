// Chat functionality

let currentConversationId = null;
let conversations = [];
let isVoiceMode = false;

// Initialize
window.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/';
        return;
    }
    
    // Verify token
    try {
        const result = await api.get('/api/auth/verify');
        if (!result.success) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/';
            return;
        }
        
        // Display user name
        const user = result.user;
        document.getElementById('user-name').textContent = user.ho_ten;
        
        // Load conversations
        await loadConversations();
        
        // Auto create conversation if none exists
        if (conversations.length === 0) {
            await createNewConversation();
        }
        
    } catch (error) {
        console.error('Auth error:', error);
        window.location.href = '/';
    }
});

// Voice mode toggle function
function toggleVoiceMode() {
    const btn = document.getElementById('voice-mode-btn');
    const icon = btn.querySelector('.voice-icon');
    const text = btn.querySelector('.voice-text');
    
    if (btn.classList.contains('active')) {
        // Stop voice mode
        btn.classList.remove('active');
        icon.textContent = '▶';
        text.textContent = 'Voice Mode';
        btn.title = 'Bắt đầu chế độ hội thoại liên tục';
        
        if (isRecording) {
            stopRecording();
        }
        isVoiceMode = false;
    } else {
        // Start voice mode
        btn.classList.add('active');
        icon.textContent = '■';
        text.textContent = 'Đang Live...';
        btn.title = 'Dừng chế độ hội thoại';
        
        isVoiceMode = true;
        startRecording();
    }
}


// Load conversations
async function loadConversations() {
    try {
        const result = await api.get('/api/conversation/list');
        
        if (result.success) {
            conversations = result.conversations;
            displayConversations();
        }
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

function displayConversations() {
    const list = document.getElementById('conversation-list');
    list.innerHTML = '';
    
    if (conversations.length === 0) {
        list.innerHTML = '<p style="text-align: center; color: #999;">Chưa có cuộc hội thoại</p>';
        return;
    }
    
    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = 'conversation-item';
        if (conv.ConversationID === currentConversationId) {
            item.classList.add('active');
        }
        
        item.innerHTML = `
            <div>Hội thoại #${conv.ConversationID}</div>
            <div class="conversation-time">${formatTime(conv.Datetime)}</div>
        `;
        
        item.onclick = () => loadConversation(conv.ConversationID);
        list.appendChild(item);
    });
}

// Create new conversation
async function createNewConversation() {
    try {
        const result = await api.post('/api/conversation/new', {});
        
        if (result.success) {
            conversations.unshift(result.conversation);
            displayConversations();
            loadConversation(result.conversation.ConversationID);
        }
    } catch (error) {
        console.error('Error creating conversation:', error);
        alert('Lỗi khi tạo cuộc hội thoại: ' + error.message);
    }
}

// Load conversation
async function loadConversation(conversationId) {
    try {
        const result = await api.get(`/api/conversation/${conversationId}`);
        
        if (result.success) {
            currentConversationId = conversationId;
            displayConversations();
            displayMessages(result.messages);
            
            // Show chat screen
            document.getElementById('welcome-screen').style.display = 'none';
            document.getElementById('chat-screen').style.display = 'flex';
        }
    } catch (error) {
        console.error('Error loading conversation:', error);
        alert('Lỗi khi tải cuộc hội thoại: ' + error.message);
    }
}

function displayMessages(messages) {
    const container = document.getElementById('messages-container');
    container.innerHTML = '';
    
    messages.forEach(msg => {
        addMessageToUI(msg.type, msg.message);
    });
    
    scrollToBottom(container);
}

function addMessageToUI(type, message) {
    const container = document.getElementById('messages-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    let content = '';
    
    if (type === 'user') {
        content = `
            <div class="message-bubble">
                <div class="message-text">${escapeHtml(message.Message)}</div>
                <div class="message-time">${formatTime(message.Createtime)}</div>
            </div>
        `;
    } else {
        content = `
            <div class="message-bubble">
                <div class="message-text">${makeWordsClickable(message.Message)}</div>
                <div class="message-actions">
                    <button class="btn-small" onclick="playTextToSpeech(${message.MessageID})">
                        🔊 Nghe
                    </button>
                </div>
                <div class="message-time">${formatTime(message.Createtime)}</div>
            </div>
        `;
    }
    
    messageDiv.innerHTML = content;
    container.appendChild(messageDiv);
}

// Send text message
async function sendTextMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    if (!currentConversationId) {
        alert('Vui lòng tạo hoặc chọn cuộc hội thoại');
        return;
    }
    
    input.value = '';
    await sendMessage(message);
}

async function sendMessage(message) {
    const container = document.getElementById('messages-container');
    
    // Add user message to UI
    addMessageToUI('user', {
        Message: message,
        Createtime: new Date().toISOString()
    });
    
    // Show loading
    const loading = showLoading(container);
    
    try {
        const result = await api.post('/api/conversation/message/send', {
            conversation_id: currentConversationId,
            message: message
        });
        
        removeLoading(loading);
        
        if (result.success) {
            // Add AI message to UI
            addMessageToUI('ai', result.ai_message);
            scrollToBottom(container);
        } else {
            alert('Lỗi: ' + result.error);
        }
        
    } catch (error) {
        removeLoading(loading);
        console.error('Error sending message:', error);
        alert('Lỗi khi gửi tin nhắn: ' + error.message);
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendTextMessage();
    }
}

// Vocabulary lookup
async function lookupWord(word) {
    try {
        const result = await api.post('/api/vocab/lookup', { word });
        
        if (result.success) {
            showVocabModal(result);
        } else {
            alert('Lỗi: ' + result.error);
        }
        
    } catch (error) {
        console.error('Error looking up word:', error);
        alert('Lỗi khi tra từ: ' + error.message);
    }
}

function showVocabModal(data) {
    document.getElementById('vocab-word').textContent = data.word;
    document.getElementById('vocab-pronunciation').textContent = data.pronunciation || 'N/A';
    document.getElementById('vocab-meaning').textContent = data.meaning || 'N/A';
    
    const audio = document.getElementById('vocab-audio');
    if (data.audio) {
        audio.src = data.audio;
        audio.style.display = 'block';
    } else {
        audio.style.display = 'none';
    }
    
    document.getElementById('vocab-modal').style.display = 'flex';
}

function closeVocabModal() {
    document.getElementById('vocab-modal').style.display = 'none';
}

// Logout
async function logout() {
    try {
        await api.post('/api/auth/logout', {});
    } catch (error) {
        console.error('Logout error:', error);
    }
    
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
}
