# Quiz Character Implementation Checklist

This checklist ensures complete implementation when adding new quiz characters. Follow every step to avoid missing character-specific logic that would cause the character to fail.

## ✅ **MANDATORY CHECKLIST FOR NEW QUIZ CHARACTERS**

### **📋 1. Character Definition (Frontend)**

#### **1.1 Character Data Structure**
- [ ] Add character to `frontend/src/data/demo-characters.ts`
- [ ] Include all required fields:
  ```typescript
  {
    id: 'your_quiz_character_id',
    name: 'Character Display Name',
    description: 'Character description for quiz specialty',
    image: '/images/character_image.png',
    prompt: `<critical_instructions>...quiz_priority>이 캐릭터는 **퀴즈 위주의 상호작용**을 전문으로 합니다...`,
    greetings: [
      '안녕하세요! 저는 [캐릭터명]입니다. [과목] 퀴즈로 함께 공부해볼까요?'
    ],
    voice_id: 'appropriate_voice_id',
    created_at: new Date('YYYY-MM-DD'),
    updated_at: new Date('YYYY-MM-DD'),
    category: 'quiz'
  }
  ```

### **📋 2. Backend Character Configuration**

#### **2.1 Character Config Manager**
- [ ] Add character to `backend_clean/services/character_config_manager.py`
- [ ] Include character in content configuration:
  ```python
  your_character_config = CharacterContentConfig(
      character_id="your_quiz_character_id",
      content_types={"quiz": quiz_content_type},  # or science_quiz, etc.
      classification_strategy="hybrid",
      global_confidence_threshold=0.7,
      fallback_strategy="adaptive",
      learning_enabled=True
  )
  self._configs["your_quiz_character_id"] = your_character_config
  ```

#### **2.2 Character Prompt Manager**
- [ ] Add character prompt to `backend_clean/services/character_prompt_manager.py`
- [ ] Add method for character-specific prompt:
  ```python
  def _get_your_subject_quiz_prompt(self) -> str:
      """Your character quiz prompt with enhanced requirements"""
      return """You are [Character Name], an enthusiastic [subject] teacher...
      
      TOOL USAGE INSTRUCTIONS:
      When user answers quiz questions:
      - If CORRECT: Celebrate specifically, provide educational content, use "show_selection" tool with NEW question
      - If WRONG: Encourage without revealing answer, provide hints, use "show_selection" tool with SAME question
      """
  ```
- [ ] Include character in prompt mapping:
  ```python
  "your_quiz_character_id": self._get_your_subject_quiz_prompt()
  ```

### **📋 3. TTS and Audio Integration**

#### **3.1 Tool Orchestrator TTS Routing**
- [ ] Add character to `backend_clean/services/tool_orchestrator.py` TTS lists:
  ```python
  if character_id in ["seol_min_seok_quiz", "dr_genie_science_quiz", "your_quiz_character_id"]:
  ```
  **LOCATIONS TO UPDATE:**
  - Line ~150: Main TTS character detection
  - Line ~170: Phase 1 TTS routing  
  - Line ~180: Phase 2 TTS routing

#### **3.2 Continuous Answer Tool TTS**
- [ ] Add character to `backend_clean/services/continuous_answer_tool.py` TTS arrays:
  ```python
  if flow_state.character_id in ['seol_min_seok', 'seol_min_seok_quiz', 'kim_daehyun_history', 'seolminseok_korean_history_chat', 'dr_genie_science_quiz', 'your_quiz_character_id']:
  ```
  **LOCATIONS TO UPDATE:**
  - Line ~400: Regular TTS generation
  - Line ~450: LLM response with tools TTS
  - Line ~500: Retry response TTS

#### **3.3 Continuous Answer Tool Clean TTS**
- [ ] Add character to `backend_clean/services/continuous_answer_tool_clean.py`:
  ```python
  if character_id in ['seol_min_seok_quiz', 'seolminseok_korean_history_chat', 'dr_genie_science_quiz', 'your_quiz_character_id']:
  ```

### **📋 4. Quiz Flow Configuration**

#### **4.1 Continuous Flow Character Lists**
- [ ] Add character to flow configurations in `backend_clean/services/continuous_answer_tool.py`:
  ```python
  "character_types": ["seol_min_seok_quiz", "seolminseok_korean_history_chat", "kim_daehyun_history", "history_teacher", "dr_genie_science_quiz", "your_quiz_character_id"]
  ```
  **FLOW CONFIGURATIONS TO UPDATE:**
  - `quiz_continuous_v1` flow
  - `quiz_feedback_continuous_v1` flow
  - `show_selection_v1` flow

#### **4.2 Character Name Mapping**
- [ ] Add character to name mapping in `backend_clean/services/continuous_answer_tool.py`:
  ```python
  def _get_character_name(self, character_id: str) -> str:
      name_mapping = {
          "seol_min_seok_quiz": "설민석",
          "dr_genie_science_quiz": "닥터 지니",
          "your_quiz_character_id": "Your Character Display Name"
      }
  ```

### **📋 5. Character-Specific Logic**

#### **5.1 Greeting Suggestions**
- [ ] Add character to `backend_clean/services/greeting_suggestion_generator.py`:
  ```python
  elif character_id == 'your_quiz_character_id':
      # Subject-specific quiz topics
      return [
          'Topic 1 퀴즈',
          'Topic 2 퀴즈',
          'Topic 3 퀴즈',
          '랜덤 퀴즈'
      ]
  ```

#### **5.2 Educational Quiz Flow**
- [ ] Add character to `backend_clean/services/educational_quiz_flow.py`:
  ```python
  elif character_id == "your_quiz_character_id":
      if is_correct:
          feedback_templates = [
              f"정답입니다! 정말 훌륭해요! {educational_content} [과목]을 이렇게 잘 이해하고 계시니 정말 기쁩니다!",
              f"맞습니다! 훌륭한 선택이에요! {educational_content} [과목] 공부가 정말 잘 되고 있는 것 같아요!",
              f"바로 그거예요! 정말 좋습니다! {educational_content} 이런 식으로 계속 공부하면 전문가가 될 수 있겠어요!"
          ]
      else:
          raise Exception(f"Educational quiz template system disabled - must use LLM")
      return random.choice(feedback_templates)
  ```

#### **5.3 Optimized Prompt Builder**
- [ ] Add character to `backend_clean/services/optimized_prompt_builder.py`:
  ```python
  elif character_id == "your_quiz_character_id":
      character_specific_section = """

  🎯 [SUBJECT] QUIZ CHARACTER SPECIAL INSTRUCTIONS:
  When the user requests a quiz or asks you to create questions:
  - ALWAYS format quiz questions in this EXACT structure: "Question? A) Option1 B) Option2 C) Option3 D) Option4"
  - Include exactly 4 options labeled with A), B), C), D)
  - Make sure there is a clear question ending with "?"
  - Choose academically accurate correct answers based on your knowledge
  - Focus on [subject] topics ([topic1], [topic2], etc.)
  - Examples:
    * "다음 중 [concept]은? A) [option1] B) [option2] C) [option3] D) [option4]"
    * "[Question about topic]? A) [answer1] B) [answer2] C) [answer3] D) [answer4]"

  CRITICAL: This A/B/C/D format is required for the quiz UI to work properly!"""
  ```

### **📋 6. Knowledge Base (Optional)**

#### **6.1 Knowledge Files**
- [ ] Create knowledge directory: `backend_clean/knowledge/characters/your_quiz_character_id/`
- [ ] Add knowledge.json with subject-specific content:
  ```json
  {
    "character_id": "your_quiz_character_id",
    "knowledge_items": [
      {
        "id": "knowledge_1",
        "title": "Topic 1 Fundamentals",
        "content": "Detailed explanation...",
        "tags": ["topic1", "fundamentals"]
      }
    ]
  }
  ```

### **📋 7. Testing and Validation**

#### **7.1 Backend API Testing**
- [ ] Test greeting generation: Empty user_input to `/api/platform-chat`
- [ ] Test topic selection: Send topic name to `/api/platform-chat`  
- [ ] Test correct answer: Send correct option to `/api/platform-chat`
- [ ] Test wrong answer: Send incorrect option to `/api/platform-chat`
- [ ] Verify TTS audio generation in all scenarios
- [ ] Verify tool generation and quiz progression

#### **7.2 Frontend Integration Testing** 
- [ ] Test character loading in browser
- [ ] Test greeting display and audio playback
- [ ] Test quiz topic selection UI
- [ ] Test quiz question display and interaction
- [ ] Test answer feedback and progression
- [ ] Test complete quiz flow without errors

#### **7.3 Comprehensive Flow Testing**
- [ ] Run character comparison test with existing quiz characters
- [ ] Verify identical behavior patterns with working characters
- [ ] Test session persistence and memory
- [ ] Verify error handling and fallback scenarios

### **📋 8. Common Pitfalls to Avoid**

#### **8.1 Missing Character ID References**
- [ ] **CRITICAL**: Search entire codebase for hardcoded character arrays
- [ ] Use command: `grep -r "seol_min_seok_quiz\|dr_genie_science_quiz" backend_clean/`
- [ ] Add your character to ALL arrays found in the search results
- [ ] Double-check TTS routing, flow configurations, and name mappings

#### **8.2 Incomplete TTS Integration**
- [ ] **CRITICAL**: Verify character appears in ALL TTS routing logic
- [ ] Test audio generation in greeting, feedback, and progression scenarios
- [ ] Ensure character uses correct TTS service (SeolMinSeokTTSService vs default)

#### **8.3 Missing Flow Configurations**
- [ ] **CRITICAL**: Verify character in ALL continuous flow character_types arrays
- [ ] Test quiz answer processing and tool generation
- [ ] Verify both correct and incorrect answer handling

#### **8.4 Frontend-Backend Mismatch**
- [ ] **CRITICAL**: Ensure character_id matches exactly between frontend and backend
- [ ] Verify character prompt includes quiz-specific instructions
- [ ] Test complete end-to-end flow from browser to backend

## ⚠️ **VALIDATION CHECKLIST**

Before deploying a new quiz character, verify:

- [ ] Character loads without errors in browser
- [ ] Greeting plays with TTS audio
- [ ] Quiz topics display correctly
- [ ] Quiz questions format properly (A/B/C/D structure)
- [ ] Correct answers provide positive feedback + new question
- [ ] Wrong answers provide hints + same question retry
- [ ] Audio plays for all responses
- [ ] No console errors or exceptions
- [ ] Character behaves identically to existing quiz characters

## 🔧 **DEBUG COMMANDS**

```bash
# Search for character references
grep -r "your_character_id" backend_clean/

# Test character endpoints
python3 test_character_comparison.py

# Monitor backend logs
tail -f backend_logs

# Test specific character flow
curl -X POST http://localhost:8001/api/platform-chat \
  -H "Content-Type: application/json" \
  -d '{"user_input": "", "character_id": "your_character_id", "user_id": "test"}'
```

---

**REMEMBER**: Every quiz character must be added to ALL character-specific arrays and configurations. Missing even one reference will cause failures. Use this checklist religiously to ensure complete implementation.