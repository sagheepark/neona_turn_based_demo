# Technical Implementation Guide
## Developer Reference for Voice Character Chat System

### 📋 Table of Contents
1. [System Architecture](#system-architecture)
2. [Character Data Structure](#character-data-structure)
3. [Multi-Character Implementation](#multi-character-implementation)
4. [Selective Memory System](#selective-memory-system)
5. [Knowledge Base Integration](#knowledge-base-integration)
6. [TTS Voice Management](#tts-voice-management)
7. [API Endpoint Reference](#api-endpoint-reference)
8. [Database Schema](#database-schema)
9. [Frontend Integration](#frontend-integration)
10. [Testing & Validation](#testing--validation)

---

## System Architecture

### Core Components
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                       │
├─────────────────────────────────────────────────────────────┤
│                   API Layer (REST/WebSocket)                │
├─────────────────────────────────────────────────────────────┤
│     Backend Services (FastAPI + MongoDB/File System)        │
├──────────────┬────────────────┬─────────────────────────────┤
│   Character  │  Memory &      │    Voice & Audio           │
│   Management │  Knowledge     │    Processing              │
│              │  Services      │                            │
├──────────────┴────────────────┴─────────────────────────────┤
│              External APIs (Azure OpenAI, TTS)             │
└─────────────────────────────────────────────────────────────┘
```

### Service Layer Architecture
```typescript
interface ServiceArchitecture {
  core_services: {
    ChatOrchestrator: "Main conversation flow coordinator",
    ConversationService: "Session and message history management",
    SelectiveMemoryService: "Character memory and status tracking",
    KnowledgeService: "RAG system for character knowledge"
  },
  character_services: {
    CharacterService: "Character CRUD operations",
    MultiCharacterOrchestrator: "Multi-character dialogue management",
    ConfigParserService: "Character configuration parsing"
  },
  audio_services: {
    TTSService: "Text-to-Speech generation",
    STTService: "Speech-to-Text processing", 
    VoiceCacheService: "Audio response caching",
    SeolMinSeokTTSService: "Character-specific TTS"
  }
}
```

---

## Character Data Structure

### 1. Core Character Schema
```typescript
interface Character {
  id: string;                    // Unique identifier
  name: string;                  // Display name
  prompt: string;                // XML-structured character definition
  greetings: string[];           // Predefined greeting messages
  voice_id: string;              // TTS voice identifier
  selective_config?: string;     // Optional memory configuration
  conversation_examples?: string[]; // Example dialogues
  created_at?: Date;
  updated_at?: Date;
}
```

### 2. XML Prompt Parsing
```python
# services/config_parser_service.py
def parse_character_prompt(prompt: str) -> Dict[str, str]:
    """
    Parse XML-structured character prompt into structured data
    
    Returns:
        Dict with keys: name, personality, speaking_style, age, 
                       gender, role, backstory, scenario, goals
    """
    character_data = {}
    
    # Extract XML elements using regex or XML parser
    xml_elements = [
        'name', 'personality', 'speaking_style', 'age',
        'gender', 'role', 'backstory', 'scenario', 'goals'
    ]
    
    for element in xml_elements:
        pattern = f'<{element}>(.*?)</{element}>'
        match = re.search(pattern, prompt, re.DOTALL | re.IGNORECASE)
        if match:
            character_data[element] = match.group(1).strip()
    
    return character_data
```

### 3. Direct Greeting Implementation
```python
# In main.py - chat-with-session endpoint
def handle_greeting_request(request: ChatWithSessionRequest) -> ChatWithSessionResponse:
    """Handle greeting with direct character greeting selection"""
    
    # Check if this is a new session greeting
    is_greeting = (
        not request.session_id and 
        request.message.lower() in GREETING_KEYWORDS
    )
    
    if is_greeting:
        # Get character with greetings
        character = await character_service.get_character(request.character_id)
        
        if character and character.get('greetings'):
            # Random greeting selection
            selected_greeting = random.choice(character['greetings'])
            
            # Create session and save messages
            session_data = conversation_service.create_session(
                request.user_id, request.character_id, request.persona_id
            )
            
            # Generate TTS and return direct response
            return generate_greeting_response(selected_greeting, session_data)
    
    # Fall through to normal LLM processing
    return process_with_llm(request)

GREETING_KEYWORDS = [
    '안녕하세요', '안녕', 'hello', 'hi', '반가워요', '처음 뵙겠습니다'
]
```

---

## Multi-Character Implementation

### 1. MultiCharacterOrchestrator Service
```python
# services/multi_character_orchestrator.py
class MultiCharacterOrchestrator:
    """Manages multi-character voice dialogues with sequential TTS"""
    
    def __init__(self):
        self.voice_mappings: Dict[str, str] = {}
    
    def parse_dialogue_blocks(self, response: str) -> List[Dict[str, str]]:
        """
        Parse [SPEAKER: name] format into dialogue blocks
        
        Input: "[SPEAKER: Alice] Hello there! [SPEAKER: Bob] Nice to meet you!"
        Output: [
            {"character": "Alice", "dialogue": "Hello there!"},
            {"character": "Bob", "dialogue": "Nice to meet you!"}
        ]
        """
        pattern = r'\[SPEAKER:\s*([^\]]+)\]\s*([^\[\n]*(?:\n(?!\[)[^\[\n]*)*)'
        matches = re.findall(pattern, response.strip(), re.MULTILINE | re.DOTALL)
        
        dialogue_blocks = []
        for character_name, dialogue_content in matches:
            dialogue_blocks.append({
                "character": character_name.strip(),
                "dialogue": dialogue_content.strip()
            })
        
        return dialogue_blocks
    
    def generate_tts_queue(self, dialogue_blocks: List[Dict]) -> List[Dict]:
        """Generate sequential TTS queue with voice mappings"""
        tts_queue = []
        
        for block in dialogue_blocks:
            voice_id = self.voice_mappings.get(block["character"])
            if voice_id:
                tts_queue.append({
                    "character": block["character"],
                    "dialogue": block["dialogue"],
                    "voice_id": voice_id,
                    "sequence_order": len(tts_queue)
                })
        
        return tts_queue
```

### 2. API Endpoints for Multi-Character
```python
# main.py - Multi-character API endpoints
@app.post("/api/multi-character/setup")
async def setup_multi_character_voices(request: MultiCharacterSetupRequest):
    """Setup voice mappings for multi-character session"""
    try:
        orchestrator = MultiCharacterOrchestrator()
        orchestrator.set_voice_mappings(request.voice_mappings)
        
        # Store in session or database for later use
        session_data = {
            "session_id": request.session_id,
            "voice_mappings": request.voice_mappings,
            "created_at": datetime.now().isoformat()
        }
        
        return {"success": True, "session_data": session_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/multi-character/chat")
async def multi_character_chat(request: MultiCharacterChatRequest):
    """Process multi-character chat with sequential TTS generation"""
    try:
        orchestrator = MultiCharacterOrchestrator()
        orchestrator.set_voice_mappings(request.voice_mappings)
        
        # Generate LLM response with multi-character prompt
        llm_response = await generate_multi_character_response(
            request.message, request.character_config
        )
        
        # Parse dialogue blocks
        dialogue_blocks = orchestrator.parse_dialogue_blocks(llm_response)
        
        # Generate TTS queue
        tts_queue = orchestrator.generate_tts_queue(dialogue_blocks)
        
        # Generate audio for each character
        audio_segments = []
        for tts_item in tts_queue:
            audio_data = await tts_service.generate_tts(
                tts_item["dialogue"], 
                tts_item["voice_id"]
            )
            audio_segments.append({
                "character": tts_item["character"],
                "audio": audio_data,
                "sequence": tts_item["sequence_order"]
            })
        
        return {
            "success": True,
            "dialogue_blocks": dialogue_blocks,
            "audio_segments": audio_segments,
            "total_segments": len(audio_segments)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Selective Memory System

### 1. Memory Configuration Parser
```python
# services/config_parser_service.py
class ConfigParserService:
    """Parse character memory configuration from text files"""
    
    def parse_selective_config(self, config_text: str) -> Dict[str, Any]:
        """
        Parse selective memory configuration
        
        Input: Text file with status_values, triggers, milestones
        Output: Structured configuration dict
        """
        config = {
            "status_values": {},
            "status_triggers": {},
            "milestones": {},
            "special_events": {}
        }
        
        current_section = None
        
        for line in config_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Section headers
            if line.endswith(':'):
                current_section = line[:-1]
                continue
            
            # Parse based on current section
            if current_section == "status_values":
                self._parse_status_value(line, config)
            elif current_section == "status_triggers":
                self._parse_trigger(line, config)
            elif current_section == "milestones":
                self._parse_milestone(line, config)
        
        return config
    
    def _parse_status_value(self, line: str, config: Dict):
        """Parse status value: affection: 50"""
        if ':' in line:
            key, value = line.split(':', 1)
            config["status_values"][key.strip()] = int(value.strip())
    
    def _parse_trigger(self, line: str, config: Dict):
        """Parse trigger conditions for status changes"""
        # Implementation for parsing trigger conditions
        pass
```

### 2. Memory Update System
```python
# services/selective_memory_service.py
class SelectiveMemoryService:
    """Manages character memory, status values, and milestones"""
    
    async def update_memory_from_message(
        self, 
        user_id: str, 
        character_id: str, 
        user_message: str,
        ai_response: str
    ) -> Dict[str, Any]:
        """Update memory based on conversation content"""
        
        # Get current memory state
        memory = await self.get_core_memory(user_id, character_id)
        if not memory:
            memory = await self.initialize_memory(user_id, character_id)
        
        # Load character configuration
        config = await self._load_character_config(character_id)
        
        # Analyze message for status triggers
        status_changes = self._analyze_status_triggers(
            user_message, ai_response, config
        )
        
        # Update status values
        for status_key, change in status_changes.items():
            current_value = memory["status_values"].get(status_key, 0)
            new_value = max(0, min(100, current_value + change))
            memory["status_values"][status_key] = new_value
        
        # Check for milestone achievements
        achieved_milestones = self._check_milestones(memory, config)
        
        # Log significant events
        if status_changes or achieved_milestones:
            event = {
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message[:100] + "...",
                "status_changes": status_changes,
                "milestones": achieved_milestones
            }
            memory["event_log"].append(event)
        
        # Update persistent facts
        facts = self._extract_facts(user_message)
        memory["persistent_facts"].extend(facts)
        
        # Save updated memory
        await self.update_core_memory(user_id, character_id, memory)
        
        return {
            "status_changes": status_changes,
            "milestones": achieved_milestones,
            "new_facts": facts
        }
```

---

## Knowledge Base Integration

### 1. Knowledge Service Structure
```python
# services/knowledge_service.py
class KnowledgeService:
    """Manages character knowledge base with semantic search"""
    
    def search_relevant_knowledge(
        self, 
        character_id: str, 
        query: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant knowledge items using weighted scoring
        
        Scoring factors:
        - Keyword matching (40%)
        - Category relevance (25%)
        - Usage frequency (20%)
        - Recency bonus (15%)
        """
        knowledge_items = self.get_character_knowledge(character_id)
        if not knowledge_items:
            return []
        
        scored_items = []
        query_keywords = self._extract_keywords(query)
        
        for item in knowledge_items:
            score = self._calculate_relevance_score(item, query_keywords)
            if score > 0.3:  # Relevance threshold
                scored_items.append((score, item))
        
        # Sort by score and return top items
        scored_items.sort(reverse=True, key=lambda x: x[0])
        return [item for score, item in scored_items[:limit]]
    
    def _calculate_relevance_score(
        self, 
        item: Dict[str, Any], 
        query_keywords: List[str]
    ) -> float:
        """Calculate weighted relevance score for knowledge item"""
        score = 0.0
        
        # Keyword matching (40% weight)
        item_keywords = item.get("keywords", [])
        keyword_matches = len(set(query_keywords) & set(item_keywords))
        keyword_score = keyword_matches / max(len(query_keywords), 1) * 0.4
        
        # Title/content matching (25% weight)
        content = f"{item.get('title', '')} {item.get('content', '')}".lower()
        content_matches = sum(1 for kw in query_keywords if kw.lower() in content)
        content_score = content_matches / max(len(query_keywords), 1) * 0.25
        
        # Usage frequency (20% weight)
        usage_count = item.get("usage_count", 0)
        max_usage = max(self._get_max_usage_count(), 1)
        usage_score = min(usage_count / max_usage, 1.0) * 0.2
        
        # Recency bonus (15% weight)
        recency_score = self._calculate_recency_score(item) * 0.15
        
        return keyword_score + content_score + usage_score + recency_score
```

### 2. Knowledge Integration in Chat
```python
# In chat processing pipeline
async def enhance_response_with_knowledge(
    character_id: str,
    user_message: str,
    base_response: str
) -> Dict[str, Any]:
    """Enhance AI response with relevant knowledge"""
    
    # Search for relevant knowledge
    knowledge_items = knowledge_service.search_relevant_knowledge(
        character_id, user_message, limit=3
    )
    
    if knowledge_items:
        # Format knowledge context for LLM
        knowledge_context = "\n".join([
            f"관련 지식: {item['title']} - {item['content'][:200]}..."
            for item in knowledge_items
        ])
        
        # Update usage counts
        for item in knowledge_items:
            knowledge_service.increment_usage_count(
                character_id, item["id"]
            )
        
        return {
            "enhanced_response": base_response,
            "knowledge_used": [item["id"] for item in knowledge_items],
            "knowledge_context": knowledge_context
        }
    
    return {"enhanced_response": base_response, "knowledge_used": []}
```

---

## TTS Voice Management

### 1. Voice Service Architecture
```python
# services/tts_service.py
class TTSService:
    """Unified TTS service with multiple provider support"""
    
    def __init__(self):
        self.providers = {
            "azure": AzureTTSProvider(),
            "typecast": TypecastTTSProvider(),
            "icepeak": IcepeakTTSProvider()
        }
    
    async def generate_tts(
        self, 
        text: str, 
        voice_id: str, 
        emotion: str = "neutral"
    ) -> str:
        """Generate TTS audio with automatic provider routing"""
        
        provider = self._get_provider_for_voice(voice_id)
        
        try:
            audio_data = await provider.generate_audio(text, voice_id, emotion)
            
            # Cache successful generation
            await self._cache_audio(text, voice_id, audio_data)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            
            # Try fallback provider
            fallback_audio = await self._generate_fallback(text, emotion)
            return fallback_audio
    
    def _get_provider_for_voice(self, voice_id: str) -> str:
        """Route voice ID to appropriate TTS provider"""
        if voice_id.startswith("tc_"):
            return "typecast"
        elif voice_id.startswith("azure_"):
            return "azure"
        elif voice_id == "seol_min_seok":
            return "icepeak"
        else:
            return "azure"  # Default provider
```

### 2. Character-Specific TTS
```python
# services/seolminseok_tts_service.py
class SeolMinSeokTTSService:
    """Dedicated TTS service for 설민석 character"""
    
    def __init__(self):
        self.endpoint = "https://dev.icepeak.ai/api/text-to-speech"
        self.actor_id = "66f691e9b38df0481f09bf5e"
        self.api_key = "__apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG"
    
    async def generate_tts(self, text: str, character_id: str) -> str:
        """Generate TTS with character-specific voice"""
        
        payload = {
            "text": text,
            "actor_id": self.actor_id,
            "format": "wav",
            "sample_rate": 22050
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint, 
                    json=payload, 
                    headers=headers
                ) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        return base64.b64encode(audio_data).decode()
                    else:
                        raise Exception(f"TTS API error: {response.status}")
        
        except Exception as e:
            logger.error(f"SeolMinSeok TTS failed: {e}")
            # Fallback to regular TTS
            return await tts_service.generate_tts(text, "tc_default", "neutral")
```

---

## API Endpoint Reference

### 1. Character Management
```python
@app.get("/api/characters")
async def get_all_characters() -> List[Character]:
    """Get all available characters"""

@app.post("/api/characters")
async def create_character(character: CharacterCreateRequest) -> Character:
    """Create new character with validation"""

@app.put("/api/characters/{character_id}")
async def update_character(character_id: str, updates: CharacterUpdateRequest):
    """Update existing character"""

@app.delete("/api/characters/{character_id}")
async def delete_character(character_id: str):
    """Delete character and associated data"""
```

### 2. Session Management
```python
@app.post("/api/sessions/start")
async def start_session(request: SessionStartRequest) -> SessionStartResponse:
    """Start new session or get continuation options"""

@app.post("/api/sessions/create")
async def create_session(request: SessionStartRequest) -> SessionCreateResponse:
    """Create new conversation session"""

@app.post("/api/sessions/continue")
async def continue_session(request: SessionContinueRequest) -> SessionContinueResponse:
    """Continue existing session with message history"""

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, request: SessionDeleteRequest):
    """Delete conversation session"""
```

### 3. Chat & Voice
```python
@app.post("/api/chat-with-session")
async def chat_with_session(request: ChatWithSessionRequest) -> ChatWithSessionResponse:
    """Main chat endpoint with session persistence and direct greeting handling"""

@app.post("/api/stt")
async def speech_to_text(request: STTRequest) -> STTResponse:
    """Convert speech to text"""

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest) -> TTSResponse:
    """Generate TTS audio with character-specific routing"""
```

---

## Database Schema

### 1. MongoDB Collections
```javascript
// characters collection
{
  "_id": ObjectId,
  "character_id": "unique_string",
  "name": "Character Name",
  "prompt": "XML structured prompt",
  "greetings": ["greeting1", "greeting2"],
  "voice_id": "tts_voice_id",
  "selective_config": "text configuration",
  "conversation_examples": ["example1", "example2"],
  "created_at": ISODate,
  "updated_at": ISODate
}

// selective_memories collection  
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

// knowledge_base collection
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
      "usage_count": 0,
      "last_used": ISODate,
      "difficulty_level": "beginner|intermediate|advanced"
    }
  ]
}
```

### 2. File System Structure
```
backend_clean/
├── conversations/           # Session storage
│   └── {user_id}/
│       └── {character_id}/
│           └── sess_{timestamp}_{id}.json
├── configurations/          # Memory configs
│   └── {character_id}_config.txt
├── knowledge/              # Knowledge bases
│   └── characters/
│       └── {character_id}/
│           └── knowledge.json
└── personas/               # User personas
    └── {user_id}.json
```

---

## Frontend Integration

### 1. Character Storage Service
```typescript
// lib/storage.ts
export class CharacterStorage {
  static async initializeDemo(forceRefresh: boolean = false): Promise<void> {
    if (typeof window === 'undefined') return;
    const existing = this.getAll();
    
    if (forceRefresh || existing.length === 0) {
      try {
        const { DEMO_CHARACTERS } = await import('@/data/demo-characters');
        localStorage.setItem(CHARACTERS_KEY, JSON.stringify(DEMO_CHARACTERS));
      } catch (error) {
        console.warn('Failed to load demo characters:', error);
      }
    }
  }
  
  static getById(id: string): Character | null {
    const characters = this.getAll();
    return characters.find(c => c.id === id) || null;
  }
}
```

### 2. API Client Methods
```typescript
// lib/api-client.ts
export class ApiClient {
  static async chatWithSession(request: ChatWithSessionRequest): Promise<ChatWithSessionResponse> {
    const response = await fetch(`${API_BASE_URL}/api/chat-with-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      mode: 'cors'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }
  
  static async deleteSession(session_id: string, user_id: string): Promise<{success: boolean}> {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${session_id}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id }),
      mode: 'cors'
    });
    
    return response.json();
  }
}
```

### 3. Chat Component Integration
```tsx
// app/chat/[characterId]/page.tsx
export default function ChatPage() {
  useEffect(() => {
    const loadCharacter = async () => {
      const characterId = params.characterId as string;
      
      // Force refresh demo characters to get latest data
      await CharacterStorage.initializeDemo(true);
      
      const char = CharacterStorage.getAll().find(c => c.id === characterId);
      if (char) {
        setCharacter(char);
        checkForExistingSessions(characterId);
      }
    };
    
    loadCharacter();
  }, [params.characterId]);
  
  const handleDeleteSession = async (sessionId: string) => {
    try {
      await ApiClient.deleteSession(sessionId, 'demo_user');
      // Refresh session list
      if (character) {
        await checkForExistingSessions(character.id);
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };
}
```

---

## Testing & Validation

### 1. TDD Test Structure
```python
# tests/test_multi_character_orchestrator.py
class TestMultiCharacterOrchestrator:
    """Following TDD methodology: RED → GREEN → REFACTOR"""
    
    def test_should_create_voice_mapping_for_characters(self):
        """Test voice mapping storage and retrieval"""
        orchestrator = MultiCharacterOrchestrator()
        character_mappings = {
            "Alice": "tc_61c97b56f1b7877a74df625b",
            "Bob": "tc_6073b2f6817dccf658bb159f"
        }
        
        orchestrator.set_voice_mappings(character_mappings)
        
        assert orchestrator.get_voice_for_character("Alice") == "tc_61c97b56f1b7877a74df625b"
        assert orchestrator.get_voice_for_character("Unknown") is None
    
    def test_should_parse_dialogue_blocks_with_speaker_format(self):
        """Test [SPEAKER: name] dialogue parsing"""
        orchestrator = MultiCharacterOrchestrator()
        multi_response = """
        [SPEAKER: Alice] Hello there!
        [SPEAKER: Bob] Nice to meet you!
        """
        
        blocks = orchestrator.parse_dialogue_blocks(multi_response)
        
        assert len(blocks) == 2
        assert blocks[0]["character"] == "Alice"
        assert blocks[0]["dialogue"] == "Hello there!"
```

### 2. Integration Testing
```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_full_chat_flow_with_greeting():
    """Test complete chat flow with direct greeting"""
    
    # Create test character with greetings
    test_character = {
        "character_id": "test_bot",
        "name": "Test Bot",
        "greetings": ["안녕하세요! 테스트 봇입니다."],
        "voice_id": "tc_61c97b56f1b7877a74df625b"
    }
    
    # Test greeting request
    request = ChatWithSessionRequest(
        user_id="test_user",
        character_id="test_bot", 
        message="안녕하세요",
        character_prompt="<character><name>Test Bot</name></character>"
    )
    
    response = await chat_with_session(request)
    
    # Verify direct greeting was used
    assert response.dialogue == "안녕하세요! 테스트 봇입니다."
    assert response.session_id is not None
    assert response.audio is not None
```

### 3. Performance Testing
```python
# tests/test_performance.py
@pytest.mark.performance
def test_greeting_response_time():
    """Test that direct greeting responses are faster than LLM generation"""
    
    start_time = time.time()
    
    # Test direct greeting
    response = handle_greeting_request(greeting_request)
    
    direct_greeting_time = time.time() - start_time
    
    # Should be under 500ms for direct greeting
    assert direct_greeting_time < 0.5
    
@pytest.mark.performance  
def test_knowledge_search_performance():
    """Test knowledge search performance with large knowledge base"""
    
    # Create knowledge base with 1000 items
    large_knowledge_base = create_large_knowledge_base(1000)
    
    start_time = time.time()
    results = knowledge_service.search_relevant_knowledge(
        "test_character", "test query", limit=5
    )
    search_time = time.time() - start_time
    
    # Should complete search within 100ms
    assert search_time < 0.1
    assert len(results) <= 5
```

---

## Configuration Examples

### 1. Environment Configuration
```env
# Azure Services
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# TTS Services
AZURE_STT_KEY=your-stt-key
AZURE_TTS_KEY=your-tts-key
ICEPEAK_API_KEY=your-icepeak-key

# Database
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=voice_character_chat
```

### 2. Character Configuration Template
```txt
# Character Memory Configuration Template
# Copy and modify for new characters

status_values:
  affection: 50
  trust: 30
  knowledge_level: 20
  mood: 70
  energy: 80

status_triggers:
  affection:
    increase: ["좋아", "고마워", "재미있어"]
    decrease: ["싫어", "별로", "지루해"]
    amount: 5

milestones:
  first_conversation:
    condition: "conversation_count >= 1"
    description: "첫 대화를 시작했습니다"
    reward: "특별 인사말 해금"
```

---

This technical guide provides comprehensive implementation details for developers working with the voice character chat system. Each section includes practical code examples and follows the established TDD methodology for reliable, maintainable code development.

For additional support, refer to the main documentation files and existing test implementations in the codebase.