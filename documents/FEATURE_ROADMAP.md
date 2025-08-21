# 음성 캐릭터 챗 - 기능 개발 로드맵

## 📋 개발 우선순위 및 일정

### Phase 0: 목소리 선택 및 추천 시스템 (1주차) ⭐ 최우선
캐릭터 생성의 핵심 UX 개선

### Phase 1: 사용자 Persona 시스템 (2주차)
사용자 맞춤형 대화 경험 제공

### Phase 2: Knowledge Base 시스템 (3-4주차)
캐릭터별 지식 저장소 구축

### Phase 3: 장기 기억 시스템 (5-6주차)
대화 연속성 및 관계 발전

---

## 🎯 Phase 0: 목소리 선택 및 추천 시스템 (최우선 구현)

### 1. 목소리 선택 UI 구현

#### 1.1 Backend - 목소리 리스트 API 활용
```python
# backend_clean/main.py (기존 endpoint 활용)
@app.get("/api/voices")
async def get_voices():
    # 이미 구현되어 있음
    return tts_service.get_available_voices()

@app.get("/api/voices/korean")
async def get_korean_voices():
    # 한국어 목소리만 필터링
    return [v for v in voices if v.language == "ko-KR"]
```

#### 1.2 Frontend - 목소리 선택 컴포넌트
```typescript
// frontend/src/components/characters/VoiceSelector.tsx
interface VoiceSelectorProps {
  selectedVoiceId?: string
  onSelect: (voiceId: string) => void
}

const VoiceSelector: React.FC<VoiceSelectorProps> = ({ selectedVoiceId, onSelect }) => {
  const [voices, setVoices] = useState<Voice[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [previewingVoiceId, setPreviewingVoiceId] = useState<string | null>(null)
  const [audioCache, setAudioCache] = useState<Map<string, string>>(new Map())

  // 목소리 리스트 불러오기
  useEffect(() => {
    fetch('/api/voices/korean')
      .then(res => res.json())
      .then(setVoices)
  }, [])

  // 목소리 미리듣기
  const previewVoice = async (voiceId: string) => {
    // 캐시 확인
    if (audioCache.has(voiceId)) {
      playAudio(audioCache.get(voiceId)!)
      return
    }

    // 샘플 음성 생성
    const response = await fetch('/api/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: "This is my voice",
        voice_id: voiceId,
        emotion: "neutral"
      })
    })

    const data = await response.json()
    
    // 캐시 저장
    audioCache.set(voiceId, data.audio_base64)
    
    // 재생
    playAudio(data.audio_base64)
  }

  return (
    <div className="relative">
      <Button onClick={() => setIsOpen(!isOpen)} variant="outline" className="w-full">
        {selectedVoiceId ? 
          voices.find(v => v.id === selectedVoiceId)?.name || '목소리 선택' : 
          '목소리 선택'}
        <ChevronDown className="ml-2 h-4 w-4" />
      </Button>

      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-white border rounded-lg shadow-lg max-h-96 overflow-y-auto">
          {voices.map(voice => (
            <div 
              key={voice.id} 
              className="flex items-center justify-between p-3 hover:bg-gray-50 cursor-pointer"
            >
              <div 
                className="flex-1"
                onClick={() => {
                  onSelect(voice.id)
                  setIsOpen(false)
                }}
              >
                <div className="font-medium">{voice.name}</div>
                <div className="text-sm text-gray-500">{voice.gender} · {voice.age}대</div>
              </div>
              
              <Button
                size="sm"
                variant="ghost"
                onClick={(e) => {
                  e.stopPropagation()
                  previewVoice(voice.id)
                }}
              >
                {previewingVoiceId === voice.id ? (
                  <Pause className="h-4 w-4" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

### 2. 목소리 추천 시스템

#### 2.1 Backend - 추천 API 연동
```python
# backend_clean/services/voice_recommend_service.py
import requests
from typing import List, Dict

class VoiceRecommendService:
    def __init__(self):
        self.base_url = "https://neona-voice-recommend-dev.z2.neosapience.xyz"
    
    async def recommend_voice(self, character_prompt: str) -> List[Dict]:
        """
        캐릭터 프롬프트를 기반으로 적합한 목소리 추천
        """
        response = requests.post(
            f"{self.base_url}/recommend",
            json={
                "text": character_prompt,
                "top_k": 5  # 상위 5개 추천
            }
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            return recommendations
        return []

# backend_clean/main.py
@app.post("/api/voices/recommend")
async def recommend_voices(request: VoiceRecommendRequest):
    """캐릭터 설명 기반 목소리 추천"""
    recommendations = await voice_recommend_service.recommend_voice(
        request.character_prompt
    )
    return recommendations
```

#### 2.2 Frontend - 추천 기능 UI
```typescript
// frontend/src/components/characters/VoiceRecommendation.tsx
interface VoiceRecommendationProps {
  characterPrompt: string
  onSelectVoice: (voiceId: string) => void
}

const VoiceRecommendation: React.FC<VoiceRecommendationProps> = ({ 
  characterPrompt, 
  onSelectVoice 
}) => {
  const [recommendations, setRecommendations] = useState<VoiceRecommendation[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const getRecommendations = async () => {
    if (!characterPrompt) {
      alert('캐릭터 설명을 먼저 입력해주세요')
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch('/api/voices/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ character_prompt: characterPrompt })
      })
      
      const data = await response.json()
      setRecommendations(data)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <Button 
        onClick={getRecommendations}
        disabled={isLoading || !characterPrompt}
        className="w-full"
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            추천받는 중...
          </>
        ) : (
          <>
            <Sparkles className="mr-2 h-4 w-4" />
            AI 목소리 추천받기
          </>
        )}
      </Button>

      {recommendations.length > 0 && (
        <div className="border rounded-lg p-4">
          <h4 className="font-medium mb-3">추천 목소리</h4>
          <div className="space-y-2">
            {recommendations.map((rec, idx) => (
              <div 
                key={rec.voice_id}
                className="flex items-center justify-between p-2 hover:bg-gray-50 rounded"
              >
                <div className="flex items-center gap-3">
                  <div className="text-sm font-medium text-primary">
                    #{idx + 1}
                  </div>
                  <div>
                    <div className="font-medium">{rec.voice_name}</div>
                    <div className="text-sm text-gray-500">
                      매칭률: {(rec.score * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => previewVoice(rec.voice_id)}
                  >
                    <Play className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onSelectVoice(rec.voice_id)}
                  >
                    선택
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
```

### 3. 샘플 음성 캐싱 시스템

```typescript
// frontend/src/lib/voice-cache.ts
class VoicePreviewCache {
  private static STORAGE_KEY = 'voice_preview_cache'
  private cache: Map<string, string>

  constructor() {
    // LocalStorage에서 캐시 로드
    const stored = localStorage.getItem(VoicePreviewCache.STORAGE_KEY)
    this.cache = stored ? new Map(JSON.parse(stored)) : new Map()
  }

  get(voiceId: string): string | null {
    return this.cache.get(voiceId) || null
  }

  set(voiceId: string, audioBase64: string): void {
    this.cache.set(voiceId, audioBase64)
    this.save()
  }

  private save(): void {
    // Map을 배열로 변환하여 저장
    const cacheArray = Array.from(this.cache.entries())
    localStorage.setItem(VoicePreviewCache.STORAGE_KEY, JSON.stringify(cacheArray))
  }

  clear(): void {
    this.cache.clear()
    localStorage.removeItem(VoicePreviewCache.STORAGE_KEY)
  }
}

export const voiceCache = new VoicePreviewCache()
```

---

## 🎤 Phase 1: 사용자 Persona 시스템

### 1. 데이터 구조 설계

```typescript
// frontend/src/types/persona.ts
interface UserPersona {
  id: string
  name: string
  description: string
  avatar?: string
  preferences: {
    speaking_style: 'formal' | 'casual' | 'friendly'
    topics_of_interest: string[]
    background: string
    age?: number
    occupation?: string
  }
  created_at: Date
  updated_at: Date
  is_active: boolean
}
```

### 2. Persona 관리 UI

```typescript
// frontend/src/app/personas/page.tsx
const PersonasPage = () => {
  // Persona 리스트
  // 생성/수정/삭제 기능
  // 활성 Persona 전환
}

// frontend/src/components/personas/PersonaCard.tsx
const PersonaCard = ({ persona, isActive, onActivate, onEdit, onDelete }) => {
  // Persona 카드 UI
  // 활성화 상태 표시
}

// frontend/src/components/personas/PersonaCreator.tsx
const PersonaCreator = () => {
  // Persona 생성 폼
  // 이름, 배경, 관심사 등 입력
}
```

### 3. Backend 통합

```python
# backend_clean/models/persona.py
class UserPersona(BaseModel):
    id: str
    name: str
    description: str
    preferences: Dict[str, Any]
    is_active: bool

# backend_clean/main.py
@app.post("/api/chat")
async def chat(request: ChatRequest):
    # Persona 정보를 시스템 프롬프트에 포함
    if request.user_persona:
        system_prompt += f"""
        <user_context>
        사용자 이름: {request.user_persona.name}
        배경: {request.user_persona.preferences.background}
        관심사: {', '.join(request.user_persona.preferences.topics_of_interest)}
        말투: {request.user_persona.preferences.speaking_style}
        </user_context>
        """
```

---

## 📚 Phase 2: Knowledge Base 시스템

### 1. 초기 구현 (JSON 기반)

```typescript
// frontend/src/data/knowledge/[character_id]/knowledge.json
{
  "character_id": "yoonari_001",
  "knowledge_items": [
    {
      "id": "k001",
      "type": "text",
      "title": "심리상담 기법",
      "content": "적극적 경청의 중요성...",
      "tags": ["상담", "심리학"],
      "trigger_keywords": ["상담", "고민", "도움"]
    },
    {
      "id": "k002",
      "type": "image",
      "title": "명상 가이드",
      "content": "/images/meditation_guide.png",
      "description": "호흡 명상 단계별 가이드",
      "tags": ["명상", "힐링"],
      "trigger_keywords": ["명상", "호흡", "마음"]
    }
  ]
}
```

### 2. Knowledge 검색 및 활용

```python
# backend_clean/services/knowledge_service.py
class KnowledgeService:
    def __init__(self):
        self.knowledge_base = {}
        self.load_knowledge()
    
    def load_knowledge(self):
        # JSON 파일에서 knowledge 로드
        for character_id in os.listdir("./knowledge"):
            with open(f"./knowledge/{character_id}/knowledge.json") as f:
                self.knowledge_base[character_id] = json.load(f)
    
    def search_relevant_knowledge(self, query: str, character_id: str) -> List[Dict]:
        # 키워드 매칭으로 관련 지식 검색
        character_knowledge = self.knowledge_base.get(character_id, {})
        relevant = []
        
        for item in character_knowledge.get("knowledge_items", []):
            # 트리거 키워드 확인
            for keyword in item.get("trigger_keywords", []):
                if keyword in query:
                    relevant.append(item)
                    break
        
        return relevant

# backend_clean/main.py
@app.post("/api/chat")
async def chat(request: ChatRequest):
    # 관련 지식 검색
    relevant_knowledge = knowledge_service.search_relevant_knowledge(
        request.message, 
        request.character_id
    )
    
    if relevant_knowledge:
        system_prompt += f"""
        <available_knowledge>
        {json.dumps(relevant_knowledge, ensure_ascii=False)}
        </available_knowledge>
        
        사용자의 질문과 관련된 지식이 있다면 활용하여 답변하세요.
        """
```

### 3. Knowledge 관리 UI

```typescript
// frontend/src/app/characters/[id]/knowledge/page.tsx
const CharacterKnowledgePage = ({ params }) => {
  // Knowledge 리스트
  // 추가/수정/삭제 기능
  // 이미지 업로드
  // 트리거 키워드 관리
}
```

---

## 💾 Phase 3: 장기 기억 시스템

### 1. 데이터베이스 스키마

```sql
-- PostgreSQL 스키마
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255),
    character_id VARCHAR(255),
    session_id VARCHAR(255),
    messages JSONB,
    summary TEXT,
    key_facts JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE user_facts (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255),
    character_id VARCHAR(255),
    fact_type VARCHAR(50), -- 'preference', 'personal_info', 'history'
    fact_content TEXT,
    confidence FLOAT,
    created_at TIMESTAMP,
    last_mentioned TIMESTAMP
);

CREATE INDEX idx_user_character ON conversations(user_id, character_id);
CREATE INDEX idx_user_facts ON user_facts(user_id, character_id);
```

### 2. Memory Service 구현

```python
# backend_clean/services/memory_service.py
from typing import List, Dict
import asyncpg
from openai import AsyncOpenAI

class LongTermMemoryService:
    def __init__(self):
        self.db_pool = None
        self.openai = AsyncOpenAI()
    
    async def initialize(self):
        self.db_pool = await asyncpg.create_pool(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST")
        )
    
    async def save_conversation(self, user_id: str, character_id: str, messages: List[Dict]):
        # 대화 요약 생성
        summary = await self.generate_summary(messages)
        
        # 주요 사실 추출
        key_facts = await self.extract_key_facts(messages, user_id)
        
        async with self.db_pool.acquire() as conn:
            # 대화 저장
            await conn.execute("""
                INSERT INTO conversations (user_id, character_id, messages, summary, key_facts, created_at)
                VALUES ($1, $2, $3, $4, $5, NOW())
            """, user_id, character_id, json.dumps(messages), summary, json.dumps(key_facts))
            
            # 사용자 사실 업데이트
            for fact in key_facts:
                await self.update_user_fact(conn, user_id, character_id, fact)
    
    async def generate_summary(self, messages: List[Dict]) -> str:
        # GPT를 사용한 대화 요약
        prompt = f"""
        다음 대화를 2-3문장으로 요약해주세요:
        {json.dumps(messages, ensure_ascii=False)}
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        
        return response.choices[0].message.content
    
    async def extract_key_facts(self, messages: List[Dict], user_id: str) -> List[Dict]:
        # 대화에서 사용자에 대한 주요 정보 추출
        prompt = f"""
        다음 대화에서 사용자({user_id})에 대한 중요한 정보를 추출해주세요.
        예: 취미, 선호도, 개인 정보, 경험 등
        
        JSON 형식으로 반환:
        [
            {{"type": "preference", "content": "커피를 좋아함"}},
            {{"type": "personal_info", "content": "서울에 거주"}}
        ]
        
        대화: {json.dumps(messages, ensure_ascii=False)}
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def get_relevant_memories(self, user_id: str, character_id: str, context: str) -> Dict:
        async with self.db_pool.acquire() as conn:
            # 최근 대화 요약
            recent_convos = await conn.fetch("""
                SELECT summary, created_at 
                FROM conversations 
                WHERE user_id = $1 AND character_id = $2 
                ORDER BY created_at DESC 
                LIMIT 5
            """, user_id, character_id)
            
            # 사용자 사실
            user_facts = await conn.fetch("""
                SELECT fact_type, fact_content, confidence 
                FROM user_facts 
                WHERE user_id = $1 AND character_id = $2 
                ORDER BY confidence DESC, last_mentioned DESC
                LIMIT 10
            """, user_id, character_id)
            
            return {
                "recent_conversations": [dict(r) for r in recent_convos],
                "user_facts": [dict(r) for r in user_facts],
                "relationship_duration": await self.get_relationship_duration(conn, user_id, character_id)
            }
    
    async def get_relationship_duration(self, conn, user_id: str, character_id: str) -> str:
        first_convo = await conn.fetchval("""
            SELECT MIN(created_at) 
            FROM conversations 
            WHERE user_id = $1 AND character_id = $2
        """, user_id, character_id)
        
        if first_convo:
            days = (datetime.now() - first_convo).days
            if days == 0:
                return "오늘 처음 만남"
            elif days < 7:
                return f"{days}일 전부터 대화"
            elif days < 30:
                return f"{days // 7}주 전부터 대화"
            else:
                return f"{days // 30}개월 전부터 대화"
        
        return "처음 만남"
```

### 3. Frontend 메모리 상태 표시

```typescript
// frontend/src/components/chat/MemoryIndicator.tsx
const MemoryIndicator = ({ userId, characterId }) => {
  const [memoryStats, setMemoryStats] = useState({
    conversationCount: 0,
    relationshipDuration: '',
    knownFacts: 0
  })

  useEffect(() => {
    // 메모리 통계 로드
    fetch(`/api/memory/stats?user_id=${userId}&character_id=${characterId}`)
      .then(res => res.json())
      .then(setMemoryStats)
  }, [userId, characterId])

  return (
    <div className="text-xs text-gray-500 p-2 bg-gray-50 rounded">
      <div className="flex items-center gap-2">
        <Brain className="h-3 w-3" />
        <span>{memoryStats.relationshipDuration}</span>
        <span>·</span>
        <span>{memoryStats.conversationCount}번의 대화</span>
        <span>·</span>
        <span>{memoryStats.knownFacts}개의 기억</span>
      </div>
    </div>
  )
}
```

---

## 📅 구현 일정 및 우선순위

### 🚀 즉시 시작 (1주차)
**Phase 0: 목소리 선택 및 추천 시스템**
- Day 1-2: 목소리 선택 UI 구현
  - VoiceSelector 컴포넌트
  - 목소리 미리듣기 기능
  - 샘플 음성 캐싱
- Day 3-4: 목소리 추천 API 연동
  - 추천 서비스 백엔드 연결
  - 추천 결과 UI
- Day 5: 테스트 및 개선

### 📝 2주차
**Phase 1: 사용자 Persona 시스템**
- Day 1-2: Persona 데이터 모델 및 저장소
- Day 3-4: Persona 관리 UI
- Day 5: Backend 통합 및 테스트

### 📚 3-4주차
**Phase 2: Knowledge Base 시스템**
- Week 3: JSON 기반 초기 구현
- Week 4: 검색 및 활용 로직

### 💾 5-6주차
**Phase 3: 장기 기억 시스템**
- Week 5: PostgreSQL 설정 및 스키마
- Week 6: Memory Service 구현 및 통합

---

## 🎯 성공 지표

### Phase 0 (목소리 시스템)
- [ ] 사용자가 10개 이상의 목소리 중 선택 가능
- [ ] 각 목소리 3초 내 미리듣기 가능
- [ ] AI 추천 정확도 70% 이상

### Phase 1 (Persona)
- [ ] 멀티 Persona 생성/전환 가능
- [ ] 캐릭터가 Persona 정보 인지하여 대화

### Phase 2 (Knowledge Base)
- [ ] 캐릭터별 10개 이상 지식 저장
- [ ] 관련 지식 자동 활용률 80% 이상

### Phase 3 (장기 기억)
- [ ] 이전 대화 내용 참조 가능
- [ ] 사용자 선호도 학습 및 반영

---

## 🔧 기술 스택 요약

### Frontend
- Next.js 14 (기존)
- TypeScript
- Tailwind CSS
- LocalStorage → IndexedDB (Phase 2)

### Backend
- FastAPI (기존)
- Azure OpenAI (기존)
- Typecast TTS (기존)
- PostgreSQL (Phase 3)
- Redis (Phase 3, 선택사항)

### 외부 API
- Typecast TTS API (기존)
- Neona Voice Recommend API (Phase 0)

---

## 📌 다음 단계

1. **즉시**: 목소리 선택 UI 컴포넌트 개발 시작
2. **이번 주**: 목소리 추천 API 연동 완료
3. **다음 주**: 사용자 Persona 시스템 설계 및 구현

이 로드맵을 따라 단계적으로 구현하면, 각 Phase마다 즉시 가치를 제공하면서 점진적으로 시스템을 고도화할 수 있습니다.