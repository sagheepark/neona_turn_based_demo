# Voice Character Chat 프로젝트 요구사항

## 프로젝트 비전
**"텍스트를 넘어선 음성 중심의 감정적 캐릭터 경험"**

기존의 텍스트 기반 캐릭터 챗봇을 넘어, 음성의 뉘앙스, 타이밍, 감정 표현을 통해 실제 대화하는 듯한 몰입감 있는 경험을 제공합니다. 단순한 TTS가 아닌, 컨텍스트를 이해하고 적절한 감정과 타이밍으로 반응하는 '음성 콘텐츠' 생성 시스템입니다.

## 프로젝트 아키텍처

### 시스템 구성
- **Frontend**: Next.js 14 웹앱 (모바일 최적화)
- **Backend**: FastAPI 서버 (Agent Core)
- **Local Storage**: 캐릭터 데이터 관리 (Demo 단계)
- **Future**: PostgreSQL, Redis (Production 단계)

## Phase 1: MVP with Character Management (현재 구현)

### 1. 캐릭터 관리 시스템 (Local Storage)

#### 캐릭터 데이터 구조
```typescript
interface Character {
  id: string
  name: string
  description: string
  image: string | File  // base64 또는 blob URL
  prompt: string        // 완전한 personality + advanced attributes
  voice_id: string      // Typecast voice ID
  created_at: Date
  updated_at: Date
}

// LocalStorage에 저장
const CHARACTERS_KEY = 'voice_chat_characters'
```

#### 캐릭터 리스트 화면
```typescript
// app/characters/page.tsx
// 2 column 그리드 레이아웃
<div className="grid grid-cols-2 gap-4 p-4">
  {characters.map(character => (
    <CharacterCard
      key={character.id}
      character={character}
      onClick={() => router.push(`/chat/${character.id}`)}
    />
  ))}
  
  {/* 새로 만들기 버튼 */}
  <Card className="border-dashed cursor-pointer hover:border-primary">
    <CardContent className="flex flex-col items-center justify-center h-full">
      <Plus className="w-12 h-12 mb-2" />
      <span>새 캐릭터 만들기</span>
    </CardContent>
  </Card>
</div>
```

#### 캐릭터 카드 컴포넌트
```typescript
const CharacterCard = ({ character, onClick }) => (
  <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={onClick}>
    <CardContent className="p-4">
      <div className="aspect-square mb-3 overflow-hidden rounded-lg">
        <img 
          src={character.image} 
          alt={character.name}
          className="w-full h-full object-cover"
        />
      </div>
      <h3 className="font-bold text-lg mb-1">{character.name}</h3>
      <p className="text-sm text-muted-foreground line-clamp-2">
        {character.description}
      </p>
    </CardContent>
  </Card>
)
```

#### 캐릭터 생성 모달/페이지
```typescript
// app/characters/create/page.tsx
const CharacterCreator = () => {
  const [formData, setFormData] = useState<CharacterFormData>({
    name: '',
    description: '',
    image: null,
    personality: '',
    voice_id: '',
    // Advanced fields (optional)
    age: '',
    gender: '',
    role: '',
    backstory: '',
    speaking_style: '',
    scenario: ''
  })
  
  const handleImageUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Convert to base64 for localStorage
      const reader = new FileReader()
      reader.onload = () => {
        setFormData(prev => ({ ...prev, image: reader.result as string }))
      }
      reader.readAsDataURL(file)
    }
  }
  
  const saveCharacter = () => {
    const character: Character = {
      id: generateId(),
      name: formData.name,
      description: formData.description,
      image: formData.image,
      prompt: buildPromptFromFormData(formData),
      voice_id: formData.voice_id,
      created_at: new Date(),
      updated_at: new Date()
    }
    
    // LocalStorage에 저장
    const existing = JSON.parse(localStorage.getItem(CHARACTERS_KEY) || '[]')
    localStorage.setItem(CHARACTERS_KEY, JSON.stringify([...existing, character]))
    
    router.push('/characters')
  }
}
```

### 2. 프론트엔드 구조 업데이트

```
frontend/
  src/
    app/
      page.tsx                    # 리다이렉트 to /characters
      layout.tsx
      
      characters/                 # 캐릭터 관리
        page.tsx                  # 캐릭터 리스트
        create/
          page.tsx               # 캐릭터 생성
        [id]/
          edit/
            page.tsx             # 캐릭터 수정
            
      chat/
        [characterId]/
          page.tsx               # 채팅 화면
          
    components/
      characters/
        CharacterCard.tsx
        CharacterForm.tsx
        CharacterList.tsx
        
      chat/
        ChatContainer.tsx
        CharacterResponseArea.tsx
        UserInputArea.tsx
        InputControls.tsx
        DialogueDisplay.tsx
        
    lib/
      characters.ts              # 캐릭터 관리 로직
      storage.ts                 # LocalStorage 헬퍼
```

### 3. 초기 데모 캐릭터 (프로젝트에 포함)

```typescript
// data/demo-characters.ts
export const DEMO_CHARACTERS: Character[] = [
  {
    id: 'taylor_demo',
    name: 'Taylor',
    description: '친근한 수학 튜터',
    image: '/characters/taylor.png',  // public 폴더에 저장
    prompt: `
      <personality>밝고 친근한 성격의 수학 튜터. 학생들의 실수를 격려하며 긍정적으로 지도합니다.</personality>
      <age>25</age>
      <gender>여성</gender>
      <role>수학 튜터</role>
      <speaking_style>친근한 반말 사용, '~야', '~아' 어미 활용</speaking_style>
      <backstory>대학에서 수학을 전공하고 과외 경험이 풍부한 튜터</backstory>
    `,
    voice_id: 'typecast_taylor_kr_001',
    created_at: new Date('2024-01-01'),
    updated_at: new Date('2024-01-01')
  },
  // ... 더 많은 데모 캐릭터
]

// 앱 초기 로드 시 데모 캐릭터 확인 및 추가
const initializeDemoCharacters = () => {
  const existing = localStorage.getItem(CHARACTERS_KEY)
  if (!existing) {
    localStorage.setItem(CHARACTERS_KEY, JSON.stringify(DEMO_CHARACTERS))
  }
}
```

## Phase 2: TTS Integration & Basic Voice Synthesis

### Typecast API 연동
- 기본 TTS 생성
- 감정 파라미터 적용
- 속도 조절
- Word-level timestamp 수신

## Phase 3: Advanced Audio Agent System (핵심 차별화)

### 3.1 음성 콘텐츠 생성 파이프라인

이 단계가 이 프로젝트의 핵심 차별화 포인트입니다. 단순 TTS를 넘어 '음성 연출'을 통해 실제 대화같은 경험을 만듭니다.

#### Audio Content Director (백엔드 서비스)
```python
class AudioContentDirector:
    """
    LLM 응답을 받아 '음성 콘텐츠'로 변환하는 핵심 엔진
    영화 사운드 디렉터처럼 음성을 연출합니다.
    """
    
    def analyze_context(self, dialogue: str, conversation_history: List) -> AudioDirection:
        """
        대화 컨텍스트 분석하여 음성 연출 방향 결정
        - 긴장감 있는 상황인지
        - 친밀한 대화인지
        - 설명이 필요한 상황인지
        """
        
    def generate_prosody_map(self, dialogue: str, emotion: str) -> ProsodyMap:
        """
        문장별, 구간별 세밀한 감정/속도 매핑
        예: "아... [pause:0.5] 그게 말이야, [speed:0.9] 사실은..."
        """
        
    def create_audio_timeline(self, tts_segments: List[AudioSegment]) -> AudioTimeline:
        """
        여러 TTS 세그먼트를 타임라인에 배치
        - 자연스러운 호흡 pause 삽입
        - 감정 전환 구간 설정
        - 중요 단어 강조 (볼륨/속도 조절)
        """
        
    def apply_audio_effects(self, timeline: AudioTimeline) -> ProcessedAudio:
        """
        음성 후처리 효과 적용
        - 생각하는 듯한 'um', 'uh' 삽입
        - 웃음, 한숨 같은 비언어적 사운드
        - 거리감 조절 (가까이/멀리)
        """
```

#### 음성 연출 기법들

1. **Dynamic Pacing (동적 속도 조절)**
   ```python
   # 예시: 중요한 정보는 천천히, 부가 설명은 빠르게
   if is_important_info(segment):
       speed = 0.85
   elif is_side_comment(segment):
       speed = 1.15
   ```

2. **Emotional Transitions (감정 전환)**
   ```python
   # 한 대사 내에서도 감정 변화
   "어? [surprised] 정말? [excited] 와, 대단한데! [happy]"
   ```

3. **Natural Interruptions (자연스러운 끊김)**
   ```python
   # 생각하면서 말하는 효과
   original: "그건 아마도 이런 이유 때문일 거야"
   processed: "그건... 음, 아마도 이런 이유 때문일 거야"
   ```

4. **Overlapping & Layering**
   ```python
   # 여러 음성 트랙 동시 재생 (미래 멀티캐릭터용)
   track1: main_dialogue
   track2: background_murmur
   track3: thinking_voice (작은 소리로)
   ```

5. **Contextual Silence (맥락적 침묵)**
   ```python
   # 상황에 따른 침묵 활용
   if user_said_something_shocking:
       insert_pause(duration=1.5)  # 놀란 침묵
   elif waiting_for_user_think:
       insert_pause(duration=0.8)  # 기다리는 침묵
   ```

### 3.2 실시간 음성 스트리밍 아키텍처

```python
class AudioStreamingService:
    """
    WebSocket을 통한 실시간 음성 스트리밍
    """
    
    async def stream_audio_chunks(self, session_id: str):
        # LLM이 텍스트 생성하는 동안
        # 완성된 문장 단위로 즉시 TTS 생성 시작
        # 클라이언트로 청크 단위 스트리밍
        
    async def adaptive_buffering(self, network_speed: float):
        # 네트워크 상황에 따른 버퍼링 조절
        # 끊김 없는 재생 보장
```

### 3.3 음성 경험 고도화 요소

#### Personality-Driven Voice Modulation
```python
# 캐릭터 성격에 따른 음성 스타일 자동 조절
shy_character = {
    'base_speed': 0.95,
    'volume_variance': 0.1,  # 작은 목소리
    'pause_frequency': 'high',  # 자주 머뭇거림
    'filler_words': ['음...', '그...', '어...']
}

confident_character = {
    'base_speed': 1.05,
    'volume_variance': 0.3,  # 강약 조절 활발
    'pause_frequency': 'low',
    'filler_words': []  # 필러 없이 명확하게
}
```

#### Conversational Memory in Audio
```python
# 이전 대화 내용을 음성적으로 참조
if mentioned_before(topic):
    # 톤을 바꿔서 "아까 얘기한 것처럼..." 느낌 전달
    adjust_tone(familiarity=0.8)
```

## Phase 4: Multi-Modal Integration

### 립싱크 준비 단계
- Phoneme-level timestamp 추출
- Viseme 매핑 테이블 구축
- 감정별 표정 프리셋

### 제스처 생성 (Future)
```python
class GestureGenerator:
    """
    음성에 맞는 자연스러운 제스처 생성
    """
    def analyze_speech_intent(self, text: str) -> GestureType:
        # 설명 → 손짓
        # 질문 → 고개 기울임
        # 강조 → 손 제스처
```

## Phase 5: Production & Scaling

### 성능 최적화
1. **Audio Processing Pipeline**
   - GPU 가속 음성 처리
   - 병렬 TTS 생성
   - 캐싱 전략 (자주 쓰는 구문)

2. **Predictive Generation**
   ```python
   # 사용자가 타이핑하는 동안 예상 응답 미리 생성
   while user_typing:
       predict_likely_responses()
       pre_generate_tts_candidates()
   ```

### 분석 및 개선
```python
class AudioExperienceAnalytics:
    """
    음성 경험 품질 측정 및 개선
    """
    
    def track_engagement(self):
        # 사용자가 끝까지 들었는지
        # skip한 구간이 있는지
        # 반복 재생한 부분이 있는지
        
    def optimize_timing(self):
        # A/B 테스트로 최적 pause 길이 찾기
        # 감정 전환 타이밍 최적화
```

## 기술적 고려사항

### 왜 이 접근이 혁신적인가?

1. **기존 TTS의 한계**
   - 단조로운 톤
   - 맥락 무시한 일률적 속도
   - 감정 표현 부족

2. **우리의 차별화**
   - 컨텍스트 기반 음성 연출
   - 실시간 감정 변화
   - 자연스러운 대화 리듬

3. **사용자 경험 향상**
   - 더 오래 듣게 됨 (engaging)
   - 감정적 연결 강화
   - 실제 대화같은 자연스러움

### 개발 우선순위 제안

1. **Phase 1 (1-2주)**
   - 기본 채팅 + 캐릭터 관리
   - LocalStorage 기반 데모

2. **Phase 2 (1주)**
   - Typecast 기본 연동
   - 단순 TTS 재생

3. **Phase 3 (2-3주) - 핵심**
   - Audio Content Director 구현
   - 음성 연출 파이프라인
   - 이 단계가 제품의 핵심 가치

4. **Phase 4+ (장기)**
   - 시각적 요소 추가
   - 스케일링

## 비즈니스 임팩트

### 잠재 사용 사례
1. **교육**: 더 engaging한 AI 튜터
2. **엔터테인먼트**: 인터랙티브 오디오 드라마
3. **mental wellness**: 공감적 대화 파트너
4. **게임**: NPC 음성 대화 시스템

### 수익 모델 가능성
1. **B2C**: 프리미엄 캐릭터/음성 팩
2. **B2B**: API 제공 (게임사, 교육 플랫폼)
3. **Content Creation**: 음성 콘텐츠 제작 툴

이 비전대로라면 단순한 "말하는 챗봇"이 아닌, "음성으로 소통하는 디지털 존재"를 만드는 것입니다.