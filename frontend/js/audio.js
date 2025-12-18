// Audio recording and playback

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let currentAudioBlob = null;

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            currentAudioBlob = audioBlob;
            
            // Close recording modal
            document.getElementById('recording-modal').style.display = 'none';
            
            // Process audio
            await processAudio(audioBlob);
            
            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        document.getElementById('mic-btn').classList.add('recording');
        document.getElementById('recording-modal').style.display = 'flex';
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Không thể truy cập microphone. Vui lòng cho phép quyền truy cập.');
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        document.getElementById('mic-btn').classList.remove('recording');
    }
}

function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

async function processAudio(audioBlob) {
    try {
        // Check if voice mode is active (from chat.js)
        const voiceModeEnabled = window.isVoiceMode || false;
        
        // Show loading
        const container = document.getElementById('messages-container');
        const loading = showLoading(container);
        
        // Create form data
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        formData.append('conversation_id', currentConversationId);
        
        // Send to server
        const result = await api.upload('/api/conversation/message/send', formData);
        
        removeLoading(loading);
        
        if (result.success) {
            if (voiceModeEnabled) {
                // Voice mode: add messages to UI and play TTS (handled by chat.js)
                addMessageToUI('user', {
                    Message: result.transcript,
                    Createtime: new Date().toISOString()
                });
                addMessageToUI('ai', result.ai_message);
                scrollToBottom(container);
                
                // Play TTS and continue loop
                await playTextToSpeechWithCallback(result.ai_message.MessageID, () => {
                    // After TTS finishes, start recording again if voice mode still on
                    if (window.isVoiceMode) {
                        setTimeout(() => startRecording(), 500); // Small delay for better UX
                    }
                });
            } else {
                // Normal mode: Auto fill transcript into input box
                const messageInput = document.getElementById('message-input');
                messageInput.value = result.transcript;
                messageInput.focus();
            }
        } else {
            alert('Lỗi: ' + result.error);
        }
        
    } catch (error) {
        console.error('Error processing audio:', error);
        alert('Lỗi khi xử lý âm thanh: ' + error.message);
    }
}

// Transcript modal functions removed - now auto-fill to input box

async function playTextToSpeech(messageId) {
    try {
        const result = await api.get(`/api/conversation/message/tts/${messageId}`);
        
        if (result.success) {
            // Decode base64 audio
            const audioData = atob(result.audio);
            const arrayBuffer = new ArrayBuffer(audioData.length);
            const view = new Uint8Array(arrayBuffer);
            
            for (let i = 0; i < audioData.length; i++) {
                view[i] = audioData.charCodeAt(i);
            }
            
            const blob = new Blob([arrayBuffer], { type: 'audio/mp3' });
            const audioUrl = URL.createObjectURL(blob);
            
            const audio = new Audio(audioUrl);
            audio.play();
            
        } else {
            alert('Lỗi: ' + result.error);
        }
        
    } catch (error) {
        console.error('Error playing TTS:', error);
        alert('Lỗi khi phát âm thanh: ' + error.message);
    }
}

async function playTextToSpeechWithCallback(messageId, callback) {
    try {
        const result = await api.get(`/api/conversation/message/tts/${messageId}`);
        
        if (result.success) {
            // Decode base64 audio
            const audioData = atob(result.audio);
            const arrayBuffer = new ArrayBuffer(audioData.length);
            const view = new Uint8Array(arrayBuffer);
            
            for (let i = 0; i < audioData.length; i++) {
                view[i] = audioData.charCodeAt(i);
            }
            
            const blob = new Blob([arrayBuffer], { type: 'audio/mp3' });
            const audioUrl = URL.createObjectURL(blob);
            
            const audio = new Audio(audioUrl);
            
            // Execute callback when audio finishes playing
            audio.onended = () => {
                if (callback) callback();
            };
            
            audio.play();
            
        } else {
            alert('Lỗi: ' + result.error);
            if (callback) callback(); // Still call callback even on error
        }
        
    } catch (error) {
        console.error('Error playing TTS:', error);
        alert('Lỗi khi phát âm thanh: ' + error.message);
        if (callback) callback(); // Still call callback even on error
    }
}

function playVocabAudio() {
    const audio = document.getElementById('vocab-audio');
    if (audio.src) {
        audio.play();
    }
}
