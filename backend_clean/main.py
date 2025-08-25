from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AzureOpenAI
import json
import random
import os
from dotenv import load_dotenv
import re
from typing import List, Dict, Any, Optional, Union

load_dotenv()

# Import services after loading environment
from services.tts_service import tts_service
from services.stt_service import stt_service
from services.voice_recommend_service import voice_recommend_service
from services.chat_orchestrator import ChatOrchestrator
from services.knowledge_service import KnowledgeService
from services.character_mood_service import CharacterMoodService
from services.conversation_service import ConversationService
from services.selective_memory_service import SelectiveMemoryService
from services.config_parser_service import ConfigParserService
from services.database_service import DatabaseService

# Initialize selective memory system
database_service = DatabaseService()
selective_memory_service = SelectiveMemoryService(database_service)
config_parser_service = ConfigParserService()

# Initialize chat orchestrator with database
chat_orchestrator = ChatOrchestrator(database_service)

# Initialize knowledge management services
knowledge_service = KnowledgeService()
character_mood_service = CharacterMoodService()
conversation_service = ConversationService()

# Print STT service status on startup
print(f"📢 STT Service Status: {'✅ Available' if stt_service.available else '❌ Not Available'}")

app = FastAPI(title="Voice Character Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
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

class ChatResponse(BaseModel):
    character: str
    dialogue: str
    emotion: str = "neutral"
    speed: float = 1.0
    audio: Optional[str] = None  # base64 encoded audio data

# Session-Aware Chat Models
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
    character_data = parse_character_prompt(character_prompt)
    history_text = format_conversation_history(history)
    
    # Check if this is a first greeting (empty history + greeting message)
    is_first_greeting = (
        len(history) == 0 and 
        user_message.strip().lower() in ['안녕하세요', '안녕', 'hello', 'hi', '반가워요', '처음 뵙겠습니다']
    )

def create_enhanced_system_prompt_with_memory(character_prompt: str, ai_context: dict, user_message: str) -> str:
    """Create a system prompt using enhanced AI context with compressed history"""
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

    return prompt

async def generate_enhanced_ai_response(character_prompt: str, ai_context: dict, user_message: str) -> ChatResponse:
    """Generate response using Azure OpenAI with enhanced context including compressed history"""
    try:
        system_prompt = create_enhanced_system_prompt_with_memory(character_prompt, ai_context, user_message)
        
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

    return prompt

async def generate_ai_response(character_prompt: str, history: list, user_message: str) -> ChatResponse:
    """Generate response using Azure OpenAI"""
    try:
        system_prompt = create_system_prompt(character_prompt, history, user_message)
        
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

async def generate_ai_response_enhanced(system_prompt: str) -> ChatResponse:
    """Generate AI response using enhanced system prompt"""
    try:
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

def generate_mock_response() -> ChatResponse:
    """Generate mock response when AI is not available"""
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
        if llm_available:
            response = await generate_ai_response(request.character_prompt, request.history, request.message)
        else:
            # Fallback to mock response
            print("⚠️ Using mock response - Azure OpenAI not available")
            response = generate_mock_response()
        
        # Generate TTS audio for the response
        try:
            # Extract character data for voice selection
            character_data = parse_character_prompt(request.character_prompt)
            
            # Use character-specific voice_id from the request
            voice_id = request.voice_id or "tc_61c97b56f1b7877a74df625b"  # Default Emma voice
            
            print(f"🎤 Using voice_id: {voice_id} for character: {request.character_id}")
            
            # Special handling for 윤아리 - always use whisper emotion
            tts_emotion = response.emotion
            if request.character_id == 'yoon_ahri':
                tts_emotion = 'whisper'
                print(f"🎵 윤아리 detected, using whisper emotion instead of {response.emotion}")
                # Also update the response emotion for consistency
                response.emotion = 'whisper'
            
            # Generate audio
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
                print("⚠️ TTS generation failed, returning text-only response")
                
        except Exception as tts_error:
            print(f"TTS Error: {tts_error}")
            # Continue without audio if TTS fails
        
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
        # Special handling for 윤아리 - always use whisper emotion
        tts_emotion = request.emotion
        if request.character_id == 'yoon_ahri':
            tts_emotion = 'whisper'
            print(f"🎵 윤아리 TTS detected, using whisper emotion instead of {request.emotion}")
        
        print(f"🎤 TTS request - voice_id: {request.voice_id}, emotion: {tts_emotion}")
        
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
            raise HTTPException(status_code=500, detail="TTS generation failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")

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
    """Chat with session persistence for character memory"""
    try:
        # Create or continue session
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
        
        # Get enhanced AI context with compressed history
        ai_context = conversation_service.get_enhanced_ai_context(session_id, request.user_id)
        
        # Generate AI response using enhanced context
        if llm_available:
            response = await generate_enhanced_ai_response(request.character_prompt, ai_context, request.message)
        else:
            response = generate_mock_response()
        
        # Save AI response to session
        conversation_service.add_message_to_session(
            session_id, "assistant", response.dialogue, request.user_id
        )
        
        # Load updated session for metadata
        updated_session = conversation_service.load_session_messages(session_id, request.user_id)
        
        # Generate TTS audio for the response
        try:
            voice_id = request.voice_id or "tc_61c97b56f1b7877a74df625b"  # Default Emma voice
            
            # Special handling for 윤아리 - always use whisper emotion
            tts_emotion = response.emotion
            if request.character_id == 'yoon_ahri':
                tts_emotion = 'whisper'
                response.emotion = 'whisper'
            
            # Generate audio
            audio_data = await tts_service.generate_speech(
                text=response.dialogue,
                voice_id=voice_id,
                emotion=tts_emotion,
                speed=response.speed
            )
            
            if audio_data:
                response.audio = audio_data
                
        except Exception as tts_error:
            print(f"TTS Error: {tts_error}")
            # Continue without audio if TTS fails
        
        # Return session-aware response
        return ChatWithSessionResponse(
            character=response.character,
            dialogue=response.dialogue,
            emotion=response.emotion,
            speed=response.speed,
            audio=response.audio,
            session_id=session_id,
            message_count=updated_session["message_count"],
            session_summary=updated_session.get("session_summary", "")
        )
        
    except Exception as e:
        print(f"Error in chat-with-session endpoint: {e}")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)