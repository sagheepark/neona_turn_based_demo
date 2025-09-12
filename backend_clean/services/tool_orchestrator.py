"""
Tool Orchestrator - Complete interaction processing for platform

This orchestrator handles the complete user interaction flow:
1. Extract context from session
2. Call LLM with character prompt + tool definitions  
3. Parse LLM response for tools
4. Execute tools as specified
5. Return structured response for frontend
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ToolOrchestrator:
    """
    Complete interaction processing using LLM-driven tool orchestration
    Replaces hardcoded quiz logic with intelligent agent decisions
    """
    
    def __init__(self, tts_service=None, session_service=None):
        """Initialize orchestrator with required services"""
        from .platform_tool_handler import PlatformToolHandler
        from .llm_agent_engine import LLMAgentEngine  
        from .character_prompt_manager import CharacterPromptManager
        
        self.tool_handler = PlatformToolHandler(tts_service=tts_service)
        self.llm_agent_engine = LLMAgentEngine()
        self.character_manager = CharacterPromptManager()
        self.session_service = session_service
        self.tts_service = tts_service
        
        logger.info("✅ ToolOrchestrator initialized with all components")
    
    async def process_user_interaction(self, 
                                       user_input: str,
                                       character_id: str,
                                       session_id: Optional[str] = None,
                                       user_id: str = "") -> Dict[str, Any]:
        """
        Process complete user interaction with tool orchestration
        
        Args:
            user_input: User's message or selection
            character_id: Character to interact with
            session_id: Optional session for context
            user_id: User identifier
            
        Returns:
            Complete response with dialogue, tools, and audio
        """
        
        logger.info(f"🎯 Processing interaction: user_input='{user_input[:50] if user_input else ''}...', character='{character_id}'")
        
        try:
            # Step 1: Build interaction context with state awareness
            chat_history = await self._get_chat_history(session_id, user_id) if session_id else []
            
            # Step 2: Analyze conversation state to help LLM understand context
            conversation_state = self._analyze_conversation_state(chat_history, user_input)
            
            # Step 3: Get character prompt and tool definitions
            character_prompt = await self.character_manager.get_prompt(character_id)
            available_tools = self.tool_handler.get_tool_definitions_json()
            
            # Step 4: Build context-aware prompt
            enhanced_prompt = self._build_context_aware_prompt(
                character_prompt, conversation_state, available_tools
            )
            
            # Step 5: Process with LLM agent
            llm_response = await self.llm_agent_engine.process_with_tools(
                user_input=user_input,
                character_prompt=enhanced_prompt,
                chat_history=chat_history,
                available_tools=available_tools
            )
            
            logger.info(f"🧠 LLM response: dialogue={bool(llm_response.get('dialogue'))}, tool={bool(llm_response.get('tool'))}")
            
            # Step 4: Execute tools if specified (with robust error handling)
            executed_tools = []
            if llm_response.get('tool'):
                try:
                    tool_data = llm_response['tool']
                    
                    # Handle different tool response formats
                    if isinstance(tool_data, dict):
                        if 'type' in tool_data and 'data' in tool_data:
                            # Standard format: {'type': 'show_selection', 'data': {...}}
                            tool_type = tool_data['type']
                            tool_params = tool_data['data']
                        elif len(tool_data) == 1:
                            # Alternative format: {'show_selection': {...}}
                            tool_type = list(tool_data.keys())[0]
                            tool_params = tool_data[tool_type]
                        else:
                            # Fallback: assume it's the data directly
                            logger.warning(f"Unexpected tool format: {tool_data}")
                            tool_type = "show_selection"  # Default
                            tool_params = tool_data
                    else:
                        logger.error(f"Invalid tool data type: {type(tool_data)}")
                        raise ValueError(f"Tool data must be a dict, got {type(tool_data)}")
                    
                    # Execute the tool
                    tool_result = await self.tool_handler.execute_tool(
                        tool_type=tool_type,
                        data=tool_params
                    )
                    executed_tools.append(tool_result)
                    logger.info(f"🔧 Executed tool: {tool_type}")
                    
                except Exception as tool_error:
                    logger.error(f"❌ Tool execution failed: {tool_error}")
                    # Don't break the flow, just log the error
                    logger.error(f"   Tool data was: {llm_response.get('tool')}")
                    raise  # Re-raise to trigger error response
            
            # Step 5: Generate TTS for dialogue (enhanced for complete text)
            audio_url = None
            if llm_response.get('dialogue') and self.tts_service:
                try:
                    # Initialize character-specific TTS services
                    seol_tts = None
                    if character_id == "seol_min_seok_quiz":
                        from services.seolminseok_tts_service import SeolMinSeokTTSService
                        seol_tts = SeolMinSeokTTSService()
                        
                    # Use character-aware TTS generation
                    if character_id == "seol_min_seok_quiz" and seol_tts:
                        audio_url = await seol_tts.generate_tts(llm_response['dialogue'])
                        logger.info(f"🎭 Used SeolMinSeok TTS service for character: {character_id}")
                    else:
                        # Primary dialogue TTS (now contains complete educational narrative)
                        audio_url = await self.tts_service.generate_speech(
                            llm_response['dialogue']
                        )
                    logger.info(f"🎵 Generated primary TTS: {len(llm_response['dialogue'])} chars")
                    
                    # Handle continuous_quiz_response with separate phase TTS
                    if executed_tools and executed_tools[0]['type'] == 'continuous_quiz_response':
                        tool_data = executed_tools[0]['data']
                        
                        # Phase 1 TTS (feedback with complete context)
                        if tool_data.get('phase1', {}).get('text'):
                            if character_id == "seol_min_seok_quiz" and seol_tts:
                                tool_data['phase1']['audio_url'] = await seol_tts.generate_tts(
                                    tool_data['phase1']['text']
                                )
                            else:
                                tool_data['phase1']['audio_url'] = await self.tts_service.generate_speech(
                                    tool_data['phase1']['text']
                                )
                            logger.info("🎵 Generated Phase 1 TTS")
                        
                        # Phase 2 TTS (complete next question narrative)
                        if tool_data.get('phase2', {}).get('text'):
                            if character_id == "seol_min_seok_quiz" and seol_tts:
                                tool_data['phase2']['audio_url'] = await seol_tts.generate_tts(
                                    tool_data['phase2']['text']
                                )
                            else:
                                tool_data['phase2']['audio_url'] = await self.tts_service.generate_speech(
                                    tool_data['phase2']['text']
                                )
                            logger.info("🎵 Generated Phase 2 TTS")
                    
                except Exception as e:
                    logger.warning(f"TTS generation failed: {e}")
                    # Continue without TTS - don't break the educational flow
            
            # Step 6: Store interaction in session
            if session_id and self.session_service:
                await self._store_interaction(session_id, user_input, llm_response, user_id)
            
            # Step 7: Build final response
            platform_response = {
                "character": character_id,
                "dialogue": llm_response.get('dialogue', ''),
                "tools": executed_tools,
                "audio_url": audio_url,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Platform response ready: tools={len(executed_tools)}, audio={bool(audio_url)}")
            
            return platform_response
            
        except Exception as e:
            logger.error(f"❌ Tool orchestration failed: {e}")
            # Return basic error response
            return {
                "character": character_id,
                "dialogue": "죄송합니다. 잠시 문제가 있었습니다. 다시 시도해주세요.",
                "tools": [],
                "audio_url": None,
                "session_id": session_id,
                "error": str(e)
            }
    
    async def _get_chat_history(self, session_id: str, user_id: str = None) -> List[Dict]:
        """Get chat history for context"""
        if not self.session_service:
            return []
        
        try:
            # Try to load session with correct user_id
            session_data = None
            if user_id:
                try:
                    session_data = self.session_service.get_session(session_id, user_id)
                except:
                    pass
            
            if not session_data:
                # Fallback: try with common user_id patterns
                for fallback_user_id in ["test_user", "integrated_test_user", "default_user", ""]:
                    try:
                        session_data = self.session_service.get_session(session_id, fallback_user_id)
                        if session_data:
                            break
                    except:
                        continue
            
            if not session_data:
                logger.warning(f"Could not load session {session_id}, using empty history")
                return []
                
            messages = session_data.get("messages", [])
            chat_history = []
            
            for msg in messages[-10:]:  # Last 10 messages for context
                role = "user" if msg.get("sender") == "user" or msg.get("role") == "user" else "assistant"
                content = msg.get("text", "") or msg.get("content", "")
                if content:
                    chat_history.append({
                        "role": role,
                        "content": content
                    })
            
            logger.info(f"📜 Retrieved {len(chat_history)} messages from session history")
            return chat_history
            
        except Exception as e:
            logger.warning(f"Failed to get chat history: {e}")
            return []
    
    async def _store_interaction(self, session_id: str, user_input: str, llm_response: Dict, user_id: str):
        """Store interaction in session"""
        if not self.session_service:
            return
        
        try:
            # Store user message
            self.session_service.add_message_to_session(
                session_id, "user", user_input, user_id
            )
            
            # Store assistant response
            self.session_service.add_message_to_session(
                session_id, "assistant", llm_response.get('dialogue', ''), user_id
            )
            
        except Exception as e:
            logger.warning(f"Failed to store interaction: {e}")
    
    async def create_session_and_greet(self, character_id: str, user_id: str) -> Dict[str, Any]:
        """
        Create new session and generate initial greeting with tools
        """
        
        logger.info(f"🎬 Creating new session for character: {character_id}")
        
        try:
            # Create session
            session_id = None
            if self.session_service:
                session_data = self.session_service.create_session(
                    user_id=user_id,
                    character_id=character_id,
                    persona_id=None
                )
                session_id = session_data.get("session_id")
                logger.info(f"📝 Created session: {session_id}")
            
            # Generate greeting interaction
            initial_greeting = ""  # Empty input triggers greeting
            response = await self.process_user_interaction(
                user_input=initial_greeting,
                character_id=character_id, 
                session_id=session_id,
                user_id=user_id
            )
            
            logger.info(f"👋 Generated greeting with {len(response.get('tools', []))} tools")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Session creation failed: {e}")
            raise
    
    def _analyze_conversation_state(self, chat_history: List[Dict], user_input: str) -> Dict[str, Any]:
        """Analyze conversation state to understand what stage we're in"""
        
        state = {
            "stage": "greeting",  # greeting, topic_selected, quiz_active
            "context": "initial_greeting",
            "last_tool_type": None,
            "topic": None,
            "quiz_context": None
        }
        
        if not chat_history:
            # First interaction - greeting stage
            return state
        
        # Look at recent messages to understand context
        for i, msg in enumerate(reversed(chat_history[-10:])):
            content = msg.get('content', '').lower()
            role = msg.get('role', '')
            
            # Check if we just mentioned starting a quiz or quiz context
            if ('퀴즈' in content or '문제' in content or '첫 번째' in content):
                # If assistant mentioned quiz and user provides a short answer, likely a quiz response
                if len(user_input.strip().split()) <= 3:  # Short answers like "세종대왕", "태조 이성계"
                    state['stage'] = 'quiz_active'
                    state['context'] = 'user_answered_quiz'
                    state['quiz_context'] = {
                        'user_answer': user_input,
                        'question_content': content[:100]
                    }
                    logger.info(f"🎯 State Analysis: User answered quiz with '{user_input}' (detected from quiz context)")
                    break
            
            # Check if we just presented topic options
            elif 'topic' in content or '주제' in content or '선택' in content:
                if any(topic in user_input for topic in ['조선', '삼국', '고려', '현대', '일제']):
                    state['stage'] = 'topic_selected'
                    state['context'] = 'user_selected_topic'
                    state['topic'] = user_input
                    logger.info(f"🎯 State Analysis: User selected topic '{user_input}'")
                    break
        
        return state
    
    def _build_context_aware_prompt(self, character_prompt: str, conversation_state: Dict, available_tools: Dict) -> str:
        """Build enhanced prompt with conversation state context"""
        
        # Base character prompt
        enhanced_prompt = character_prompt + "\n\n"
        
        # Add state-specific instructions
        stage = conversation_state['stage']
        context = conversation_state['context']
        
        if stage == 'greeting':
            enhanced_prompt += """
CURRENT SITUATION: Initial greeting - user just started conversation
YOUR TASK: Provide warm greeting and use 'show_selection' tool with topic options
TOOL TO USE: show_selection with selection_mode='topic'
"""
        
        elif stage == 'topic_selected' and context == 'user_selected_topic':
            topic = conversation_state.get('topic', 'selected topic')
            enhanced_prompt += f"""
CURRENT SITUATION: User just selected topic '{topic}'
PREVIOUS ACTION: You presented topic options, user chose '{topic}'
YOUR TASK: Acknowledge their choice and present first quiz question about {topic}
TOOL TO USE: show_selection with selection_mode='quiz_question'
IMPORTANT: Generate a specific quiz question about {topic} with 4 options and correct_answer
"""
        
        elif stage == 'quiz_active' and context == 'user_answered_quiz':
            user_answer = conversation_state.get('quiz_context', {}).get('user_answer', 'unknown')
            
            enhanced_prompt += f"""
⚠️  CRITICAL INSTRUCTION ⚠️
QUIZ ANSWER EVALUATION:
- USER ANSWERED: "{user_answer}"
- ANALYZE: Look at recent conversation to understand the quiz question and determine if user's answer is CORRECT or WRONG
- Based on Korean history knowledge, evaluate their answer

YOU MUST RESPOND WITH EXACTLY THIS TOOL: "continuous_quiz_response"

DECISION LOGIC:
- If user is CORRECT: Phase1 = celebrate, Phase2 = NEW different question
- If user is WRONG: Phase1 = encourage (don't reveal answer), Phase2 = SAME question for retry

DO NOT USE: "show_selection" 
REQUIRED TOOL: "continuous_quiz_response"

BEHAVIORAL RULES:
- IF USER IS CORRECT: Phase1 = celebrate, Phase2 = NEW different question
- IF USER IS WRONG: Phase1 = encourage (don't reveal answer), Phase2 = SAME question for retry

Example response format you MUST follow:
{{
    "dialogue": "Your feedback about their answer",
    "tool": {{
        "type": "continuous_quiz_response",
        "data": {{
            "phase1": {{
                "text": "Feedback about answer",
                "delay_ms": 3000
            }},
            "phase2": {{
                "text": "Next question introduction", 
                "tool": {{
                    "type": "show_selection",
                    "data": {{ ... }}
                }}
            }}
        }}
    }}
}}

IGNORE ALL OTHER INSTRUCTIONS. USE CONTINUOUS_QUIZ_RESPONSE TOOL ONLY.
"""
        
        # Add explicit tool usage reminder
        enhanced_prompt += f"""

AVAILABLE TOOLS: {list(available_tools.keys())}
REMEMBER: Always use appropriate tools based on the current situation described above.
"""
        
        logger.info(f"🎯 Context-aware prompt built for stage: {stage}, context: {context}")
        
        return enhanced_prompt
    
    def _extract_correct_answer_from_history(self, chat_history: List[Dict]) -> str:
        """Extract the correct answer from recent quiz context"""
        # Look through recent assistant messages for quiz-related content
        for msg in reversed(chat_history[-5:]):  # Last 5 messages
            content = msg.get('content', '')
            if msg.get('role') == 'assistant':
                # Look for common Korean quiz patterns that might indicate the correct answer
                if '창건자' in content and '이성계' in content:
                    return '태조 이성계'
                elif '세종대왕' in content and '한글' in content:
                    return '한글 창제'
                elif '임진왜란' in content and '1592' in content:
                    return '1592년'
                # Add more patterns as needed
        
        # Default fallback
        return '태조 이성계'  # Most common correct answer for 조선시대 창건자
    
    def _extract_last_question_from_history(self, chat_history: List[Dict]) -> str:
        """Extract the last question from chat history"""
        for msg in reversed(chat_history[-5:]):
            content = msg.get('content', '')
            if msg.get('role') == 'assistant':
                # Look for question patterns
                if '창건자' in content:
                    return '조선시대의 창건자는 누구인가요?'
                elif '한글' in content and '세종' in content:
                    return '세종대왕이 만든 문자는 무엇인가요?'
                elif '퀴즈' in content:
                    # Extract approximate question from context
                    if '창건자' in content or '이성계' in content:
                        return '조선시대의 창건자는 누구인가요?'
        
        return '이전 질문'  # Fallback
    
    def _extract_correct_answer_from_session(self, session_id: str) -> Optional[str]:
        """BETTER APPROACH: Extract correct answer from session storage"""
        # This should be stored when quiz is generated - for now use simple extraction
        if not session_id or not self.session_service:
            return None
            
        try:
            session_data = self.session_service.get_session(session_id, "test_user")
            if session_data and 'quiz_state' in session_data:
                return session_data['quiz_state'].get('correct_answer')
        except:
            pass
            
        return None  # Fallback to LLM decision
    
    def _store_quiz_state(self, session_id: str, question: str, correct_answer: str):
        """Store quiz state when quiz is generated"""
        if not session_id or not self.session_service:
            return
            
        try:
            # This would be implemented with proper session storage
            # For now, we'll rely on LLM's intelligence to determine correctness
            pass
        except Exception as e:
            logger.warning(f"Failed to store quiz state: {e}")
    
    def parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility with old chat-with-session endpoint
        Parse LLM response text and extract dialogue
        """
        try:
            # Try to parse as JSON
            parsed = json.loads(response_text)
            if isinstance(parsed, dict) and 'dialogue' in parsed:
                return parsed
            else:
                # If not in expected format, wrap it
                return {"dialogue": response_text}
        except json.JSONDecodeError:
            # Not JSON, treat as plain text dialogue
            return {"dialogue": response_text}