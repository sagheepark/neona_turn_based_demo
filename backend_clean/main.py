from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AzureOpenAI
import json
import random
import os
from dotenv import load_dotenv
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

load_dotenv()

# Session-Aware Chat Models - Moved to top to avoid forward reference issues
class ChatWithSessionRequest(BaseModel):
    message: str
    character_prompt: str
    character_id: str
    user_id: str                    # NEW: User identification
    session_id: Optional[str] = None       # NEW: Session continuation
    voice_id: Optional[str] = None
    persona_id: Optional[str] = None

class ChatWithSessionResponse(BaseModel):
    character: str
    dialogue: str
    emotion: str = "neutral"
    speed: float = 1.0
    audio: Optional[str] = None
    session_id: str                 # NEW: Session identification
    message_count: int              # NEW: Conversation progress
    session_summary: Optional[str] = None    # NEW: Story progression context
    tools: Optional[List[Dict[str, Any]]] = None  # NEW: Tool-based interactions

# Import services after loading environment
from services.tts_service import tts_service
from services.stt_service import stt_service
from services.voice_recommend_service import voice_recommend_service
from services.seolminseok_tts_service import seolminseok_tts_service

# 🚀 PLATFORM-GRADE HELPER FUNCTIONS
async def create_session_with_auto_greeting(request: ChatWithSessionRequest):
    """Smart session creation with automatic character greeting"""
    # Create session
    session_data = conversation_service.create_session(
        request.user_id, 
        request.character_id, 
        request.persona_id
    )
    session_id = session_data["session_id"]
    
    # Get character for greeting
    character = await character_service.get_character(request.character_id)
    
    # Auto-generate greeting based on character
    if character and character.get('greetings'):
        greeting = character['greetings'][0]  # Use first greeting
        
        # Store greeting in session
        conversation_service.add_message_to_session(session_id, "user", "안녕하세요", request.user_id)
        conversation_service.add_message_to_session(session_id, "assistant", greeting, request.user_id)
        
        # Generate greeting tools if needed (for quiz characters)
        tools = None
        if 'quiz' in request.character_id:  # Generic quiz character detection
            from services.greeting_suggestion_generator import GreetingSuggestionGenerator
            greeting_generator = GreetingSuggestionGenerator()
            suggestions = greeting_generator.generate_greeting_suggestions({
                "character_id": request.character_id,
                "greeting_message": greeting,
                "character_personality": "교육적이고 친근한 역사 튜터",
                "suggestions_enabled": True
            })
            tools = [{
                "type": "show_selection",
                "data": {
                    "items": suggestions,
                    "question": "어떤 퀴즈로 시작할까요?"
                }
            }]
        
        # Generate TTS for greeting
        audio_base64 = None
        try:
            if 'quiz' in request.character_id:  # Generic quiz character detection
                print(f"🎵 Generating TTS for quiz character greeting (helper)")
                audio_base64 = await seolminseok_tts_service.generate_tts(greeting)
                
                # No fallback - keep 설민석's unique voice
                if audio_base64 is None:
                    print(f"⚠️ Seolminseok TTS failed, continuing without audio")
            else:
                audio_response = await tts_service.generate_speech(greeting, request.voice_id or "duke")
                audio_base64 = audio_response.get("audio")
        except Exception as e:
            print(f"TTS generation failed in helper: {e}")
            audio_base64 = None
        
        return ChatWithSessionResponse(
            character=request.character_id,
            dialogue=greeting,
            emotion="happy",
            speed=1.0,
            audio=audio_base64,
            session_id=session_id,
            message_count=1,
            session_summary="",
            tools=tools
        )
    
    # Fallback to basic greeting
    return ChatWithSessionResponse(
        character=request.character_id,
        dialogue="안녕하세요! 무엇을 도와드릴까요?",
        emotion="happy",
        speed=1.0,
        audio=None,
        session_id=session_id,
        message_count=1,
        session_summary=""
    )

def parse_quiz_answer(user_message: str, question_text: str) -> Dict[str, Any]:
    """Parse user's quiz choice and map to question options"""
    import re
    
    # Extract user choice (A, B, C, D, 1, 2, 3, 4)
    user_choice = None
    choice_patterns = [
        r'([A-D])\)',  # A), B), C), D)
        r'([1-4])\.',  # 1., 2., 3., 4.
        r'([1-4])\)',  # 1), 2), 3), 4)
        r'([A-D])',    # A, B, C, D
        r'([1-4])'     # 1, 2, 3, 4
    ]
    
    for pattern in choice_patterns:
        match = re.search(pattern, user_message)
        if match:
            user_choice = match.group(1)
            break
    
    if not user_choice:
        return {"error": "Could not parse user choice"}
    
    # Extract all options from question
    options = []
    option_patterns = [
        r'([1-4])\.\s*(\S+)',  # 1. option text (simple word capture)
        r'([1-4])\)\s*(\S+)',  # 1) option text (simple word capture) 
        r'([A-D])\)\s*(\S+)'   # A) option text (simple word capture)
    ]
    
    for pattern in option_patterns:
        matches = re.findall(pattern, question_text)
        if matches:
            options = matches
            break
    
    if not options:
        return {"error": "Could not parse question options"}
    
    # Map user choice to option content
    choice_mapping = {}
    for i, (choice_key, option_text) in enumerate(options):
        choice_mapping[choice_key] = option_text.strip()
        # Also map numeric/letter equivalents
        if choice_key.isdigit():
            letter = chr(ord('A') + int(choice_key) - 1)
            choice_mapping[letter] = option_text.strip()
        else:
            number = str(ord(choice_key) - ord('A') + 1)
            choice_mapping[number] = option_text.strip()
    
    user_option_text = choice_mapping.get(user_choice)
    if not user_option_text:
        return {"error": f"Invalid choice {user_choice}"}
    
    return {
        "user_choice": user_choice,
        "user_option_text": user_option_text,
        "all_options": choice_mapping,
        "question_text": question_text
    }

def build_educational_quiz_prompt(character_name: str, conversation_history: list, user_message: str) -> str:
    """
    Build educational quiz prompt using structured logic and EducationalQuizFlow
    """
    
    # Analyze conversation to detect quiz context
    last_assistant_msg = None
    last_question = None
    
    for msg in reversed(conversation_history):
        if msg.startswith("assistant:") and not last_assistant_msg:
            last_assistant_msg = msg.replace("assistant:", "").strip()
            # Check if this message contains a quiz question
            if any(marker in last_assistant_msg for marker in ["1.", "2.", "3.", "4.", "1)", "2)", "3)", "4)", "A)", "B)", "C)", "D)"]):
                last_question = last_assistant_msg
                break
    
    # Check if user is answering a quiz question
    is_quiz_answer = any(marker in user_message for marker in ["1.", "2.", "3.", "4.", "1)", "2)", "3)", "4)", "A)", "B)", "C)", "D)"])
    
    print(f"🔍 DEBUG: is_quiz_answer={is_quiz_answer}, last_question={last_question is not None}")
    print(f"🔍 DEBUG: user_message='{user_message}'")
    
    if is_quiz_answer and last_question:
        # Parse the user's answer choice
        parsed_answer = parse_quiz_answer(user_message, last_question)
        
        if "error" in parsed_answer:
            # Handle parsing error
            return f"""당신은 {character_name} 역사 선생님입니다. 
            
사용자가 "{user_message}"라고 답했지만, 선택지 형식이 명확하지 않습니다. 
"1", "2", "3", "4" 또는 "A", "B", "C", "D" 형태로 답변해주세요.

{last_question}"""
        
        # Use EducationalQuizFlow for structured processing
        try:
            from services.educational_quiz_flow import EducationalQuizFlow
            quiz_flow = EducationalQuizFlow()
            
            # Create question data structure for educational flow
            question_data = {
                "question": parsed_answer["question_text"],
                "correct_answer": "A) 한글 창제",  # This should be determined dynamically
                "topic": "조선시대",
                "educational_context": {
                    "why_correct": "세종대왕은 1443년 한글(훈민정음)을 창제하여 백성들이 쉽게 글을 배울 수 있도록 했습니다.",
                    "why_wrong": {
                        "B": "불교 장려는 고려시대의 특징입니다.",
                        "C": "몽골 침입은 고려시대 사건입니다.", 
                        "D": "일제강점은 1910-1945년 시기입니다."
                    },
                    "hint": "세종대왕 하면 가장 먼저 떠오르는 문화적 업적을 생각해보세요."
                }
            }
            
            # For now, use simple correct answer detection
            # TODO: Implement proper answer validation logic
            user_full_answer = f"{parsed_answer['user_choice']}) {parsed_answer['user_option_text']}"
            
            # Simple correctness check (this should be improved with proper answer key)
            is_correct = "이성계" in parsed_answer['user_option_text'] or "한글" in parsed_answer['user_option_text']
            
            if is_correct:
                return f"""당신은 {character_name} 역사 선생님입니다.

정답입니다! 훌륭해요! 

{parsed_answer['user_option_text']}이(가) 맞습니다. 

[교육적 설명 제공 후 새로운 문제 출제]

다음 문제입니다:
세종대왕이 한글을 창제한 연도는?
1. 1443년
2. 1453년  
3. 1463년
4. 1473년

정답을 골라보세요!"""
            
            else:
                return f"""당신은 {character_name} 역사 선생님입니다.

아쉽지만 틀렸어요! 하지만 괜찮습니다. 

선택하신 "{parsed_answer['user_option_text']}"은(는) 정답이 아닙니다.
[교육적 힌트와 설명]

다시 한 번 도전해보세요!

{last_question}"""
                
        except ImportError:
            # Fallback if EducationalQuizFlow is not available
            return f"""당신은 {character_name} 역사 선생님입니다. 
            
사용자가 "{parsed_answer['user_choice']}번 {parsed_answer['user_option_text']}"을(를) 선택했습니다.

교육적 피드백을 제공하고 적절히 응답하세요."""
    
    else:
        # Normal conversation or quiz start
        return f"""당신은 {character_name} 역사 선생님입니다. 열정적이고 재미있게 한국사를 가르치는 교육자입니다.

사용자와 재미있는 한국사 퀴즈를 진행하세요:
- 친근하고 열정적인 말투 사용
- 퀴즈를 시작하려면 4지선다 문제 제시
- 교육적이면서도 재미있게 설명

IMPORTANT - Tool Output Format:
When providing quiz questions or interactive content, you MUST output a JSON response in this exact format:
{{
    "character": "quiz_character",
    "dialogue": "Your speaking dialogue here",
    "emotion": "enthusiastic",
    "speed": 1.0,
    "tool": "show_selection",
    "tool_data": {{
        "type": "quiz_question",
        "question": "다음 중 세종대왕의 업적은?",
        "items": ["한글 창제", "불교 장려", "몽골 침입", "일제강점"],
        "correct_answer": "한글 창제"
    }}
}}

For topic selection, use:
{{
    "character": "quiz_character",
    "dialogue": "어떤 주제로 퀴즈를 할까요?",
    "emotion": "curious",
    "tool": "quiz",
    "tool_data": {{
        "type": "topic_selection",
        "items": ["조선시대", "근현대사", "일제강점기"]
    }}
}}

최근 대화:
{chr(10).join(conversation_history[-6:])}

현재 사용자 메시지: {user_message}

자연스럽게 응답하되, 퀴즈 관련 상황에서는 반드시 위의 JSON 형식으로 응답하세요."""

async def process_unified_conversation(request: ChatWithSessionRequest):
    """Unified conversation processing with intelligent context awareness"""
    
    # Load session and build enhanced character context
    session_data = conversation_service.load_session_messages(request.session_id, request.user_id)
    
    # Check if session data was loaded successfully
    if session_data is None:
        print(f"❌ ERROR: Session {request.session_id} not found for user {request.user_id}")
        raise HTTPException(status_code=404, detail=f"Session {request.session_id} not found")
    
    character = await character_service.get_character(request.character_id)
    
    # Check if character was found
    if character is None:
        print(f"⚠️  WARNING: Character '{request.character_id}' not found, using default settings")
        character = {
            "name": request.character_id,
            "personality": "Friendly and helpful",
            "temperature": 0.7
        }
    
    # 🧠 ENHANCED CHARACTER CONTEXT: Let character handle flow naturally
    conversation_history = []
    for msg in session_data.get('messages', []):
        conversation_history.append(f"{msg['role']}: {msg['content']}")
    
    # Special handling for quiz characters with educational logic - DISABLED FOR LLM INTEGRATION TESTING
    if False and 'quiz' in request.character_id:
        print(f"🔍 DEBUG: Building educational quiz prompt for message: '{request.message}'")
        character_name = character.get('name', '설민석') if character else '설민석'
        enhanced_prompt = build_educational_quiz_prompt(
            character_name=character_name,
            conversation_history=conversation_history,
            user_message=request.message
        )
        print(f"🔍 DEBUG: Enhanced prompt length: {len(enhanced_prompt)} chars")
    else:
        # Build standard character prompt
        character_name = character.get('name', request.character_id) if character else request.character_id
        enhanced_prompt = f"""당신은 {character_name}입니다.
    
대화 맥락을 파악하고 자연스럽게 응답하세요:
- 사용자가 "정답", "맞습니다", "훌륭해요" 등의 피드백을 주면, 격려하고 다음 질문을 제공하세요
- 퀴즈나 질문 상황에서는 교육적이고 친근하게 응답하세요  
- 대화 흐름을 자연스럽게 이어가세요

최근 대화:
{chr(10).join(conversation_history[-6:])}

현재 사용자 메시지: {request.message}

위 맥락에 맞춰 적절히 응답해주세요."""

    # Process with enhanced context
    return await process_llm_conversation(request, enhanced_prompt, session_data)

async def process_llm_conversation(request: ChatWithSessionRequest, enhanced_prompt: str, session_data: Dict) -> ChatWithSessionResponse:
    """Process LLM conversation with enhanced prompt and session management"""
    
    # Add user message to session
    conversation_service.add_message_to_session(
        request.session_id, 
        "user", 
        request.message, 
        request.user_id
    )
    
    # Get character for temperature
    character = await character_service.get_character(request.character_id)
    temperature = character.get('temperature', 0.7) if character else 0.7
    
    # Generate AI response using enhanced prompt
    response = azure_client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": enhanced_prompt}
        ],
        max_tokens=300,
        temperature=temperature,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    response_text = response.choices[0].message.content.strip()
    
    # Extract dialogue for conversation history storage
    try:
        # Try to parse as JSON (tool-based response)
        parsed_response = tool_orchestrator.parse_llm_response(response_text)
        dialogue_for_history = parsed_response["dialogue"]
        print(f"🔧 Storing clean dialogue in history: {dialogue_for_history[:50]}...")
    except (ValueError, json.JSONDecodeError):
        # Not JSON, use raw response (normal chat)
        dialogue_for_history = response_text
        print(f"🔧 Storing normal chat response: {dialogue_for_history[:50]}...")
    
    # Add AI response to session (clean dialogue only)
    conversation_service.add_message_to_session(
        request.session_id,
        "assistant", 
        dialogue_for_history, 
        request.user_id
    )
    
    # 🎯 LLM AGENT ENGINE INTEGRATION: Check if this is a quiz request that needs tools
    tools = None
    
    # 🧠 QUIZ DETECTION: Check if this is a quiz request that needs LLM Agent Engine
    is_quiz_request = (
        '퀴즈' in request.message or 
        'quiz' in request.message.lower() or
        '문제' in request.message or
        '시작' in request.message or
        'quiz' in request.character_id  # Generic quiz character
    ) and (
        'seolminseok' in request.character_id or 
        'quiz' in request.character_id or
        'seol_min_seok' in request.character_id or  # Keep for backward compatibility
        'science' in request.character_id  # Generic science character detection
    )
    
    if is_quiz_request:
        print(f"🎯 QUIZ REQUEST DETECTED in process_unified_conversation: '{request.message}' for character '{request.character_id}'")
        
        # Use LLM Agent Engine for quiz processing
        try:
            from services.llm_agent_engine import LLMAgentEngine, InteractionContext
            from services.character_prompt_manager import CharacterPromptManager
            
            # Initialize components
            llm_agent_engine = LLMAgentEngine()
            character_prompt_manager = CharacterPromptManager()
            
            # Create interaction context for the current message
            interaction_context = InteractionContext(
                question="",  # Will be populated by LLM Agent Engine
                user_answer=request.message,  # User's current input
                correct_answer="",  # Will be populated by LLM Agent Engine
                options=[],  # Will be populated by LLM Agent Engine
                session_id=request.session_id,
                character_id=request.character_id
            )
            
            # Get character prompt
            character_prompt = await character_prompt_manager.get_prompt(request.character_id)
            print(f"🎯 Using LLM Agent Engine with character prompt for quiz processing")
            
            # Process with LLM Agent Engine
            # Get chat history for context
            chat_history = await get_chat_history(request.session_id) if hasattr(request, 'session_id') else []
            
            # Define available tools
            available_tools = {
                "show_selection": {
                    "description": "Display quiz question with multiple choice options",
                    "parameters": ["question", "options", "correct_answer", "selection_mode"]
                },
                "continuous_quiz_response": {
                    "description": "Provide two-phase continuous quiz response",
                    "parameters": ["phase1", "phase2"]
                }
            }
            
            agent_response = await llm_agent_engine.process_with_tools(
                user_input=request.message,
                character_prompt=character_prompt,
                chat_history=chat_history,
                available_tools=available_tools
            )
            
            # Use agent response instead of regular LLM response
            response_text = agent_response.get('dialogue', '')
            tool = agent_response.get('tool', {})
            tools = [tool] if tool else []
            print(f"✅ Generated {len(tools)} quiz tools from LLM Agent Engine")
            print(f"🎯 LLM Agent Engine dialogue: '{response_text[:100]}...'")
            print(f"🎯 Tool type: {tool.get('type', 'none')}")
            
        except Exception as e:
            print(f"❌ LLM Agent Engine failed for quiz in process_unified_conversation: {e}")
            import traceback
            traceback.print_exc()
            # Continue with regular processing as fallback
    
    # 🔧 FALLBACK TOOL-ORCHESTRATED PROCESSING: Parse LLM response for tool commands if LLM Agent Engine didn't run
    if tools is None:
        print(f"🔧 EDUCATIONAL QUIZ: Analyzing response for tool commands...")
        try:
            from services.tool_orchestrator import ToolOrchestrator
            from services.platform_tool_handler import PlatformToolHandler
            
            orchestrator = ToolOrchestrator()
            handler = PlatformToolHandler()
            
            # Check if LLM response contains JSON tool commands
            if response_text.strip().startswith('{') and response_text.strip().endswith('}'):
                print(f"🔧 EDUCATIONAL: Detected JSON tool response, parsing...")
                print(f"🔍 RAW LLM RESPONSE: {response_text[:200]}...")
                parsed_response = orchestrator.parse_llm_response(response_text)
                
                # Extract dialogue and tool information
                response_text = parsed_response["dialogue"]
                print(f"🔍 EXTRACTED DIALOGUE: {response_text}")
                
                if "tool" in parsed_response:
                    print(f"🔧 EDUCATIONAL: Tool detected: {parsed_response['tool']}")
                    
                    # Execute the tool using PlatformToolHandler
                    tool_result = await handler.execute_tool(
                        parsed_response["tool"], 
                        parsed_response["tool_data"]
                    )
                    
                    # Convert tool result to legacy format for compatibility
                    tools = [{
                        "type": parsed_response["tool"],
                        "data": tool_result
                    }]
                    
                    print(f"🔧 EDUCATIONAL: Tool executed successfully: {parsed_response['tool']}")
                    print(f"🔧 EDUCATIONAL: Generated UI: {tool_result.get('ui_type', 'unknown')}")
                    
            else:
                print(f"🔧 EDUCATIONAL: Normal dialogue response, no tools detected")
                
        except Exception as tool_error:
            print(f"🔧 EDUCATIONAL: ToolOrchestrator error: {tool_error}")
            import traceback
            traceback.print_exc()
    
    # Generate TTS audio AFTER tool parsing (using clean dialogue text)
    audio_base64 = None
    try:
        if 'quiz' in request.character_id:  # Generic quiz character detection
            print(f"🎵 Generating TTS for educational quiz dialogue: '{response_text[:50]}...'")
            audio_base64 = await seolminseok_tts_service.generate_tts(response_text)
            print(f"🔍 TTS DEBUG: audio_base64={'✅ Present' if audio_base64 else '❌ None'}")
            
            # No fallback - keep 설민석's unique voice
            if audio_base64 is None:
                print(f"⚠️ Seolminseok TTS failed, continuing without audio")
            else:
                print(f"✅ Seolminseok TTS success: {len(audio_base64)} chars")
        else:
            # Use regular TTS for other characters
            audio_response = await tts_service.generate_speech(response_text, request.voice_id or "duke")
            audio_base64 = audio_response.get("audio")
    except Exception as e:
        print(f"TTS generation failed: {e}")
        audio_base64 = None
        
    # Update session metadata
    updated_session = conversation_service.load_session_messages(request.session_id, request.user_id)
    
    return ChatWithSessionResponse(
        character=character.get('name', request.character_id) if character else request.character_id,
        dialogue=response_text,
        emotion="neutral",
        speed=1.0,
        audio=audio_base64,
        session_id=request.session_id,
        message_count=len(updated_session.get('messages', [])),
        session_summary=updated_session.get("session_summary", ""),
        tools=tools
    )

from services.chat_orchestrator import ChatOrchestrator
from services.knowledge_service import KnowledgeService
from services.character_mood_service import CharacterMoodService
from services.conversation_service import ConversationService
from services.selective_memory_service import SelectiveMemoryService
from services.config_parser_service import ConfigParserService
from services.database_service import DatabaseService
from services.character_service import CharacterService
from services.incremental_knowledge_cache import IncrementalKnowledgeCache
from services.optimized_prompt_builder import OptimizedPromptBuilder
from services.fallback_tts_service import FallbackTTSService
from services.continuous_answer_tool import continuous_answer_tool, ToolTriggerEvent
from services.tool_orchestrator import ToolOrchestrator

# Initialize selective memory system
database_service = DatabaseService()
selective_memory_service = SelectiveMemoryService(database_service)
config_parser_service = ConfigParserService()

# Initialize character service
character_service = CharacterService(database_service)

# Initialize chat orchestrator with database
chat_orchestrator = ChatOrchestrator(database_service)

# Initialize knowledge management services
knowledge_service = KnowledgeService()
character_mood_service = CharacterMoodService()
conversation_service = ConversationService()
incremental_cache = IncrementalKnowledgeCache()
prompt_builder = OptimizedPromptBuilder()
fallback_tts = FallbackTTSService()

# 🚀 PRIORITY 1 FIX: Global ToolOrchestrator with cached TTS services
# Create single instance that's reused across all API calls
global_tool_orchestrator = ToolOrchestrator(
    tts_service=tts_service,
    session_service=conversation_service
)
print("✅ Global ToolOrchestrator initialized with cached SeolMinSeok TTS service")

# Print STT service status on startup
print(f"📢 STT Service Status: {'✅ Available' if stt_service.available else '❌ Not Available'}")

app = FastAPI(title="Voice Character Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3008"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

# Initialize Azure OpenAI client
try:
    azure_client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION
    )
    llm_available = True
    print("✅ Azure OpenAI client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Azure OpenAI client: {e}")
    llm_available = False

class ChatRequest(BaseModel):
    message: str
    character_prompt: str
    history: list = []
    character_id: str
    voice_id: Optional[str] = None
    character_temperature: Optional[float] = None

class ChatResponse(BaseModel):
    character: str
    dialogue: str
    emotion: str = "neutral"
    speed: float = 1.0
    audio: Optional[str] = None  # base64 encoded audio data
    tools: Optional[List[Dict]] = None  # Quiz tools for frontend
    session_id: Optional[str] = None  # Session ID for frontend state management

# Session-Aware Chat Models
# Classes moved to top of file

# Knowledge Management Models
from pydantic import Field, validator

class KnowledgeItemCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title cannot be empty")
    content: str = Field(..., min_length=1, description="Content cannot be empty") 
    keywords: Union[List[str], str] = Field(..., description="Keywords cannot be empty")
    category: str = Field(..., min_length=1, description="Category cannot be empty")
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Keywords cannot be empty")
        elif isinstance(v, list):
            if not v or all(not k.strip() for k in v):
                raise ValueError("Keywords cannot be empty")
        return v

class KnowledgeItemUpdate(BaseModel):
    character_id: str
    title: Optional[str] = None
    content: Optional[str] = None
    keywords: Optional[List[str]] = None
    category: Optional[str] = None

class KnowledgeItemDelete(BaseModel):
    character_id: str

def parse_character_prompt(character_prompt: str) -> Dict[str, str]:
    """Extract character data from XML-like tags in the prompt"""
    character_data = {
        'name': '',
        'personality': '',
        'speaking_style': '',
        'age': '',
        'gender': '',
        'role': '',
        'backstory': '',
        'scenario': ''
    }
    
    patterns = {
        'name': r'<name>(.*?)</name>',
        'personality': r'<personality>(.*?)</personality>',
        'speaking_style': r'<speaking_style>(.*?)</speaking_style>',
        'age': r'<age>(.*?)</age>',
        'gender': r'<gender>(.*?)</gender>',
        'role': r'<role>(.*?)</role>',
        'backstory': r'<backstory>(.*?)</backstory>',
        'scenario': r'<scenario>(.*?)</scenario>'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, character_prompt, re.DOTALL)
        if match:
            character_data[key] = match.group(1).strip()
    
    return character_data

def format_conversation_history(history: list) -> str:
    """Format conversation history for the prompt"""
    if not history:
        return "No previous conversation."
    
    formatted_history = []
    for msg in history:
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        if role == 'user':
            formatted_history.append(f"User: {content}")
        else:
            formatted_history.append(f"Assistant: {content}")
    
    return "\n".join(formatted_history)

def create_system_prompt(character_prompt: str, history: list, user_message: str) -> str:
    """Create a system prompt for the character (legacy version)"""
    return create_system_prompt_original(character_prompt, history, user_message)

def create_enhanced_system_prompt_with_memory(character_prompt: str, ai_context: dict, user_message: str, character_id: str = None) -> str:
    """Create a system prompt using enhanced AI context with compressed history and character-specific instructions"""
    if not character_prompt:
        print(f"⚠️  WARNING: character_prompt is None or empty")
        character_prompt = "You are a helpful assistant."
    character_data = parse_character_prompt(character_prompt)
    
    # Use the formatted context prompt that includes actual message history
    context_prompt = ai_context.get("context_prompt", "")
    recent_messages = ai_context.get("recent_messages", [])
    
    # Check if this is a first greeting (empty recent messages + greeting message)
    is_first_greeting = (
        len(recent_messages) == 0 and 
        user_message.strip().lower() in ['안녕하세요', '안녕', 'hello', 'hi', '반가워요', '처음 뵙겠습니다']
    )
    
    if is_first_greeting:
        # Generate welcome message
        character_name = character_data.get('name', 'Assistant')
        prompt = f"""You are {character_name}. This is your first meeting with the user.

Character Information:
- Personality: {character_data.get('personality', 'Friendly and helpful')}
- Speaking Style: {character_data.get('speaking_style', 'Natural conversational Korean')}
- Age: {character_data.get('age', 'Not specified')}
- Gender: {character_data.get('gender', 'Not specified')}
- Role: {character_data.get('role', 'Assistant')}
- Background: {character_data.get('backstory', 'Not specified')}
- Scenario: {character_data.get('scenario', 'General conversation')}

TASK: Generate a warm, character-appropriate welcome greeting. Introduce yourself naturally and invite conversation.

IMPORTANT: You must respond ONLY with a valid JSON object in exactly this format:
{{"character": "{character_name}", "dialogue": "your_welcome_greeting_in_korean", "emotion": "happy", "speed": 1.0}}

Rules:
1. Use only Korean language for dialogue
2. Keep the greeting natural and character-appropriate
3. Mention your name and role briefly
4. Invite the user to share what's on their mind
5. emotion should be "happy" for welcome messages
6. Do not include any text outside the JSON format
7. Do not use markdown, asterisks, or action descriptions"""
    else:
        # Normal conversation with enhanced context
        prompt = f"""You are {character_data.get('name', 'a helpful assistant')}. 

Character Information:
- Personality: {character_data.get('personality', 'Friendly and helpful')}
- Speaking Style: {character_data.get('speaking_style', 'Natural conversational Korean')}
- Age: {character_data.get('age', 'Not specified')}
- Gender: {character_data.get('gender', 'Not specified')}
- Role: {character_data.get('role', 'Assistant')}
- Background: {character_data.get('backstory', 'Not specified')}
- Scenario: {character_data.get('scenario', 'General conversation')}

{context_prompt}

Current User Message: {user_message}

IMPORTANT: You must respond ONLY with a valid JSON object in exactly this format:
{{"character": "character_name", "dialogue": "your_response_in_korean", "emotion": "emotion", "speed": speed_value}}

Rules:
1. Use only Korean language for dialogue
2. Stay in character based on the personality and speaking style
3. Use the conversation history above to maintain context and continuity
4. Remember past interactions and refer to them naturally
5. emotion must be one of: normal, happy, sad, angry, surprised, fearful, disgusted, excited
6. speed must be a number between 0.8 and 1.2
7. Do not include any text outside the JSON format
8. Do not use markdown, asterisks, or action descriptions"""

    # Add character-specific instructions
    if 'quiz' in character_id:
        quiz_instructions = """

🎯 QUIZ CHARACTER SPECIAL INSTRUCTIONS:
When the user requests a quiz or asks you to create questions:
- ALWAYS format quiz questions in this EXACT structure: "Question? A) Option1 B) Option2 C) Option3 D) Option4"
- Include exactly 4 options labeled with A), B), C), D)
- Make sure there is a clear question ending with "?"
- Choose historically accurate correct answers based on your knowledge
- Focus on Korean history topics (조선시대, 고려시대, etc.)
- Examples:
  * "다음 중 세종대왕의 업적은? A) 한글 창제 B) 불교 장려 C) 몽골 침입 D) 일제강점"
  * "고려를 건국한 인물은? A) 왕건 B) 이성계 C) 박혁거세 D) 온조"

CRITICAL: This A/B/C/D format is required for the quiz UI to work properly!"""
        prompt += quiz_instructions
    
    return prompt

async def generate_enhanced_ai_response(character_prompt: str, ai_context: dict, user_message: str, character_id: str = None) -> ChatResponse:
    """Generate response using Azure OpenAI with enhanced context including compressed history"""
    try:
        system_prompt = create_enhanced_system_prompt_with_memory(character_prompt, ai_context, user_message, character_id)
        
        if not system_prompt:
            print(f"❌ FATAL: system_prompt is None or empty!")
            raise ValueError("System prompt cannot be empty")
        
        print(f"🔍 System prompt length: {len(system_prompt)} chars")
        
        # Get temperature from ai_context or use default
        temperature = ai_context.get("character_temperature", 0.7)
        
        response = azure_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            max_tokens=300,
            temperature=temperature,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Try to parse JSON response
        try:
            # Extract JSON from response if there's extra text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_data = json.loads(json_match.group())
            else:
                response_data = json.loads(response_text)
            
            # Validate required fields
            if not all(key in response_data for key in ['character', 'dialogue', 'emotion', 'speed']):
                raise ValueError("Missing required fields in response")
            
            # Validate emotion
            valid_emotions = ['normal', 'happy', 'sad', 'angry', 'surprised', 'fearful', 'disgusted', 'excited']
            if response_data['emotion'] not in valid_emotions:
                response_data['emotion'] = 'normal'
            
            # Validate speed
            try:
                speed = float(response_data['speed'])
                if not (0.8 <= speed <= 1.2):
                    response_data['speed'] = 1.0
            except (ValueError, TypeError):
                response_data['speed'] = 1.0
            
            return ChatResponse(**response_data)
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse AI response: {e}")
            print(f"Raw response: {response_text}")
            
            # Fallback response
            return ChatResponse(
                character="Assistant",
                dialogue="죄송합니다. 응답을 처리하는 중에 문제가 발생했습니다.",
                emotion="neutral",
                speed=1.0
            )
            
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return ChatResponse(
            character="Assistant",
            dialogue="죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다.",
            emotion="neutral",
            speed=1.0
        )

# Legacy function - keeping for backward compatibility
def create_system_prompt_original(character_prompt: str, history: list, user_message: str) -> str:
    """Original create_system_prompt function for backward compatibility"""
    character_data = parse_character_prompt(character_prompt)
    history_text = format_conversation_history(history)
    
    # Check if this is a first greeting (empty history + greeting message)
    is_first_greeting = (
        len(history) == 0 and 
        user_message.strip().lower() in ['안녕하세요', '안녕', 'hello', 'hi', '반가워요', '처음 뵙겠습니다']
    )
    
    if is_first_greeting:
        # Generate welcome message
        character_name = character_data.get('name', 'Assistant')
        prompt = f"""You are {character_name}. This is your first meeting with the user. 

Character Information:
- Personality: {character_data.get('personality', 'Friendly and helpful')}
- Speaking Style: {character_data.get('speaking_style', 'Natural conversational Korean')}
- Age: {character_data.get('age', 'Not specified')}
- Gender: {character_data.get('gender', 'Not specified')}
- Role: {character_data.get('role', 'Assistant')}
- Background: {character_data.get('backstory', 'Not specified')}
- Scenario: {character_data.get('scenario', 'General conversation')}

Conversation History:
{history_text}

Current User Message: {user_message}

IMPORTANT: You must respond ONLY with a valid JSON object in exactly this format:
{{"character": "character_name", "dialogue": "your_response_in_korean", "emotion": "emotion", "speed": speed_value}}

Rules:
1. Use only Korean language for dialogue
2. Stay in character based on the personality and speaking style
3. emotion must be one of: normal, happy, sad, angry, surprised, fearful, disgusted, excited
4. speed must be a number between 0.8 and 1.2
5. Do not include any text outside the JSON format
6. Do not use markdown, asterisks, or action descriptions"""
    else:
        # Normal conversation
        prompt = f"""You are {character_data.get('name', 'a helpful assistant')}.

Character Information:
- Personality: {character_data.get('personality', 'Friendly and helpful')}
- Speaking Style: {character_data.get('speaking_style', 'Natural conversational Korean')}
- Age: {character_data.get('age', 'Not specified')}
- Gender: {character_data.get('gender', 'Not specified')}
- Role: {character_data.get('role', 'Assistant')}
- Background: {character_data.get('backstory', 'Not specified')}
- Scenario: {character_data.get('scenario', 'General conversation')}

Conversation History:
{history_text}

Current User Message: {user_message}

IMPORTANT: You must respond ONLY with a valid JSON object in exactly this format:
{{"character": "character_name", "dialogue": "your_response_in_korean", "emotion": "emotion", "speed": speed_value}}

Rules:
1. Use only Korean language for dialogue
2. Stay in character based on the personality and speaking style
3. emotion must be one of: normal, happy, sad, angry, surprised, fearful, disgusted, excited
4. speed must be a number between 0.8 and 1.2
5. Do not include any text outside the JSON format
6. Do not use markdown, asterisks, or action descriptions"""

    return prompt

async def generate_ai_response(character_prompt: str, history: list, user_message: str, character_temperature: float = None) -> ChatResponse:
    """Generate response using Azure OpenAI"""
    try:
        system_prompt = create_system_prompt(character_prompt, history, user_message)
        
        # Use character-specific temperature or default to 0.7
        temperature = character_temperature if character_temperature is not None else 0.7
        
        response = azure_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            max_tokens=300,
            temperature=temperature,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Try to parse JSON response
        try:
            # Extract JSON from response if there's extra text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_data = json.loads(json_match.group())
            else:
                response_data = json.loads(response_text)
            
            # Validate required fields
            if not all(key in response_data for key in ['character', 'dialogue', 'emotion', 'speed']):
                raise ValueError("Missing required fields in response")
            
            # Validate emotion
            valid_emotions = ['normal', 'happy', 'sad', 'angry', 'surprised', 'fearful', 'disgusted', 'excited']
            if response_data['emotion'] not in valid_emotions:
                response_data['emotion'] = 'normal'
            
            # Validate speed
            try:
                speed = float(response_data['speed'])
                if not (0.8 <= speed <= 1.2):
                    response_data['speed'] = 1.0
            except (ValueError, TypeError):
                response_data['speed'] = 1.0
            
            return ChatResponse(**response_data)
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse AI response: {e}")
            print(f"Raw response: {response_text}")
            
            # Fallback response
            return ChatResponse(
                character="Assistant",
                dialogue="죄송합니다. 응답을 처리하는 중에 문제가 발생했습니다.",
                emotion="neutral",
                speed=1.0
            )
            
    except Exception as e:
        print(f"Error calling Azure OpenAI: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

def create_enhanced_system_prompt(character_prompt: str, user_message: str, knowledge: list, persona_context: str) -> str:
    """Create enhanced system prompt with knowledge and persona context"""
    
    knowledge_text = ""
    if knowledge:
        knowledge_items = []
        for item in knowledge:
            knowledge_items.append(f"- {item.get('title', 'Knowledge')}: {item.get('content', '')}")
        knowledge_text = f"\n\n관련 지식:\n" + "\n".join(knowledge_items)
    
    persona_text = ""
    if persona_context:
        persona_text = f"\n\n사용자 페르소나:\n{persona_context}"
    
    enhanced_prompt = f"""{character_prompt}
    
사용자 메시지: {user_message}{knowledge_text}{persona_text}

위 정보를 바탕으로 적절한 응답을 생성하세요. 응답은 다음 JSON 형식으로 해주세요:
{{
    "character": "캐릭터 이름",
    "dialogue": "실제 응답 내용",
    "emotion": "감정 (normal, happy, sad, angry, surprised, fearful, disgusted, excited 중 하나)",
    "speed": "말하기 속도 (0.8-1.2 사이의 숫자)"
}}"""
    
    return enhanced_prompt

async def generate_ai_response_enhanced(system_prompt: str, character_temperature: float = None) -> ChatResponse:
    """Generate AI response using enhanced system prompt"""
    try:
        # Use character-specific temperature or default to 0.7
        temperature = character_temperature if character_temperature is not None else 0.7
        
        response = azure_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            max_tokens=300,
            temperature=temperature,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Try to parse JSON response (same logic as original function)
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_data = json.loads(json_match.group())
            else:
                response_data = json.loads(response_text)
            
            # Validate required fields
            if not all(key in response_data for key in ['character', 'dialogue', 'emotion', 'speed']):
                raise ValueError("Missing required fields in response")
                
            return ChatResponse(
                character=response_data.get('character', 'Assistant'),
                dialogue=response_data['dialogue'],
                emotion=response_data.get('emotion', 'normal'),
                speed=response_data.get('speed', 1.0),
                audio=None  # TTS will be handled separately if needed
            )
            
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback to treating entire response as dialogue
            return ChatResponse(
                character="Assistant",
                dialogue=response_text,
                emotion='normal',
                speed=1.0,
                audio=None
            )
            
    except Exception as e:
        print(f"Error in enhanced AI response generation: {e}")
        # Return fallback response
        return ChatResponse(
            character="Assistant",
            dialogue="죄송해요, 응답을 생성하는 중에 문제가 발생했습니다.",
            emotion='normal',
            speed=1.0,
            audio=None
        )

def generate_mock_response(character_id: str = None, user_message: str = "") -> ChatResponse:
    """Generate mock response when AI is not available - DISABLED TO FORCE REAL LLM USAGE"""
    
    # FORCE FAILURE TO EXPOSE REAL LLM ISSUES
    raise Exception("Mock responses disabled - must use actual LLM integration. This error exposes that the system is falling back to mocks instead of using real LLM responses.")
    
    # Default responses for other cases
    responses = [
        "안녕하세요! 만나서 반가워요.",
        "오늘은 어떤 것을 배우고 싶으신가요?", 
        "정말 흥미로운 질문이네요!",
        "함께 차근차근 풀어보죠.",
        "좋은 시도였어요. 다시 한 번 해볼까요?",
        "그렇네요, 재미있는 관점이에요!",
        "더 자세히 설명해 드릴게요.",
        "좋은 질문이군요!"
    ]
    
    emotions = ["neutral", "happy", "excited", "thoughtful"]
    
    return ChatResponse(
        character="Demo Character",
        dialogue=random.choice(responses),
        emotion=random.choice(emotions),
        speed=round(random.uniform(0.9, 1.1), 1)
    )

class LLMConfig(BaseModel):
    endpoint: str
    api_key: str
    api_version: str = "2025-01-01-preview"
    deployment_name: str = "gpt-4o"

@app.get("/")
async def root():
    return {
        "message": "Voice Character Chat API",
        "azure_openai_available": llm_available,
        "endpoint": AZURE_OPENAI_ENDPOINT if llm_available else "Not configured",
        "deployment": AZURE_OPENAI_DEPLOYMENT if llm_available else "Not configured"
    }

@app.get("/api/config")
async def get_config():
    """Get current LLM configuration"""
    return {
        "endpoint": AZURE_OPENAI_ENDPOINT,
        "api_version": AZURE_OPENAI_API_VERSION,
        "deployment_name": AZURE_OPENAI_DEPLOYMENT,
        "available": llm_available
    }

@app.post("/api/config")
async def update_config(config: LLMConfig):
    """Update LLM configuration (for future use - requires restart currently)"""
    global azure_client, llm_available, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT
    
    try:
        # Test new configuration
        test_client = AzureOpenAI(
            azure_endpoint=config.endpoint,
            api_key=config.api_key,
            api_version=config.api_version
        )
        
        # If successful, update global variables
        AZURE_OPENAI_ENDPOINT = config.endpoint
        AZURE_OPENAI_API_KEY = config.api_key
        AZURE_OPENAI_API_VERSION = config.api_version
        AZURE_OPENAI_DEPLOYMENT = config.deployment_name
        azure_client = test_client
        llm_available = True
        
        return {
            "success": True,
            "message": "LLM configuration updated successfully",
            "endpoint": config.endpoint,
            "deployment_name": config.deployment_name
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update configuration: {str(e)}")

@app.get("/api/models")
async def list_available_models():
    """List available models (placeholder for future enhancement)"""
    return {
        "models": [
            {"name": "gpt-4o", "description": "GPT-4 Omni - Latest multimodal model"},
            {"name": "gpt-4", "description": "GPT-4 - Advanced language model"},
            {"name": "gpt-3.5-turbo", "description": "GPT-3.5 Turbo - Fast and efficient"}
        ],
        "current": AZURE_OPENAI_DEPLOYMENT if llm_available else None
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        tools = None  # Default: no tools
        session_id = None  # No session creation by default
        
        # 🧠 QUIZ DETECTION: Check if this is a quiz request that needs tools
        # NOTE: Legacy endpoint - /api/platform-chat is used in production
        is_quiz_request = (
            '퀴즈' in request.message or 
            'quiz' in request.message.lower() or
            '문제' in request.message or
            '시작' in request.message
        ) and (
            'quiz' in request.character_id  # Generic quiz detection
        )
        
        if is_quiz_request and llm_available:
            print(f"🎯 QUIZ REQUEST DETECTED: Generating tools for '{request.message}'")
            
            # Use LLM Agent Engine to generate both dialogue and tools
            try:
                from services.llm_agent_engine import LLMAgentEngine, InteractionContext
                from services.character_prompt_manager import CharacterPromptManager
                
                # Initialize components
                llm_agent_engine = LLMAgentEngine()
                character_prompt_manager = CharacterPromptManager()
                
                # Create interaction context for quiz start (no previous question/answer)
                interaction_context = InteractionContext(
                    question="",  # Empty for initial quiz request
                    user_answer="",  # Empty for initial quiz request  
                    correct_answer="",  # Empty for initial quiz request
                    options=[],  # Empty for initial quiz request
                    session_id="",
                    character_id=request.character_id
                )
                
                # Get character prompt
                character_prompt = await character_prompt_manager.get_prompt(request.character_id)
                print(f"🎯 Using character prompt for quiz generation")
                
                # Process with LLM Agent Engine
                # Get chat history for context
                chat_history = await get_chat_history(request.session_id) if hasattr(request, 'session_id') else []
                
                # Define available tools
                available_tools = {
                    "show_selection": {
                        "description": "Display quiz question with multiple choice options",
                        "parameters": ["question", "options", "correct_answer", "selection_mode"]
                    },
                    "continuous_quiz_response": {
                        "description": "Provide two-phase continuous quiz response",
                        "parameters": ["phase1", "phase2"]
                    }
                }
                
                agent_response = await llm_agent_engine.process_with_tools(
                    user_input=request.message,
                    character_prompt=character_prompt,
                    chat_history=chat_history,
                    available_tools=available_tools
                )
                
                # Use agent response
                response = type('obj', (object,), {
                    'character': request.character_id or "설민석",
                    'dialogue': agent_response.get('dialogue', ''),
                    'emotion': 'excited',
                    'speed': 1.0
                })()
                
                tools = agent_response.tools
                print(f"✅ Generated {len(tools)} quiz tools from LLM Agent Engine")
                
            except Exception as e:
                print(f"❌ LLM Agent Engine failed for quiz: {e}")
                import traceback
                traceback.print_exc()  # Print full stack trace
                print(f"🔍 DEBUG: Exception type: {type(e)}")
                print(f"🔍 DEBUG: Exception args: {e.args}")
                # Fallback to regular LLM response
                if llm_available:
                    response = await generate_ai_response(request.character_prompt, request.history, request.message, request.character_temperature)
                else:
                    response = generate_mock_response(request.character_id, request.message)
        else:
            # Regular chat (non-quiz) processing
            if llm_available:
                response = await generate_ai_response(request.character_prompt, request.history, request.message, request.character_temperature)
            else:
                # Fallback to mock response
                print("⚠️ Using mock response - Azure OpenAI not available")
                response = generate_mock_response(request.character_id, request.message)
        
        # Generate TTS audio for the response
        try:
            # Extract character data for voice selection
            character_data = parse_character_prompt(request.character_prompt)
            
            # Use character-specific voice_id from the request
            voice_id = request.voice_id or "tc_61c97b56f1b7877a74df625b"  # Default Emma voice
            
            print(f"🎤 Using voice_id: {voice_id} for character: {request.character_id}")
            
            # Special handling for specific characters
            tts_emotion = response.emotion
            
            # 설민석 characters (both regular and quiz) - use dedicated TTS service
            if 'quiz' in request.character_id:  # Generic quiz character detection
                print(f"🎭 설민석 character detected ({request.character_id}) - using dedicated TTS service")
                audio_data = await seolminseok_tts_service.generate_tts(
                    text=response.dialogue,
                    use_hd=True,
                    language="auto"
                )
            # 윤아리 - always use whisper emotion
            elif request.character_id == 'yoon_ahri':
                tts_emotion = 'whisper'
                print(f"🎵 윤아리 detected, using whisper emotion instead of {response.emotion}")
                # Also update the response emotion for consistency
                response.emotion = 'whisper'
                
                # Generate audio with regular TTS service
                audio_data = await tts_service.generate_speech(
                    text=response.dialogue,
                    voice_id=voice_id,
                    emotion=tts_emotion,
                    speed=response.speed
                )
            # Default - use regular TTS service
            else:
                # Generate audio with regular TTS service
                audio_data = await tts_service.generate_speech(
                    text=response.dialogue,
                    voice_id=voice_id,
                    emotion=tts_emotion,
                    speed=response.speed
                )
            
            if audio_data:
                response.audio = audio_data
                print(f"✅ TTS generated for dialogue: '{response.dialogue[:50]}...'")
            else:
                print(f"❌ TTS generation failed, no audio will be provided")
                response.audio = None
                
        except Exception as tts_error:
            print(f"❌ TTS Error: {tts_error}")
            response.audio = None
        
        # 🎯 QUIZ TOOLS: Generate session ID for quiz requests and add tools/session to response
        if tools:
            import uuid
            session_id = f"sess_{str(uuid.uuid4())[:8]}"
            print(f"🆔 Generated session ID for quiz: {session_id}")
        
        # Add tools and session_id to response for quiz requests
        if hasattr(response, 'tools'):
            response.tools = tools
            response.session_id = session_id
        else:
            # Create new ChatResponse with tools if original doesn't support it
            response = ChatResponse(
                character=response.character,
                dialogue=response.dialogue,
                emotion=response.emotion,
                speed=response.speed,
                audio=getattr(response, 'audio', None),
                tools=tools,
                session_id=session_id
            )
        
        return response
            
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        # Return mock response as fallback
        return generate_mock_response()

@app.get("/api/voices")
async def get_voices():
    """Get available TTS voices"""
    try:
        voices = await tts_service.get_voices()
        if voices:
            return {"voices": voices, "status": "success"}
        else:
            return {"voices": [], "status": "error", "message": "Failed to fetch voices"}
    except Exception as e:
        return {"voices": [], "status": "error", "message": str(e)}

@app.get("/api/voices/korean")
async def get_korean_voices():
    """Get Korean TTS voices with caching"""
    try:
        voices = await tts_service.get_korean_voices()
        return {"voices": voices, "status": "success"}
    except Exception as e:
        return {"voices": [], "status": "error", "message": str(e)}

@app.get("/api/voices/cache-stats")
async def get_voice_cache_stats():
    """Get voice cache statistics"""
    try:
        from services.voice_cache_service import voice_cache_service
        stats = voice_cache_service.get_cache_stats()
        return {"cache_stats": stats, "status": "success"}
    except Exception as e:
        return {"cache_stats": {}, "status": "error", "message": str(e)}

class VoiceRecommendRequest(BaseModel):
    character_prompt: str
    top_k: int = 5

@app.post("/api/voices/recommend")
async def recommend_voices(request: VoiceRecommendRequest):
    """Recommend voices based on character description"""
    try:
        print(f"🎤 Voice recommendation request: {request.character_prompt[:100]}...")
        recommendations = await voice_recommend_service.recommend_voices(
            character_prompt=request.character_prompt,
            top_k=request.top_k
        )
        
        if recommendations:
            print(f"✅ Got {len(recommendations)} recommendations")
            return {
                "recommendations": recommendations,
                "status": "success"
            }
        else:
            print("⚠️ No recommendations received")
            return {
                "recommendations": [],
                "status": "error",
                "message": "Failed to get recommendations"
            }
    except Exception as e:
        print(f"❌ Error in voice recommendation: {e}")
        return {
            "recommendations": [],
            "status": "error",
            "message": str(e)
        }

class TTSRequest(BaseModel):
    text: str
    voice_id: str = "tc_61c97b56f1b7877a74df625b"  # Default Emma
    emotion: str = "normal"
    speed: float = 1.0
    character_id: Optional[str] = None

@app.post("/api/tts")
async def generate_tts(request: TTSRequest):
    """Generate TTS audio for given text"""
    try:
        # Special handling for specific characters
        tts_emotion = request.emotion
        
        # 설민석 and Dr.Genie characters - use dedicated TTS service
        if 'seol_min_seok' in request.character_id or request.character_id == 'dr_genie_science_quiz':
            print(f"🎭 Quiz character detected ({request.character_id}) - using dedicated TTS service for standalone TTS")
            audio_data = await seolminseok_tts_service.generate_tts(
                text=request.text,
                use_hd=True,
                language="auto"
            )
        # Special handling for 윤아리 - always use whisper emotion
        elif request.character_id == 'yoon_ahri':
            tts_emotion = 'whisper'
            print(f"🎵 윤아리 TTS detected, using whisper emotion instead of {request.emotion}")
            audio_data = await tts_service.generate_speech(
                text=request.text,
                voice_id=request.voice_id,
                emotion=tts_emotion,
                speed=request.speed
            )
        else:
            print(f"🎤 Regular TTS request - voice_id: {request.voice_id}, emotion: {tts_emotion}")
            audio_data = await tts_service.generate_speech(
                text=request.text,
                voice_id=request.voice_id,
                emotion=tts_emotion,
                speed=request.speed
            )
        
        if audio_data:
            return {
                "status": "success",
                "audio": audio_data,
                "audio_base64": audio_data,  # Frontend expects this key
                "text": request.text,
                "voice_id": request.voice_id,
                "emotion": request.emotion
            }
        else:
            print(f"❌ TTS generation failed, no audio will be provided")
            return {
                "status": "error",
                "audio": None,
                "audio_base64": None,
                "text": request.text,
                "voice_id": request.voice_id,
                "emotion": request.emotion,
                "error": "TTS service failed"
            }
            
    except Exception as e:
        print(f"❌ TTS exception occurred: {str(e)}")
        return {
            "status": "error",
            "audio": None,
            "audio_base64": None,
            "text": request.text,
            "voice_id": request.voice_id,
            "emotion": request.emotion,
            "error": str(e)
        }

class STTRequest(BaseModel):
    audio: str  # base64 encoded audio data
    language: str = "ko-KR"

@app.post("/api/stt")
async def speech_to_text(request: STTRequest):
    """Convert speech audio to text using Azure STT"""
    try:
        if not stt_service.available:
            raise HTTPException(status_code=503, detail="STT service not available")
        
        print(f"🎤 STT request received, audio length: {len(request.audio)} chars")
        
        text = await stt_service.transcribe_audio(request.audio)
        
        if text and text.strip():
            print(f"✅ STT SUCCESS: '{text}'")
            return {
                "status": "success",
                "text": text,
                "language": request.language
            }
        else:
            print("⚠️ STT: No speech detected or empty result")
            return {
                "status": "no_speech",
                "text": "",
                "message": "No speech detected in audio"
            }
            
    except Exception as e:
        print(f"❌ STT ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"STT error: {str(e)}")

@app.get("/api/stt/languages")
async def get_stt_languages():
    """Get supported STT languages"""
    return {
        "languages": stt_service.get_supported_languages(),
        "default": "ko-KR"
    }

# =============================================
# NEW ENDPOINTS FOR SESSION AND PERSONA MANAGEMENT
# =============================================

class SessionStartRequest(BaseModel):
    user_id: str
    character_id: str
    persona_id: Optional[str] = None

class SessionContinueRequest(BaseModel):
    session_id: str
    user_id: str

class SessionDeleteRequest(BaseModel):
    user_id: str

class PersonaCreateRequest(BaseModel):
    user_id: str
    name: str
    description: str
    attributes: Dict[str, Any]

class MessageRequest(BaseModel):
    session_id: str
    user_id: str
    message: str
    character_id: str
    character_prompt: Optional[str] = None  # Add character prompt for proper identity

@app.post("/api/sessions/start")
async def start_session(request: SessionStartRequest):
    """Start a new chat session or get existing sessions for continuation"""
    try:
        result = chat_orchestrator.start_chat_session(
            request.user_id, 
            request.character_id,
            request.persona_id
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        print(f"Error starting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/create")
async def create_session(request: SessionStartRequest):
    """Create a new conversation session"""
    try:
        result = chat_orchestrator.create_new_session(
            request.user_id,
            request.character_id,
            request.persona_id
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        print(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/continue")
async def continue_session(request: SessionContinueRequest):
    """Continue an existing conversation session"""
    try:
        result = chat_orchestrator.continue_session(
            request.session_id,
            request.user_id
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        print(f"Error continuing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/message")
async def process_session_message(request: MessageRequest):
    """Process a message in a conversation session with knowledge retrieval"""
    try:
        # Process message and get knowledge
        response_data = chat_orchestrator.process_message(
            request.session_id,
            request.user_id,
            request.message,
            request.character_id
        )
        
        # Generate AI response using the processed data
        if llm_available:
            # Use provided character prompt or fallback to basic prompt
            character_prompt = request.character_prompt or f"You are a helpful AI assistant for character {request.character_id}."
            
            # Use the same system prompt creation as regular chat for consistency
            system_prompt = create_system_prompt(
                character_prompt,
                [],  # Empty history for session messages (history is managed separately)
                response_data.get("user_message", request.message)
            )
            
            # Add knowledge and persona context if available
            if response_data.get("relevant_knowledge") or response_data.get("persona_context"):
                knowledge_text = ""
                if response_data.get("relevant_knowledge"):
                    knowledge_items = []
                    for item in response_data.get("relevant_knowledge", []):
                        knowledge_items.append(f"- {item.get('title', 'Knowledge')}: {item.get('content', '')}")
                    knowledge_text = f"\n\n관련 지식:\n" + "\n".join(knowledge_items)
                
                persona_text = ""
                if response_data.get("persona_context"):
                    persona_text = f"\n\n사용자 페르소나:\n{response_data.get('persona_context')}"
                
                system_prompt += knowledge_text + persona_text
            
            # Generate AI response using the built system prompt directly
            response = azure_client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": system_prompt}
                ],
                max_tokens=300,
                temperature=0.7,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response (same logic as generate_ai_response)
            try:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    response_data_ai = json.loads(json_match.group())
                else:
                    response_data_ai = json.loads(response_text)
                
                # Validate required fields
                if not all(key in response_data_ai for key in ['character', 'dialogue', 'emotion', 'speed']):
                    raise ValueError("Missing required fields in response")
                
                # Validate emotion
                valid_emotions = ['normal', 'happy', 'sad', 'angry', 'surprised', 'fearful', 'disgusted', 'excited']
                if response_data_ai['emotion'] not in valid_emotions:
                    response_data_ai['emotion'] = 'normal'
                
                # Validate speed
                try:
                    speed = float(response_data_ai['speed'])
                    if not (0.8 <= speed <= 1.2):
                        response_data_ai['speed'] = 1.0
                except (ValueError, TypeError):
                    response_data_ai['speed'] = 1.0
                
                ai_response = ChatResponse(**response_data_ai)
                
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Failed to parse session AI response: {e}")
                print(f"Raw response: {response_text}")
                
                # Fallback response
                ai_response = ChatResponse(
                    character="Assistant",
                    dialogue="죄송합니다. 응답을 처리하는 중에 문제가 발생했습니다.",
                    emotion="normal",
                    speed=1.0
                )
            
            # Save AI response to session
            chat_orchestrator.save_ai_response(
                request.session_id,
                request.user_id,
                ai_response.dialogue,
                response_data.get("knowledge_ids", [])
            )
            
            # Return complete response with AI dialogue
            return {
                "success": True,
                "data": {
                    **response_data,
                    "ai_response": ai_response.dialogue,
                    "emotion": ai_response.emotion
                }
            }
        else:
            # Fallback when AI is not available
            fallback_response = "AI가 현재 사용 불가능합니다."
            return {
                "success": True, 
                "data": {
                    **response_data,
                    "ai_response": fallback_response,
                    "emotion": "neutral"
                }
            }
    except Exception as e:
        print(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{user_id}/{character_id}")
async def get_sessions(user_id: str, character_id: str):
    """Get all sessions for a user-character pair"""
    try:
        sessions = chat_orchestrator.get_session_summaries(user_id, character_id)
        return {
            "success": True,
            "sessions": sessions
        }
    except Exception as e:
        print(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, request: SessionDeleteRequest):
    """Delete a conversation session"""
    try:
        result = chat_orchestrator.delete_session(session_id, request.user_id)
        return result
    except Exception as e:
        print(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/personas/create")
async def create_persona(request: PersonaCreateRequest):
    """Create a new user persona"""
    try:
        persona_data = {
            "name": request.name,
            "description": request.description,
            "attributes": request.attributes
        }
        result = chat_orchestrator.create_persona(request.user_id, persona_data)
        return {
            "success": True,
            "persona": result
        }
    except Exception as e:
        print(f"Error creating persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/personas/activate")
async def activate_persona(user_id: str, persona_id: str):
    """Set active persona for user"""
    try:
        result = chat_orchestrator.set_active_persona(user_id, persona_id)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        print(f"Error activating persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/personas/{user_id}/active")
async def get_active_persona(user_id: str):
    """Get current active persona for user"""
    try:
        persona = chat_orchestrator.get_active_persona(user_id)
        return {
            "success": True,
            "persona": persona
        }
    except Exception as e:
        print(f"Error getting active persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/personas/{user_id}")
async def get_user_personas(user_id: str):
    """Get all personas for a user"""
    try:
        personas = chat_orchestrator.get_user_personas(user_id)
        return {
            "success": True,
            "personas": personas
        }
    except Exception as e:
        print(f"Error getting user personas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/personas/{persona_id}")
async def update_persona(persona_id: str, request: PersonaCreateRequest):
    """Update an existing persona"""
    try:
        persona_data = {
            "name": request.name,
            "description": request.description,
            "attributes": request.attributes
        }
        result = chat_orchestrator.update_persona(request.user_id, persona_id, persona_data)
        return {
            "success": True,
            "persona": result
        }
    except Exception as e:
        print(f"Error updating persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/personas/{user_id}/{persona_id}")
async def delete_persona(user_id: str, persona_id: str):
    """Delete a persona"""
    try:
        result = chat_orchestrator.delete_persona(user_id, persona_id)
        return {
            "success": True,
            "message": "Persona deleted successfully"
        }
    except Exception as e:
        print(f"Error deleting persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================
# KNOWLEDGE MANAGEMENT ENDPOINTS
# =============================================

@app.get("/api/characters/{character_id}/knowledge")
async def get_character_knowledge(character_id: str):
    """Get all knowledge items for a character"""
    try:
        knowledge_items = knowledge_service.get_character_knowledge(character_id)
        return knowledge_items
    except Exception as e:
        print(f"Error getting character knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/characters/{character_id}/knowledge", status_code=201)
async def create_knowledge_item(character_id: str, request: KnowledgeItemCreate):
    """Create a new knowledge item for a character"""
    try:
        knowledge_data = {
            "title": request.title,
            "content": request.content,
            "keywords": request.keywords,
            "category": request.category
        }
        
        # Process simplified keywords (handles both string and list formats)
        processed_data = knowledge_service.process_simplified_keywords(knowledge_data)
        
        result = knowledge_service.create_knowledge_item(character_id, processed_data)
        return result
    except Exception as e:
        print(f"Error creating knowledge item: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/knowledge/{knowledge_id}")
async def update_knowledge_item(knowledge_id: str, request: KnowledgeItemUpdate):
    """Update an existing knowledge item"""
    try:
        update_data = {}
        if request.title is not None:
            update_data["title"] = request.title
        if request.content is not None:
            update_data["content"] = request.content
        if request.keywords is not None:
            update_data["keywords"] = request.keywords
        if request.category is not None:
            update_data["category"] = request.category
        
        result = knowledge_service.update_knowledge_item(request.character_id, knowledge_id, update_data)
        
        # Check if update failed and raise appropriate error
        if not result.get("success", False):
            error_msg = result.get("error", "Knowledge item not found")
            raise HTTPException(status_code=404, detail=error_msg)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating knowledge item: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/knowledge/{knowledge_id}")
async def delete_knowledge_item(knowledge_id: str, request: KnowledgeItemDelete):
    """Delete a knowledge item"""
    try:
        result = knowledge_service.delete_knowledge_item(request.character_id, knowledge_id)
        
        # Check if deletion failed and raise appropriate error
        if not result.get("success", False):
            error_msg = result.get("error", "Knowledge item not found")
            raise HTTPException(status_code=404, detail=error_msg)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting knowledge item: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================
# SELECTIVE MEMORY SYSTEM ENDPOINTS
# =============================================

class SelectiveConfigRequest(BaseModel):
    """Request model for updating character selective configuration"""
    config_text: str

class MemoryUpdateRequest(BaseModel):
    """Request model for updating memory status values"""
    status_updates: Dict[str, float]
    events: Optional[List[Dict]] = []
    facts: Optional[List[str]] = []

@app.post("/api/startup")
async def startup():
    """Initialize database connection on startup"""
    try:
        connected = await database_service.connect()
        return {"status": "connected" if connected else "disconnected"}
    except Exception as e:
        print(f"Database connection error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/characters/{character_id}/selective-config")
async def get_selective_config(character_id: str):
    """Get character's selective knowledge configuration"""
    try:
        # Check if we have a custom config for this character
        config_path = f"configurations/{character_id}_config.txt"
        config_text = ""
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_text = f.read()
        except FileNotFoundError:
            # Fallback to default config based on character type
            if character_id == "game_master":
                character_type = "default"  # Use default template for now
            else:
                character_type = "companion"
            config_text = config_parser_service.generate_default_config(character_type)
        
        return {
            "character_id": character_id,
            "config_text": config_text,
            "parsed": config_parser_service.parse_configuration(config_text)
        }
    except Exception as e:
        print(f"Error getting selective config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/characters/{character_id}/selective-config")
async def update_selective_config(character_id: str, request: SelectiveConfigRequest):
    """Update character's selective knowledge configuration"""
    try:
        # Parse the configuration
        parsed_config = config_parser_service.parse_configuration(request.config_text)
        
        # Validate configuration
        errors = config_parser_service.validate_configuration(parsed_config)
        if errors:
            raise HTTPException(status_code=400, detail={"errors": errors})
        
        # TODO: Save to database
        # For now, just return success
        return {
            "success": True,
            "character_id": character_id,
            "parsed_config": parsed_config
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating selective config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/{character_id}/{user_id}")
async def get_core_memory(character_id: str, user_id: str):
    """Get core memory for user-character pair"""
    try:
        # Ensure database is connected
        if not database_service.is_connected():
            await database_service.connect()
        
        core_memory = await selective_memory_service.get_core_memory(user_id, character_id)
        
        if not core_memory:
            # Initialize if doesn't exist - get character-specific config
            config_response = await get_selective_config(character_id)
            config = config_response["parsed"]
            core_memory = await selective_memory_service.initialize_memory(
                user_id, character_id, config
            )
        
        return {
            "user_id": user_id,
            "character_id": character_id,
            "core_memory": core_memory
        }
    except Exception as e:
        print(f"Error getting core memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/{character_id}/{user_id}/initialize")
async def initialize_memory(character_id: str, user_id: str):
    """Initialize or reset core memory"""
    try:
        # Ensure database is connected
        if not database_service.is_connected():
            await database_service.connect()
        
        # Get character config (would fetch from DB in production)
        config = config_parser_service.parse_configuration(
            config_parser_service.generate_default_config()
        )
        
        core_memory = await selective_memory_service.reset_memory(
            user_id, character_id, config
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "character_id": character_id,
            "core_memory": core_memory
        }
    except Exception as e:
        print(f"Error initializing memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/memory/{character_id}/{user_id}/update")
async def update_memory(character_id: str, user_id: str, request: MemoryUpdateRequest):
    """Update memory with status changes, events, and facts"""
    try:
        # Ensure database is connected
        if not database_service.is_connected():
            await database_service.connect()
        
        # Get character config
        config = config_parser_service.parse_configuration(
            config_parser_service.generate_default_config()
        )
        
        # Update status values
        if request.status_updates:
            await selective_memory_service.update_status_values(
                user_id, character_id, request.status_updates, config
            )
        
        # Add events
        for event in request.events or []:
            await selective_memory_service.add_event(user_id, character_id, event)
        
        # Add facts
        for fact in request.facts or []:
            await selective_memory_service.add_persistent_fact(user_id, character_id, fact)
        
        # Get updated memory
        core_memory = await selective_memory_service.get_core_memory(user_id, character_id)
        
        return {
            "success": True,
            "core_memory": core_memory
        }
    except Exception as e:
        print(f"Error updating memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/{character_id}/{user_id}/compress")
async def compress_memory_history(character_id: str, user_id: str, messages: List[Dict]):
    """Compress conversation history into memory"""
    try:
        # Get character config for compression prompt
        config = config_parser_service.parse_configuration(
            config_parser_service.generate_default_config()
        )
        
        compression_prompt = config.get("memory_compression_prompt", "")
        
        compressed = await selective_memory_service.compress_history(
            user_id, character_id, messages, compression_prompt
        )
        
        return {
            "success": True,
            "compressed_history": compressed
        }
    except Exception as e:
        print(f"Error compressing history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================
# EXISTING TEST ENDPOINTS
# =============================================

@app.post("/api/test-stt-tts")
async def test_stt_with_tts():
    """Test STT accuracy by generating TTS audio and sending it back through STT"""
    try:
        test_text = "안녕하세요, 반갑습니다"
        print(f"🧪 Starting TTS→STT test with text: '{test_text}'")
        
        # Step 1: Generate TTS audio
        print("🎤 Step 1: Generating TTS audio...")
        tts_audio_base64 = await tts_service.generate_speech(
            text=test_text,
            voice_id="tc_61c97b56f1b7877a74df625b",  # Emma voice
            emotion="normal",
            speed=1.0
        )
        
        if not tts_audio_base64:
            return {
                "success": False,
                "error": "Failed to generate TTS audio",
                "original_text": test_text
            }
        
        print(f"✅ TTS audio generated, length: {len(tts_audio_base64)} chars")
        
        # Step 2: Send TTS audio through STT
        print("🔄 Step 2: Processing TTS audio through STT...")
        stt_result = await stt_service.transcribe_audio(tts_audio_base64)
        
        print(f"🎯 STT Result: '{stt_result}'")
        
        # Step 3: Compare results
        success = bool(stt_result and stt_result.strip())
        accuracy_match = stt_result == test_text if stt_result else False
        
        result = {
            "success": success,
            "original_text": test_text,
            "stt_result": stt_result,
            "exact_match": accuracy_match,
            "tts_audio_length": len(tts_audio_base64),
            "test_summary": f"Generated TTS for '{test_text}' and got STT result: '{stt_result}'"
        }
        
        if accuracy_match:
            print("🎉 PERFECT MATCH! STT correctly recognized TTS audio")
        elif stt_result:
            print(f"⚠️ PARTIAL SUCCESS: STT recognized something but not exact match")
        else:
            print("❌ FAILURE: STT could not recognize TTS audio")
            
        return result
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "original_text": "안녕하세요, 반갑습니다"
        }

# Session Management API Endpoints
@app.post("/api/sessions/create")
async def create_session(user_id: str, character_id: str, persona_id: str = None):
    """Create new conversation session"""
    try:
        session = conversation_service.create_session(user_id, character_id, persona_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{user_id}/{character_id}")
async def get_sessions(user_id: str, character_id: str):
    """Get all sessions for user and character"""
    try:
        sessions = conversation_service.get_previous_sessions(user_id, character_id)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat-with-session", response_model=ChatWithSessionResponse)
async def chat_with_session(request: ChatWithSessionRequest):
    """Platform-grade chat with intelligent session management"""
    try:
        # 🎯 SMART SESSION HANDLING: Auto-create with greeting if new session
        if not request.session_id:
            return await create_session_with_auto_greeting(request)
        
        # 🚀 UNIFIED CONVERSATION PROCESSING: All existing sessions use single flow
        return await process_unified_conversation(request)
        
        # Check for predefined greeting message from frontend  
        if request.message.startswith("__PREDEFINED_GREETING__:"):
            predefined_greeting = request.message[len("__PREDEFINED_GREETING__:"):]
            print(f"🎭 Received predefined greeting from frontend: '{predefined_greeting}'")
            
            # Create or get session
            if not request.session_id:
                session_data = conversation_service.create_session(
                    request.user_id, 
                    request.character_id, 
                    request.persona_id
                )
                session_id = session_data["session_id"]
                print(f"✅ Created new session for predefined greeting: {session_id}")
            else:
                session_id = request.session_id
            
            # 🆕 PROACTIVE KNOWLEDGE CACHING FROM GREETING
            cached_knowledge = incremental_cache.cache_greeting_knowledge(
                session_id, predefined_greeting, request.character_id
            )
            print(f"📚 Cached {len(cached_knowledge)} knowledge items from greeting")
            
            # Store the greeting exchange in session history
            # Store user's greeting request
            conversation_service.add_message_to_session(
                session_id, "user", "안녕하세요", request.user_id
            )
            
            # Store the predefined greeting as assistant response
            conversation_service.add_message_to_session(
                session_id, "assistant", predefined_greeting, request.user_id
            )
            
            # Get updated session info
            updated_session = conversation_service.get_session(session_id, request.user_id)
            
            # Check if this is the quiz character and add greeting suggestions
            tools = None
            if 'quiz' in request.character_id:  # Generic quiz character detection
                from services.greeting_suggestion_generator import GreetingSuggestionGenerator
                greeting_generator = GreetingSuggestionGenerator()
                greeting_context = {
                    "character_id": request.character_id,
                    "greeting_message": predefined_greeting,
                    "character_personality": "교육적이고 친근한 역사 튜터",
                    "suggestions_enabled": True
                }
                suggestions = greeting_generator.generate_greeting_suggestions(greeting_context)
                tools = [
                    {
                        "type": "show_selection",
                        "data": {
                            "items": suggestions,
                            "question": "어떤 퀴즈로 시작할까요?"
                        }
                    }
                ]
            
            # Return the predefined greeting (no LLM call needed)
            return ChatWithSessionResponse(
                character=request.character_id,
                dialogue=predefined_greeting,
                emotion="happy",
                speed=1.0,
                audio=None,  # Frontend will handle TTS separately
                session_id=session_id,
                message_count=updated_session["message_count"],
                session_summary=updated_session.get("session_summary", ""),
                tools=tools  # Add tools if present
            )
        
        # 🎯 STREAMLINED: Removed incorrect user input pattern detection
        # Continuous flow detection now happens after LLM response generation
        
        # Check if this is a new session and user is asking for greeting
        is_new_session = not request.session_id
        is_greeting_request = (
            is_new_session and
            request.message.strip().lower() in ['안녕하세요', '안녕', 'hello', 'hi', '반가워요', '처음 뵙겠습니다']
        )
        
        print(f"🔍 Greeting check - New session: {is_new_session}, Message: '{request.message}', Is greeting: {is_greeting_request}")
        print(f"🔍 Character ID: {request.character_id}")
        
        # 🎯 CONTINUOUS FLOW DETECTION: Check user input for feedback patterns BEFORE greeting check
        print(f"🔍 Checking user input for continuous flow patterns...")
        # Removed erroneous user input pattern detection - continuous flow now happens after LLM response
        
        # If it's a greeting request, try to use direct greeting from character data
        if is_greeting_request:
            try:
                # Get character data with greetings
                character = await character_service.get_character(request.character_id)
                print(f"🎭 Character found: {character is not None}")
                if character:
                    print(f"🎭 Character greetings: {character.get('greetings', 'NOT FOUND')}")
                    print(f"🎭 Greeting suggestions enabled: {character.get('greeting_suggestions_enabled', False)}")
                
                # Special handling for quiz character with greeting suggestions
                print(f"🎭 Quiz character check: {'quiz' in request.character_id}")
                print(f"🎭 Character exists: {character is not None}")
                print(f"🎭 Suggestions enabled: {character.get('greeting_suggestions_enabled', False) if character else False}")
                
                if 'quiz' in request.character_id and character and character.get('greeting_suggestions_enabled', False):  # Generic quiz character
                    print(f"🎭 ENTERING QUIZ CHARACTER GREETING PATH")
                    from services.greeting_suggestion_generator import GreetingSuggestionGenerator
                    
                    greeting_generator = GreetingSuggestionGenerator()
                    greeting_context = {
                        "character_id": request.character_id,
                        "greeting_message": "안녕하세요! 한국사 퀴즈를 함께 풀어볼까요?",
                        "character_personality": "교육적이고 친근한 역사 튜터",
                        "suggestions_enabled": True
                    }
                    
                    suggestions = greeting_generator.generate_greeting_suggestions(greeting_context)
                    
                    # Create new session
                    session_data = conversation_service.create_session(
                        request.user_id, 
                        request.character_id, 
                        request.persona_id
                    )
                    session_id = session_data["session_id"]
                    
                    greeting_text = "안녕하세요! 한국사 퀴즈를 함께 풀어볼까요? 어떤 주제로 시작하고 싶으신가요?"
                    
                    # Save messages to session
                    conversation_service.add_message_to_session(
                        session_id, "user", request.message, request.user_id
                    )
                    conversation_service.add_message_to_session(
                        session_id, "assistant", greeting_text, request.user_id
                    )
                    
                    # Load updated session
                    updated_session = conversation_service.load_session_messages(session_id, request.user_id)
                    
                    # Generate TTS for greeting
                    audio_base64 = None
                    try:
                        print(f"🎵 Generating TTS for quiz character greeting")
                        audio_base64 = await seolminseok_tts_service.generate_tts(greeting_text)
                        
                        # No fallback - keep 설민석's unique voice
                        if audio_base64 is None:
                            print(f"⚠️ Seolminseok TTS failed, continuing without audio")
                    except Exception as e:
                        print(f"TTS generation failed: {e}")
                        audio_base64 = None
                    
                    # Return response with tools
                    return ChatWithSessionResponse(
                        character=character.get('name', request.character_id),
                        dialogue=greeting_text,
                        emotion="happy",
                        speed=1.0,
                        audio=audio_base64,
                        session_id=session_id,
                        message_count=updated_session["message_count"],
                        session_summary=updated_session.get("session_summary", ""),
                        tools=[
                            {
                                "type": "show_selection",
                                "data": {
                                    "items": suggestions,
                                    "question": "어떤 퀴즈로 시작할까요?"
                                }
                            }
                        ]
                    )
                
                elif character and 'greetings' in character and character['greetings']:
                    # Randomly select a greeting
                    selected_greeting = random.choice(character['greetings'])
                    print(f"✅ Using direct greeting: '{selected_greeting}'")
                    
                    # Create new session first
                    session_data = conversation_service.create_session(
                        request.user_id, 
                        request.character_id, 
                        request.persona_id
                    )
                    session_id = session_data["session_id"]
                    
                    # Save user message to session
                    conversation_service.add_message_to_session(
                        session_id, "user", request.message, request.user_id
                    )
                    
                    # Save the direct greeting as assistant response
                    conversation_service.add_message_to_session(
                        session_id, "assistant", selected_greeting, request.user_id
                    )
                    
                    # Generate TTS for the greeting
                    voice_id = request.voice_id or "tc_61c97b56f1b7877a74df625b"
                    
                    # Special handling for 설민석 character
                    if 'seol_min_seok' in request.character_id:
                        print(f"🎭 설민석 character detected - using dedicated TTS service for greeting")
                        audio_data = await seolminseok_tts_service.generate_tts(
                            selected_greeting, 
                            request.character_id
                        )
                    else:
                        # Use regular TTS service
                        audio_data = await tts_service.generate_speech(
                            selected_greeting, 
                            voice_id
                        )
                    
                    # Load updated session for metadata
                    updated_session = conversation_service.load_session_messages(session_id, request.user_id)
                    
                    return ChatWithSessionResponse(
                        character=character.get('name', request.character_id),
                        dialogue=selected_greeting,
                        emotion="happy",
                        speed=1.0,
                        audio=audio_data,
                        session_id=session_id,
                        message_count=updated_session["message_count"],
                        session_summary=updated_session.get("session_summary", "")
                    )
                    
            except Exception as e:
                print(f"❌ Failed to use direct greeting, falling back to LLM: {e}")
                # Fall through to normal LLM processing
        else:
            print(f"⏭️  Not a greeting request, proceeding with normal LLM flow")
        
        # Normal session flow (continue existing or create new without direct greeting)
        if request.session_id:
            # Continue existing session - load enhanced context with compressed history
            session_data = conversation_service.load_session_messages(request.session_id, request.user_id)
            session_id = request.session_id
        else:
            # Create new session
            session_data = conversation_service.create_session(
                request.user_id, 
                request.character_id, 
                request.persona_id
            )
            session_id = session_data["session_id"]
        
        # Save user message to session
        conversation_service.add_message_to_session(
            session_id, "user", request.message, request.user_id
        )
        
        # 🆕 ENHANCED: Use incremental knowledge cache + optimized prompts
        
        # Get cached knowledge with incremental additions
        cached_knowledge = incremental_cache.add_knowledge_incrementally(
            session_id, request.message, request.character_id
        )
        
        # Get conversation history for prompt building
        session_data = conversation_service.load_session_messages(session_id, request.user_id)
        
        # Check if session data was loaded successfully
        if session_data is None:
            print(f"❌ ERROR: Session {session_id} not found for user {request.user_id}")
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        conversation_history = session_data.get("messages", [])
        
        # Generate AI response using optimized prompt structure
        if llm_available:
            # Build optimized prompt with 3-tier structure
            optimized_prompt = prompt_builder.build_llm_prompt(
                character_prompt=request.character_prompt,
                cached_knowledge=cached_knowledge,
                conversation_history=conversation_history,
                current_user_input=request.message,
                character_id=request.character_id
            )
            
            print(f"🔧 Using optimized prompt with {len(cached_knowledge)} cached knowledge items")
            
            # Generate response using optimized prompt
            response = azure_client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[{"role": "system", "content": optimized_prompt}],
                max_tokens=300,
                temperature=0.7,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    response_data = json.loads(json_match.group())
                else:
                    response_data = json.loads(response_text)
                
                # Create ChatResponse object
                from dataclasses import dataclass
                @dataclass 
                class ChatResponse:
                    character: str
                    dialogue: str
                    emotion: str
                    speed: float
                    audio: Optional[str] = None  # Add audio attribute
                
                response = ChatResponse(
                    character=response_data.get('character', request.character_id),
                    dialogue=response_data.get('dialogue', '응답을 생성할 수 없습니다.'),
                    emotion=response_data.get('emotion', 'normal'),
                    speed=response_data.get('speed', 1.0),
                    audio=None  # Initialize with None
                )
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Failed to parse AI response: {e}")
                response = ChatResponse(
                    character=request.character_id,
                    dialogue="응답을 생성하는 중 오류가 발생했습니다.",
                    emotion="normal",
                    speed=1.0,
                    audio=None  # Add audio attribute
                )
        else:
            response = generate_mock_response(request.character_id, request.message)
        
        # Save AI response to session
        conversation_service.add_message_to_session(
            session_id, "assistant", response.dialogue, request.user_id
        )
        
        # Load updated session for metadata
        updated_session = conversation_service.load_session_messages(session_id, request.user_id)
        
        # Generate TTS audio for the response
        try:
            voice_id = request.voice_id or "tc_61c97b56f1b7877a74df625b"  # Default Emma voice
            
            # Special handling for specific characters
            tts_emotion = response.emotion
            
            # 설민석 characters (both regular and quiz) - use dedicated TTS service
            if 'quiz' in request.character_id:  # Generic quiz character detection
                print(f"🎭 설민석 character detected ({request.character_id}) - using dedicated TTS service")
                audio_data = await seolminseok_tts_service.generate_tts(
                    text=response.dialogue,
                    use_hd=True,
                    language="auto"
                )
            # 윤아리 - always use whisper emotion
            elif request.character_id == 'yoon_ahri':
                tts_emotion = 'whisper'
                response.emotion = 'whisper'
                
                # Generate audio with regular TTS service
                audio_data = await tts_service.generate_speech(
                    text=response.dialogue,
                    voice_id=voice_id,
                    emotion=tts_emotion,
                    speed=response.speed
                )
            # Default - use regular TTS service
            else:
                # Generate audio with regular TTS service
                audio_data = await tts_service.generate_speech(
                    text=response.dialogue,
                    voice_id=voice_id,
                    emotion=tts_emotion,
                    speed=response.speed
                )
            
            if audio_data:
                response.audio = audio_data
                print(f"✅ TTS SUCCESS: Audio generated for dialogue")
            else:
                print(f"❌ TTS generation failed, no audio will be provided")
                response.audio = None
                
        except Exception as tts_error:
            print(f"❌ TTS Error: {tts_error}")
            response.audio = None
        
        print(f"📝 TTS section completed, moving to ContentIntelligence...")
        
        # 🔍 DEBUG: Check if we reach the ContentIntelligence section
        print(f"🔍 DEBUG: About to start ContentIntelligence analysis...")
        print(f"🔍 DEBUG: Response dialogue: '{response.dialogue}'")
        
        # 🧠 INTELLIGENT TOOL DETECTION: Analyze LLM response for tool opportunities
        print(f"🔧 TOOL-ORCHESTRATED SYSTEM: Analyzing LLM response for structured tool commands...")
        tools = None
        try:
            from services.tool_orchestrator import ToolOrchestrator
            from services.platform_tool_handler import PlatformToolHandler
            
            orchestrator = ToolOrchestrator()
            handler = PlatformToolHandler()
            print(f"🔧 ToolOrchestrator and PlatformToolHandler initialized successfully")
            
            # Check if LLM response contains JSON tool commands
            raw_response = response.dialogue.strip()
            
            # Try to parse the response as JSON (for tool-structured responses)
            if raw_response.startswith('{') and raw_response.endswith('}'):
                try:
                    print(f"🔧 Detected JSON tool response, parsing with ToolOrchestrator...")
                    parsed_response = orchestrator.parse_llm_response(raw_response)
                    
                    # Extract dialogue and tool information
                    response.dialogue = parsed_response["dialogue"]
                    response.emotion = parsed_response.get("emotion", "neutral")
                    response.speed = parsed_response.get("speed", 1.0)
                    
                    if "tool" in parsed_response:
                        print(f"🔧 Tool detected: {parsed_response['tool']}")
                        
                        # Execute the tool using PlatformToolHandler
                        tool_result = handler.execute_tool(
                            parsed_response["tool"], 
                            parsed_response["tool_data"]
                        )
                        
                        # Convert tool result to legacy format for compatibility
                        tools = [{
                            "type": parsed_response["tool"],
                            "data": tool_result
                        }]
                        
                        print(f"🔧 Tool executed successfully: {parsed_response['tool']}")
                        print(f"🔧 Generated UI: {tool_result.get('ui_type', 'unknown')}")
                        
                except Exception as parse_error:
                    print(f"🔧 JSON parsing failed, treating as normal dialogue: {parse_error}")
                    # Not a JSON response, treat as normal dialogue
            else:
                print(f"🔧 Normal dialogue response, no tools detected")
                
        except Exception as tool_orchestrator_error:
            print(f"🔧 ToolOrchestrator error: {tool_orchestrator_error}")
            import traceback
            traceback.print_exc()
            # Continue without tools if orchestrator fails
        
        # Return session-aware response with intelligent tools
        return ChatWithSessionResponse(
            character=response.character,
            dialogue=response.dialogue,
            emotion=response.emotion,
            speed=response.speed,
            audio=response.audio,
            session_id=session_id,
            message_count=updated_session["message_count"],
            session_summary=updated_session.get("session_summary", ""),
            tools=tools  # 🆕 Add intelligent tools
        )
        
    except Exception as e:
        print(f"Error in chat-with-session endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, user_id: str):
    """Get message history for a session"""
    try:
        session_data = conversation_service.load_session_messages(session_id, user_id)
        return session_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, user_id: str):
    """Delete a conversation session"""
    try:
        result = conversation_service.delete_session(session_id, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Interactive Chat API Endpoints for Tool-based Chat
# ====================================================

class InteractiveChatRequest(BaseModel):
    message: str
    character_id: str
    session_id: str

class ContinuationRequest(BaseModel):
    session_id: str
    context: Dict[str, Any]

@app.post("/api/chat/interactive")
async def interactive_chat(request: InteractiveChatRequest):
    """Interactive chat endpoint that returns responses with tools"""
    try:
        # Import our new services
        from services.tool_processor import ToolProcessor
        from services.continuous_output_manager import ContinuousOutputManager
        from services.suggestion_chip_generator import SuggestionChipGenerator
        from services.greeting_suggestion_generator import GreetingSuggestionGenerator
        
        # Check for greeting messages first
        greeting_messages = ["안녕하세요", "안녕", "hello", "hi"]
        if any(greeting in request.message.lower() for greeting in greeting_messages):
            # Handle greeting with suggestions for quiz-focused character
            if 'quiz' in request.character_id:  # Generic quiz character detection
                greeting_generator = GreetingSuggestionGenerator()
                greeting_context = {
                    "character_id": request.character_id,
                    "greeting_message": "안녕하세요! 한국사 퀴즈를 함께 풀어볼까요?",
                    "character_personality": "교육적이고 친근한 역사 튜터",
                    "suggestions_enabled": True
                }
                
                suggestions = greeting_generator.generate_greeting_suggestions(greeting_context)
                
                response_data = {
                    "character": request.character_id,
                    "dialogue": "안녕하세요! 한국사 퀴즈를 함께 풀어볼까요? 어떤 주제로 시작하고 싶으신가요?",
                    "emotion": "friendly",
                    "speed": 1.0,
                    "tools": [
                        {
                            "type": "show_selection",
                            "data": {
                                "items": suggestions,
                                "question": "어떤 퀴즈로 시작할까요?"
                            }
                        }
                    ]
                }
                return response_data
        
        # Check if this is an answer to a quiz question
        if request.message in ["1919년", "1920년", "1921년", "1922년"]:
            if request.message == "1919년":
                # Correct answer - provide positive feedback with continuation
                response_data = {
                    "character": request.character_id,
                    "dialogue": "정답입니다! 3·1 운동은 1919년 3월 1일에 시작되었죠. 다음 문제로 가볼까요?",
                    "emotion": "happy",
                    "speed": 1.0,
                    "tools": [
                        {
                            "type": "continue_output",
                            "data": {
                                "reason": "quiz_continuation"
                            }
                        }
                    ]
                }
            else:
                # Wrong answer - provide explanation
                response_data = {
                    "character": request.character_id,
                    "dialogue": f"아쉽네요. 정답은 1919년입니다. 3·1 운동은 1919년 3월 1일에 시작된 독립운동이에요.",
                    "emotion": "supportive", 
                    "speed": 1.0,
                    "tools": []
                }
        else:
            # Initial quiz request or general conversation
            response_data = {
                "character": request.character_id,
                "dialogue": "퀴즈를 시작하겠습니다! 3·1 운동이 일어난 연도는?",
                "emotion": "excited",
                "speed": 1.0,
                "tools": [
                    {
                        "type": "show_selection",
                        "data": {
                            "items": ["1919년", "1920년", "1921년", "1922년"],
                            "question": "3·1 운동이 일어난 연도는?",
                            "correctAnswer": "1919년"
                        }
                    }
                ]
            }
        
        return response_data
        
    except Exception as e:
        print(f"Error in interactive chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/continuation")
async def handle_continuation(request: ContinuationRequest):
    """Handle continuation requests for multi-turn conversations"""
    try:
        from services.continuous_output_manager import ContinuousOutputManager
        
        continuator = ContinuousOutputManager()
        
        # Simple continuation response for testing
        continuation_data = {
            "character": "history_character",
            "dialogue": "다음 문제입니다! 조선시대 첫 번째 왕은?",
            "emotion": "normal",
            "speed": 1.0,
            "tools": [
                {
                    "type": "show_selection",
                    "data": {
                        "items": ["태조", "태종", "세종", "성종"],
                        "question": "조선시대 첫 번째 왕은?",
                        "correctAnswer": "태조"
                    }
                }
            ]
        }
        
        return continuation_data
        
    except Exception as e:
        print(f"Error in continuation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Continuous Answer Tool API Models
class ContinuousFlowTriggerRequest(BaseModel):
    session_id: str
    character_id: str
    tool_type: str
    data: Dict[str, Any]

class ContinuousFlowProgressRequest(BaseModel):
    session_id: str
    trigger_type: str
    data: Optional[Dict[str, Any]] = None


@app.post("/api/continuous-flow/trigger")
async def trigger_continuous_flow(request: ContinuousFlowTriggerRequest):
    """
    REDIRECT: Old legacy endpoint - now redirects to modern platform-chat
    This ensures all requests use the working ToolOrchestrator architecture
    """
    print(f"🔄 LEGACY ENDPOINT HIT: Redirecting to platform-chat")
    print(f"   Session: {request.session_id}")
    print(f"   Character: {request.character_id}")
    print(f"   User Selection: {request.data.get('selection', 'N/A')}")
    
    # Import the orchestrator
    orchestrator = global_tool_orchestrator
    
    # Process through modern ToolOrchestrator instead of legacy system
    response = await orchestrator.process_user_interaction(
        user_input=request.data.get("selection", ""),
        character_id=request.character_id,
        session_id=request.session_id,
        user_id="legacy_redirect_user"
    )
    
    print(f"✅ REDIRECTED RESPONSE: {len(response.get('tools', []))} tools")
    
    # Return in legacy format for compatibility 
    return {
        "status": "flow_completed",
        "session_id": request.session_id,
        "step_result": {
            "step_id": "redirected_response",
            "step_type": "platform_chat_redirect", 
            "response": {
                "dialogue": response.get("dialogue", ""),
                "tools": response.get("tools", [])
            },
            "audio": response.get("audio_url"),
            "error": None,
            "metadata": {
                "architecture": "redirected_to_tool_orchestrator",
                "redirect_note": "Legacy endpoint redirected to modern ToolOrchestrator"
            }
        },
        "flow_continues": False,
        "next_step_index": None
    }


@app.post("/api/continuous-flow/progress")
async def progress_continuous_flow(request: ContinuousFlowProgressRequest):
    """
    Progress a continuous flow to next step
    Called when conditions are met (e.g., audio completion)
    """
    try:
        print(f"⏭️  Progressing continuous flow: {request.session_id}, {request.trigger_type}")
        
        # Progress the flow
        flow_execution = await continuous_answer_tool.progress_flow(
            session_id=request.session_id,
            trigger_type=request.trigger_type,
            data=request.data
        )
        
        if not flow_execution:
            return {"error": "No active flow found or invalid trigger"}
        
        return {
            "status": "step_executed" if flow_execution.flow_continues else "flow_completed",
            "session_id": flow_execution.session_id,
            "step_result": {
                "step_id": flow_execution.step_result.step_id,
                "step_type": flow_execution.step_result.step_type,
                "response": flow_execution.step_result.response,
                "audio": flow_execution.step_result.audio,
                "error": flow_execution.step_result.error,
                "metadata": flow_execution.step_result.metadata
            } if flow_execution.step_result else None,
            "flow_continues": flow_execution.flow_continues,
            "next_step_index": flow_execution.next_step_index
        }
        
    except Exception as e:
        print(f"❌ Error progressing continuous flow: {e}")
        raise HTTPException(status_code=500, detail=f"Flow progression failed: {str(e)}")


@app.get("/api/continuous-flow/status/{session_id}")
async def get_continuous_flow_status(session_id: str):
    """
    Get status of active continuous flow for a session
    """
    try:
        flow_state = continuous_answer_tool.get_active_flow(session_id)
        
        if not flow_state:
            return {"active": False}
        
        return {
            "active": True,
            "session_id": flow_state.session_id,
            "character_id": flow_state.character_id,
            "flow_id": flow_state.flow_config.get("flow_id"),
            "current_step": flow_state.current_step,
            "total_steps": len(flow_state.flow_config.get("steps", [])),
            "step_results_count": len(flow_state.step_results),
            "created_at": flow_state.created_at.isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error getting flow status: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@app.get("/api/continuous-flow/second-phase/{session_id}")
async def get_continuous_flow_second_phase(session_id: str, wait_timeout: int = 10, poll_interval: float = 0.5):
    """
    Get second phase data for a session after first phase completes
    Returns the question dialogue, quiz tools, and audio for second phase
    
    Args:
        session_id: Session identifier
        wait_timeout: Maximum seconds to wait for data (default 10)
        poll_interval: Seconds between polling attempts (default 0.5)
    """
    import asyncio
    import time
    
    start_time = time.time()
    
    try:
        # Always use polling mechanism to handle race condition correctly
        print(f"⏳ Polling for second phase data for session {session_id}, timeout: {wait_timeout}s")
        
        while (time.time() - start_time) < wait_timeout:
            # Check without removing data first
            second_phase_data = await continuous_answer_tool.check_second_phase_data(session_id)
            
            if second_phase_data:
                wait_time = round(time.time() - start_time, 2)
                print(f"✅ Second phase data available after {wait_time}s wait for session {session_id}")
                
                # Now retrieve and remove the data
                final_data = await continuous_answer_tool.get_second_phase_data(session_id)
                
                return {
                    "available": True,
                    "dialogue": final_data.get("dialogue", ""),
                    "tools": final_data.get("tools", []),
                    "audio_url": final_data.get("audio_url", ""),
                    "session_id": session_id,
                    "wait_time": wait_time
                }
        
        # Timeout reached
        wait_time = round(time.time() - start_time, 2)
        print(f"⏰ Timeout after {wait_time}s waiting for second phase data for session {session_id}")
        
        return {
            "available": False, 
            "message": f"Second phase data not available after {wait_time}s timeout",
            "wait_time": wait_time,
            "session_id": session_id
        }
        
    except Exception as e:
        wait_time = round(time.time() - start_time, 2)
        print(f"❌ Error getting second phase data after {wait_time}s: {e}")
        raise HTTPException(status_code=500, detail=f"Second phase retrieval failed: {str(e)}")


# Debug endpoint for tool selection debugging
class DebugToolSelectionRequest(BaseModel):
    session_id: str
    character_id: str
    selection: str
    tool_data: Optional[Dict[str, Any]] = None

@app.post("/api/debug-tool-selection")
async def debug_tool_selection(request: DebugToolSelectionRequest):
    """
    Debug endpoint to track tool selection calls from frontend
    Called by handleToolSelection function for debugging
    """
    try:
        print(f"🐛 DEBUG: Tool selection called")
        print(f"   Session: {request.session_id}")
        print(f"   Character: {request.character_id}")
        print(f"   Selection: {request.selection}")
        print(f"   Tool Data: {request.tool_data}")
        
        # Log this for debugging the continuous flow integration
        return {
            "status": "debug_logged",
            "message": f"Selection '{request.selection}' logged for session {request.session_id}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error in debug tool selection: {e}")
        raise HTTPException(status_code=500, detail=f"Debug logging failed: {str(e)}")


def get_assistant_tools():
    """
    Get assistant-ui compatible tool function definitions
    """
    return {
        "show_selection": {
            "description": "Show selection options to user for quiz or choices",
            "parameters": {
                "question": {
                    "type": "string",
                    "description": "The question to display to the user"
                },
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Array of selection options"
                },
                "correctAnswer": {
                    "type": "string", 
                    "description": "The correct answer (if applicable)"
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata for the selection"
                }
            }
        },
        "continue_output": {
            "description": "Continue multi-step conversation output", 
            "parameters": {
                "trigger_type": {
                    "type": "string",
                    "description": "Type of trigger for continuation"
                },
                "context": {
                    "type": "object",
                    "description": "Context information for continuation"
                }
            }
        }
    }

# 🚀 NEW TOOL-DRIVEN ARCHITECTURE ENDPOINT
class PlatformChatRequest(BaseModel):
    user_input: str
    character_id: str
    session_id: Optional[str] = None
    user_id: str = "default_user"

class PlatformChatResponse(BaseModel):
    character: str
    dialogue: str
    tools: List[Dict[str, Any]] = []
    audio_url: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: str

@app.post("/api/platform-chat", response_model=PlatformChatResponse)
async def platform_chat(request: PlatformChatRequest):
    """
    NEW: Platform-grade chat using tool orchestration
    
    This endpoint uses the new tool-driven architecture:
    - LLM processes user input with character prompts
    - Tools are generated based on context and character behavior
    - No hardcoded logic - all behavior driven by prompts
    """
    try:
        print(f"🚀 Platform chat: {request.user_input[:50]}... for character {request.character_id}")
        
        # 🚀 PRIORITY 1 FIX: Use global orchestrator with cached TTS services
        # No more fresh instance creation - reuse cached SeolMinSeok TTS service
        orchestrator = global_tool_orchestrator
        
        # Process interaction through orchestrator
        if not request.session_id:
            # Create new session and generate greeting
            response = await orchestrator.create_session_and_greet(
                character_id=request.character_id,
                user_id=request.user_id
            )
        else:
            # Continue existing conversation
            response = await orchestrator.process_user_interaction(
                user_input=request.user_input,
                character_id=request.character_id,
                session_id=request.session_id,
                user_id=request.user_id
            )
        
        print(f"✅ Platform response: {len(response.get('tools', []))} tools, audio={bool(response.get('audio_url'))}")
        
        return PlatformChatResponse(
            character=response.get('character', request.character_id),
            dialogue=response.get('dialogue', ''),
            tools=response.get('tools', []),
            audio_url=response.get('audio_url'),
            session_id=response.get('session_id'),
            timestamp=response.get('timestamp', datetime.utcnow().isoformat())
        )
        
    except Exception as e:
        print(f"❌ Platform chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Platform chat error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)