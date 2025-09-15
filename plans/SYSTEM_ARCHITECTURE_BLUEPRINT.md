# SYSTEM ARCHITECTURE BLUEPRINT
**Complete Technical Documentation for seol_min_seok and dr_genie Characters**

---

## 🏗️ **OVERVIEW**

This document provides a complete technical blueprint of the quiz system architecture, covering both `seol_min_seok_quiz` (Korean History) and `dr_genie_science_quiz` (Science) characters. Every component, file, flow, and integration is documented without omission.

## 🔴 **CRITICAL STATUS UPDATE (2025-09-14)**

**LLM-Based Answer Evaluation**: ✅ **IMPLEMENTED & WORKING**
- Two-step answer checking flow successfully implemented
- Frontend integration complete with continuous_quiz_response tool
- TTS generation working for both feedback and question phases

**✅ CRITICAL BUGS RESOLVED**: 

### **1. Progression Fallback Bug - FIXED**
- **Problem**: When user answers second question wrong, system falls back to first question instead of retrying second question
- **Root Cause**: Hardcoded fallback patterns in `tool_orchestrator.py:583-605`
  - `_extract_last_question_from_history`: Had hardcoded patterns matching "창건자" or "이성계"
  - `_extract_correct_answer_from_history`: Always returned first question data regardless of context
- **Solution**: Removed ALL hardcoded patterns, now uses proper tool data extraction
- **Status**: ✅ **RESOLVED** - Question progression works correctly

### **2. Dr.Genie TTS Service Routing - FIXED**
- **Problem**: Dr.Genie greeting had no TTS audio while seol_min_seok_quiz worked fine
- **Root Cause**: Two different TTS endpoints with inconsistent routing
  - `/api/platform-chat` → tool_orchestrator → ✅ seolminseok_tts_service
  - `/api/tts` → main.py:1529 → ❌ TypecastTTS (wrong service)
- **Solution**: Updated condition in `main.py:1529` to include `dr_genie_science_quiz`
- **Status**: ✅ **RESOLVED** - Both characters use same TTS service

### **3. Server Import Caching Issue**
- **Problem**: TTS method signatures cached old versions causing parameter errors
- **Solution**: Server restart + consistent use of `--reload` flag
- **Status**: ✅ **RESOLVED** - Development caching strategy documented

---

## 📁 **PROJECT STRUCTURE**

```
neona_turn_based_demo_with_agent/
├── backend_clean/                    # Python FastAPI Backend
│   ├── main.py                      # Main API server
│   ├── services/                    # Core business logic
│   │   ├── tool_orchestrator.py     # LLM-driven tool coordination
│   │   ├── continuous_answer_tool.py # Quiz flow management
│   │   ├── llm_agent_engine.py      # Azure GPT-4o integration
│   │   ├── platform_tool_handler.py # Tool definitions & execution
│   │   ├── character_config_manager.py # Character configurations
│   │   ├── greeting_suggestion_generator.py # Topic generation
│   │   ├── educational_quiz_flow.py # Quiz feedback templates
│   │   ├── learning_content_classifier.py # Content analysis
│   │   ├── platform_content_classifier.py # Platform routing
│   │   └── tts_service.py           # Text-to-Speech integration
│   └── session_management/          # Session & conversation state
└── frontend/                        # Next.js React Frontend
    ├── src/app/chat/[characterId]/  # Character-specific chat pages
    ├── src/components/              # Reusable UI components
    ├── src/lib/api-client.ts        # Backend API integration
    └── src/data/demo-characters.ts  # Character definitions
```

---

## 🎯 **CHARACTER DEFINITIONS**

### **seol_min_seok_quiz (Korean History Teacher)**
```typescript
// File: frontend/src/data/demo-characters.ts
{
  id: "seol_min_seok_quiz",
  name: "설민석 선생님",
  description: "한국사 퀴즈 전문 선생님",
  personality: "따뜻하고 격려적인 역사 교육자",
  specialization: "한국사",
  avatar: "/seol_character.png",
  voice: "korean_male_teacher",
  greeting: "안녕하세요! 한국사 퀴즈를 함께 풀어볼까요?"
}
```

### **dr_genie_science_quiz (Science Teacher)**
```typescript
// File: frontend/src/data/demo-characters.ts  
{
  id: "dr_genie_science_quiz",
  name: "닥터 지니",
  description: "과학 퀴즈 전문 선생님",
  personality: "호기심 넘치는 과학 교육자",
  specialization: "과학",
  avatar: "/genie_character.png", 
  voice: "korean_female_teacher",
  greeting: "안녕하세요, 여러분의 과학 선생님 닥터 지니예요!"
}
```

---

## 🌊 **COMPLETE USER FLOW**

### **Phase 1: Initial Greeting**
```
User Opens Chat → Frontend loads character → POST /api/platform-chat
```

**Frontend Request:**
```typescript
// File: frontend/src/app/chat/[characterId]/page.tsx
const response = await fetch('/api/platform-chat', {
  method: 'POST',
  body: JSON.stringify({
    user_input: "",
    character_id: characterId,
    session_id: null,
    user_id: "user"
  })
});
```

**Backend Processing:**
```python
# File: backend_clean/main.py (platform-chat endpoint)
@app.post("/api/platform-chat")
async def platform_chat_endpoint(request: PlatformChatRequest):
    # Routes to tool_orchestrator.py
    response = await tool_orchestrator.process_interaction(
        session_id=request.session_id,
        user_input=request.user_input,
        character_id=request.character_id,
        user_id=request.user_id
    )
```

### **Phase 2: Topic Selection**
```
User selects topic → POST /api/platform-chat → LLM generates first quiz
```

**LLM Processing:**
```python
# File: backend_clean/services/tool_orchestrator.py
elif stage == 'topic_selected' and context == 'user_selected_topic':
    topic = conversation_state.get('topic', 'selected topic')
    enhanced_prompt += f"""
CURRENT SITUATION: User just selected topic '{topic}'
YOUR TASK: Acknowledge their choice and present first quiz question about {topic}
TOOL TO USE: show_selection with selection_mode='quiz_question'
"""
```

### **Phase 3: Quiz Question & Answer Loop**
```
User answers question → POST /api/platform-chat → LLM evaluates → Response with next action
```

**Critical Flow Points:**
1. **Correct Answer**: Generate new question on different topic
2. **Wrong Answer**: Show same question again for retry
3. **Question Context**: Must be stored in chat history for LLM reference

---

## 🧠 **LLM INTEGRATION ARCHITECTURE**

### **Azure GPT-4o Integration**
```python
# File: backend_clean/services/llm_agent_engine.py
class LLMAgentEngine:
    def __init__(self):
        self.azure_client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-08-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    
    async def process_interaction(self, context, character_prompt):
        # Build comprehensive prompt with character behavior + tools
        system_prompt = self._build_system_prompt(character_prompt, available_tools)
        
        messages = [
            {"role": "system", "content": system_prompt},
            *chat_history,
            {"role": "user", "content": user_input}
        ]
        
        response = await self.azure_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000
        )
```

### **Character-Specific Prompts**
```python
# File: backend_clean/services/character_config_manager.py
class CharacterConfigManager:
    def get_character_prompt(self, character_id: str) -> str:
        prompts = {
            "seol_min_seok_quiz": """
당신은 설민석, 열정적인 한국사 교육자입니다.

퀴즈 답변 처리:
- 정답일 때: 구체적으로 축하하고 역사적 배경 설명 후 새로운 주제의 문제 출제
- 오답일 때: 격려하며 힌트 제공 후 같은 문제 재출제

응답 형식: JSON으로 dialogue와 tool 포함
            """,
            
            "dr_genie_science_quiz": """
당신은 닥터 지니, 호기심 넘치는 과학 교육자입니다.

퀴즈 답변 처리:  
- 정답일 때: 과학적 원리 설명과 함께 축하 후 새로운 과학 문제 출제
- 오답일 때: 과학적 사고 과정 힌트 제공 후 같은 문제 재출제

응답 형식: JSON으로 dialogue와 tool 포함
            """
        }
```

---

## 🔧 **TOOL SYSTEM ARCHITECTURE**

### **Tool Definitions**
```python
# File: backend_clean/services/platform_tool_handler.py
class PlatformToolHandler:
    def _initialize_tools(self) -> Dict[str, ToolDefinition]:
        return {
            "show_selection": ToolDefinition(
                name="show_selection",
                description="Display quiz questions or topic selection",
                parameters={
                    "question": "string - The question text",
                    "options": "array[string] - Multiple choice options",
                    "correct_answer": "string - The scientifically/historically correct answer",
                    "selection_mode": "string - 'topic' or 'quiz_question'"
                }
            ),
            
            "continuous_quiz_response": ToolDefinition(
                name="continuous_quiz_response", 
                description="Two-phase quiz response with feedback then next question",
                parameters={
                    "phase1": {
                        "text": "string - Answer feedback",
                        "delay_ms": "number - Delay before phase2"
                    },
                    "phase2": {
                        "text": "string - Introduction to next question", 
                        "tool": "object - Nested show_selection tool"
                    }
                }
            )
        }
```

### **Tool Execution Pipeline**
```python
# File: backend_clean/services/platform_tool_handler.py
async def execute_tool(self, tool_type: str, data: Dict[str, Any]):
    if tool_type == "show_selection":
        # CRITICAL: Auto-detect correct answer if missing
        if data["selection_mode"] == "quiz_question":
            if not data.get("correct_answer"):
                data["correct_answer"] = self._detect_correct_answer(
                    data["question"], data["options"]
                )
        
        return {"type": "show_selection", "data": data}
    
    elif tool_type == "continuous_quiz_response":
        # Generate TTS for both phases
        return await self._execute_continuous_quiz_response(data)
```

---

## 🎵 **TTS (Text-to-Speech) INTEGRATION**

### **🚨 CRITICAL: TTS Routing Architecture**

**Frontend makes requests to TWO different TTS endpoints that MUST be kept in sync:**

#### **Path 1: Platform Chat TTS (Greeting)**
```
Frontend → POST /api/platform-chat → tool_orchestrator.py:139 
→ if character_id in ["seol_min_seok_quiz", "dr_genie_science_quiz"]: 
→ seol_tts_service.generate_tts()
```

#### **Path 2: Direct TTS (Additional Audio)**
```
Frontend → POST /api/tts → main.py:1529
→ if 'seol_min_seok' in request.character_id or request.character_id == 'dr_genie_science_quiz':
→ seolminseok_tts_service.generate_tts()
```

**⚠️ DANGER**: If these two conditions get out of sync, characters will have inconsistent TTS behavior!

### **Service Architecture**
```python
# File: backend_clean/services/tts_service.py  
class TypecastTTSService:
    async def generate_speech(
        self, 
        text: str, 
        voice_id: str = "tc_61c97b56f1b7877a74df625b",
        character_id: str = None,  # For compatibility
        **kwargs
    ) -> Optional[str]:
        # Generate audio and return base64 data URL
        return f"data:audio/wav;base64,{base64_audio}"
        
# Character-specific TTS routing
class SeolMinSeokTTSService:
    async def generate_speech(self, text: str, character_id: str) -> str:
        # Korean male voice optimized for history content
        return await self.typecast_tts.generate_speech(
            text, voice_id="seol_voice_id"
        )
```

### **New Character TTS Checklist** 
When adding new quiz characters, update BOTH:
1. `tool_orchestrator.py:139` character list
2. `main.py:1529` condition logic

### **Frontend Audio Integration**
```typescript  
// File: frontend/src/app/chat/[characterId]/page.tsx
const handleAudioPlayback = (audioUrl: string) => {
  if (audioUrl && audioUrl.startsWith('data:audio')) {
    const audio = new Audio(audioUrl);
    audio.play().catch(console.error);
  }
};

// Process chat response with audio
if (data.audio_url) {
  handleAudioPlayback(data.audio_url);
}
```

---

## 📊 **SESSION MANAGEMENT**

### **Session State Structure**
```python
# File: backend_clean/session_management/
class SessionState:
    session_id: str
    user_id: str  
    character_id: str
    conversation_stage: str  # 'greeting', 'topic_selected', 'quiz_active'
    context: str            # 'initial', 'user_selected_topic', 'user_answered_quiz'
    chat_history: List[Dict]
    current_topic: str
    quiz_context: Dict      # Current question, correct answer, attempt count
```

### **Context Analysis**
```python
# File: backend_clean/services/tool_orchestrator.py
def _analyze_conversation_state(self, chat_history: List[Dict], user_input: str):
    # Detect current conversation stage and context
    if not chat_history:
        return {'stage': 'greeting', 'context': 'initial'}
    
    # Topic selection detection
    for topic in ["조선시대", "고려시대", "삼국시대", "물리", "화학", "생물"]:
        if topic in user_input:
            return {'stage': 'topic_selected', 'context': 'user_selected_topic', 'topic': user_input}
    
    # Quiz answer detection
    last_assistant = next((msg for msg in reversed(chat_history) if msg.get('role') == 'assistant'), None)
    if last_assistant and 'tools' in last_assistant:
        for tool in last_assistant['tools']:
            if tool.get('type') == 'show_selection' and tool.get('data', {}).get('selection_mode') == 'quiz_question':
                return {'stage': 'quiz_active', 'context': 'user_answered_quiz'}
```

---

## ⚡ **API ENDPOINTS**

### **Primary Chat Endpoint**
```python
# File: backend_clean/main.py
@app.post("/api/platform-chat")
async def platform_chat_endpoint(request: PlatformChatRequest):
    """
    Main chat endpoint handling both characters
    Processes: greetings, topic selection, quiz interactions
    Returns: dialogue, tools, audio_url, session_id
    """
    
    response = await tool_orchestrator.process_interaction(
        session_id=request.session_id or generate_session_id(),
        user_input=request.user_input, 
        character_id=request.character_id,
        user_id=request.user_id or "anonymous"
    )
    
    return {
        "character": request.character_id,
        "dialogue": response["dialogue"], 
        "emotion": response.get("emotion", "neutral"),
        "tools": response["tools"],
        "audio_url": response.get("audio_url"),
        "session_id": response["session_id"]
    }
```

### **Request/Response Schemas**
```python
class PlatformChatRequest(BaseModel):
    user_input: str
    character_id: str  
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class PlatformChatResponse(BaseModel):
    character: str
    dialogue: str
    emotion: str
    tools: List[Dict[str, Any]]
    audio_url: Optional[str]
    session_id: str
```

---

## 🎨 **FRONTEND ARCHITECTURE**

### **Character Chat Component**
```typescript
// File: frontend/src/app/chat/[characterId]/page.tsx
export default function CharacterChatPage({ params }: { params: { id: string } }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  // Initialize chat with character greeting
  useEffect(() => {
    initializeChat();
  }, [params.id]);
  
  const sendMessage = async (userInput: string) => {
    const response = await fetch('/api/platform-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_input: userInput,
        character_id: params.id,
        session_id: sessionId,
        user_id: 'user'
      })
    });
    
    const data = await response.json();
    
    // Handle audio playback
    if (data.audio_url) {
      handleAudioPlayback(data.audio_url);
    }
    
    // Render tools (quiz questions, topic selection)
    if (data.tools?.length > 0) {
      renderInteractiveTools(data.tools);
    }
    
    setMessages(prev => [...prev, {
      role: 'assistant',
      content: data.dialogue,
      tools: data.tools
    }]);
  };
}
```

### **Quiz Tool Rendering**
```typescript
// File: frontend/src/components/quiz/QuizComponent.tsx
interface QuizToolProps {
  question: string;
  options: string[];
  onAnswer: (answer: string) => void;
}

export function QuizTool({ question, options, onAnswer }: QuizToolProps) {
  return (
    <div className="quiz-container">
      <h3>{question}</h3>
      <div className="options-grid">
        {options.map((option, index) => (
          <button
            key={index}
            onClick={() => onAnswer(option)}
            className="option-button"
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}
```

---

## 🔄 **CRITICAL SYSTEM FLOWS**

### **1. Greeting Flow**
```
Frontend Load → POST /api/platform-chat (empty input) 
→ tool_orchestrator detects 'greeting' stage 
→ character_config_manager provides greeting prompt
→ LLM generates topic selection tool
→ Frontend renders topic buttons
```

### **2. Topic Selection Flow**
```  
User clicks topic → POST /api/platform-chat (topic name)
→ tool_orchestrator detects 'topic_selected' stage
→ LLM generates first quiz question with show_selection tool
→ platform_tool_handler adds correct_answer via _detect_correct_answer()
→ Frontend renders quiz question
```

### **3. Quiz Answer Flow (CRITICAL)**
```
User answers → POST /api/platform-chat (answer)
→ tool_orchestrator detects 'quiz_active' stage
→ _extract_current_question_context() gets question from chat history
→ LLM evaluates with explicit question context
→ If WRONG: continuous_quiz_response with same question
→ If CORRECT: continuous_quiz_response with new question  
→ TTS generation for both phases
→ Frontend plays audio and renders next question
```

---

## ⚠️ **CRITICAL IMPLEMENTATION DETAILS**

### **1. Answer Validation Logic**
```python
# CRITICAL: LLM must have explicit question context
current_question_data = self._extract_current_question_context(chat_history)
enhanced_prompt += f"""
THE CURRENT QUESTION USER JUST ANSWERED:
QUESTION: "{current_question_data['question']}"
OPTIONS: {current_question_data['options']}
USER'S ANSWER: "{user_input}"

Use your knowledge to determine if the answer is correct for THIS SPECIFIC QUESTION.
"""
```

### **2. Question Context Extraction**  
```python
def _extract_current_question_context(self, chat_history: List[Dict]) -> Dict:
    # Find most recent quiz question from assistant messages
    for message in reversed(chat_history):
        if message.get('role') == 'assistant' and 'tools' in message:
            for tool in message['tools']:
                # Handle continuous_quiz_response (nested structure)
                if tool.get('type') == 'continuous_quiz_response':
                    phase2_tool = tool['data']['phase2']['tool']
                    if phase2_tool.get('type') == 'show_selection':
                        return phase2_tool['data']
                
                # Handle direct show_selection
                elif tool.get('type') == 'show_selection':
                    return tool['data']
    
    return {'question': 'unknown', 'options': [], 'correct_answer': ''}
```

### **3. Intelligent Correct Answer Detection**
```python
def _detect_correct_answer(self, question: str, options: List[str]) -> str:
    # Science patterns for dr_genie
    if "물이 0도 이하" in question:
        return next((opt for opt in options if "고체" in opt), options[0])
    elif "물의 화학식" in question:
        return next((opt for opt in options if "h2o" in opt.lower()), options[0])
    
    # History patterns for seol_min_seok  
    elif "세종대왕" in question:
        return next((opt for opt in options if "한글" in opt), options[0])
    elif "3·1 운동" in question:
        return next((opt for opt in options if "1919" in opt), options[0])
    
    return options[0]  # Fallback to first option
```

---

## 🚨 **KNOWN ISSUES & FIXES**

### **Issue 1: Wrong Answer Progression Fallback**
**Problem**: When user answers second question wrong, system falls back to first question instead of retrying second question.

**Root Cause**: LLM lacks explicit current question context.

**Solution**: Implemented `_extract_current_question_context()` and explicit prompting.

### **Issue 2: Missing Correct Answers**  
**Problem**: Quiz questions generated without correct_answer field, causing all answers to be marked wrong.

**Solution**: Added intelligent correct answer detection in `platform_tool_handler.py`.

### **Issue 3: TTS Compatibility**
**Problem**: Different TTS services have incompatible method signatures.

**Solution**: Added character_id parameter and **kwargs to all TTS methods.

---

## 📈 **PERFORMANCE & SCALING**

### **Response Time Targets**
- Initial greeting: < 500ms
- Topic selection: < 800ms  
- Quiz generation: < 1200ms
- Answer evaluation: < 1000ms

### **Concurrent Users**
- Session isolation via session_id
- Stateless LLM processing
- Async/await throughout pipeline

### **Caching Strategy**
- TTS audio caching (base64 URLs)
- Character prompt caching
- Session state in memory/Redis

---

## 🔧 **DEVELOPMENT & DEBUGGING**

### **Debug Scripts**
- `debug_wrong_answer_progression.py`: Test answer progression flow
- `debug_quiz_answer_validation.py`: Test answer validation logic
- `debug_correct_answer_progression.py`: Test correct answer flow
- `debug_character_greeting.py`: Compare TTS routing between characters

### **🚨 COMMON DEBUGGING SCENARIOS**

#### **Scenario 1: Character has no TTS audio**
**Symptoms**: Frontend shows "No TTS audio generated" or audio_url=false
**Debug Steps**:
1. Check server logs for TTS service routing:
   ```bash
   # Look for these log messages:
   🎭 Quiz character detected - using dedicated TTS service  # ✅ Good
   🎤 Regular TTS request - voice_id: xyz  # ❌ Wrong service
   ```
2. Verify both TTS endpoints route to same service:
   - `tool_orchestrator.py:139` character list
   - `main.py:1529` condition logic
3. Test direct TTS endpoint: `curl -X POST /api/tts -d '{"character_id":"your_character"}'`

#### **Scenario 2: Quiz progression fallback issue**
**Symptoms**: Wrong answer at question N falls back to question 1 instead of retrying question N
**Debug Steps**:
1. Check for hardcoded fallback patterns in `tool_orchestrator.py`
2. Look for `_extract_last_question_from_history` hardcoded text matching
3. Verify `_extract_current_question_context` returns proper tool data
4. Test with: `debug_wrong_answer_progression.py`

#### **Scenario 3: Server import caching issues**
**Symptoms**: Method signature errors, "unexpected keyword argument"  
**Debug Steps**:
1. Restart server completely: `kill uvicorn && python3 -m uvicorn main:app --reload`
2. Check method signatures: `python3 -c "from services.tts_service import TypecastTTSService; import inspect; print(inspect.signature(TypecastTTSService.generate_speech))"`
3. Always use `--reload` flag for development

### **Logging Points**
```python
logger.info(f"🚀 Platform chat: {user_input} for character {character_id}")
logger.info(f"🔍 QUIZ EVALUATION DEBUG: question={question}, answer={answer}")
logger.info(f"🎯 STAGE MATCH: {stage} + {context} detected!")
```

### **Key Metrics**
- Session success rate
- Quiz completion rate  
- Answer accuracy rate
- TTS generation success rate

---

This blueprint provides complete technical documentation for both character systems. Every file, flow, integration point, and critical implementation detail is documented for future development and maintenance.