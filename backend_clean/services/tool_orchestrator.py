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
        from .knowledge_service import KnowledgeService
        from .seolminseok_tts_service import SeolMinSeokTTSService
        
        self.tool_handler = PlatformToolHandler(tts_service=tts_service)
        self.llm_agent_engine = LLMAgentEngine()
        self.character_manager = CharacterPromptManager()
        self.knowledge_service = KnowledgeService()
        self.session_service = session_service
        self.tts_service = tts_service
        
        # Cache SeolMinSeok TTS service for quiz characters (seol_min_seok_quiz, dr_genie_science_quiz)
        self.seol_tts_service = SeolMinSeokTTSService()
        
        logger.info("✅ ToolOrchestrator initialized with all components")
        logger.info("✅ SeolMinSeok TTS service cached for quiz characters")
    
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
            
            # Step 1.5: Get relevant knowledge for the interaction
            relevant_knowledge = await self._get_relevant_knowledge(user_input, character_id)
            
            # Step 2: Analyze conversation state to help LLM understand context
            conversation_state = self._analyze_conversation_state(chat_history, user_input)
            
            # Step 3: Get character prompt and tool definitions
            character_prompt = await self.character_manager.get_prompt(character_id)
            available_tools = self.tool_handler.get_tool_definitions_json()
            
            # Step 4: Build context-aware prompt
            enhanced_prompt = self._build_context_aware_prompt(
                character_prompt, conversation_state, available_tools, relevant_knowledge, user_input
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
                    # Use cached character-specific TTS services
                    if character_id in ["seol_min_seok_quiz", "dr_genie_science_quiz"]:
                        audio_url = await self.seol_tts_service.generate_tts(llm_response['dialogue'])
                        logger.info(f"🎭 Used cached SeolMinSeok TTS service for character: {character_id}")
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
                            if character_id in ["seol_min_seok_quiz", "dr_genie_science_quiz"]:
                                tool_data['phase1']['audio_url'] = await self.seol_tts_service.generate_tts(
                                    tool_data['phase1']['text']
                                )
                            else:
                                tool_data['phase1']['audio_url'] = await self.tts_service.generate_speech(
                                    tool_data['phase1']['text']
                                )
                            logger.info("🎵 Generated Phase 1 TTS")
                        
                        # Phase 2 TTS (complete next question narrative)
                        if tool_data.get('phase2', {}).get('text'):
                            if character_id in ["seol_min_seok_quiz", "dr_genie_science_quiz"]:
                                tool_data['phase2']['audio_url'] = await self.seol_tts_service.generate_tts(
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
            initial_greeting = "안녕하세요"  # Explicit greeting request for better LLM response
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
    
    def _build_context_aware_prompt(self, character_prompt: str, conversation_state: Dict, available_tools: Dict, relevant_knowledge: List[Dict] = None, user_input: str = "") -> str:
        """Build enhanced prompt with conversation state context and relevant knowledge"""
        
        # Base character prompt
        enhanced_prompt = character_prompt + "\n\n"
        
        # Add relevant knowledge if available
        if relevant_knowledge:
            enhanced_prompt += "RELEVANT KNOWLEDGE:\n"
            for item in relevant_knowledge[:3]:  # Limit to top 3 most relevant
                enhanced_prompt += f"- {item.get('content', '')}\n"
            enhanced_prompt += "\n"
        
        # Add state-specific instructions
        stage = conversation_state['stage']
        context = conversation_state['context']
        
        if stage == 'greeting':
            enhanced_prompt += """
현재 상황: 초기 인사 - 사용자가 방금 대화를 시작함
당신의 역할: 따뜻한 인사를 제공하고 주제 선택지와 함께 'show_selection' 도구 사용
사용할 도구: show_selection with selection_mode='topic'
"""
        
        elif stage == 'topic_selected' and context == 'user_selected_topic':
            topic = conversation_state.get('topic', 'selected topic')
            enhanced_prompt += f"""
현재 상황: 사용자가 방금 주제 '{topic}'를 선택함
이전 행동: 당신이 주제 선택지를 제시했고, 사용자가 '{topic}'를 선택함
당신의 역할: 선택을 인정하고 {topic}에 대한 첫 번째 퀴즈 문제 제시
사용할 도구: show_selection with selection_mode='quiz_question'
중요: {topic}에 대한 구체적인 퀴즈 문제를 4개 선택지와 정답과 함께 생성하세요
"""
        
        elif stage == 'quiz_active' and context == 'user_answered_quiz':
            logger.info(f"🎯 STAGE MATCH: quiz_active + user_answered_quiz detected!")
            # EXTRACT current question explicitly - don't rely on LLM to find it
            current_user_input = user_input.strip()
            current_question_data = self._extract_current_question_context(conversation_state.get('chat_history', []))
            current_question = current_question_data.get('question', 'unknown question')
            current_options = current_question_data.get('options', [])
            
            # COMPREHENSIVE LOGGING
            logger.info(f"🔍 QUIZ EVALUATION DEBUG:")
            logger.info(f"   User answered: '{current_user_input}'")
            logger.info(f"   Current question: '{current_question}'")
            logger.info(f"   Current options: {current_options}")
            logger.info(f"   Question extraction successful: {current_question != 'unknown question'}")
            logger.info(f"   Options extracted: {len(current_options)} options")
            
            enhanced_prompt += f"""
⚠️  직접 문제 평가 ⚠️

사용자가 방금 답변한 현재 문제:
문제: "{current_question}"
선택지: {current_options}
사용자 답변: "{current_user_input}"

당신의 역할:
1. 당신의 지식을 사용하여 "{current_user_input}"이 "{current_question}"의 정답인지 판단하세요
2. 추측하지 말고, 위에 제공된 정확한 문제와 선택지를 사용하세요

정답인 경우:
- Phase1: 축하하고 왜 답이 맞는지 설명하기
- Phase2: show_selection 도구로 새로운 다른 문제 만들기

오답인 경우:
- Phase1: 답을 공개하지 않고 격려하며, 교육적 힌트 제공
- Phase2: 정확히 같은 문제를 같은 선택지로 보여주기:
  * 문제: "{current_question}"
  * 선택지: {current_options}
  * 정답: 당신의 지식을 사용하여 선택지에서 정답 찾기

중요: 당신의 지식을 사용하여 "{current_user_input}"을 평가하세요 - 제공된 "정답" 필드에 의존하지 마세요.

오답 예시:
{{
    "dialogue": "답을 공개하지 않는 격려적 피드백",
    "tool": {{
        "type": "continuous_quiz_response",
        "data": {{
            "phase1": {{
                "text": "좋은 시도예요! 관련이 있지만 온도가 빙점 이하로 떨어질 때 어떤 일이 일어나는지 생각해보세요...",
                "delay_ms": 3000
            }},
            "phase2": {{
                "text": "그 문제를 다시 한번 시도해볼까요:",
                "tool": {{
                    "type": "show_selection",
                    "data": {{
                        "question": "최근 대화의 정확히 같은 문제",
                        "options": ["같은", "선택지들", "그대로", "유지"],
                        "correct_answer": "과학적으로 정확한 답",
                        "selection_mode": "quiz_question"
                    }}
                }}
            }}
        }}
    }}
}}

정답 예시:
{{
    "dialogue": "정답에 대한 축하 메시지",
    "tool": {{
        "type": "continuous_quiz_response", 
        "data": {{
            "phase1": {{
                "text": "훌륭해요! 정말 맞습니다. [왜 맞는지 설명]",
                "delay_ms": 3000
            }},
            "phase2": {{
                "text": "이제 다른 과학 주제로 넘어가볼까요:",
                "tool": {{
                    "type": "show_selection",
                    "data": {{
                        "question": "새로운 다른 과학 문제",
                        "options": ["새로운", "선택지들", "여기에", "추가"],
                        "correct_answer": "새 문제의 과학적으로 정확한 답",
                        "selection_mode": "quiz_question"
                    }}
                }}
            }}
        }}
    }}
}}

DO NOT USE: "show_selection" 
REQUIRED TOOL: "continuous_quiz_response"

BEHAVIORAL RULES:
- 사용자가 정답인 경우: Phase1 = 축하 + 교육적 맥락, Phase2 = 새로운 다른 문제
- 사용자가 오답인 경우: Phase1 = 격려 + 교육적 힌트 (절대 정답 공개 금지), Phase2 = 똑같은 문제와 선택지

⚠️ CRITICAL: For wrong answers, your Phase1 feedback must be educational but NOT reveal the answer.
Focus on guiding the student toward the right thinking, not giving them the solution.

Example response format you MUST follow:
{{
    "dialogue": "답변에 대한 피드백",
    "tool": {{
        "type": "continuous_quiz_response",
        "data": {{
            "phase1": {{
                "text": "답변에 대한 피드백",
                "delay_ms": 3000
            }},
            "phase2": {{
                "text": "다음 문제 소개", 
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

사용 가능한 도구: {list(available_tools.keys())}
기억하세요: 위에서 설명한 현재 상황에 따라 항상 적절한 도구를 사용하세요.
"""
        
        logger.info(f"🎯 Context-aware prompt built for stage: {stage}, context: {context}")
        
        return enhanced_prompt
    
    def _extract_current_question_context(self, chat_history: List[Dict]) -> Dict[str, Any]:
        """Extract the most recent quiz question context from chat history"""
        
        # Look for the most recent assistant message with tools
        for message in reversed(chat_history):
            if message.get('role') == 'assistant':
                # Check if this message has tools with quiz question data
                tools = message.get('tools', [])
                
                for tool in tools:
                    # Handle continuous_quiz_response tools (phase2 contains actual question)
                    if tool.get('type') == 'continuous_quiz_response':
                        phase2 = tool.get('data', {}).get('phase2', {})
                        nested_tool = phase2.get('tool', {})
                        if nested_tool.get('type') == 'show_selection':
                            nested_data = nested_tool.get('data', {})
                            if nested_data.get('selection_mode') == 'quiz_question':
                                return {
                                    'question': nested_data.get('question', ''),
                                    'options': nested_data.get('options', []),
                                    'correct_answer': nested_data.get('correct_answer', ''),
                                    'selection_mode': nested_data.get('selection_mode', '')
                                }
                    
                    # Handle direct show_selection tools
                    elif tool.get('type') == 'show_selection':
                        tool_data = tool.get('data', {})
                        if tool_data.get('selection_mode') == 'quiz_question':
                            return {
                                'question': tool_data.get('question', ''),
                                'options': tool_data.get('options', []),
                                'correct_answer': tool_data.get('correct_answer', ''),
                                'selection_mode': tool_data.get('selection_mode', '')
                            }
        
        # Fallback: return empty context
        return {
            'question': 'unknown question',
            'options': [],
            'correct_answer': '',
            'selection_mode': 'quiz_question'
        }
    
    def _extract_correct_answer_from_history(self, chat_history: List[Dict]) -> str:
        """Extract the correct answer from recent quiz context using proper tool data"""
        # FIXED: Use proper tool data extraction instead of hardcoded patterns
        context = self._extract_current_question_context(chat_history)
        if context and context.get('correct_answer'):
            return context['correct_answer']
        
        # REMOVED HARDCODED FALLBACKS - they were causing progression issues
        # If no context found, return empty string to let LLM decide
        return ''
    
    def _extract_last_question_from_history(self, chat_history: List[Dict]) -> str:
        """Extract the last question from chat history using proper tool data"""
        # FIXED: Use proper tool data extraction instead of hardcoded patterns
        context = self._extract_current_question_context(chat_history)
        if context and context.get('question') and context['question'] != 'unknown question':
            return context['question']
        
        # REMOVED HARDCODED FALLBACKS - they were causing progression issues
        # If no proper context found, return generic message to let LLM decide
        return '이전 질문을 다시 시도해보세요'
    
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
    
    async def _get_relevant_knowledge(self, user_input: str, character_id: str) -> List[Dict]:
        """Get relevant knowledge items for the current interaction"""
        try:
            if not user_input or not user_input.strip():
                return []
            
            # Use knowledge service to search for relevant content
            knowledge_items = self.knowledge_service.search_relevant_knowledge(
                user_input, character_id, max_results=3
            )
            
            logger.info(f"📚 Found {len(knowledge_items)} relevant knowledge items for '{character_id}'")
            return knowledge_items
            
        except Exception as e:
            logger.warning(f"Failed to get relevant knowledge: {e}")
            return []