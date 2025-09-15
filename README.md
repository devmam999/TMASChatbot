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
3. Update envs: `VITE_BACKEND_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` (see Supabase setup below)
4. Install dependencies: `npm install`
5. Run: `npm run dev`

## 🔑 Supabase Setup (Auth, Achievements, Chat)

This app uses Supabase for authentication, achievements (badges + quiz counters), and chat history.

### 1) Create a Supabase project
- Go to https://supabase.com → Sign in → New Project
- Choose an organization, name the project, select a region, and set a strong database password
- Wait for provisioning to complete

### 2) Get API URL and Anon key (frontend env)
- In your Supabase project: Settings → API
- Copy these values:
   - Project URL → use as `VITE_SUPABASE_URL`
   - `anon` public key → use as `VITE_SUPABASE_ANON_KEY`
- Update `frontend/.env` with the three variables:

```
VITE_BACKEND_URL=http://localhost:8000
VITE_SUPABASE_URL=https://YOUR-PROJECT-REF.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Notes:
- Only use the Anon key in the browser. Never expose the Service Role key.
- Default local frontend URL is http://localhost:5173 or 5174 depending on availability.

### 3) Enable Email auth (optional providers are fine too)
- Authentication → Providers → Email → Enable email/password
- Save

### 4) Create tables, RLS, and RPCs (run SQL in dashboard)
- Database → SQL Editor → New query
- Run the following in order:
   1. Enable gen_random_uuid (usually enabled by default):
       ```sql
       create extension if not exists pgcrypto;
       ```
   2. Achievements table + RPC: open `docs/supabase.sql` and paste contents, then Run
   3. Chat + Badges: open `docs/supabase_chat_and_badges.sql` and paste contents, then Run

This creates:
- `user_achievements` with RLS and `increment_quizzes_completed(p_user_id, ...)`
- `chat_sessions`, `chat_messages` with RLS
- `user_badges`, `badge_catalog` with RLS and `award_badge(p_user_id, p_badge_key)`

### 5) Enable Realtime for live UI updates
- Database → Replication → Configure → Add tables to publication:
   - Required: `public.user_achievements`, `public.user_badges`
   - Optional (for multi-tab live chat): `public.chat_messages`
- Save

### 6) Add your frontend envs and run
- Ensure `frontend/.env` has `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`
- Restart the dev server after editing envs:

```powershell
cd "frontend"
$env:NODE_OPTIONS=""; npm run dev
```

### 7) Verify
- Open the app, Sign up / Sign in (top-level gate)
- Create a new chat, send a message → AI reply persists when switching chats
- Click “Generate Quiz” on an AI message → complete it
- Achievements chip should increment; click “Achievements” to see earned badges

If the achievements chip doesn’t change until you re-login, double-check step 5 (Realtime enabled) and that the correct project URL/key are in `frontend/.env`.

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

# Supabase Configuration
VITE_SUPABASE_URL=https://YOUR-PROJECT-REF.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key_here
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

6. **Achievements don’t update live**:
 - Ensure Realtime is enabled for `user_achievements` and `user_badges`
 - Confirm `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` are correct and the user is authenticated

7. **No chat history or missing AI replies in history**:
 - Confirm both `chat_sessions` and `chat_messages` tables exist with the RLS policies from `docs/supabase_chat_and_badges.sql`
 - Create a new chat session in-app and send a message; the AI reply is saved after streaming completes

### Debug Mode
- Backend: Set `DEBUG=True` in `.env`
- Frontend: Check browser console for errors
- Check network tab for API request/response details 
