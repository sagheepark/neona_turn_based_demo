# Voice Character Chat Demo - Project Structure Documentation

## 🎯 Project Overview

A sophisticated voice-based character chat application featuring AI-powered conversations with multiple personas, selective memory systems, and game-like interaction mechanics. Built with FastAPI (Python) backend and Next.js (TypeScript) frontend.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
├─────────────────────────────────────────────────────────────┤
│                   API Layer (REST/WebSocket)                 │
├─────────────────────────────────────────────────────────────┤
│                    Backend Services (FastAPI)                │
├──────────────┬────────────────┬─────────────────────────────┤
│   MongoDB    │  File System   │    Azure OpenAI/TTS/STT     │
└──────────────┴────────────────┴─────────────────────────────┘
```

## 📁 Directory Structure

### Backend (`backend_clean/`)

```
backend_clean/
├── main.py                          # FastAPI application entry point
├── services/                        # Core business logic services
│   ├── chat_orchestrator.py        # Main chat flow coordinator
│   ├── selective_memory_service.py # Dynamic memory & status management
│   ├── conversation_service.py     # Session & message history
│   ├── knowledge_service.py        # RAG knowledge retrieval
│   ├── persona_service.py          # User persona management
│   ├── character_service.py        # Character CRUD operations
│   ├── database_service.py         # MongoDB connection handler
│   ├── config_parser_service.py    # Character config text parser
│   ├── tts_service.py              # Text-to-Speech (Azure/IcePeak)
│   ├── stt_service.py              # Speech-to-Text (Azure)
│   └── voice_cache_service.py      # Audio caching for performance
├── conversations/                   # JSON conversation storage
│   └── {user_id}/
│       └── {character_id}/
│           └── sess_{timestamp}_{id}.json
├── characters/                      # Character definitions (migrated to MongoDB)
├── configurations/                  # Character simulation configs
│   └── {character_id}_config.txt
├── knowledge/                       # Character knowledge bases
│   └── characters/
│       └── {character_id}/
│           └── knowledge.json
└── tests/                          # Comprehensive test suite
```

### Frontend (`frontend/src/`)

```
frontend/src/
├── app/                            # Next.js 14 App Router pages
│   ├── page.tsx                   # Home/landing page
│   ├── chat/
│   │   └── [characterId]/
│   │       └── page.tsx           # Main chat interface
│   └── characters/
│       ├── page.tsx               # Character selection grid
│       ├── create/page.tsx        # Character creation form
│       ├── [id]/
│       │   ├── edit/page.tsx      # Character edit form
│       │   └── simulation/page.tsx # Selective memory config
├── components/
│   ├── chat/
│   │   ├── AudioPlayer.tsx       # Voice playback controls
│   │   ├── TypewriterText.tsx    # Animated text display
│   │   ├── SessionContinuationModal.tsx # Session selection
│   │   ├── PersonaSelector.tsx   # User persona switcher
│   │   ├── MemoryStatusDisplay.tsx # Real-time status bars
│   │   └── KnowledgeIndicator.tsx # Knowledge usage indicator
│   ├── characters/
│   │   ├── CharacterCard.tsx     # Character display card
│   │   ├── VoiceSelector.tsx     # TTS voice selection
│   │   ├── SelectiveConfigEditor.tsx # Memory config editor
│   │   └── VoiceRecommendation.tsx # AI voice suggestions
│   └── knowledge/
│       ├── KnowledgeManagementSection.tsx # Knowledge CRUD UI
│       ├── AddKnowledgeButton.tsx # Quick add knowledge
│       └── KnowledgeItemRow.tsx  # Knowledge item display
├── lib/
│   ├── api-client.ts             # Backend API communication
│   └── storage.ts                # Local storage utilities
├── types/
│   ├── character.ts              # Character type definitions
│   ├── chat.ts                   # Chat message types
│   └── knowledge.ts              # Knowledge system types
└── data/
    └── demo-characters.ts        # Pre-configured characters
```

## 🔑 Core Systems & Features

### 1. Character System
- **Character Management**: Full CRUD operations with MongoDB persistence
- **Prompt Engineering**: Sophisticated XML-structured prompts for character personalities
- **Voice Integration**: Per-character TTS voice selection with IcePeak.ai integration
- **Multiple Personas**: 5 distinct characters (Game Master, 윤아리, 태풍, 박현, 김파이썬)

### 2. Selective Memory System (Simulation-like Chat)
- **Status Values**: Dynamic character-specific metrics (affection, trust, stress, etc.)
- **Milestones**: Achievement tracking with condition-based triggers
- **Event Logging**: Timestamped event tracking with status impacts
- **Persistent Facts**: Long-term memory of important user information
- **Configuration Parser**: Text-based config system for easy character customization

### 3. Conversation Management
- **Session Handling**: Create, continue, and manage conversation sessions
- **Message History**: Full conversation persistence with compression
- **Context Window**: Smart history compression for long conversations
- **Session Continuation Modal**: UI for resuming previous conversations

### 4. Knowledge Base (RAG System)
- **Knowledge Storage**: Per-character knowledge repositories
- **Semantic Search**: Weighted keyword matching for relevance
- **Knowledge Management UI**: Add/edit/delete knowledge items
- **Usage Tracking**: Monitor which knowledge is used in conversations

### 5. Voice Integration
- **Text-to-Speech**: Azure TTS & IcePeak.ai integration
- **Speech-to-Text**: Azure STT for voice input
- **Voice Caching**: Performance optimization through audio caching
- **Voice Recommendation**: AI-powered voice suggestions for characters

### 6. User Persona System
- **Multiple Personas**: Users can create different personas
- **Persona Context**: Inject persona attributes into conversations
- **Active Persona Switching**: Change personas mid-conversation

## 🔄 Data Flow

### Chat Message Flow
1. **User Input** → Voice/Text input from frontend
2. **STT Processing** → Convert voice to text (if voice input)
3. **Session Management** → Load/create session, retrieve history
4. **Knowledge Retrieval** → Search relevant knowledge (RAG)
5. **Memory Loading** → Fetch selective memory & status values
6. **Prompt Construction** → Build context with character, persona, knowledge
7. **LLM Processing** → Azure OpenAI generates response
8. **Memory Update** → Update status values, log events, check milestones
9. **TTS Generation** → Convert response to voice
10. **Response Delivery** → Send text + audio to frontend

### Memory Update Flow
1. **Parse Response** → Analyze AI response for triggers
2. **Update Status** → Modify status values based on config rules
3. **Check Milestones** → Evaluate milestone conditions
4. **Log Events** → Record significant interactions
5. **Compress History** → Periodic history compression for context
6. **Persist Changes** → Save to MongoDB

## 🗄️ Database Schema

### MongoDB Collections

#### `characters`
```javascript
{
  "_id": ObjectId,
  "character_id": "unique_string",
  "name": "Character Name",
  "prompt": "XML structured prompt",
  "greetings": ["greeting1", "greeting2"],
  "voice_id": "tts_voice_id",
  "selective_config": "text config",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### `selective_memories`
```javascript
{
  "_id": ObjectId,
  "user_id": "user_identifier",
  "character_id": "character_identifier",
  "core_memory": {
    "status_values": { /* dynamic key-value pairs */ },
    "milestones": [ /* achievement records */ ],
    "event_log": [ /* timestamped events */ ],
    "persistent_facts": [ /* user facts */ ],
    "compressed_history": "summarized conversation"
  },
  "last_updated": ISODate,
  "version": 1
}
```

#### `knowledge_base`
```javascript
{
  "_id": ObjectId,
  "character_id": "character_identifier",
  "items": [
    {
      "id": "k_001",
      "title": "Knowledge Title",
      "content": "Detailed content",
      "keywords": ["keyword1", "keyword2"],
      "category": "category_name",
      "usage_count": 0
    }
  ]
}
```

## 🚀 API Endpoints

### Core Chat Endpoints
- `POST /chat/session/start` - Initialize or resume session
- `POST /chat/session/continue/{session_id}` - Continue specific session
- `POST /chat/message` - Send message with session context
- `POST /chat/tts` - Generate TTS audio
- `POST /chat/stt` - Convert speech to text

### Character Management
- `GET /characters` - List all characters
- `POST /characters` - Create new character
- `PUT /characters/{id}` - Update character
- `DELETE /characters/{id}` - Delete character
- `GET /characters/{id}/selective-config` - Get simulation config
- `PUT /characters/{id}/selective-config` - Update simulation config

### Knowledge Management
- `GET /knowledge/{character_id}` - Get character knowledge
- `POST /knowledge/{character_id}` - Add knowledge item
- `PUT /knowledge/{character_id}/{item_id}` - Update knowledge
- `DELETE /knowledge/{character_id}/{item_id}` - Delete knowledge

### Memory Management
- `GET /memory/{user_id}/{character_id}` - Get core memory
- `POST /memory/initialize` - Initialize memory for user-character
- `PUT /memory/update` - Update status values
- `POST /memory/compress` - Compress conversation history

## 🎮 Game System (Chronicles of Aetheria)

### Fantasy RPG Implementation
- **Dynamic Storytelling**: Branching narratives based on choices
- **Status Tracking**: Hero level, reputation, corruption, wisdom, bonds
- **Choice Consequences**: Actions affect multiple status values
- **Milestone System**: Story progression through achievements
- **World State**: Persistent world changes based on player actions

## 🔧 Configuration

### Environment Variables
```env
# Azure Services
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_STT_KEY=your-stt-key
AZURE_STT_REGION=your-region
AZURE_TTS_KEY=your-tts-key

# IcePeak.ai TTS
ICEPEAK_API_KEY=your-icepeak-key

# MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=voice_character_chat
```

## 🧪 Testing Strategy

### Test Categories
1. **Unit Tests**: Service-level function testing
2. **Integration Tests**: API endpoint testing
3. **Session Tests**: Conversation flow validation
4. **Memory Tests**: Selective memory system validation
5. **Knowledge Tests**: RAG system accuracy
6. **Voice Tests**: TTS/STT connectivity

### Key Test Files
- `test_integration.py` - Full system integration
- `test_selective_memory_service.py` - Memory system
- `test_conversation_service.py` - Session management
- `test_knowledge_service.py` - RAG functionality
- `test_chat_api_character_prompts.py` - Prompt validation

## 🚦 Development Workflow

### Adding a New Character
1. Create character definition in `demo-characters.ts`
2. Design XML-structured prompt with persona details
3. Create selective memory config in `configurations/`
4. Add character-specific knowledge in `knowledge/characters/`
5. Select appropriate TTS voice
6. Test conversation flow

### Implementing New Features
1. Follow TDD approach (Red → Green → Refactor)
2. Update relevant services in `backend_clean/services/`
3. Add API endpoints in `main.py`
4. Create frontend components in `frontend/src/components/`
5. Update types in `frontend/src/types/`
6. Write comprehensive tests

## 🔍 Common Issues & Solutions

### Session Continuation Issues
- **Problem**: Sessions not loading properly
- **Solution**: Check `conversation_service.py` session loading logic
- **Related Files**: `SessionContinuationModal.tsx`, `chat_orchestrator.py`

### Memory Update Delays
- **Problem**: Status values not updating in real-time
- **Solution**: Verify MongoDB connection and update operations
- **Related Files**: `selective_memory_service.py`, `MemoryStatusDisplay.tsx`

### Voice Playback Problems
- **Problem**: TTS audio not playing
- **Solution**: Check API keys and voice_id validity
- **Related Files**: `tts_service.py`, `AudioPlayer.tsx`

### Knowledge Retrieval Accuracy
- **Problem**: Irrelevant knowledge being retrieved
- **Solution**: Adjust relevance scoring weights
- **Related Files**: `knowledge_service.py`, `enhanced_knowledge_service.py`

## 📈 Performance Considerations

### Optimization Points
1. **Voice Caching**: Cache frequently used TTS responses
2. **Session Compression**: Compress old messages to reduce token usage
3. **Knowledge Indexing**: Use weighted scoring for faster retrieval
4. **Memory Caching**: In-memory cache for active sessions
5. **Batch Operations**: Group database operations when possible

### Monitoring
- Backend logs in `backend_clean/backend.log`
- Frontend logs in browser console
- MongoDB performance through MongoDB Compass
- API response times through FastAPI metrics

## 🔐 Security Considerations

1. **Input Validation**: Pydantic models for all API inputs
2. **Session Security**: User ID validation for all session operations
3. **Rate Limiting**: Consider implementing for production
4. **API Key Management**: Environment variables for sensitive data
5. **CORS Configuration**: Restricted to specific origins

## 🎯 Future Enhancements

### Planned Features (from plan.md)
- Advanced agent-based reasoning system
- Multi-modal interactions (images, documents)
- Collaborative multi-character conversations
- Enhanced emotion detection and response
- Real-time voice conversation (WebRTC)
- Mobile application development

### Technical Improvements
- Migrate to vector database for knowledge retrieval
- Implement WebSocket for real-time updates
- Add comprehensive logging and monitoring
- Optimize LLM token usage
- Implement user authentication system

## 📚 Key Technologies

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database for flexible schemas
- **Azure OpenAI**: GPT-4 for conversation generation
- **Azure Cognitive Services**: STT/TTS capabilities
- **IcePeak.ai**: Alternative TTS provider
- **Pydantic**: Data validation and settings

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **Lucide Icons**: Icon library
- **Shadcn/ui**: Component library

## 🤝 Development Guidelines

### Code Style
- Python: Follow PEP 8 with type hints
- TypeScript: Use strict mode with proper typing
- Components: Functional components with hooks
- Services: Single responsibility principle
- Testing: Descriptive test names with clear assertions

### Git Workflow
- Feature branches from `main`
- Descriptive commit messages
- PR reviews before merging
- Regular rebasing to avoid conflicts

## 🚀 Recent Updates (2025-08-27)

### Conference Demo Character: 설민석 AI 튜터
- ✅ **Character Implementation**: Full Korean history tutor with 100 Q&A knowledge items
- ✅ **Dedicated TTS Service**: Custom voice using dev.icepeak.ai server
  - Endpoint: `https://dev.icepeak.ai/api/text-to-speech`
  - Actor ID: `66f691e9b38df0481f09bf5e`
  - Service: `services/seolminseok_tts_service.py`
- ✅ **Selective Memory System**: Educational progress tracking
- ✅ **Voice Integration**: Automatic routing based on character_id

### New Services Added
- **SeolMinSeok TTS Service** (`services/seolminseok_tts_service.py`)
  - Dedicated TTS for 설민석 character
  - HD audio quality
  - Fallback mechanism to regular TTS

### Documentation Updates
- `SEOLMINSEOK_TTS_SUCCESS_REPORT.md`: Implementation success report
- `SEOLMINSEOK_TTS_IMPLEMENTATION_PLAN.md`: Detailed implementation plan
- `TTS_ENDPOINT_TEST_RESULTS.md`: Comprehensive testing results
- `plans/Character.md`: Conference demo character specifications

## 📞 Support & Documentation

### Internal Documentation
- `IMPLEMENTATION_SUMMARY.md`: Technical implementation details
- `API_DOCUMENTATION.md`: Detailed API specifications
- `PROMPT_TEMPLATES.md`: Character prompt guidelines
- `plans/plan.md`: Development roadmap and planning
- `structure.md`: This file - comprehensive project structure

### External Resources
- Azure OpenAI Documentation
- FastAPI Documentation
- Next.js Documentation
- MongoDB Documentation

---

*This documentation provides a comprehensive overview of the Voice Character Chat Demo project structure. For specific implementation details, refer to the individual service files and test cases.*