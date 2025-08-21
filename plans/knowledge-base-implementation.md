# Enhanced Knowledge & Conversation System Implementation

## 🎯 Overview
Implement a comprehensive system following TDD principles with:
1. **Enhanced Knowledge Base** - Smart retrieval with context awareness
2. **Conversation History** - Session persistence and continuation 
3. **Multi-Persona System** - User identity management
4. **Hybrid RAG-Agent Architecture** - Scalable from simple to sophisticated

**Development Approach**: Following claude.md TDD methodology (Red → Green → Refactor) with Tidy First principles.

## 📁 File Structure

```
backend_clean/
├── knowledge/
│   ├── characters/
│   │   ├── yoon_ahri/
│   │   │   ├── knowledge.json      # Character-specific knowledge
│   │   │   ├── documents/          # Text files, PDFs
│   │   │   └── media/             # Images, audio files
│   │   ├── taepung/
│   │   │   ├── knowledge.json
│   │   │   └── documents/
│   │   └── park_hyun/
│   │       ├── knowledge.json
│   │       └── documents/
│   └── shared/
│       └── common.json            # Shared knowledge across characters
├── conversations/
│   └── {user_id}/
│       ├── {character_id}/
│       │   ├── sessions.json      # Session metadata
│       │   └── {session_id}.json  # Individual conversation data
│       └── personas.json          # User's personas
├── personas/
│   └── {user_id}/
│       └── personas.json          # User persona definitions
├── services/
│   ├── knowledge_service.py       # Enhanced knowledge retrieval
│   ├── conversation_service.py    # Session management
│   ├── persona_service.py         # User persona management
│   └── chat_orchestrator.py       # Combines all services
├── models/
│   ├── conversation.py            # Session data models
│   ├── persona.py                 # Persona data models
│   └── knowledge.py               # Enhanced knowledge models
└── tests/
    ├── test_knowledge_service.py  # Knowledge service tests
    ├── test_conversation_service.py # Conversation tests
    └── test_persona_service.py    # Persona tests

frontend/
└── src/
    ├── app/
    │   ├── chat/[characterId]/
    │   │   └── page.tsx           # Enhanced with session selection
    │   ├── personas/
    │   │   ├── page.tsx           # Persona management
    │   │   └── create/page.tsx    # Persona creation
    │   ├── sessions/
    │   │   └── [characterId]/page.tsx # Session history
    │   └── characters/[id]/knowledge/
    │       └── page.tsx           # Knowledge management UI
    ├── components/
    │   ├── chat/
    │   │   ├── SessionSelector.tsx    # Continue/new session choice
    │   │   └── KnowledgeIndicator.tsx # Show when knowledge used
    │   ├── personas/
    │   │   ├── PersonaSelector.tsx    # Persona selection
    │   │   └── PersonaEditor.tsx      # Persona creation/edit
    │   ├── sessions/
    │   │   └── SessionList.tsx        # Previous sessions list
    │   └── knowledge/
    │       ├── KnowledgeEditor.tsx
    │       ├── KnowledgeList.tsx
    │       └── KnowledgeSearch.tsx
    └── lib/
        ├── conversation-storage.ts    # Session management
        └── persona-storage.ts         # Persona management
```

## 💾 Enhanced Data Schemas

### 1. Knowledge Schema (Enhanced)
```json
{
  "character_id": "yoon_ahri",
  "version": "2.0",
  "last_updated": "2025-01-18T10:00:00Z",
  "knowledge_items": [
    {
      "id": "k_001",
      "type": "text",
      "category": "expertise",
      "title": "ASMR 트리거 기법",
      "content": "귓속말(Whispering)은 가장 인기 있는 ASMR 트리거입니다. 부드럽고 느린 속도로 말하면서 'ㅅ', 'ㅊ', 'ㅎ' 같은 자음을 강조하면 효과적입니다.",
      "tags": ["ASMR", "귓속말", "릴렉스"],
      "trigger_keywords": ["ASMR", "귓속말", "잠", "수면", "릴렉스", "스트레스"],
      "context_keywords": ["밤", "피곤", "긴장", "휴식"],
      "priority": 1,
      "usage_count": 0,
      "relevance_score": 0.0,
      "persona_affinity": ["student", "stressed_worker"],
      "created_at": "2025-01-18T10:00:00Z",
      "last_used": null
    }
  ],
  "knowledge_stats": {
    "total_items": 15,
    "categories": {
      "expertise": 8,
      "technique": 4,
      "recommendation": 3
    },
    "avg_usage": 2.3,
    "last_updated": "2025-01-18T10:00:00Z"
  }
}
```

### 2. Conversation Session Schema
```json
{
  "session_id": "sess_20250118_001",
  "user_id": "user_123",
  "character_id": "yoon_ahri",
  "persona_id": "persona_student", 
  "created_at": "2025-01-18T10:00:00Z",
  "last_updated": "2025-01-18T11:30:00Z",
  "message_count": 15,
  "session_summary": "ASMR 상담 세션 - 수면 문제 해결",
  "session_tags": ["sleep", "stress", "ASMR"],
  "status": "active",
  "messages": [
    {
      "id": "msg_001",
      "role": "user",
      "content": "잠이 안 와요",
      "timestamp": "2025-01-18T10:00:00Z",
      "persona_context": "stressed student preparing for exams"
    },
    {
      "id": "msg_002", 
      "role": "assistant",
      "content": "스트레스 때문에 잠이 안 오는 것 같네요. 4-7-8 호흡법을 한번 해보실까요?",
      "timestamp": "2025-01-18T10:01:00Z",
      "knowledge_used": [
        {
          "knowledge_id": "k_001",
          "relevance_score": 0.9,
          "usage_type": "direct"
        },
        {
          "knowledge_id": "k_002",
          "relevance_score": 0.7,
          "usage_type": "suggested"
        }
      ],
      "emotion": "whisper",
      "response_time_ms": 1250
    }
  ],
  "knowledge_usage_summary": {
    "k_001": 3,
    "k_002": 1,
    "k_003": 2
  },
  "conversation_metrics": {
    "avg_response_time": 1100,
    "knowledge_hit_rate": 0.8,
    "user_satisfaction": null
  }
}
```

### 3. User Persona Schema
```json
{
  "user_id": "user_123",
  "personas": [
    {
      "id": "persona_student",
      "name": "스트레스 받는 대학생",
      "description": "시험 스트레스와 진로 고민이 많은 대학생",
      "avatar": "/images/student-avatar.png",
      "attributes": {
        "age": "20대 초반",
        "occupation": "대학생",
        "personality_traits": ["내향적", "완벽주의", "예민함"],
        "interests": ["공부", "게임", "음악", "웹툰"],
        "speaking_style": "존댓말, 조심스러운 톤",
        "background_context": "시험 스트레스, 진로 고민, 수면 부족",
        "emotional_state": "불안, 스트레스",
        "goals": ["성적 향상", "스트레스 관리", "수면 개선"]
      },
      "conversation_preferences": {
        "formality": "polite",
        "response_length": "medium",
        "tone": "supportive",
        "topics_to_avoid": ["가족 문제", "연애"]
      },
      "created_at": "2025-01-18T10:00:00Z",
      "last_used": "2025-01-18T11:00:00Z",
      "usage_count": 15,
      "is_active": true
    },
    {
      "id": "persona_professional",
      "name": "직장인",
      "description": "업무 스트레스가 많은 회사원",
      "attributes": {
        "age": "30대 초반",
        "occupation": "회사원",
        "personality_traits": ["외향적", "목표지향적"],
        "speaking_style": "반말 혼용, 친근한 톤"
      },
      "is_active": false
    }
  ],
  "active_persona_id": "persona_student",
  "persona_stats": {
    "total_personas": 2,
    "most_used": "persona_student",
    "last_created": "2025-01-15T10:00:00Z"
  }
}
```

### 4. Session Metadata Schema
```json
{
  "user_id": "user_123",
  "character_id": "yoon_ahri",
  "sessions": [
    {
      "session_id": "sess_20250118_001",
      "title": "수면 문제 상담",
      "created_at": "2025-01-18T10:00:00Z",
      "last_updated": "2025-01-18T11:30:00Z",
      "message_count": 15,
      "duration_minutes": 90,
      "persona_used": "persona_student",
      "summary": "ASMR 기법과 호흡법을 통한 수면 개선 상담",
      "tags": ["sleep", "stress", "ASMR"],
      "status": "completed",
      "satisfaction_rating": null
    },
    {
      "session_id": "sess_20250117_002",
      "title": "시험 스트레스 관리",
      "created_at": "2025-01-17T14:00:00Z",
      "message_count": 8,
      "status": "active",
      "summary": "시험 기간 스트레스 해소 방법 논의"
    }
  ],
  "session_stats": {
    "total_sessions": 12,
    "avg_duration": 65,
    "favorite_topics": ["sleep", "stress", "study"],
    "last_session": "2025-01-18T11:30:00Z"
  }
}
```

## 🧪 TDD Implementation Plan

Following TDD methodology from claude.md - implement tests first, then minimal code to pass.

### Phase 1: Enhanced Knowledge System (Following plan.md Test Group 1)

#### Test 1.1: shouldFindRelevantKnowledgeByKeyword

**RED Phase** - Write failing test first:
```python
# backend_clean/tests/test_knowledge_service.py
import pytest
from services.knowledge_service import KnowledgeService

class TestKnowledgeService:
    def test_shouldFindRelevantKnowledgeByKeyword(self):
        # Given: Knowledge service with ASMR knowledge
        service = KnowledgeService()
        
        # When: Search for sleep-related keyword
        results = service.search_relevant_knowledge("잠", "yoon_ahri", max_results=3)
        
        # Then: Returns ASMR sleep-related knowledge
        assert len(results) > 0
        assert any("ASMR" in item.get("title", "") for item in results)
        assert any("잠" in item.get("trigger_keywords", []) for item in results)
```

**GREEN Phase** - Minimal implementation to pass:
```python
# backend_clean/services/knowledge_service.py
import json
import os
from typing import List, Dict, Optional
from pathlib import Path

class KnowledgeService:
    def __init__(self):
        self.knowledge_base_path = Path("knowledge/characters")
        self.knowledge_cache = {}
        self._load_all_knowledge()
    
    def _load_all_knowledge(self):
        """Load character knowledge - minimal implementation"""
        if not self.knowledge_base_path.exists():
            self.knowledge_base_path.mkdir(parents=True, exist_ok=True)
            self._create_sample_knowledge()
        
        for character_dir in self.knowledge_base_path.iterdir():
            if character_dir.is_dir():
                knowledge_file = character_dir / "knowledge.json"
                if knowledge_file.exists():
                    with open(knowledge_file, 'r', encoding='utf-8') as f:
                        self.knowledge_cache[character_dir.name] = json.load(f)
    
    def search_relevant_knowledge(self, query: str, character_id: str, max_results: int = 3) -> List[Dict]:
        """Search for relevant knowledge - minimal implementation to pass test"""
        if character_id not in self.knowledge_cache:
            return []
        
        knowledge_items = self.knowledge_cache[character_id].get("knowledge_items", [])
        query_lower = query.lower()
        
        # Simple keyword matching
        results = []
        for item in knowledge_items:
            for keyword in item.get("trigger_keywords", []):
                if keyword.lower() in query_lower:
                    results.append(item)
                    break
        
        return results[:max_results]
    
    def _create_sample_knowledge(self):
        """Create minimal sample knowledge for tests"""
        yoon_ahri_knowledge = {
            "character_id": "yoon_ahri",
            "version": "2.0",
            "knowledge_items": [
                {
                    "id": "k_001",
                    "title": "ASMR 수면 유도 기법",
                    "content": "ASMR 귓속말을 통한 수면 유도 방법",
                    "trigger_keywords": ["ASMR", "잠", "수면", "귓속말"],
                    "priority": 1
                }
            ]
        }
        
        char_dir = self.knowledge_base_path / "yoon_ahri"
        char_dir.mkdir(parents=True, exist_ok=True)
        
        with open(char_dir / "knowledge.json", 'w', encoding='utf-8') as f:
            json.dump(yoon_ahri_knowledge, f, ensure_ascii=False, indent=2)
```

**REFACTOR Phase** - After test passes, improve structure if needed.

---

### Phase 2: Conversation History System (Following plan.md Test Group 2)

#### Test 2.1: shouldCreateNewConversationSession

**RED Phase** - Write failing test:
```python
# backend_clean/tests/test_conversation_service.py
import pytest
from services.conversation_service import ConversationService

class TestConversationService:
    def test_shouldCreateNewConversationSession(self):
        # Given: Conversation service
        service = ConversationService()
        
        # When: Create new session
        session = service.create_session(
            user_id="user_123",
            character_id="yoon_ahri", 
            persona_id="persona_student"
        )
        
        # Then: Returns session with unique ID and metadata
        assert session["session_id"] is not None
        assert session["user_id"] == "user_123"
        assert session["character_id"] == "yoon_ahri"
        assert session["persona_id"] == "persona_student"
        assert session["status"] == "active"
```

**GREEN Phase** - Minimal implementation:
```python
# backend_clean/services/conversation_service.py
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class ConversationService:
    def __init__(self):
        self.conversations_path = Path("conversations")
        self.conversations_path.mkdir(exist_ok=True)
    
    def create_session(self, user_id: str, character_id: str, persona_id: str) -> Dict:
        """Create new conversation session"""
        session_id = f"sess_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "character_id": character_id,
            "persona_id": persona_id,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "messages": [],
            "message_count": 0
        }
        
        # Save session
        user_dir = self.conversations_path / user_id / character_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        with open(user_dir / f"{session_id}.json", 'w', encoding='utf-8') as f:
            json.dump(session, f, ensure_ascii=False, indent=2)
        
        return session
```

---

### Phase 3: Multi-Persona System (Following plan.md Test Group 3)

#### Test 3.1: shouldCreateNewUserPersona

**RED Phase** - Write failing test:
```python
# backend_clean/tests/test_persona_service.py
import pytest
from services.persona_service import PersonaService

class TestPersonaService:
    def test_shouldCreateNewUserPersona(self):
        # Given: Persona service
        service = PersonaService()
        
        # When: Create new persona
        persona_data = {
            "name": "스트레스 받는 대학생",
            "description": "시험 스트레스가 많은 대학생",
            "attributes": {
                "age": "20대 초반",
                "occupation": "대학생"
            }
        }
        
        persona = service.create_persona("user_123", persona_data)
        
        # Then: Saves persona with unique ID
        assert persona["id"] is not None
        assert persona["name"] == "스트레스 받는 대학생"
        assert persona["user_id"] == "user_123"
```

**GREEN Phase** - Minimal implementation:
```python
# backend_clean/services/persona_service.py
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class PersonaService:
    def __init__(self):
        self.personas_path = Path("personas")
        self.personas_path.mkdir(exist_ok=True)
    
    def create_persona(self, user_id: str, persona_data: Dict) -> Dict:
        """Create new user persona"""
        persona_id = f"persona_{uuid.uuid4().hex[:8]}"
        
        persona = {
            "id": persona_id,
            "user_id": user_id,
            "name": persona_data["name"],
            "description": persona_data["description"],
            "attributes": persona_data.get("attributes", {}),
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        
        # Load or create user personas file
        user_personas_file = self.personas_path / user_id / "personas.json"
        user_personas_file.parent.mkdir(parents=True, exist_ok=True)
        
        if user_personas_file.exists():
            with open(user_personas_file, 'r', encoding='utf-8') as f:
                user_personas = json.load(f)
        else:
            user_personas = {"user_id": user_id, "personas": [], "active_persona_id": None}
        
        # Add new persona
        user_personas["personas"].append(persona)
        if user_personas["active_persona_id"] is None:
            user_personas["active_persona_id"] = persona_id
        
        # Save updated personas
        with open(user_personas_file, 'w', encoding='utf-8') as f:
            json.dump(user_personas, f, ensure_ascii=False, indent=2)
        
        return persona
```

---

## 🔄 Integration & API Updates

### Enhanced Chat Orchestrator
```python
# backend_clean/services/chat_orchestrator.py
from .knowledge_service import KnowledgeService
from .conversation_service import ConversationService  
from .persona_service import PersonaService

class ChatOrchestrator:
    def __init__(self):
        self.knowledge_service = KnowledgeService()
        self.conversation_service = ConversationService()
        self.persona_service = PersonaService()
    
    async def process_chat_message(
        self,
        user_id: str,
        character_id: str,
        message: str,
        session_id: Optional[str] = None,
        persona_id: Optional[str] = None
    ) -> Dict:
        """Orchestrate complete chat flow with knowledge, history, and persona"""
        
        # 1. Get or create session
        if session_id:
            session = self.conversation_service.get_session(session_id)
        else:
            session = self.conversation_service.create_session(user_id, character_id, persona_id)
        
        # 2. Get persona context
        persona_context = ""
        if persona_id:
            persona = self.persona_service.get_persona(user_id, persona_id)
            if persona:
                persona_context = self._build_persona_context(persona)
        
        # 3. Search relevant knowledge
        relevant_knowledge = self.knowledge_service.search_relevant_knowledge(
            message, character_id, max_results=2
        )
        
        # 4. Build enhanced system prompt
        system_prompt = self._build_system_prompt(
            character_id, 
            session["messages"], 
            persona_context, 
            relevant_knowledge
        )
        
        # 5. Generate AI response (existing logic)
        # 6. Save message to session
        # 7. Return enhanced response
        
        return {
            "session_id": session["session_id"],
            "response": response,
            "knowledge_used": relevant_knowledge,
            "persona_context": persona_context
        }
```

### Frontend Components Architecture

#### SessionSelector Component
```typescript
// frontend/src/components/chat/SessionSelector.tsx
interface SessionSelectorProps {
  characterId: string
  onSessionSelected: (sessionId: string | null) => void
}

export function SessionSelector({ characterId, onSessionSelected }: SessionSelectorProps) {
  const [sessions, setSessions] = useState([])
  const [showPrevious, setShowPrevious] = useState(false)
  
  useEffect(() => {
    loadPreviousSessions()
  }, [characterId])
  
  const loadPreviousSessions = async () => {
    const response = await fetch(`/api/sessions/${characterId}`)
    const data = await response.json()
    
    if (data.sessions.length > 0) {
      setShowPrevious(true)
      setSessions(data.sessions)
    }
  }
  
  if (!showPrevious) {
    onSessionSelected(null) // Start new conversation
    return null
  }
  
  return (
    <Card className="mb-4">
      <CardContent className="p-4">
        <h3 className="font-semibold mb-3">이전 대화</h3>
        <p className="text-sm text-gray-600 mb-3">
          이전 대화를 이어서 하시겠어요?
        </p>
        
        <div className="space-y-2 mb-4">
          {sessions.slice(0, 3).map(session => (
            <div key={session.session_id} 
                 className="p-2 border rounded cursor-pointer hover:bg-gray-50"
                 onClick={() => onSessionSelected(session.session_id)}>
              <div className="font-medium">{session.title || '제목 없음'}</div>
              <div className="text-xs text-gray-500">
                {new Date(session.last_updated).toLocaleDateString()} · {session.message_count}개 메시지
              </div>
            </div>
          ))}
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => onSessionSelected(null)}>
            새 대화 시작
          </Button>
          <Button variant="default" 
                  onClick={() => onSessionSelected(sessions[0]?.session_id)}>
            이전 대화 계속
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
```

#### PersonaSelector Component  
```typescript
// frontend/src/components/personas/PersonaSelector.tsx
interface PersonaSelectorProps {
  selectedPersonaId?: string
  onPersonaSelected: (personaId: string) => void
}

export function PersonaSelector({ selectedPersonaId, onPersonaSelected }: PersonaSelectorProps) {
  const [personas, setPersonas] = useState([])
  const [isOpen, setIsOpen] = useState(false)
  
  useEffect(() => {
    loadPersonas()
  }, [])
  
  const selectedPersona = personas.find(p => p.id === selectedPersonaId)
  
  return (
    <div className="relative">
      <Button variant="outline" onClick={() => setIsOpen(!isOpen)} className="w-full">
        {selectedPersona ? selectedPersona.name : '페르소나 선택'}
        <ChevronDown className="ml-2 h-4 w-4" />
      </Button>
      
      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-white border rounded-lg shadow-lg">
          {personas.map(persona => (
            <div key={persona.id} 
                 className="p-3 hover:bg-gray-50 cursor-pointer"
                 onClick={() => {
                   onPersonaSelected(persona.id)
                   setIsOpen(false)
                 }}>
              <div className="font-medium">{persona.name}</div>
              <div className="text-sm text-gray-500">{persona.description}</div>
            </div>
          ))}
          
          <div className="border-t p-2">
            <Button size="sm" variant="ghost" className="w-full">
              <Plus className="h-4 w-4 mr-2" />
              새 페르소나 만들기
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
```

---

## 🎯 Implementation Timeline

### Week 1: Enhanced Knowledge System
- [ ] Test 1.1: shouldFindRelevantKnowledgeByKeyword
- [ ] Test 1.2: shouldRankKnowledgeByRelevanceScore  
- [ ] Test 1.3: shouldReturnOnlyCharacterSpecificKnowledge
- [ ] Test 1.4: shouldReturnEmptyArrayWhenNoKnowledgeFound
- [ ] Enhanced knowledge retrieval with context awareness
- [ ] Knowledge usage tracking and analytics

### Week 2: Conversation History System  
- [ ] Test 2.1: shouldCreateNewConversationSession
- [ ] Test 2.2: shouldRetrievePreviousSessionsForUserAndCharacter
- [ ] Test 2.3: shouldLoadPreviousMessagesWhenContinuingSession
- [ ] Test 2.4: shouldSaveMessageToExistingSession
- [ ] Session continuation UI implementation
- [ ] Session management APIs

### Week 3: Multi-Persona System
- [ ] Test 3.1: shouldCreateNewUserPersona
- [ ] Test 3.2: shouldSetActivePersonaForUser  
- [ ] Test 3.3: shouldIncludePersonaContextInChatPrompt
- [ ] Persona creation/editing UI
- [ ] Persona selection integration with chat

### Week 4: Integration & Polish
- [ ] Test 4.1: shouldHandleFullConversationWithKnowledgeAndPersona
- [ ] Test 4.2: shouldOfferSessionContinuationAtChatStart
- [ ] Complete system integration
- [ ] Performance optimization
- [ ] Error handling and edge cases

## 🚀 Ready to Start TDD Implementation

**Next Action**: Run the first test `shouldFindRelevantKnowledgeByKeyword` to see it fail (RED), then implement minimal code to make it pass (GREEN).

Follow the TDD cycle religiously: Red → Green → Refactor for each feature increment.

class KnowledgeService:
    def __init__(self):
        self.knowledge_base_path = Path("knowledge")
        self.knowledge_cache = {}
        self._load_all_knowledge()
    
    def _load_all_knowledge(self):
        """Load all character knowledge into memory for fast access"""
        if not self.knowledge_base_path.exists():
            self.knowledge_base_path.mkdir(parents=True, exist_ok=True)
            self._create_sample_knowledge()
        
        for character_dir in self.knowledge_base_path.iterdir():
            if character_dir.is_dir():
                knowledge_file = character_dir / "knowledge.json"
                if knowledge_file.exists():
                    with open(knowledge_file, 'r', encoding='utf-8') as f:
                        self.knowledge_cache[character_dir.name] = json.load(f)
    
    def search_relevant_knowledge(
        self, 
        query: str, 
        character_id: str, 
        max_results: int = 3
    ) -> List[Dict]:
        """Search for relevant knowledge based on user query"""
        
        if character_id not in self.knowledge_cache:
            return []
        
        character_knowledge = self.knowledge_cache[character_id]
        knowledge_items = character_knowledge.get("knowledge_items", [])
        
        # Score each knowledge item
        scored_items = []
        query_lower = query.lower()
        
        for item in knowledge_items:
            score = 0
            
            # Check trigger keywords (highest weight)
            for keyword in item.get("trigger_keywords", []):
                if keyword.lower() in query_lower:
                    score += 10
            
            # Check tags (medium weight)
            for tag in item.get("tags", []):
                if tag.lower() in query_lower:
                    score += 5
            
            # Check title (low weight)
            if item.get("title", "").lower() in query_lower:
                score += 3
            
            # Check content (lowest weight)
            if any(word in item.get("content", "").lower() 
                   for word in query_lower.split()):
                score += 1
            
            # Apply priority multiplier
            score *= item.get("priority", 1)
            
            if score > 0:
                scored_items.append((score, item))
        
        # Sort by score and return top results
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        results = [item for score, item in scored_items[:max_results]]
        
        # Update usage count
        for item in results:
            item["usage_count"] = item.get("usage_count", 0) + 1
        
        # Save updated counts (async in production)
        self._save_knowledge(character_id, character_knowledge)
        
        return results
    
    def add_knowledge(self, character_id: str, knowledge_item: Dict) -> bool:
        """Add new knowledge item"""
        if character_id not in self.knowledge_cache:
            self.knowledge_cache[character_id] = {
                "character_id": character_id,
                "version": "1.0",
                "knowledge_items": []
            }
        
        # Generate ID
        import uuid
        knowledge_item["id"] = f"k_{uuid.uuid4().hex[:8]}"
        knowledge_item["created_at"] = datetime.now().isoformat()
        
        self.knowledge_cache[character_id]["knowledge_items"].append(knowledge_item)
        return self._save_knowledge(character_id, self.knowledge_cache[character_id])
    
    def _save_knowledge(self, character_id: str, knowledge_data: Dict) -> bool:
        """Save knowledge to JSON file"""
        character_dir = self.knowledge_base_path / character_id
        character_dir.mkdir(parents=True, exist_ok=True)
        
        knowledge_file = character_dir / "knowledge.json"
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
        return True
    
    def _create_sample_knowledge(self):
        """Create sample knowledge for demo characters"""
        samples = {
            "yoon_ahri": {
                "character_id": "yoon_ahri",
                "knowledge_items": [
                    {
                        "id": "k_001",
                        "type": "text",
                        "title": "ASMR 트리거 종류",
                        "content": "탭핑, 브러싱, 페이지 넘기기, 물소리 등 다양한 ASMR 트리거가 있습니다.",
                        "tags": ["ASMR", "트리거"],
                        "trigger_keywords": ["ASMR", "소리", "트리거"],
                        "priority": 1
                    }
                ]
            },
            "taepung": {
                "character_id": "taepung",
                "knowledge_items": [
                    {
                        "id": "k_001",
                        "type": "text",
                        "title": "논증의 기본 구조",
                        "content": "주장-근거-예시의 3단 구조로 논리적 주장을 전개합니다.",
                        "tags": ["논증", "토론"],
                        "trigger_keywords": ["논리", "주장", "근거", "토론"],
                        "priority": 1
                    }
                ]
            },
            "park_hyun": {
                "character_id": "park_hyun",
                "knowledge_items": [
                    {
                        "id": "k_001",
                        "type": "text",
                        "title": "분노 표출의 건강한 방법",
                        "content": "운동, 일기쓰기, 명상 등으로 분노를 건강하게 표출할 수 있습니다.",
                        "tags": ["분노", "감정"],
                        "trigger_keywords": ["화", "분노", "스트레스", "짜증"],
                        "priority": 1
                    }
                ]
            }
        }
        
        for char_id, knowledge in samples.items():
            self._save_knowledge(char_id, knowledge)

# Initialize service
knowledge_service = KnowledgeService()
```

### Step 2: API Endpoints (30 min)

```python
# Add to backend_clean/main.py

from services.knowledge_service import knowledge_service

@app.get("/api/knowledge/{character_id}")
async def get_character_knowledge(character_id: str):
    """Get all knowledge for a character"""
    knowledge = knowledge_service.knowledge_cache.get(character_id, {})
    return {
        "character_id": character_id,
        "knowledge_items": knowledge.get("knowledge_items", []),
        "total": len(knowledge.get("knowledge_items", []))
    }

@app.post("/api/knowledge/{character_id}/search")
async def search_knowledge(character_id: str, request: dict):
    """Search relevant knowledge for a query"""
    query = request.get("query", "")
    max_results = request.get("max_results", 3)
    
    results = knowledge_service.search_relevant_knowledge(
        query, character_id, max_results
    )
    
    return {
        "query": query,
        "results": results,
        "count": len(results)
    }

@app.post("/api/knowledge/{character_id}/add")
async def add_knowledge(character_id: str, knowledge_item: dict):
    """Add new knowledge item"""
    success = knowledge_service.add_knowledge(character_id, knowledge_item)
    return {"success": success}

# Modify existing chat endpoint to include knowledge
@app.post("/api/chat")
async def chat(request: ChatRequest):
    # ... existing code ...
    
    # Search for relevant knowledge
    relevant_knowledge = knowledge_service.search_relevant_knowledge(
        request.message,
        request.character_id,
        max_results=2
    )
    
    # Add to system prompt if knowledge found
    if relevant_knowledge:
        knowledge_context = "\n\n<available_knowledge>\n"
        for item in relevant_knowledge:
            knowledge_context += f"- {item['title']}: {item['content']}\n"
        knowledge_context += "</available_knowledge>\n"
        knowledge_context += "위 지식을 참고하여 답변하되, 자연스럽게 대화에 녹여내세요."
        
        # Append to system prompt
        system_prompt += knowledge_context
    
    # ... rest of chat logic ...
```

### Step 3: Frontend UI Components (2 hours)

```typescript
// frontend/src/app/characters/[id]/knowledge/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Plus, Search, Tag, Edit, Trash } from 'lucide-react'

interface KnowledgeItem {
  id: string
  type: string
  title: string
  content: string
  tags: string[]
  trigger_keywords: string[]
  priority: number
  usage_count?: number
}

export default function KnowledgePage() {
  const params = useParams()
  const characterId = params.id as string
  const [knowledge, setKnowledge] = useState<KnowledgeItem[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [isAddingNew, setIsAddingNew] = useState(false)
  
  useEffect(() => {
    loadKnowledge()
  }, [characterId])
  
  const loadKnowledge = async () => {
    const response = await fetch(`/api/knowledge/${characterId}`)
    const data = await response.json()
    setKnowledge(data.knowledge_items || [])
  }
  
  const addKnowledge = async (item: Partial<KnowledgeItem>) => {
    const response = await fetch(`/api/knowledge/${characterId}/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(item)
    })
    
    if (response.ok) {
      loadKnowledge()
      setIsAddingNew(false)
    }
  }
  
  const filteredKnowledge = knowledge.filter(item =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.tags.some(tag => tag.includes(searchTerm))
  )
  
  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-2xl font-bold mb-4">Knowledge Base</h1>
      
      {/* Search Bar */}
      <div className="flex gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search knowledge..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button onClick={() => setIsAddingNew(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Knowledge
        </Button>
      </div>
      
      {/* Knowledge List */}
      <div className="space-y-4">
        {filteredKnowledge.map(item => (
          <Card key={item.id} className="p-4">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold">{item.title}</h3>
              <div className="flex gap-2">
                <Button size="sm" variant="ghost">
                  <Edit className="h-4 w-4" />
                </Button>
                <Button size="sm" variant="ghost">
                  <Trash className="h-4 w-4" />
                </Button>
              </div>
            </div>
            
            <p className="text-sm text-gray-600 mb-2">{item.content}</p>
            
            <div className="flex flex-wrap gap-1">
              {item.tags.map(tag => (
                <span key={tag} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                  {tag}
                </span>
              ))}
            </div>
            
            {item.usage_count !== undefined && (
              <p className="text-xs text-gray-400 mt-2">
                Used {item.usage_count} times
              </p>
            )}
          </Card>
        ))}
      </div>
      
      {/* Add New Knowledge Modal/Form */}
      {isAddingNew && (
        <KnowledgeEditor
          onSave={addKnowledge}
          onCancel={() => setIsAddingNew(false)}
        />
      )}
    </div>
  )
}
```

## 🧪 Testing Plan

### 1. Create Test Knowledge
```bash
# Create knowledge directories
mkdir -p backend_clean/knowledge/{yoon_ahri,taepung,park_hyun}

# Test API
curl http://localhost:8000/api/knowledge/yoon_ahri
```

### 2. Test Knowledge Search
```bash
# Test search
curl -X POST http://localhost:8000/api/knowledge/yoon_ahri/search \
  -H "Content-Type: application/json" \
  -d '{"query": "ASMR"}'
```

### 3. Test Chat Integration
Send a message that triggers knowledge:
- "ASMR이 뭐예요?" → Should retrieve ASMR knowledge
- "스트레스 받아요" → Should retrieve stress management tips

## 📈 Performance Metrics

### Expected Performance
- Knowledge loading: <10ms (in-memory cache)
- Search time: <5ms for 100 items
- Memory usage: ~1MB per 1000 knowledge items
- No database latency
- Zero external dependencies

## 🚀 Next Steps

1. **Implement image support** in knowledge items
2. **Add knowledge analytics** dashboard
3. **Export/Import** knowledge as JSON
4. **Version control** for knowledge updates
5. **Multi-language** knowledge support

## 💡 Pro Tips

1. **Keep knowledge items focused** - One concept per item
2. **Use specific trigger keywords** - Better matching
3. **Prioritize frequently used items** - Set higher priority
4. **Regular cleanup** - Remove unused knowledge
5. **Backup JSON files** - Simple copy/paste backup

This implementation requires NO database and can be built today! All data is stored in JSON files and cached in memory for ultra-fast access.