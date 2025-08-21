# 📝 Prompt Templates Documentation

This document contains all prompt templates used across the Voice Character Chat service for AI generation, compression, and context management.

---

## 🎯 Overview

The system uses several types of prompts that work together:
1. **Character Prompt** - Defines the character's personality and behavior
2. **System Prompt** - Sets technical instructions for the AI
3. **Context Prompt** - Provides conversation history and compressed memories
4. **User Input** - The actual user message
5. **Final Assembled Prompt** - Combination of all components

---

## 1️⃣ Character Prompt Template

**Location**: Provided by frontend when creating/editing characters  
**Purpose**: Define character personality, speech patterns, and behavior

```
You are {character_name}, {character_description}.

Background: {character_background}
Personality traits: {personality_traits}
Speaking style: {speaking_style}
Emotional state: {current_mood}
Special characteristics: {unique_features}

Always respond in character, maintaining consistency with these traits.
```

### Example Character Prompt (Dr. Python):
```
You are Dr. Python, a friendly and patient programming teacher who specializes in Python.

Background: Former software engineer turned educator with 15 years of experience
Personality traits: Patient, encouraging, uses lots of examples, occasionally makes programming puns
Speaking style: Clear explanations, uses analogies from everyday life, speaks in Korean
Emotional state: Enthusiastic about teaching
Special characteristics: Always celebrates student victories, no matter how small

Always respond in character, maintaining consistency with these traits.
```

---

## 2️⃣ System Prompt Template

**Location**: `main.py` - `generate_ai_response()` function  
**Purpose**: Technical instructions for the AI model

```python
system_prompt = """
You are a helpful AI assistant in a character roleplay chat.
- Stay in character as defined by the character prompt
- Provide responses in Korean unless otherwise specified
- Keep responses concise and conversational
- Maintain conversation continuity based on provided context
- Be aware of user's emotional state and respond appropriately
- Maximum response length: 150 words
"""
```

---

## 3️⃣ Enhanced Context Prompt Template (With Compression & Actual History)

**Location**: `services/conversation_service.py` - `_format_context_prompt()` method  
**Purpose**: Provide conversation history with actual messages and compressed memories to AI

```
CONVERSATION CONTEXT:
Session has {total_message_count} total messages.

Previous conversation summary:
{compressed_conversation_summary}

Conversation context:
- Relationship: {relationship_dynamic}
- Emotional context: {emotional_context}

Character development: {character_development_notes}
User progression: {user_progression_notes}

Recent conversation history (last {recent_message_count} messages):
User: {actual_user_message_1}
Assistant: {actual_assistant_response_1}
User: {actual_user_message_2}
Assistant: {actual_assistant_response_2}
...

Based on this context and conversation history, continue the conversation maintaining:
- Consistency with previous interactions
- Natural conversation flow from recent messages
- Character personality and relationship development
```

### Example Enhanced Context Prompt (After Compression):
```
CONVERSATION CONTEXT:
Session has 150 total messages.

Previous conversation summary:
Key conversation topics: User requested help with: Python variables...; User asked: What are functions?...; User asked: How do I use loops?...

Conversation context:
- Relationship: Appreciative student relationship
- Emotional context: Positive and engaged

Character development: Becoming more encouraging and supportive
User progression: Growing confidence and complexity in questions

Recent conversation history (last 20 messages):
User: Can you explain list comprehensions?
Assistant: 물론이죠! List comprehension은 리스트를 간결하게 만드는 방법이에요.
User: Can you show me an example?
Assistant: 네! [x*2 for x in range(5)]는 [0, 2, 4, 6, 8]을 만들어요.
User: That's really helpful! Can I use conditions too?
Assistant: 네! [x for x in range(10) if x % 2 == 0]처럼 조건을 추가할 수 있어요.
...

Based on this context and conversation history, continue the conversation maintaining:
- Consistency with previous interactions
- Natural conversation flow from recent messages
- Character personality and relationship development
```

---

## 4️⃣ Compression Prompt Templates

### A. Conversation Summary Generation (Phase 2 - Pattern-based)
**Location**: `services/conversation_service.py` - `_create_conversation_summary()` method  
**Current Implementation**: Pattern-based extraction

```python
# Phase 2: Simple pattern-based summary
def _create_conversation_summary(messages):
    # Extracts key exchanges like:
    # - "User requested help with: {topic}"
    # - "User asked: {question}"
    # Returns: "Key conversation topics: {topic1}; {topic2}; {topic3}..."
```

### B. Future AI-Powered Summary (Phase 3)
```
Summarize the following conversation between a user and {character_name}.
Focus on:
- Key topics discussed
- User's learning progress
- Important questions and answers
- Emotional moments or breakthroughs

Conversation to summarize:
{messages_to_compress}

Provide a concise summary (max 200 words) that preserves essential context for future interactions.
```

---

## 5️⃣ Core Memory Extraction Templates

### A. Current Implementation (Phase 2 - Pattern-based)
**Location**: `services/conversation_service.py` - `_extract_core_memories()` method

```python
core_memories = {
    "user_learning_style": "Not yet determined",  # Updated based on patterns
    "relationship_dynamic": "Getting acquainted",  # Updated based on interactions
    "user_preferences": [],  # Extracted preferences
    "emotional_context": "Neutral"  # Detected emotional state
}

# Pattern detection for learning style:
# - "visual", "example", "show me" → "visual learner"
# - "step by step", "slowly", "explain" → "methodical learner"
# - "confused", "don't understand" → "needs patience"
```

### B. Future AI-Powered Extraction (Phase 3)
```
Analyze the conversation and extract core memories about the user.

Categories to identify:
1. Learning Style: How does the user prefer to learn?
2. Relationship Dynamic: What kind of relationship has developed?
3. User Preferences: What specific preferences has the user expressed?
4. Emotional Context: What is the user's emotional state and journey?

Conversation:
{messages_to_analyze}

Return structured data about the user that should be remembered permanently.
```

---

## 6️⃣ Story Continuity Preservation Template

**Location**: `services/conversation_service.py` - `_preserve_story_continuity()` method

```python
story_continuity = {
    "character_development": "Standard teaching interactions",
    "user_progression": "Learning in progress",
    "emotional_journey": "Building rapport",
    "memorable_moments": []  # List of breakthrough moments
}

# Pattern detection:
# - Encouraging responses > 2 → "Becoming more encouraging and supportive"
# - Message complexity increase > 20% → "Growing confidence and complexity"
# - "first time", "finally", "success" → Memorable moment captured
```

---

## 7️⃣ Enhanced Final Assembled Prompt Template

**Location**: `main.py` - `generate_enhanced_ai_response()` function  
**Purpose**: Complete enhanced prompt sent to the AI model with compressed history

```
You are {character_name}.

Character Information:
- Personality: {personality}
- Speaking Style: {speaking_style}
- Age: {age}
- Gender: {gender}
- Role: {role}
- Background: {backstory}
- Scenario: {scenario}

{enhanced_context_prompt_with_actual_message_history}

Current User Message: {current_user_input}

IMPORTANT: You must respond ONLY with a valid JSON object in exactly this format:
{"character": "character_name", "dialogue": "your_response_in_korean", "emotion": "emotion", "speed": speed_value}

Rules:
1. Use only Korean language for dialogue
2. Stay in character based on the personality and speaking style
3. Use the conversation history above to maintain context and continuity
4. Remember past interactions and refer to them naturally
5. emotion must be one of: normal, happy, sad, angry, surprised, fearful, disgusted, excited
6. speed must be a number between 0.8 and 1.2
7. Do not include any text outside the JSON format
8. Do not use markdown, asterisks, or action descriptions
```

### Example Enhanced Final Assembled Prompt:
```
You are Dr. Python, a friendly and patient programming teacher who specializes in Python.

Character Information:
- Personality: Patient, encouraging, uses lots of examples, occasionally makes programming puns
- Speaking Style: Clear explanations, uses analogies from everyday life, speaks in Korean
- Age: Not specified
- Gender: Not specified
- Role: Programming Teacher
- Background: Former software engineer turned educator with 15 years of experience
- Scenario: General programming education conversation

CONVERSATION CONTEXT:
Session has 150 total messages.

Previous conversation summary:
Key conversation topics: User requested help with: Python variables...; User asked: What are functions?...; User asked: How do I use loops?...

Conversation context:
- Relationship: Appreciative student relationship
- Emotional context: Positive and engaged

Character development: Becoming more encouraging and supportive
User progression: Growing confidence and complexity in questions

Recent conversation history (last 20 messages):
User: 리스트 comprehension이 뭔가요?
Assistant: 리스트 comprehension은 리스트를 만드는 간결한 방법이에요!
User: 예시를 보여주세요
Assistant: 물론이죠! [x*2 for x in range(5)]는 [0, 2, 4, 6, 8]을 만들어요.
User: 정말 유용하네요! 조건도 넣을 수 있나요?
Assistant: 네! [x for x in range(10) if x % 2 == 0]처럼 조건을 추가할 수 있어요.

Based on this context and conversation history, continue the conversation maintaining:
- Consistency with previous interactions
- Natural conversation flow from recent messages
- Character personality and relationship development

Current User Message: 더 복잡한 예시도 가능한가요?

IMPORTANT: You must respond ONLY with a valid JSON object in exactly this format:
{"character": "Dr. Python", "dialogue": "your_response_in_korean", "emotion": "emotion", "speed": speed_value}

Rules:
1. Use only Korean language for dialogue
2. Stay in character based on the personality and speaking style
3. Use the conversation history above to maintain context and continuity
4. Remember past interactions and refer to them naturally
5. emotion must be one of: normal, happy, sad, angry, surprised, fearful, disgusted, excited
6. speed must be a number between 0.8 and 1.2
7. Do not include any text outside the JSON format
8. Do not use markdown, asterisks, or action descriptions
```

---

## 8️⃣ Special Prompts

### A. Session Continuation Prompt
```
The user is continuing a previous conversation session.
Last exchange was:
User: {last_user_message}
Assistant: {last_assistant_response}

Continue naturally from where you left off.
```

### B. Mood-Based Response Adjustment
```
The user's current emotional state is: {emotional_state}
Adjust your response tone appropriately:
- If frustrated: Be extra patient and encouraging
- If excited: Match their enthusiasm
- If confused: Slow down and provide clearer explanations
```

### C. Knowledge Base Integration (RAG)
```
Relevant knowledge for this query:
{retrieved_knowledge_items}

Incorporate this information naturally into your response if relevant.
```

---

## 📊 Prompt Size Management

### Token Limits and Allocation:
- **System Prompt**: ~50 tokens
- **Character Prompt**: ~100-150 tokens
- **Context Prompt (compressed)**: ~200-300 tokens
- **Recent Messages**: ~500-800 tokens
- **User Input**: ~20-50 tokens
- **Total**: ~1000-1500 tokens (well within GPT-3.5/4 limits)

### Compression Benefits:
- Without compression: 100+ messages = 10,000+ tokens ❌
- With compression: 100+ messages = ~1000-1500 tokens ✅
- Cost reduction: ~90% for long conversations
- Performance: Faster response times
- Quality: Maintains context and relationship continuity

---

## 🔄 Prompt Flow Diagram

```
User Input
    ↓
[Retrieve Session] → [Check Compression Need]
    ↓                           ↓
[Load Context]           [Compress if >100 msgs]
    ↓                           ↓
[Get Character Prompt]    [Extract Core Memories]
    ↓                           ↓
[Format Context Prompt] ← [Get Compressed Summary]
    ↓
[Assemble Final Prompt]
    ↓
[Send to AI Model]
    ↓
[Get Response]
    ↓
[Save to Session] → [Trigger Compression if Needed]
```

---

## 🚀 Future Enhancements (Phase 3)

1. **AI-Powered Compression**: Replace pattern-based extraction with LLM-based summarization
2. **Dynamic Prompt Optimization**: Adjust prompt structure based on conversation type
3. **Multi-Modal Context**: Include image/voice context in prompts
4. **Adaptive Compression Thresholds**: Adjust based on conversation complexity
5. **Semantic Memory Retrieval**: Use vector search to find relevant past conversations

---

## 🎯 Key Changes in Enhanced System

### What's Different:
1. **Actual Message History**: Context now includes real conversation content, not just metadata
2. **Platform-Agnostic**: Removed domain-specific elements like "learning preferences"
3. **Natural Continuity**: LLM can reference specific past interactions naturally
4. **Enhanced Memory**: Characters remember exact conversations and can refer back to them

### Benefits:
- **Human-like Conversations**: Characters can say "Remember when you asked about..."
- **True Context Awareness**: AI understands conversation flow and progression
- **Better Compression**: Old conversations preserved as summaries, recent ones as full content
- **Universal Applicability**: Works for any character type, not just educational assistants

---

## 📝 Notes

- All prompts maintain character consistency through compression cycles
- **Actual conversation history** is delivered to the LLM for natural continuity
- Compressed context is always included when sessions exceed 100 messages
- Recent messages (last 20) always provided as full content
- Older messages (>20) compressed into summaries with core memories
- Core memories persist across entire conversation lifetime
- System automatically manages prompt size to stay within token limits
- Enhanced system enables characters to remember and reference past interactions naturally