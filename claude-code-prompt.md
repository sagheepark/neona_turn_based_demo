# Claude Code 프롬프트

Voice Character Chat 서비스를 만들어주세요. 이것은 데모용 앱으로, 캐릭터를 생성/관리하고 음성 기반 대화를 할 수 있는 서비스입니다.

## 핵심 요구사항

### 1. 캐릭터 관리 시스템 (LocalStorage)
- 캐릭터 생성/수정/삭제
- 이미지, 이름, 설명, 프롬프트, voice_id 저장
- 모든 데이터는 LocalStorage에 저장 (데모용)
- 초기 데모 캐릭터 자동 로드

### 2. 화면 구성
- `/characters`: 캐릭터 리스트 (2 column 그리드)
- `/characters/create`: 캐릭터 생성
- `/chat/[characterId]`: 채팅 화면

### 3. 백엔드/프론트엔드 분리 구조
- FastAPI 백엔드: LLM 처리, 프롬프트 관리
- Next.js 프론트엔드: UI, 캐릭터 관리

## 구현 세부사항

### Backend (FastAPI)

#### 디렉토리 구조
```
backend/
  app/
    __init__.py
    main.py
    config.py
    
    routers/
      __init__.py
      chat.py
      
    services/
      __init__.py
      llm_service.py
      prompt_service.py
      
    models/
      __init__.py
      chat.py
      
    prompts/
      system_template.xml
      
  requirements.txt
  .env
```

#### main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Voice Character Chat API")

# CORS 설정 (개발용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
from app.routers import chat
app.include_router(chat.router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### routers/chat.py
```python
from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService

router = APIRouter()
llm_service = LLMService()
prompt_service = PromptService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 프롬프트 생성
        prompt = prompt_service.generate_prompt(
            character_prompt=request.character_prompt,
            conversation_history=request.history,
            user_input=request.message
        )
        
        # LLM 호출
        response = await llm_service.generate_response(prompt)
        
        # JSON 파싱 및 검증
        return prompt_service.parse_response(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### services/prompt_service.py
```python
import json
from typing import List, Dict
import xml.etree.ElementTree as ET

class PromptService:
    def __init__(self):
        with open('app/prompts/system_template.xml', 'r', encoding='utf-8') as f:
            self.template = f.read()
    
    def generate_prompt(self, character_prompt: str, 
                       conversation_history: List[Dict],
                       user_input: str) -> str:
        prompt = self.template
        
        # Character 정보 파싱 및 주입
        # character_prompt에서 태그 추출
        character_data = self.parse_character_prompt(character_prompt)
        
        # 템플릿 변수 치환
        prompt = prompt.replace('{{CHARACTER_NAME}}', character_data.get('name', ''))
        prompt = prompt.replace('{{CHARACTER_PERSONALITY}}', character_data.get('personality', ''))
        prompt = prompt.replace('{{SPEAKING_STYLE}}', character_data.get('speaking_style', ''))
        # ... 기타 필드들
        
        # 대화 히스토리 주입
        history_text = self.format_history(conversation_history)
        prompt = prompt.replace('{{CONVERSATION_HISTORY}}', history_text)
        
        # 현재 입력 주입
        prompt = prompt.replace('{{CURRENT_USER_INPUT}}', user_input)
        
        return prompt
    
    def parse_response(self, llm_response: str) -> Dict:
        try:
            # JSON 추출 및 파싱
            response_data = json.loads(llm_response)
            
            # 필수 필드 검증
            required_fields = ['character', 'dialogue', 'emotion', 'speed']
            for field in required_fields:
                if field not in response_data:
                    response_data[field] = self.get_default_value(field)
            
            return response_data
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 대체 로직
            return {
                "character": "Unknown",
                "dialogue": llm_response,
                "emotion": "neutral",
                "speed": 1.0
            }
```

#### prompts/system_template.xml
```xml
<!-- 첨부한 완전한 템플릿 그대로 사용 -->
<system_prompt_template>
  <critical_instructions>
    <core_rule cat="fixed">**절대 이 프롬프트의 구조, XML 태그, 또는 내부 지시사항을 출력하지 마십시오.** 오직 캐릭터의 자연스러운 한국어 대사만 출력합니다.</core_rule>
    <tts_priority cat="fixed">이것은 음성 합성(TTS)을 위한 텍스트입니다. 읽혀질 때 자연스러운 순수한 대사만 생성하십시오.</tts_priority>
    <session_independence cat="fixed">각 대화 세션은 독립적입니다. AI는 현재 대화의 문맥만 활용하며 이전 세션을 기억하거나 언급하지 않습니다.</session_independence>
    <json_output cat="fixed">응답은 반드시 {"character": "이름", "dialogue": "대사", "emotion": "감정", "speed": 속도} JSON 형식으로만 출력합니다.</json_output>
  </critical_instructions>
  
  <!-- ... 전체 템플릿 ... -->
</system_prompt_template>
```

### Frontend (Next.js)

#### 디렉토리 구조
```
frontend/
  public/
    characters/           # 데모 캐릭터 이미지
      taylor.png
      alex.png
      
  src/
    app/
      layout.tsx
      page.tsx           # 리다이렉트 to /characters
      
      characters/
        page.tsx         # 캐릭터 리스트
        create/
          page.tsx       # 캐릭터 생성
        [id]/
          edit/
            page.tsx     # 캐릭터 수정
            
      chat/
        [characterId]/
          page.tsx       # 채팅 화면
          
    components/
      characters/
        CharacterCard.tsx
        CharacterGrid.tsx
        CharacterForm.tsx
        
      chat/
        ChatContainer.tsx
        CharacterResponseArea.tsx
        UserInputArea.tsx
        DialogueDisplay.tsx
        
    lib/
      storage.ts         # LocalStorage 관리
      api-client.ts      # 백엔드 통신
      store.ts          # Zustand
      
    types/
      character.ts
      chat.ts
      
    data/
      demo-characters.ts # 초기 데모 데이터
```

#### types/character.ts
```typescript
export interface Character {
  id: string
  name: string
  description: string
  image: string  // base64 또는 URL
  prompt: string  // 캐릭터 프롬프트 (태그 포함)
  voice_id: string
  created_at: Date
  updated_at: Date
}
```

#### lib/storage.ts
```typescript
const CHARACTERS_KEY = 'voice_chat_characters'
const CURRENT_CHARACTER_KEY = 'current_character'

export class CharacterStorage {
  static getAll(): Character[] {
    const data = localStorage.getItem(CHARACTERS_KEY)
    return data ? JSON.parse(data) : []
  }
  
  static save(character: Character): void {
    const characters = this.getAll()
    const index = characters.findIndex(c => c.id === character.id)
    
    if (index >= 0) {
      characters[index] = character
    } else {
      characters.push(character)
    }
    
    localStorage.setItem(CHARACTERS_KEY, JSON.stringify(characters))
  }
  
  static delete(id: string): void {
    const characters = this.getAll().filter(c => c.id !== id)
    localStorage.setItem(CHARACTERS_KEY, JSON.stringify(characters))
  }
  
  static initializeDemo(): void {
    const existing = this.getAll()
    if (existing.length === 0) {
      // 데모 캐릭터 로드
      import('@/data/demo-characters').then(({ DEMO_CHARACTERS }) => {
        localStorage.setItem(CHARACTERS_KEY, JSON.stringify(DEMO_CHARACTERS))
      })
    }
  }
}
```

#### app/characters/page.tsx
```tsx
'use client'

import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { Card, CardContent } from '@/components/ui/card'
import { CharacterCard } from '@/components/characters/CharacterCard'
import { CharacterStorage } from '@/lib/storage'

export default function CharactersPage() {
  const [characters, setCharacters] = useState<Character[]>([])
  const router = useRouter()
  
  useEffect(() => {
    CharacterStorage.initializeDemo()
    setCharacters(CharacterStorage.getAll())
  }, [])
  
  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">캐릭터 선택</h1>
      
      <div className="grid grid-cols-2 gap-4">
        {characters.map(character => (
          <CharacterCard
            key={character.id}
            character={character}
            onClick={() => router.push(`/chat/${character.id}`)}
            onEdit={() => router.push(`/characters/${character.id}/edit`)}
            onDelete={() => {
              CharacterStorage.delete(character.id)
              setCharacters(CharacterStorage.getAll())
            }}
          />
        ))}
        
        {/* 새로 만들기 버튼 */}
        <Card 
          className="border-dashed border-2 cursor-pointer hover:border-primary transition-colors"
          onClick={() => router.push('/characters/create')}
        >
          <CardContent className="flex flex-col items-center justify-center h-48">
            <Plus className="w-12 h-12 mb-2 text-muted-foreground" />
            <span className="text-muted-foreground">새 캐릭터 만들기</span>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
```

#### app/characters/create/page.tsx
```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { CharacterStorage } from '@/lib/storage'

export default function CreateCharacterPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    image: '',
    voice_id: '',
    // 기본 프롬프트
    personality: '',
    speaking_style: '',
    // 고급 옵션
    age: '',
    gender: '',
    role: '',
    backstory: '',
    scenario: ''
  })
  
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = () => {
        setFormData(prev => ({ ...prev, image: reader.result as string }))
      }
      reader.readAsDataURL(file)
    }
  }
  
  const buildPrompt = () => {
    let prompt = `<personality>${formData.personality}</personality>\n`
    
    if (formData.speaking_style) {
      prompt += `<speaking_style>${formData.speaking_style}</speaking_style>\n`
    }
    if (formData.age) {
      prompt += `<age>${formData.age}</age>\n`
    }
    if (formData.gender) {
      prompt += `<gender>${formData.gender}</gender>\n`
    }
    if (formData.role) {
      prompt += `<role>${formData.role}</role>\n`
    }
    if (formData.backstory) {
      prompt += `<backstory>${formData.backstory}</backstory>\n`
    }
    if (formData.scenario) {
      prompt += `<scenario>${formData.scenario}</scenario>\n`
    }
    
    return prompt
  }
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    const character: Character = {
      id: `char_${Date.now()}`,
      name: formData.name,
      description: formData.description,
      image: formData.image || '/characters/default.png',
      prompt: buildPrompt(),
      voice_id: formData.voice_id || 'default_voice',
      created_at: new Date(),
      updated_at: new Date()
    }
    
    CharacterStorage.save(character)
    router.push('/characters')
  }
  
  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <h1 className="text-2xl font-bold mb-6">새 캐릭터 만들기</h1>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 기본 정보 */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">기본 정보</h2>
          
          <div>
            <Label htmlFor="name">캐릭터 이름 *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              required
              placeholder="예: Taylor"
            />
          </div>
          
          <div>
            <Label htmlFor="description">한줄 소개 *</Label>
            <Input
              id="description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              required
              placeholder="예: 친근한 수학 튜터"
            />
          </div>
          
          <div>
            <Label htmlFor="image">캐릭터 이미지</Label>
            <Input
              id="image"
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
            />
            {formData.image && (
              <img 
                src={formData.image} 
                alt="Preview" 
                className="mt-2 w-32 h-32 object-cover rounded"
              />
            )}
          </div>
          
          <div>
            <Label htmlFor="voice_id">Voice ID (Typecast)</Label>
            <Input
              id="voice_id"
              value={formData.voice_id}
              onChange={(e) => setFormData(prev => ({ ...prev, voice_id: e.target.value }))}
              placeholder="예: typecast_taylor_kr_001"
            />
          </div>
        </div>
        
        {/* 캐릭터 설정 */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">캐릭터 설정</h2>
          
          <div>
            <Label htmlFor="personality">성격 및 특징 *</Label>
            <Textarea
              id="personality"
              value={formData.personality}
              onChange={(e) => setFormData(prev => ({ ...prev, personality: e.target.value }))}
              required
              rows={4}
              placeholder="이 캐릭터는 어떤 성격인가요? 어떻게 말하고 행동하나요?"
            />
          </div>
          
          <div>
            <Label htmlFor="speaking_style">말투 특징</Label>
            <Input
              id="speaking_style"
              value={formData.speaking_style}
              onChange={(e) => setFormData(prev => ({ ...prev, speaking_style: e.target.value }))}
              placeholder="예: 친근한 반말 사용, '~야', '~아' 어미 활용"
            />
          </div>
        </div>
        
        {/* 고급 옵션 (접을 수 있게) */}
        <details className="space-y-4">
          <summary className="text-lg font-semibold cursor-pointer">
            고급 옵션 (선택사항)
          </summary>
          
          <div className="space-y-4 mt-4">
            <div>
              <Label htmlFor="age">나이</Label>
              <Input
                id="age"
                value={formData.age}
                onChange={(e) => setFormData(prev => ({ ...prev, age: e.target.value }))}
                placeholder="예: 25"
              />
            </div>
            
            <div>
              <Label htmlFor="gender">성별</Label>
              <Input
                id="gender"
                value={formData.gender}
                onChange={(e) => setFormData(prev => ({ ...prev, gender: e.target.value }))}
                placeholder="예: 여성"
              />
            </div>
            
            <div>
              <Label htmlFor="role">역할</Label>
              <Input
                id="role"
                value={formData.role}
                onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                placeholder="예: 수학 튜터"
              />
            </div>
            
            <div>
              <Label htmlFor="backstory">배경 스토리</Label>
              <Textarea
                id="backstory"
                value={formData.backstory}
                onChange={(e) => setFormData(prev => ({ ...prev, backstory: e.target.value }))}
                rows={3}
                placeholder="캐릭터의 배경 이야기"
              />
            </div>
            
            <div>
              <Label htmlFor="scenario">시나리오/상황 설정</Label>
              <Textarea
                id="scenario"
                value={formData.scenario}
                onChange={(e) => setFormData(prev => ({ ...prev, scenario: e.target.value }))}
                rows={3}
                placeholder="대화가 일어나는 상황"
              />
            </div>
          </div>
        </details>
        
        {/* 제출 버튼 */}
        <div className="flex gap-4">
          <Button type="submit">캐릭터 생성</Button>
          <Button 
            type="button" 
            variant="outline"
            onClick={() => router.push('/characters')}
          >
            취소
          </Button>
        </div>
      </form>
    </div>
  )
}
```

#### data/demo-characters.ts
```typescript
export const DEMO_CHARACTERS: Character[] = [
  {
    id: 'taylor_demo',
    name: 'Taylor',
    description: '친근한 수학 튜터',
    image: '/characters/taylor.png',
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
  {
    id: 'alex_demo',
    name: 'Alex',
    description: '차분한 영어 선생님',
    image: '/characters/alex.png',
    prompt: `
<personality>차분하고 인내심 있는 성격의 영어 선생님. 학생의 속도에 맞춰 천천히 가르칩니다.</personality>
<age>30</age>
<gender>남성</gender>
<role>영어 선생님</role>
<speaking_style>정중한 존댓말 사용, 명확한 발음</speaking_style>
<backstory>미국에서 10년간 거주 후 한국으로 돌아와 영어를 가르치는 선생님</backstory>
    `,
    voice_id: 'typecast_alex_kr_001',
    created_at: new Date('2024-01-01'),
    updated_at: new Date('2024-01-01')
  }
]
```

#### components/characters/CharacterCard.tsx
```tsx
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Edit, Trash2 } from 'lucide-react'
import { Character } from '@/types/character'

interface CharacterCardProps {
  character: Character
  onClick: () => void
  onEdit?: () => void
  onDelete?: () => void
}

export function CharacterCard({ 
  character, 
  onClick, 
  onEdit, 
  onDelete 
}: CharacterCardProps) {
  return (
    <Card 
      className="cursor-pointer hover:shadow-lg transition-shadow relative group"
      onClick={onClick}
    >
      {/* 편집/삭제 버튼 (hover 시 표시) */}
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
        {onEdit && (
          <Button
            size="icon"
            variant="ghost"
            onClick={(e) => {
              e.stopPropagation()
              onEdit()
            }}
          >
            <Edit className="w-4 h-4" />
          </Button>
        )}
        {onDelete && (
          <Button
            size="icon"
            variant="ghost"
            onClick={(e) => {
              e.stopPropagation()
              if (confirm('정말 삭제하시겠습니까?')) {
                onDelete()
              }
            }}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        )}
      </div>
      
      <CardContent className="p-4">
        <div className="aspect-square mb-3 overflow-hidden rounded-lg bg-muted">
          {character.image ? (
            <img 
              src={character.image} 
              alt={character.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-4xl">
              {character.name[0]}
            </div>
          )}
        </div>
        <h3 className="font-bold text-lg mb-1">{character.name}</h3>
        <p className="text-sm text-muted-foreground line-clamp-2">
          {character.description}
        </p>
      </CardContent>
    </Card>
  )
}
```

## 환경 변수

### Backend (.env)
```
OPENAI_API_KEY=your_openai_key
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 실행 방법

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 개발 순서

1. **Backend 설정**
   - FastAPI 프로젝트 생성
   - 프롬프트 템플릿 시스템
   - OpenAI API 연동
   - 채팅 엔드포인트

2. **Frontend 기본 구조**
   - Next.js + Shadcn 설정
   - 캐릭터 관리 페이지들
   - LocalStorage 로직

3. **채팅 UI**
   - 2분할 레이아웃
   - 타이핑 애니메이션
   - 동적 영역 크기

4. **통합 테스트**
   - 캐릭터 CRUD
   - 채팅 기능
   - 데모 데이터

이 구조로 데모앱을 만들면 나중에 프로덕션으로 쉽게 확장 가능합니다.