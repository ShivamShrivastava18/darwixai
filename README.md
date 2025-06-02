# Darwix AI - Audio Transcription & Blog Title Generator

A Django-based web application that provides AI-powered audio transcription with speaker diarization and intelligent blog title suggestions.

## 🚀 Features

### 🎙️ Audio Transcription with Speaker Diarization
- Upload audio files (MP3, WAV, M4A, FLAC, etc.) and get accurate transcriptions
- Advanced speaker diarization to identify different speakers in the conversation
- Clean, interactive UI for reviewing transcription results
- Supports multiple audio formats without requiring FFmpeg
- Uses Google's Gemini 1.5 Pro model for transcription

### 📝 AI Blog Title Generator
- Generate SEO-friendly blog post titles based on content
- Powered by Groq API with Llama 4 Scout model
- Provides multiple title suggestions with one click
- Easy copy-to-clipboard functionality

## 🛠️ Technology Stack

### Backend
- **Django 4.2.7**: Core web framework
- **Django REST Framework 3.14.0**: API development
- **Whisper**: Local audio transcription model
- **Pyannote Audio 3.1.1**: Speaker diarization
- **Groq API**: LLM integration for title generation
- **Google Gemini 1.5 Pro**: Advanced transcription capabilities

### Frontend
- **HTML/CSS/JavaScript**: Modern, responsive UI
- **Fetch API**: Asynchronous API requests
- **CSS Grid/Flexbox**: Responsive layout

## 📋 Requirements
- Python 3.8+
- Django 4.2.7
- Django REST Framework 3.14.0
- PyTorch 2.1.0
- TorchAudio 2.1.0
- Transformers 4.35.0
- Groq 0.4.1
- Python-dotenv 1.0.0
- Librosa 0.10.1
- SoundFile 0.12.1
- Pydub 0.25.1

## 🔧 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd darwixai_task
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your-django-secret-key
   GROQ_API_KEY=your-groq-api-key
   GOOGLE_API_KEY=your-google-api-key
   HUGGINGFACE_TOKEN=your-huggingface-token
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   Open your browser and navigate to `http://localhost:8000`

## 🗄️ Project Structure

```
darwix_ai/
├── ai_features/                # Main application
│   ├── services/               # AI service modules
│   │   ├── transcription_service.py  # Audio transcription logic
│   │   └── title_suggestion_service.py  # Title generation logic
│   ├── templates/              # HTML templates
│   │   └── ai_features/
│   │       └── home.html       # Main application interface
│   ├── models.py               # Database models
│   ├── views.py                # API and view handlers
│   ├── urls.py                 # URL routing
│   └── serializers.py          # REST API serializers
├── darwix_ai/                  # Project settings
│   ├── settings.py             # Django settings
│   └── urls.py                 # Main URL routing
├── media/                      # User-uploaded files
├── temp_audio/                 # Temporary audio processing
├── temp_uploads/               # Temporary file uploads
├── manage.py                   # Django management script
└── requirements.txt            # Python dependencies
```

## 🔌 API Endpoints

### Audio Transcription
- **POST** `/api/transcribe/`: Upload and transcribe audio files
- **GET** `/api/transcriptions/`: Retrieve transcription history

### Blog Title Generation
- **POST** `/api/suggest-titles/`: Generate title suggestions from content

### Blog Posts
- **GET** `/api/blog-posts/`: List all blog posts
- **POST** `/api/blog-posts/`: Create a new blog post

### System
- **GET** `/api/health/`: System health check

## 📝 Usage Examples

### Audio Transcription
1. Navigate to the home page
2. Drag and drop an audio file or click to select one
3. Wait for the transcription process to complete
4. Review the transcription with speaker identification

### Blog Title Generation
1. Navigate to the home page
2. Enter your blog content in the text area
3. Click "Generate Title Suggestions"
4. Select and copy your preferred title

## 🔒 Security Notes
- API keys are stored in environment variables for security
- File uploads are validated for type and size
- Temporary files are automatically cleaned up

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

## 📄 License
[Include your license information here]
