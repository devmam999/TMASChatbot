# TMAS Chatbot - AI Chatbot with Manim Animations

## 🎯 Project Overview

This web application allows users to submit text and/or images to get AI-generated explanations with custom Manim animations.

### Features
 - ✅ Text-only input
 - ✅ Image-only input (with OCR/VLM processing)
 - ✅ Combined text and image input
 - ✅ Interactive quiz generation from AI explanations
 - 🔄 Real-time Manim animation generation
 - 🎬 Inline video playback in chat interface

## 🏗️ Architecture

### Backend (FastAPI + Python)
 - **Framework**: FastAPI
 - **AI Provider**: Anthropic Claude and Gemini for explanations
 - **Animation**: Manim library
 - **Quiz Generation**: Custom logic for interactive quizzes
 - **Hosting**: Render

### Frontend (React + TypeScript)
- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS
- **Hosting**: Vercel

## 📁 Project Structure

```
TMASInternship/
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI application
│   ├── models.py           # Pydantic models
│   ├── services/           # Business logic
│   │   ├── ai_service.py        # Anthropic Claude API integration
│   │   ├── manim_service.py     # Manim code execution
│   │   └── image_service.py     # Image processing
│   ├── utils/              # Utility functions
│   │   ├── config.py            # Environment configuration
│   │   └── file_utils.py        # File handling utilities
│   ├── requirements.txt    # Python dependencies
│   └── .env.example       # Environment variables template
|   └── Dockerfile         # Docker container containing the FastAPI backend service
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── ChatInterface.tsx    # Main chat interface
│   │   │   ├── ChatInput.tsx        # Input component
│   │   │   ├── MessageBubble.tsx    # Message display
│   │   │   ├── FileUpload.tsx       # File upload component
│   │   │   ├── InteractiveQuiz.tsx  # Interactive quiz component
│   │   │   └── VideoPlayer.tsx      # Video player component
│   │   ├── services/       # API services
│   │   │   └── api.ts              # API communication
│   │   ├── types/          # TypeScript types
│   │   │   └── index.ts            # Type definitions
│   │   ├── App.tsx         # Main app component
│   │   └── index.css       # Global styles
│   ├── package.json        # Node.js dependencies
│   └── .env.example       # Environment variables template
└── .gitignore             # Git ignore rules
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 16+ with npm
- Anthropic API key (get from https://console.anthropic.com/keys)
- Docker 20.10+

### Backend Setup
1. Navigate to `backend/`
2. Copy `.env.example` to `.env`
3. Add your `ANTHROPIC_API_KEY` to `.env`
4. Build the Docker Image: `docker build -t tmas-backend ./backend`
5. Run the Docker Container: `docker run -p 8000:8000 tmas-backend`

### Frontend Setup
1. Navigate to `frontend/`
2. Copy `.env.example` to `.env`
3. Update `VITE_BACKEND_URL` if needed (default: http://localhost:8000)
4. Install dependencies: `npm install`
5. Run: `npm run dev`

## 🧪 Testing the Application

### 1. Start Both Servers

**Terminal 1 - Backend:**
```bash
cd backend
docker build -t tmas-backend ./backend
docker run -p 8000:8000 tmas-backend
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 2. Test Different Input Types

#### Text-Only Test
1. Open http://localhost:5173 in your browser
2. Type: "Explain how a binary search tree works"
3. Click Send
4. Wait for AI response with explanation and animation

#### Image-Only Test
1. Click the image upload button (📷 icon)
2. Upload an image of a mathematical concept
3. Click Send
4. Wait for AI to analyze the image and generate explanation + animation

#### Combined Test
1. Type: "Explain this graph"
2. Upload an image of a graph/chart
3. Click Send
4. Wait for AI to process both text and image

### 3. Verify Features
- ✅ Text input with auto-resize
- ✅ Image upload with drag & drop
- ✅ Loading states and error handling
- ✅ Auto-scrolling chat
- ✅ Inline video playback
- ✅ Responsive design

## 🔐 Environment Variables

### Backend (.env)
```
# Anthropic Claude API Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-opus-4-1-20250805

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# File Upload Configuration
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=./uploads
MEDIA_DIR=./media

# Manim Configuration
MANIM_OUTPUT_DIR=./media
MANIM_QUALITY=medium_quality
MANIM_FRAME_RATE=30

# Security
SECRET_KEY=your-secret-key-here-change-in-production
```

### Frontend (.env)
```
# Backend API Configuration
VITE_BACKEND_URL=http://localhost:8000
```

## 🎬 How It Works

1. **User Input**: User submits text and/or image through the chat interface
2. **Frontend Processing**: 
   - Validates input (text length, image size/type)
   - Converts image to base64 if present
   - Sends FormData to backend
3. **Backend Processing**: 
   - Processes image with OCR/VLM if present
   - Combines text and image analysis
   - Sends prompt to Anthropic Claude or Gemini
   - Receives explanation + Manim Python code
4. **Animation Generation**: 
   - Executes Manim code server-side
   - Renders MP4 video file
   - Stores in media directory
5. **Response**: Returns explanation + video URL
6. **Frontend Display**: 
   - Shows explanation text
   - Autoplays animation inline
   - Handles loading states and errors
7. **Quiz Generation**:
   - User can click "Generate Quiz" on any AI message
   - The backend creates a quiz based on the explanation
   - The frontend displays an interactive quiz with scoring, hints, and explanations

## 🛠️ Technologies Used

- **AI**: Anthropic Claude
- **Animation**: Manim library (v0.18.0+)
- **Backend**: FastAPI, Python, Uvicorn, Docker
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Image Processing**: Pillow, OpenCV, pytesseract
- **Deployment**: Render (backend), Vercel (frontend)

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**: Check if port 8000 is available
2. **Frontend can't connect**: Verify `VITE_BACKEND_URL` in `.env`
3. **API errors**: Ensure `ANTHROPIC_API_KEY` is valid
4. **Manim errors**: Check Python dependencies and Manim installation
5. **CORS errors**: Verify `ALLOWED_ORIGINS` includes frontend URL

### Debug Mode
- Backend: Set `DEBUG=True` in `.env`
- Frontend: Check browser console for errors
- Check network tab for API request/response details 
