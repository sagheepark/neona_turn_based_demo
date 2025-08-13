from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AzureOpenAI
import json
import random
import os
from dotenv import load_dotenv
import re
from typing import List, Dict, Any, Optional

load_dotenv()

# Import services after loading environment
from services.tts_service import tts_service
from services.stt_service import stt_service
from services.voice_recommend_service import voice_recommend_service

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
    """Create a system prompt for the character"""
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)