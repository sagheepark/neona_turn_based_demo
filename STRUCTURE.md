# Voice Character Chat - Project Structure

## 📋 Project Overview
Real-time voice character chat application with AI-powered responses, TTS (Text-to-Speech), and STT (Speech-to-Text) capabilities.

## 🏗️ Architecture

### Backend (`/backend_clean/`)
```
backend_clean/
├── main.py                 # FastAPI server with chat endpoints
├── .env                    # Environment variables
├── services/
│   ├── tts_service.py      # Typecast TTS integration
│   └── __init__.py
├── test_tts.py            # TTS testing script
└── requirements.txt       # Python dependencies
```

**Key Features:**
- FastAPI REST API server
- Azure OpenAI GPT-4o integration for Korean responses
- Typecast TTS API integration (alpha: api.icepeak.ai)
- CORS enabled for frontend communication

**Endpoints:**
- `POST /api/chat` - Main chat with TTS audio
- `GET /api/voices` - List available TTS voices
- `GET /api/voices/korean` - Korean voices only
- `POST /api/tts` - Direct TTS generation
- `POST /api/stt` - Speech-to-Text conversion
- `GET /api/stt/languages` - Supported STT languages

### Frontend (`/frontend/`)
```
frontend/src/
├── app/
│   ├── page.tsx               # Redirect to characters
│   ├── layout.tsx             # Root layout
│   ├── globals.css            # Global styles + chat animations
│   ├── characters/
│   │   ├── page.tsx           # Character list
│   │   ├── create/page.tsx    # Character creation
│   │   └── [id]/edit/page.tsx # Character editing
│   └── chat/
│       └── [characterId]/page.tsx # Main chat interface
├── components/
│   ├── characters/
│   │   └── CharacterCard.tsx  # Character display card
│   ├── chat/
│   │   ├── TypewriterText.tsx # Animated text reveal
│   │   └── AudioPlayer.tsx    # Audio playback with waveform
│   └── ui/                    # Shadcn UI components
├── lib/
│   ├── api-client.ts          # Backend API calls
│   ├── storage.ts             # LocalStorage management
│   └── utils.ts               # Utility functions
├── types/
│   ├── character.ts           # Character data types
│   └── chat.ts               # Chat message types
└── data/
    └── demo-characters.ts     # 3 characters: 윤아리, 태풍, 박현 with unique voices
└── public/
    └── images/                # Character avatar images
        ├── 윤아리.png
        ├── 태풍.png
        └── 박현.png
```

**Key Features:**
- Next.js 14 with App Router
- Mobile-first responsive design
- Real-time animated chat bubbles with typewriter sync
- 3 unique characters with individual voice personalities
- Character management with LocalStorage
- Audio playback with visual waveform feedback
- Character avatars with top-aligned images
- Voice recording with STT integration
- Clean, minimal UI with emotion/debug displays hidden
- Comprehensive error handling for microphone access

## 🔧 Current Technology Stack

### Backend Technologies
- **FastAPI** - Python web framework
- **Azure OpenAI** - GPT-4o for Korean language responses
- **Typecast TTS** - Character-specific voice synthesis (Emma/Duke/Tyson voices)
- **Python-dotenv** - Environment management
- **CORS Middleware** - Cross-origin requests

### Frontend Technologies
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling framework
- **Shadcn/ui** - Component library
- **Framer Motion** - Animations
- **Lucide React** - Icons

## 🌐 API Integration Status

### Azure OpenAI
- **Status**: ✅ Active
- **Model**: GPT-4o
- **Endpoint**: `https://neo-research.openai.azure.com/`
- **Features**: Korean language responses, character personality

### Typecast TTS (Alpha)
- **Status**: ✅ Active
- **Endpoint**: `https://api.icepeak.ai/v1` (development)
- **Character Voices**:
  - 윤아리 (ASMR 상담사): Emma - `tc_61c97b56f1b7877a74df625b` (whisper 감정 전용)
  - 태풍 (논쟁꾼): Duke - `tc_6073b2f6817dccf658bb159f` (강한 남성)
  - 박현 (분노 대행): Tyson - `tc_624152dced4a43e78f703148` (격한 남성)
- **Features**: Character-specific voices, emotion mapping, whisper support, Base64 audio

### Character Storage
- **Status**: ✅ Active
- **Method**: LocalStorage (demo phase)
- **Features**: CRUD operations, demo characters pre-loaded

## 📱 Current UI/UX Features

### Chat Interface
- **Mobile-optimized**: Maximum width, safe area handling
- **Dynamic Bubbles**: Character/user bubbles resize based on activity
- **Animations**: Smooth transitions, typewriter text effect
- **Audio Integration**: Auto-play with waveform visualization

### Character Management
- **Character Cards**: Grid layout with images and descriptions
- **Creation/Editing**: Form-based character customization
- **Personality System**: XML-style prompt structure

## 🔄 Data Flow

### Chat Flow
**Text Input:**
1. User types message → Frontend captures input
2. Frontend sends to `/api/chat` with character context
3. Backend processes with Azure OpenAI
4. Backend generates TTS audio via Typecast
5. Response with text + Base64 audio returned
6. Frontend displays text with typewriter effect
7. Audio auto-plays with visual feedback

**Voice Input:**
1. User clicks microphone → Permission requested
2. Voice recording with MediaRecorder
3. Audio converted to Base64 → Sent to `/api/stt`
4. Backend transcribes speech to text
5. Recognized text auto-submitted as chat message
6. Follows same chat flow as text input above

### Character Flow
1. Characters stored in LocalStorage
2. Demo characters auto-loaded on first visit
3. CRUD operations via storage service
4. Character prompts used for AI personality

## 🚀 Deployment Status

### Development Environment
- **Backend**: `http://localhost:8000`
- **Frontend**: `http://localhost:3001`
- **Status**: Fully functional for alpha testing

### Production Readiness
- Backend: Ready for containerization
- Frontend: Ready for Vercel/Netlify deployment
- Database: Needs migration from LocalStorage to PostgreSQL
- Audio: Ready to switch to production Typecast endpoint

## 📦 Key Dependencies

### Backend
```python
fastapi>=0.104.1
openai>=1.99.6
requests>=2.31.0
python-dotenv>=1.0.0
uvicorn>=0.24.0
```

### Frontend
```json
{
  "next": "15.4.6",
  "react": "19.0.0",
  "typescript": "5.7.2",
  "tailwindcss": "3.4.1",
  "framer-motion": "^11.15.0"
}
```

## 🎯 Current Capabilities

### 🎤 Voice Features
- **Voice Input**: Full STT integration with microphone recording
- **Voice Output**: Character-specific TTS with emotion mapping
- **Audio Controls**: Start/stop/cancel recording with visual feedback
- **Permission Handling**: Graceful microphone access with error messages
- **Audio Processing**: Optimized MediaRecorder settings for quality
- **Auto-submission**: Voice messages automatically converted and sent
- **Performance**: Optimized to prevent infinite request loops

### ⚡ Performance Optimizations
- **Fixed Infinite Loop Issue**: Resolved useEffect dependency causing hundreds of duplicate TTS requests
- **Welcome Message**: Single generation per character visit (was generating 50+ duplicates)
- **Backend Response**: Improved from 25-43s to 0.009s response time
- **TTS Request Throttling**: Eliminated concurrent request conflicts
- **Memory Usage**: Reduced client-side memory consumption from duplicate audio generation

### 🎭 Character System

### ✅ Implemented
- **Real-time Korean TTS** with character-specific voices
- **3 unique characters** with individual personalities and voices:
  - 윤아리: ASMR 심리상담사 (Emma voice, whisper emotion)
  - 태풍: 논쟁 전문 캐릭터 (Duke voice)
  - 박현: 분노 대행 캐릭터 (Tyson voice)
- **Mobile-optimized chat interface** with animations
- **Character creation and management**
- **Azure OpenAI integration** for Korean responses
- **Audio-text synchronization** (typewriter starts with audio)
- **Audio playback** with visual waveform feedback
- **Character avatars** with proper image positioning
- **Error handling and fallbacks** with mock audio
- **STT (Speech-to-Text) integration** with microphone recording:
  - Voice permission handling with user-friendly error messages
  - Real-time recording with start/stop/cancel controls
  - Auto-conversion to text and chat submission
  - MediaRecorder with audio optimization (echo/noise cancellation)
- **UI refinements completed**:
  - Removed "You:" prefix from messages
  - Hidden emotion display and audio state debug UI
  - Clean, minimal interface focused on conversation
- **Performance fixes**:
  - **Critical**: Fixed infinite useEffect loop causing 100+ duplicate welcome messages
  - **Optimized**: Welcome message generation from multiple concurrent calls to single call
  - **Resolved**: ERR_CONNECTION_REFUSED errors caused by backend overload
  - **Improved**: Backend response time from 25-43 seconds to <0.01 seconds

### 🔄 In Progress  
- **STT Recognition**: Investigating voice recognition accuracy issues
- **Audio Quality**: Fine-tuning MediaRecorder settings for better speech capture
- **Error Handling**: Improving STT failure feedback and retry mechanisms

### 📋 Planned
- Database migration (PostgreSQL)
- User authentication
- Production TTS endpoint (full api.typecast.ai access)
- Multi-language support
- Voice emotion customization per character

## 🎭 Character System

### Character Definitions
Characters are loaded from `/Users/bagsanghui/neona_turn_based_demo_with_agent/characters.md` with detailed personality prompts and voice specifications.

### Voice Mapping System
Each character has a unique voice_id mapped to icepeak.ai endpoint:
- Voice consistency between welcome messages and chat responses
- Character-specific emotion overrides (윤아리 → whisper)
- Fallback to mock audio when API calls fail

### Image System
Character avatars are stored in `/public/images/` with:
- Top-aligned positioning (`object-top`) for proper face visibility
- Aspect ratio preservation (`object-cover`)
- Fallback to initials when images fail to load