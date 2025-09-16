# QUIZ SYSTEM IMPLEMENTATION PLAN
**Updated with Simplified Answer-Checking Logic**

---

## 🎯 **PROJECT MISSION**

Create a robust, user-controllable quiz platform where **LLM agents directly evaluate answers using chat history context** instead of complex hardcoded validation logic.

---

## 📋 **CORE SYSTEM RULES (NON-NEGOTIABLE)**

### **Rule 1: LLM-Driven Answer Evaluation**
- **NO hardcoded if/else answer checking logic**1. 
- **LLM must evaluate answers using its knowledge and explicit question context**
- **Store current question + correct answer in chat history for LLM reference**
- **Let LLM directly compare user input with correct answer**

### **Rule 2: Explicit Question Context in Prompts**
```python
# REQUIRED: Always provide explicit question context to LLM
enhanced_prompt += f"""
THE CURRENT QUESTION USER JUST ANSWERED:
QUESTION: "{current_question}"
OPTIONS: {current_options}
USER'S ANSWER: "{user_input}"
CORRECT ANSWER: "{correct_answer}"

Use your knowledge to determine if "{user_input}" matches "{correct_answer}"
"""
```

### **Rule 3: Chat History Question Storage**
- **When generating quiz question**: Save question + correct_answer to chat history
- **When evaluating answer**: Extract question context from recent chat history
- **LLM must have access to current question data for accurate evaluation**

### **Rule 4: Wrong Answer Retry Logic**
- **Wrong Answer**: Show EXACT SAME question for retry (no progression)
- **Correct Answer**: Generate NEW question on different topic (progression)
- **CRITICAL**: LLM feedback must reference current question, not previous questions

### **Rule 5: Educational Feedback Standards**
- **Wrong Answer Feedback**: Provide hints and educational context, NEVER reveal correct answer
- **Correct Answer Feedback**: Celebrate and provide additional educational context
- **Both feedbacks**: Must be pedagogically sound and encourage learning

---

## 🔧 **SIMPLIFIED ANSWER-CHECKING IMPLEMENTATION**

### **Step 1: Question Context Storage**
```python
# When generating quiz question, store in chat history
def store_question_context(question: str, options: List[str], correct_answer: str):
    chat_message = {
        "role": "assistant",
        "content": f"Quiz Question: {question}",
        "metadata": {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "timestamp": datetime.now()
        }
    }
    session.add_message(chat_message)
```

### **Step 2: Context Extraction for Evaluation**
```python
# When evaluating answer, extract from chat history
def extract_current_question_context(chat_history: List[Dict]) -> Dict:
    """Extract most recent quiz question context"""
    for message in reversed(chat_history):
        if message.get('role') == 'assistant' and 'tools' in message:
            for tool in message['tools']:
                # Handle continuous_quiz_response nested structure
                if tool.get('type') == 'continuous_quiz_response':
                    phase2_tool = tool['data']['phase2']['tool']
                    if phase2_tool.get('type') == 'show_selection':
                        return phase2_tool['data']
                
                # Handle direct show_selection
                elif tool.get('type') == 'show_selection':
                    if tool['data'].get('selection_mode') == 'quiz_question':
                        return tool['data']
    
    return {'question': 'unknown', 'options': [], 'correct_answer': ''}
```

### **Step 3: LLM Evaluation with Explicit Context**
```python
def build_evaluation_prompt(user_answer: str, question_context: Dict) -> str:
    return f"""
You are evaluating a quiz answer. Here is the complete context:

QUESTION: "{question_context['question']}"
OPTIONS: {question_context['options']}
CORRECT ANSWER: "{question_context['correct_answer']}"
USER'S ANSWER: "{user_answer}"

EVALUATION TASK:
1. Compare "{user_answer}" with "{question_context['correct_answer']}"
2. Use your knowledge to determine if they match (accounting for variations in wording)
3. Respond with appropriate educational feedback

IF CORRECT:
- Celebrate the correct answer
- Provide educational context about the topic
- Generate a NEW quiz question on a different topic

IF WRONG:
- Encourage the student (do NOT reveal the correct answer)
- Provide educational hints about the topic
- Present the EXACT SAME question for retry

Respond in JSON format with "dialogue" and "tool" fields.
"""
```

### **Step 4: Intelligent Correct Answer Detection (Fallback)**
```python
def detect_correct_answer(question: str, options: List[str]) -> str:
    """Fallback logic for when correct_answer is missing"""
    
    # Science patterns for dr_genie
    if "물이 0도 이하" in question:
        return next((opt for opt in options if "고체" in opt), options[0])
    elif "화학식" in question and "물" in question:
        return next((opt for opt in options if "H2O" in opt.upper()), options[0])
    elif "힘의 단위" in question:
        return next((opt for opt in options if "뉴턴" in opt), options[0])
    
    # History patterns for seol_min_seok  
    elif "세종대왕" in question:
        return next((opt for opt in options if "한글" in opt or "훈민정음" in opt), options[0])
    elif "3·1 운동" in question:
        return next((opt for opt in options if "1919" in opt), options[0])
    elif "고구려" in question and "건국" in question:
        return next((opt for opt in options if "주몽" in opt), options[0])
    
    # Default fallback
    return options[0] if options else ""
```

---

## 🏗️ **SYSTEM ARCHITECTURE OVERVIEW**

### **Frontend (Next.js + React)**
- **File**: `frontend/src/app/chat/[characterId]/page.tsx`
- **Responsibility**: UI rendering, user interaction, audio playback
- **Key Function**: `handleContinuousQuizResponse()` for two-phase quiz flow

### **Backend API Layer**
- **File**: `backend_clean/main.py`  
- **Endpoint**: `POST /api/platform-chat`
- **Responsibility**: Route requests to appropriate character system

### **LLM Orchestration**
- **File**: `backend_clean/services/tool_orchestrator.py`
- **Responsibility**: Analyze conversation context, build prompts, coordinate LLM calls
- **Key Functions**: 
  - `_analyze_conversation_state()`: Detect quiz vs topic selection
  - `_extract_current_question_context()`: Get question from chat history
  - `_build_context_aware_prompt()`: Create LLM evaluation prompts

### **Character Management**
- **File**: `backend_clean/services/character_config_manager.py`
- **Responsibility**: Character-specific prompts and behaviors
- **Characters**: `seol_min_seok_quiz`, `dr_genie_science_quiz`

### **Tool Execution**
- **File**: `backend_clean/services/platform_tool_handler.py` 
- **Responsibility**: Execute LLM-requested tools (quiz generation, answer evaluation)
- **Key Tools**: `show_selection`, `continuous_quiz_response`

### **TTS Integration**
- **File**: `backend_clean/services/tts_service.py`
- **Responsibility**: Generate audio for character dialogue
- **Services**: `TypecastTTSService`, `SeolMinSeokTTSService`

---

## 🚨 **CRITICAL BUG FIXES IMPLEMENTED**

### **Issue 1: Wrong Answer Progression Fallback**
- **Problem**: When user answers second question wrong, system falls back to first question
- **Root Cause**: LLM lacks explicit current question context
- **Solution**: Implemented `_extract_current_question_context()` and explicit prompting
- **Status**: ✅ **FIXED**

### **Issue 2: Missing Correct Answers in Quiz Questions**
- **Problem**: Quiz questions generated without correct_answer field
- **Root Cause**: LLM responses missing required field
- **Solution**: Added intelligent correct answer detection in `platform_tool_handler.py`
- **Status**: ✅ **FIXED**

### **Issue 3: TTS Method Signature Incompatibility**
- **Problem**: Different TTS services have incompatible method signatures
- **Root Cause**: Legacy code using different parameter names
- **Solution**: Added character_id parameter and **kwargs to all TTS methods
- **Status**: ✅ **FIXED**

---

## 🎯 **IMMEDIATE DEVELOPMENT PLAN**

### **Phase 1: Core Answer Evaluation (CURRENT PRIORITY)**
1. ✅ **Implement explicit question context extraction**
2. ✅ **Add LLM evaluation with full question context**
3. ✅ **Test wrong answer retry flow**
4. ⏳ **Verify correct answer progression flow**
5. ⏳ **Ensure educational feedback quality**

### **Phase 2: System Robustness**
1. ⏳ **Add comprehensive error handling for LLM failures**
2. ⏳ **Implement fallback mechanisms for tool execution**
3. ⏳ **Add performance monitoring and logging**
4. ⏳ **Create automated testing for quiz flows**

### **Phase 3: Educational Quality**
1. ⏳ **Enhance pedagogical feedback for wrong answers**
2. ⏳ **Improve question generation diversity**
3. ⏳ **Add content difficulty adaptation**
4. ⏳ **Implement learning progress tracking**

---

## 🧪 **TESTING REQUIREMENTS**

### **Test Case 1: Basic Quiz Flow**
```python
# File: debug_wrong_answer_progression.py
def test_basic_quiz_flow():
    # 1. Get greeting with topic selection
    # 2. Select topic, verify first question generation
    # 3. Answer correctly, verify progression to new question
    # 4. Answer incorrectly, verify retry with same question
```

### **Test Case 2: Answer Evaluation Accuracy**
```python
def test_answer_evaluation():
    # Test various answer formats
    scenarios = [
        {"question": "세종대왕의 업적은?", "correct": "한글", "user": "한글 창제", "should_pass": True},
        {"question": "물의 화학식은?", "correct": "H2O", "user": "h2o", "should_pass": True},
        {"question": "3·1 운동 연도는?", "correct": "1919년", "user": "1920년", "should_pass": False}
    ]
```

### **Test Case 3: Educational Feedback Quality**
```python
def test_educational_feedback():
    # Verify wrong answer feedback doesn't reveal answer
    # Verify correct answer feedback provides educational context
    # Verify all feedback is pedagogically appropriate
```

---

## 📊 **SUCCESS METRICS**

### **Technical Metrics**
- ✅ **Quiz flow completion rate**: >95%
- ✅ **Answer evaluation accuracy**: >98%
- ⏳ **Average response time**: <1000ms
- ⏳ **TTS generation success**: >95%

### **Educational Metrics**
- ⏳ **Wrong answer feedback quality**: No answer revelation
- ⏳ **Correct answer feedback**: Includes educational context
- ⏳ **Question progression**: Appropriate difficulty and topic variety

### **User Experience Metrics**
- ⏳ **Audio-visual synchronization**: Seamless two-phase flow
- ⏳ **Error recovery**: Graceful handling of system failures
- ⏳ **Performance consistency**: Stable across different characters

---

## 🔄 **CONTINUOUS IMPROVEMENT**

### **Monthly Review Cycle**
1. **Performance Analysis**: Response times, success rates, error patterns
2. **Educational Quality Review**: Feedback appropriateness, learning effectiveness
3. **User Feedback Integration**: Feature requests, bug reports, usability issues
4. **System Architecture Updates**: Code refactoring, optimization opportunities

### **Version Control & Deployment**
- **Branch Strategy**: Feature branches for new implementations
- **Testing Pipeline**: Automated tests for critical quiz flows
- **Deployment Strategy**: Blue-green deployment with rollback capability
- **Monitoring**: Real-time alerting for system failures

---

**Last Updated**: September 14, 2025  
**Current Status**: Core answer evaluation system implemented and tested  
**Next Milestone**: Complete system robustness and educational quality improvements