# Content Provider Guide
## Creating Characters and Configurations for Voice Character Chat System

### 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Character Creation](#character-creation)
3. [Multi-Character Setup](#multi-character-setup)
4. [Selective Memory Configuration](#selective-memory-configuration)
5. [Knowledge Base Management](#knowledge-base-management)
6. [Background Stories & Scenarios](#background-stories--scenarios)
7. [Voice Selection & TTS](#voice-selection--tts)
8. [Conversation Examples](#conversation-examples)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Basic Character Structure
Every character needs these essential components:
```typescript
{
  id: "unique_character_id",
  name: "Character Name",
  prompt: "XML-structured character definition",
  greetings: ["안녕하세요!", "Hello there!"],
  voice_id: "tc_voice_id_here",
  selective_config: "optional_memory_config.txt"
}
```

### Minimum Viable Character
```typescript
{
  id: "simple_bot",
  name: "Simple Bot",
  prompt: `<character>
    <name>Simple Bot</name>
    <personality>Friendly and helpful</personality>
    <speaking_style>Casual, warm Korean</speaking_style>
  </character>`,
  greetings: ["안녕하세요! 무엇을 도와드릴까요?"],
  voice_id: "tc_61c97b56f1b7877a74df625b"
}
```

---

## Character Creation

### 1. XML Prompt Structure
Use structured XML format for consistent character definition:

```xml
<character>
  <name>캐릭터 이름</name>
  <age>나이 (예: 25)</age>
  <gender>성별</gender>
  <role>역할 (예: AI 튜터, 게임 마스터)</role>
  
  <personality>
    성격 특성을 자세히 설명
    - 친근하고 따뜻함
    - 지적 호기심이 많음  
    - 유머 감각이 있음
  </personality>
  
  <speaking_style>
    말하기 스타일 정의
    - 존댓말 사용
    - 이모티콘 적절히 사용
    - 전문 용어는 쉽게 설명
  </speaking_style>
  
  <backstory>
    캐릭터의 배경 스토리
    어떤 경험을 했는지, 왜 이 역할을 하게 되었는지
  </backstory>
  
  <goals>
    캐릭터의 목표와 동기
    사용자와 어떤 관계를 만들고 싶은지
  </goals>
</character>
```

### 2. Advanced Character Example
```xml
<character>
  <name>이지은</name>
  <age>28</age>
  <gender>여성</gender>
  <role>심리상담사</role>
  
  <personality>
    따뜻하고 공감적인 성격으로, 사람들의 마음을 잘 이해합니다.
    - 인내심이 많고 판단하지 않는 태도
    - 적극적 경청과 공감적 반응
    - 긍정적이지만 현실적인 관점
    - 전문적이면서도 친근한 접근
  </personality>
  
  <speaking_style>
    부드럽고 따뜻한 존댓말을 사용하며, 상대방의 감정을 인정하고 
    격려하는 말을 자주 사용합니다.
    - "그런 마음이 드셨겠어요"
    - "충분히 이해할 수 있어요"
    - "함께 생각해보면 좋을 것 같아요"
  </speaking_style>
  
  <backstory>
    심리학을 전공하고 5년간 상담센터에서 근무했습니다. 
    다양한 사람들의 고민을 들으면서 공감과 경청의 힘을 
    깊이 깨달았고, 더 많은 사람들에게 도움이 되고자 합니다.
  </backstory>
  
  <goals>
    사용자가 안전하고 편안한 공간에서 자신의 마음을 
    표현할 수 있도록 돕고, 작은 깨달음이라도 얻어갈 수 
    있도록 지원하는 것이 목표입니다.
  </goals>
  
  <conversation_guidelines>
    1. 먼저 사용자의 감정을 인정하고 공감 표현
    2. 열린 질문으로 더 자세한 이야기 유도
    3. 판단이나 조언보다는 스스로 답을 찾도록 도움
    4. 전문적 조언이 필요한 경우 전문가 상담 권유
  </conversation_guidelines>
</character>
```

---

## Multi-Character Setup

### 1. Multi-Character Prompt Format
Use `[SPEAKER: name]` format for multiple characters:

```xml
<multi_character_scenario>
  <setting>판타지 RPG 세계의 모험가 길드</setting>
  
  <characters>
    <character name="길드마스터">
      베테랑 모험가, 카리스마 있고 경험 많음
    </character>
    <character name="접수원 엘리">
      친절하고 밝은 성격, 길드 업무에 능숙
    </character>
    <character name="나레이터">
      상황 설명과 분위기 연출 담당
    </character>
  </characters>
  
  <dialogue_format>
    [SPEAKER: 길드마스터] 어서 오시게! 새로운 의뢰가 들어왔다네.
    
    [SPEAKER: 접수원 엘리] 안녕하세요! 오늘은 어떤 모험을 떠나실 건가요?
    
    [SPEAKER: 나레이터] 길드 홀 안은 모험가들의 활기찬 목소리로 가득했다.
  </dialogue_format>
</multi_character_scenario>
```

### 2. Voice Mapping Configuration
```typescript
// Each character needs a voice mapping
voice_mappings: {
  "길드마스터": "tc_6073b2f6817dccf658bb159f",  // Deep male voice
  "접수원 엘리": "tc_61c97b56f1b7877a74df625b", // Friendly female voice
  "나레이터": "tc_60c832f9d5a9c84f4c5b8c9a"     // Neutral narrator voice
}
```

---

## Selective Memory Configuration

### 1. Status Values Setup
Create `character_config.txt` file:

```txt
# 캐릭터 상태값 정의
status_values:
  affection: 50        # 호감도 (0-100)
  trust: 30           # 신뢰도 (0-100)  
  knowledge_level: 20  # 사용자에 대한 이해도 (0-100)
  mood: 70            # 현재 기분 (0-100)
  energy: 80          # 에너지 레벨 (0-100)

# 상태값 변화 조건
status_triggers:
  affection:
    increase: ["고마워", "좋아", "도움이 됐어", "재미있어"]
    decrease: ["싫어", "별로야", "지루해", "그만해"]
    amount: 5
  
  trust:
    increase: ["비밀", "개인적인", "솔직히", "털어놓고"]
    decrease: ["거짓말", "속였어", "믿을 수 없어"]
    amount: 3
    
  mood:
    increase: ["웃긴", "즐거운", "행복", "기분 좋아"]
    decrease: ["슬픈", "우울", "화나", "스트레스"]
    amount: 10

# 마일스톤 정의
milestones:
  first_heart_to_heart:
    condition: "trust >= 60 AND conversation_count >= 5"
    description: "첫 번째 진솔한 대화를 나눴습니다"
    reward: "특별한 개인 스토리 공개"
    
  close_friendship:
    condition: "affection >= 80 AND trust >= 70"
    description: "가까운 친구가 되었습니다"
    reward: "친구만 아는 특별한 대화 주제 해금"
```

### 2. Event Tracking Examples
```txt
# 특별 이벤트 추적
special_events:
  user_birthday:
    trigger: "생일"
    action: "기억하고 특별한 축하 메시지"
    memory_priority: "high"
    
  shared_hobby:
    trigger: ["취미", "좋아하는 것", "관심사"]
    action: "공통 관심사 탐색 및 기억"
    memory_priority: "medium"
    
  personal_problem:
    trigger: ["고민", "문제", "힘들어", "스트레스"]
    action: "공감하고 지지, 다음 대화에서 안부 묻기"
    memory_priority: "high"
```

---

## Knowledge Base Management

### 1. Knowledge Item Structure
```json
{
  "id": "k_001",
  "title": "한국사 - 조선 건국",
  "content": "1392년 이성계가 조선을 건국했습니다. 수도는 한양(현재의 서울)으로 정했고...",
  "keywords": ["조선", "이성계", "1392년", "한양", "건국"],
  "category": "역사",
  "difficulty_level": "초급",
  "usage_count": 0,
  "last_used": null,
  "related_topics": ["k_002", "k_003"]
}
```

### 2. Conversation Examples Integration
```json
{
  "conversation_examples": [
    {
      "user": "조선이 언제 건국되었나요?",
      "assistant": "조선은 1392년에 이성계에 의해 건국되었습니다. 고려 말기의 정치적 혼란을 수습하고 새로운 왕조를 열었죠. 수도는 한양, 지금의 서울로 정했답니다."
    },
    {
      "user": "왜 한양을 수도로 정했을까요?",
      "assistant": "한양을 수도로 선택한 이유는 여러 가지가 있어요. 지리적으로 한반도 중앙에 위치해 있고, 한강이라는 큰 강이 있어 교통과 물류에 유리했습니다. 또한 주변 산들이 자연 방벽 역할을 해서 방어에도 좋았어요."
    }
  ]
}
```

### 3. Dynamic Knowledge Updates
```json
{
  "adaptive_responses": {
    "beginner_level": {
      "explanation_style": "기본 개념부터 차근차근",
      "vocabulary": "쉬운 단어 사용",
      "examples": "일상적인 비유 활용"
    },
    "advanced_level": {
      "explanation_style": "심화 내용과 배경 맥락",
      "vocabulary": "전문 용어 사용 가능",
      "examples": "학술적 관점에서 분석"
    }
  }
}
```

---

## Background Stories & Scenarios

### 1. Fantasy RPG Scenario
```xml
<scenario>
  <title>아에테리아 연대기 - 판타지 RPG</title>
  
  <world_setting>
    마법과 검이 공존하는 중세 판타지 세계 아에테리아.
    고대 드래곤들이 남긴 마법의 유적이 곳곳에 숨어있고,
    다양한 종족들이 함께 살아가는 모험의 땅입니다.
  </world_setting>
  
  <character_role>
    당신은 이제 막 모험을 시작한 신참 모험가입니다.
    용기와 열정은 있지만 경험이 부족한 상태로,
    다양한 퀘스트를 통해 성장해 나가게 됩니다.
  </character_role>
  
  <progression_system>
    status_values:
      hero_level: 1          # 영웅 레벨 (1-100)
      reputation: 10         # 명성 (0-100)
      corruption: 0          # 타락도 (0-100)
      wisdom: 15            # 지혜 (0-100)
      magical_bond: 5       # 마법 친화도 (0-100)
      
    milestone_events:
      first_quest_complete:
        trigger: "퀘스트 첫 완료"
        reward: "길드 정식 회원 등록"
        
      dragon_encounter:
        trigger: "고대 드래곤과의 만남"
        reward: "드래곤의 축복 또는 저주"
  </progression_system>
</scenario>
```

### 2. Modern Life Scenario
```xml
<scenario>
  <title>현대 도시 생활 시뮬레이션</title>
  
  <world_setting>
    2024년 서울, 바쁜 현대인들의 일상 속에서
    AI 비서가 사용자의 삶에 동반자 역할을 합니다.
    일, 인간관계, 취미, 건강 등 다양한 영역에서
    실질적인 도움을 제공합니다.
  </world_setting>
  
  <character_role>
    개인 AI 어시스턴트로서 사용자의 하루 일과를 
    함께하며 스케줄 관리, 감정 관리, 생활 개선 등을
    도와주는 역할을 합니다.
  </character_role>
  
  <daily_life_tracking>
    status_values:
      stress_level: 30       # 스트레스 수준 (0-100)
      work_satisfaction: 60  # 업무 만족도 (0-100)
      social_connection: 45  # 사회적 연결감 (0-100)
      health_score: 70      # 건강 점수 (0-100)
      
    routine_events:
      morning_briefing:
        trigger: "아침 인사"
        action: "오늘 일정과 날씨, 컨디션 확인"
        
      stress_check:
        trigger: "피곤", "스트레스"
        action: "휴식 제안 및 스트레스 관리 팁"
  </daily_life_tracking>
</scenario>
```

---

## Voice Selection & TTS

### 1. Available Voice Types
```typescript
// 한국어 음성 옵션
korean_voices: {
  "tc_61c97b56f1b7877a74df625b": "Emma - 친근한 여성",
  "tc_6073b2f6817dccf658bb159f": "Duke - 중후한 남성", 
  "tc_60c832f9d5a9c84f4c5b8c9a": "Luna - 차분한 여성",
  "tc_70d841e9c5b4d2f3a1e8f7b6": "Mark - 활기찬 남성"
}

// 특수 캐릭터용 전용 음성
dedicated_voices: {
  "seol_min_seok": {
    service: "dev.icepeak.ai",
    actor_id: "66f691e9b38df0481f09bf5e",
    description: "설민석 AI 튜터 전용 음성"
  }
}
```

### 2. Voice Selection Guidelines
- **교육 캐릭터**: 명확하고 또렷한 발음의 음성 선택
- **친구/동반자 캐릭터**: 친근하고 따뜻한 톤의 음성
- **전문가 캐릭터**: 신뢰감 있고 안정적인 음성
- **게임 캐릭터**: 캐릭터 성격에 맞는 개성 있는 음성

---

## Conversation Examples

### 1. Educational Conversation
```json
{
  "conversation_flow": [
    {
      "context": "역사 학습 - 첫 만남",
      "user": "안녕하세요, 한국사 공부하고 싶어요",
      "assistant": "안녕하세요! 한국사 공부를 시작하시는군요. 정말 좋은 선택이에요! 어떤 시대부터 관심이 있으신가요? 고대부터 차근차근 시작할까요, 아니면 특별히 궁금한 시대가 있나요?",
      "emotion": "happy",
      "memory_action": "사용자 학습 목표 기록"
    },
    {
      "context": "구체적 질문 응답",
      "user": "조선시대에 대해 알고 싶어요",
      "assistant": "조선시대는 정말 흥미진진한 시대예요! 518년간 이어진 긴 왕조로, 우리 문화의 뿌리가 되는 많은 것들이 만들어졌죠. 먼저 조선 건국 이야기부터 들어보실까요? 이성계가 어떻게 새로운 나라를 세웠는지 말이에요.",
      "emotion": "excited",
      "knowledge_used": ["k_001", "k_002"],
      "memory_action": "학습 진도 업데이트"
    }
  ]
}
```

### 2. Casual Conversation
```json
{
  "conversation_flow": [
    {
      "context": "일상 대화 - 감정 공유",
      "user": "오늘 하루가 너무 힘들었어",
      "assistant": "아, 정말 힘든 하루를 보내셨군요. 무슨 일이 있으셨는지 말씀해주세요. 제가 들어드릴게요. 때로는 누군가에게 털어놓는 것만으로도 마음이 좀 가벼워지거든요.",
      "emotion": "empathetic",
      "status_change": {"mood": -10, "trust": +3}
    },
    {
      "context": "공감과 위로",
      "user": "직장에서 상사한테 혼났어요",
      "assistant": "그런 일이 있으셨구나... 직장에서 혼나는 건 정말 기분이 안 좋죠. 그 상황에서 어떤 기분이셨을지 충분히 이해해요. 혹시 어떤 일로 그런 상황이 생긴 건지, 편하실 때 얘기해주시면 함께 생각해볼 수 있을 것 같아요.",
      "emotion": "supportive",
      "status_change": {"trust": +5, "affection": +3},
      "memory_action": "개인적 고민 기록 - 직장 스트레스"
    }
  ]
}
```

---

## Best Practices

### 1. Character Consistency
- **성격 유지**: 모든 대화에서 일관된 성격과 말투 유지
- **배경 설정 준수**: 설정된 배경과 모순되지 않는 응답
- **점진적 관계 발전**: 대화 횟수에 따른 자연스러운 친밀감 변화

### 2. Memory System Optimization
- **중요도 분류**: 개인정보, 감정적 순간, 공통 관심사는 높은 우선순위
- **상태값 밸런싱**: 너무 급격한 변화보다는 점진적 변화 선호
- **마일스톤 설계**: 의미 있는 관계 진전 단계 설정

### 3. Knowledge Base Curation
- **정확성 확보**: 사실 확인된 정보만 포함
- **난이도 조절**: 사용자 수준에 맞는 설명 제공
- **연관성 구축**: 관련 주제들 간의 연결 고리 설정

### 4. Multi-Character Design
- **역할 분담**: 각 캐릭터의 고유한 역할과 특성 명확화
- **대화 균형**: 모든 캐릭터가 적절히 참여하는 대화 구성
- **음성 구분**: 캐릭터별로 구별되는 음성 특성 선택

---

## Troubleshooting

### 1. Common Issues

**문제**: 캐릭터가 일관성 없는 응답을 함
**해결**: XML 구조에서 personality와 speaking_style을 더 구체적으로 정의

**문제**: 메모리 시스템이 제대로 작동하지 않음  
**해결**: status_triggers의 키워드를 사용자가 실제 사용할 법한 표현으로 수정

**문제**: 지식베이스 내용이 검색되지 않음
**해결**: keywords 배열에 다양한 표현과 동의어 추가

**문제**: 다중 캐릭터 대화가 파싱되지 않음
**해결**: `[SPEAKER: 이름]` 형식을 정확히 지키고, 이름 앞뒤 공백 확인

### 2. Performance Tips
- 지식베이스 항목은 500자 이내로 작성 (검색 효율성)
- 상태값 트리거는 5개 이내로 제한 (처리 속도)
- 대화 예시는 10개 이내로 구성 (메모리 효율성)

### 3. Testing Checklist
- [ ] 첫 인사가 제대로 출력되는가?
- [ ] 캐릭터 성격이 일관되게 나타나는가?
- [ ] 음성이 캐릭터에 적합한가?
- [ ] 메모리 상태값이 적절히 변화하는가?
- [ ] 지식베이스 내용이 관련 질문에서 활용되는가?

---

## 📞 Support & Resources

### Documentation Files
- `structure.md`: 시스템 전체 구조 이해
- `IMPLEMENTATION_SUMMARY.md`: 기술 구현 세부사항
- `API_DOCUMENTATION.md`: API 엔드포인트 사용법
- `plans/plan.md`: 개발 로드맵 및 진행 상황

### Example Characters
- `frontend/src/data/demo-characters.ts`: 5개 샘플 캐릭터 참조
- `backend_clean/configurations/`: 메모리 설정 예시
- `backend_clean/knowledge/characters/`: 지식베이스 구조 예시

### Testing Environment
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

*이 가이드를 통해 매력적이고 기억에 남는 AI 캐릭터를 만들어보세요! 궁금한 점이 있으시면 언제든 문의해 주세요.* 🎭✨