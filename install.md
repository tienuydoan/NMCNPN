# Hướng dẫn cài đặt English Chat AI

## Yêu cầu hệ thống

- Python 3.9 trở lên
- pip (Python package installer)
- Trình duyệt web hiện đại (Chrome, Firefox, Edge, Safari)

## Bước 1: Cài đặt Python và pip

### Windows:
Kiểm tra cài đặt:
```bash
python --version
pip --version
```

## Bước 2: Tạo virtual environment (khuyến nghị)

```bash
# Windows
python -m venv venv
venv\Scripts\activate
```

## Bước 3: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

## Bước 4: Cấu hình API Keys

### 4.1. Tạo file .env từ template:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### 4.2. Chỉnh sửa file .env:

Mở file `.env` bằng text editor và cập nhật các thông tin:

#### Cập nhật các API Key (Các key và model em đã gửi trong excel):
```
LITELLM_API_KEY=
LITELLM_MODEL=
ELEVENLABS_API_KEY=
```


## Bước 6: Chạy ứng dụng

```bash
python -m backend.main
```


## Bước 7: Truy cập ứng dụng
Mở trình duyệt và truy cập:
- **Trang chủ/Login:** http://127.0.0.1:5000/
- **Trang chat:** http://127.0.0.1:5000/chat

## Cấu trúc thư mục

```
NMCNPM/
├── backend/
│   ├── main.py              # Entry point
│   ├── routes/              # API routes
│   ├── services/            # Business logic
│   ├── models/              # Data models
│   └── utils/               # Utilities
├── database/
│   └── db_manager.py        # Database operations
├── data/                    # CSV data files
│   ├── nguoi_dung.csv
│   ├── hoi_thoai.csv
│   ├── user_message.csv
│   ├── ai_message.csv
│   └── ...
├── frontend/
│   ├── index.html           # Login page
│   ├── chat.html            # Chat page
│   ├── css/                 # Stylesheets
│   └── js/                  # JavaScript files
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
└── install.md              # This file
```


## Tính năng chính
1. **Đăng ký/Đăng nhập:** Tạo tài khoản và đăng nhập
2. **Chat text:** Gửi tin nhắn văn bản và nhận phản hồi từ AI
3. **Speech-to-Text:** Ghi âm giọng nói và chuyển thành văn bản
4. **Text-to-Speech:** Nghe phát âm câu trả lời của AI
5. **Tra từ vựng:** Click vào từ trong câu trả lời để tra nghĩa
6. **Lịch sử hội thoại:** Xem lại các cuộc hội thoại trước đó
7. **Voice Mode:** Chế độ tự động phát âm câu trả lời
