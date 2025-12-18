// Auth functions

function showLoginForm() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
    hideMessage();
}

function showRegisterForm() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
    hideMessage();
}

function showMessage(message, type = 'error') {
    const messageEl = document.getElementById('message');
    messageEl.textContent = message;
    messageEl.className = `message ${type}`;
    messageEl.style.display = 'block';
}

function hideMessage() {
    const messageEl = document.getElementById('message');
    messageEl.style.display = 'none';
}

function setLoading(formId, isLoading) {
    const form = document.getElementById(formId);
    const button = form.querySelector('button[type="submit"]');
    
    if (isLoading) {
        button.disabled = true;
        button.classList.add('loading');
        button.dataset.originalText = button.textContent;
        button.textContent = 'Đang xử lý...';
    } else {
        button.disabled = false;
        button.classList.remove('loading');
        if (button.dataset.originalText) {
            button.textContent = button.dataset.originalText;
        }
    }
}

async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const data = {
        tai_khoan: formData.get('tai_khoan').trim(),
        mat_khau: formData.get('mat_khau')
    };
    
    hideMessage();
    setLoading('loginForm', true);
    
    try {
        const response = await api.post('/api/auth/login', data);
        
        if (response.success) {
            // Save token and user info
            localStorage.setItem('token', response.token);
            localStorage.setItem('user', JSON.stringify(response.user));
            
            // Show success message
            showMessage('Đăng nhập thành công! Đang chuyển hướng...', 'success');
            
            // Redirect to chat page
            setTimeout(() => {
                window.location.href = '/chat';
            }, 1000);
        } else {
            showMessage(response.error || 'Đăng nhập thất bại', 'error');
        }
    } catch (error) {
        showMessage(error.message || 'Đăng nhập thất bại', 'error');
    } finally {
        setLoading('loginForm', false);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const data = {
        tai_khoan: formData.get('tai_khoan').trim(),
        mat_khau: formData.get('mat_khau'),
        ho_ten: formData.get('ho_ten').trim()
    };
    
    hideMessage();
    setLoading('registerForm', true);
    
    try {
        const response = await api.post('/api/auth/register', data);
        
        if (response.success) {
            // Show success message
            showMessage('Đăng ký thành công! Vui lòng đăng nhập.', 'success');
            
            // Switch to login form after 2 seconds
            setTimeout(() => {
                showLoginForm();
                // Pre-fill username
                document.getElementById('login-username').value = data.tai_khoan;
            }, 2000);
        } else {
            showMessage(response.error || 'Đăng ký thất bại', 'error');
        }
    } catch (error) {
        showMessage(error.message || 'Đăng ký thất bại', 'error');
    } finally {
        setLoading('registerForm', false);
    }
}

// Check if already logged in
window.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    if (token) {
        // Verify token
        api.get('/api/auth/verify')
            .then(response => {
                if (response.success) {
                    // Already logged in, redirect to chat
                    window.location.href = '/chat';
                }
            })
            .catch(() => {
                // Invalid token, clear storage
                localStorage.removeItem('token');
                localStorage.removeItem('user');
            });
    }
});
