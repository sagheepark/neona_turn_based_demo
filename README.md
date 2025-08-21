# Neona Turn-Based Demo

Voice Character Chat application with AI-powered character conversations and voice synthesis.

## Features

- 🎭 **Character Management**: Create and manage custom characters with unique personalities
- 🎙️ **Voice Synthesis**: Text-to-speech with multiple voice options
- 🤖 **AI Conversations**: GPT-4 powered character interactions
- 🎵 **Voice Recommendations**: AI-based voice matching for characters
- 🎤 **Speech Recognition**: Voice input support (STT)

## Tech Stack

### Backend
- FastAPI
- Azure OpenAI (GPT-4)
- Typecast TTS API
- Python 3.9+

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- shadcn/ui

## Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Azure OpenAI API access
- Typecast API key

### Backend Setup

```bash
cd backend_clean
pip install -r requirements.txt

# Create .env file with:
# AZURE_OPENAI_ENDPOINT=your_endpoint
# AZURE_OPENAI_API_KEY=your_key
# TYPECAST_API_KEY=your_typecast_key

python main.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
├── backend_clean/          # FastAPI backend
│   ├── main.py            # Main API server
│   ├── services/          # Service modules
│   │   ├── tts_service.py
│   │   ├── stt_service.py
│   │   └── voice_recommend_service.py
│   └── requirements.txt
│
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/          # Next.js app router
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities
│   └── package.json
│
└── docs/                  # Documentation
    ├── STRUCTURE.md
    └── FEATURE_ROADMAP.md
```

## Current Status

✅ Core features implemented:
- Character creation and management
- Real-time voice chat
- Voice selection and preview
- AI voice recommendations (Korean names display)

🚧 In Progress:
- Voice ID mapping between recommendation and TTS APIs
- Extended voice library support

## Contributing

This is a demo project for Neosapience's voice technology capabilities.

## License

Proprietary - Neosapience# ssfm_qa
