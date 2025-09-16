"""
Tool Orchestrator - Complete interaction processing for platform

This orchestrator handles the complete user interaction flow:
1. Extract context from session
2. Call LLM with character prompt + tool definitions  
3. Parse LLM response for tools
4. Execute tools as specified
5. Return structured response for frontend
"""

import time
import json
import logging
import uuid
import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
# Performance logger removed
# from .performance_logger import performance_logger, track_async_operation

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
        # STREAMING TTS MANAGER COMMENTED OUT - using direct TTS for immediate audio
        # from .streaming_tts_manager import StreamingTTSManager
        
        # UNIFIED TTS ARCHITECTURE: Only use working SeolMinSeok TTS for ALL characters
        self.seol_tts_service = SeolMinSeokTTSService()
        
        # STREAMING TTS ARCHITECTURE DISABLED: Use direct TTS calls instead
        # self.streaming_tts_manager = StreamingTTSManager(self.seol_tts_service)
        
        self.tool_handler = PlatformToolHandler(tts_service=self.seol_tts_service)
        self.llm_agent_engine = LLMAgentEngine()
        self.character_manager = CharacterPromptManager()
        self.knowledge_service = KnowledgeService()
        self.session_service = session_service
        
        # Remove broken primary TTS - SeolMinSeok TTS works for greeting, use for everything
        # self.tts_service = tts_service  # REMOVED - this was failing with 403 AUTH_TOKEN_INVALID
        
        logger.info("✅ ToolOrchestrator initialized with direct TTS architecture")
        logger.info("✅ ALL characters now use SeolMinSeok TTS with direct calls (streaming disabled)")
    
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
        
        # Generate request ID for logging
        request_id = str(uuid.uuid4())
        # Performance tracking removed
        
        logger.info(f"🎯 Processing interaction: user_input='{user_input[:50] if user_input else ''}...', character='{character_id}', request_id='{request_id}'")
        print(f"🔥 TOOL ORCHESTRATOR DEBUG: process_user_interaction called with user_input='{user_input[:50]}', character_id='{character_id}', request_id='{request_id}'")
        
        try:
            start_total = time.time()
            
            # Step 1: Build interaction context with state awareness
            start_context = time.time()
            chat_history = await self._get_chat_history(session_id, user_id) if session_id else []
            end_context = time.time()
            print(f"⏱️ Context loading: {int((end_context - start_context) * 1000)}ms")
            
            # Step 1.5: Get relevant knowledge for the interaction
            start_knowledge = time.time()
            relevant_knowledge = await self._get_relevant_knowledge(user_input, character_id)
            end_knowledge = time.time()
            print(f"⏱️ Knowledge search: {int((end_knowledge - start_knowledge) * 1000)}ms")
            
            # Step 2: Analyze conversation state to help LLM understand context
            start_analysis = time.time()
            conversation_state = self._analyze_conversation_state(chat_history, user_input)
            end_analysis = time.time()
            print(f"⏱️ State analysis: {int((end_analysis - start_analysis) * 1000)}ms")
            
            # Step 3: Get character prompt and tool definitions
            start_prompt = time.time()
            character_prompt = await self.character_manager.get_prompt(character_id)
            available_tools = self.tool_handler.get_tool_definitions_json()
            end_prompt = time.time()
            print(f"⏱️ Prompt preparation: {int((end_prompt - start_prompt) * 1000)}ms")
            
            # Step 4: Build context-aware prompt
            start_enhance = time.time()
            enhanced_prompt = self._build_context_aware_prompt(
                character_prompt, conversation_state, available_tools, relevant_knowledge, user_input
            )
            end_enhance = time.time()
            print(f"⏱️ Prompt enhancement: {int((end_enhance - start_enhance) * 1000)}ms")
            
            # Step 5: Process with LLM agent
            start_llm = time.time()
            llm_response = await self.llm_agent_engine.process_with_tools(
                user_input=user_input,
                character_prompt=enhanced_prompt,
                chat_history=chat_history,
                available_tools=available_tools,
                character_id=character_id,  # Pass character_id for tool enforcement
                request_id=request_id  # Pass request_id for performance tracking
            )
            end_llm = time.time()
            print(f"⏱️ LLM processing: {int((end_llm - start_llm) * 1000)}ms")
            
            logger.info(f"🧠 LLM response: dialogue={bool(llm_response.get('dialogue'))}, tool={bool(llm_response.get('tool'))}")
            print(f"🔍 LLM response: {llm_response}")
            # Step 4: Execute tools if specified (with robust error handling)
            start_tools = time.time()
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
                    start_tool_exec = time.time()
                    tool_result = await self.tool_handler.execute_tool(
                        tool_type=tool_type,
                        data=tool_params
                    )
                    end_tool_exec = time.time()
                    print(f"⏱️ Tool execution: {int((end_tool_exec - start_tool_exec) * 1000)}ms")
                    executed_tools.append(tool_result)
                    logger.info(f"🔧 Executed tool: {tool_type}")
                    
                except Exception as tool_error:
                    logger.error(f"❌ Tool execution failed: {tool_error}")
                    # Don't break the flow, just log the error
                    logger.error(f"   Tool data was: {llm_response.get('tool')}")
                    raise  # Re-raise to trigger error response
            end_tools = time.time()
            print(f"⏱️ Tools processing: {int((end_tools - start_tools) * 1000)}ms")
            
            # Step 5: Generate TTS for dialogue - PARALLEL SENTENCE PROCESSING
            start_tts_total = time.time()
            audio_url = None
            streaming_audio_info = None
            
            dialogue = llm_response.get('dialogue')
            print(f"🔍 TTS CHECK: dialogue exists = {bool(dialogue)}")
            print(f"🔍 TTS CHECK: dialogue length = {len(dialogue) if dialogue else 0}")
            
            if dialogue:
                try:
                    print("🎯 STARTING PARALLEL SENTENCE TTS GENERATION")
                    logger.info(f"🎯 PARALLEL SENTENCE TTS: dialogue_length={len(dialogue)}")
                    
                    # Handle continuous_quiz_response with sentence-level parallel TTS within phases
                    if executed_tools and executed_tools[0]['type'] == 'continuous_quiz_response':
                        print("🔄 CONTINUOUS_QUIZ_RESPONSE: Processing phases only (skipping dialogue to avoid duplication)")
                        tool_data = executed_tools[0]['data']
                        
                        # Process each phase with sentence-level parallelization
                        phase_tasks = []
                        phase_keys = []
                        
                        # Phase 1 with sentence-level parallel processing
                        if tool_data.get('phase1', {}).get('text'):
                            # For phase1, just use the phase text
                            phase1_text = tool_data['phase1']['text']
                            phase_tasks.append(self._generate_parallel_sentence_tts(
                                phase1_text, timeout_seconds=15.0
                            ))
                            phase_keys.append('phase1')
                        
                        # Phase 2 with sentence-level parallel processing
                        if tool_data.get('phase2', {}).get('text'):
                            phase2_text = tool_data['phase2']['text']
                            nested_tool = tool_data.get('phase2', {}).get('tool', {})
                            
                            # Check if phase2_text already contains the question to avoid duplication
                            if nested_tool and nested_tool.get('data', {}).get('question'):
                                question = nested_tool['data']['question']
                                if question.strip() in phase2_text:
                                    # Question already in phase2_text, don't add it again
                                    phase2_combined = phase2_text
                                    logger.info(f"🎯 Phase2 TTS: question already included in phase2_text")
                                else:
                                    # Question not in phase2_text, add it
                                    phase2_combined = f"{phase2_text}\n{question}"
                                    logger.info(f"🎯 Phase2 TTS: added missing question to phase2_text")
                            else:
                                phase2_combined = phase2_text
                                logger.info(f"🎯 Phase2 TTS: no nested question found, using phase2_text only")
                            
                            phase_tasks.append(self._generate_parallel_sentence_tts(
                                phase2_combined, timeout_seconds=15.0
                            ))
                            phase_keys.append('phase2')
                        
                        # Execute phase processing in parallel
                        if phase_tasks:
                            start_parallel_tts = time.time()
                            phase_results = await asyncio.gather(*phase_tasks)
                            end_parallel_tts = time.time()
                            print(f"⏱️ Parallel sentence TTS ({len(phase_tasks)} phases): {int((end_parallel_tts - start_parallel_tts) * 1000)}ms")
                            
                            # Assign results back to tool_data
                            for i, phase_key in enumerate(phase_keys):
                                tool_data[phase_key]['audio_url'] = phase_results[i]
                                logger.info(f"🎵 {phase_key.title()} sentence-parallel TTS generated")
                        
                        # For continuous_quiz_response, don't process dialogue separately (it's in phase1)
                        audio_url = None
                        
                    else:
                        # Regular dialogue + tool text combined for TTS
                        combined_text = self._combine_dialogue_and_tool_text(dialogue, executed_tools)
                        print(f"🔍 COMBINED TEXT: dialogue={len(dialogue)} + tool_text={len(combined_text)-len(dialogue)} = {len(combined_text)} total chars")
                        
                        start_dialogue_tts = time.time()
                        audio_url = await self._generate_parallel_sentence_tts(
                            combined_text, timeout_seconds=15.0
                        )
                        end_dialogue_tts = time.time()
                        print(f"⏱️ Combined dialogue+tool sentence-parallel TTS: {int((end_dialogue_tts - start_dialogue_tts) * 1000)}ms")
                        print(f"🔍 PARALLEL TTS RESULT: {audio_url[:50] if audio_url else None}...")
                        logger.info(f"📝 Sentence-parallel TTS generated for {len(combined_text)} chars (dialogue+tool)")
                    
                except Exception as e:
                    logger.error(f"🚨 Direct TTS generation failed: {type(e).__name__}: {e}")
                    logger.error(f"🔍 TTS Details: character={character_id}, dialogue_length={len(llm_response.get('dialogue', ''))}")
                    import traceback
                    logger.error(f"🔍 TTS Traceback: {traceback.format_exc()}")
                    # Continue without TTS - don't break the educational flow
                    audio_url = None
            end_tts_total = time.time()
            print(f"⏱️ Total TTS processing: {int((end_tts_total - start_tts_total) * 1000)}ms")
            
            # COMMENTED OUT: Complex streaming logic that was causing delays
            # The original streaming TTS architecture with chunking, parallel generation,
            # and complex result handling has been replaced with direct TTS calls above
            # for immediate audio availability without waiting for streaming setup
            
            # Step 6: Store interaction in session
            start_session = time.time()
            if session_id and self.session_service:
                await self._store_interaction(session_id, user_input, llm_response, user_id)
            end_session = time.time()
            print(f"⏱️ Session storage: {int((end_session - start_session) * 1000)}ms")
            
            # Step 7: Build final response with direct TTS support
            start_response = time.time()
            platform_response = {
                "character": character_id,
                "dialogue": llm_response.get('dialogue', ''),
                "tools": executed_tools,
                "audio_url": audio_url,
                # streaming_audio removed - using direct TTS calls only
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            end_response = time.time()
            print(f"⏱️ Response building: {int((end_response - start_response) * 1000)}ms")
            
            logger.info(f"✅ Platform response ready: tools={len(executed_tools)}, audio={'direct' if audio_url else 'none'}")
            
            # Performance tracking removed

            end_total = time.time()
            print(f"🔥 TOTAL TIME: {int((end_total - start_total) * 1000)}ms")
            
            return platform_response
            
        except Exception as e:
            logger.error(f"❌ Tool orchestration failed: {e}")
            
            # Performance tracking removed
            
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
                # IMPROVED: Create session automatically if not found (instead of just warning)
                logger.info(f"Session {session_id} not found, creating new session automatically")
                try:
                    # Use a consistent fallback user_id for auto-created sessions
                    fallback_user_id = user_id or "default_user"
                    self.session_service.create_session(session_id, fallback_user_id)
                    session_data = self.session_service.get_session(session_id, fallback_user_id)
                except Exception as create_error:
                    logger.warning(f"Failed to auto-create session {session_id}: {create_error}")
                    return []
                
            if not session_data:
                logger.warning(f"Could not load or create session {session_id}, using empty history")
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
            # IMPROVED: Ensure consistent user_id and create session if needed
            effective_user_id = user_id or "default_user"
            
            # Verify session exists before storing, create if needed
            try:
                session_data = self.session_service.get_session(session_id, effective_user_id)
                if not session_data:
                    self.session_service.create_session(session_id, effective_user_id)
            except:
                # Session doesn't exist, create it
                self.session_service.create_session(session_id, effective_user_id)
            
            # Store user message
            self.session_service.add_message_to_session(
                session_id, "user", user_input, effective_user_id
            )
            
            # Store assistant response
            self.session_service.add_message_to_session(
                session_id, "assistant", llm_response.get('dialogue', ''), effective_user_id
            )
            
        except Exception as e:
            logger.warning(f"Failed to store interaction: {e}")
            # Continue gracefully - interaction storage failure shouldn't break the flow
    
    async def create_session_and_greet(self, character_id: str, user_id: str) -> Dict[str, Any]:
        """
        Create new session and generate initial greeting with tools
        """
        
        logger.info(f"🎬 Creating new session for character: {character_id}")
        print(f"🔥 GREET DEBUG: create_session_and_greet called for character={character_id}")
        
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
                # If assistant mentioned quiz, treat any user input as quiz response
                # REMOVED: word limit restriction that was breaking 4+ word quiz options
                state['stage'] = 'quiz_active'
                state['context'] = 'user_answered_quiz'
                state['quiz_context'] = {
                    'user_answer': user_input,
                    'question_content': content[:100]
                }
                logger.info(f"🎯 State Analysis: User answered quiz with '{user_input}' (quiz context detected, no word limit)")
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
- Phase2: 새로운 다른 문제 만들기

오답인 경우:
- Phase1: 답을 공개하지 않고 격려하며, 교육적 힌트 제공
- Phase2: 정확히 같은 문제를 같은 선택지로 보여주기:
  * 문제: "{current_question}"
  * 선택지: {current_options}
  * 정답: 당신의 지식을 사용하여 선택지에서 정답 찾기

중요:
- 당신의 지식을 사용하여 "{current_user_input}"을 평가하세요 - 제공된 "정답" 필드에 의존하지 마세요.
- Phase1 의 text 길이는 한국어 기준 70자 정도로 제한해 주세요.
- 오답인 경우 Phase1 응답에서 절대로 정답을 언급하지 마세요.
- 정답 예시, 오답 예시를 준수해 주세요.
- JSON 문자열 값 안에서 문장을 구분할 때는 실제 줄바꿈을 사용하지 마세요.
- 대신 백슬래시+n 두 글자로 이루어진 리터럴 문자열 \\n 을 사용하세요.
- dialogue, phase1.text, phase2.text 필드에서 여러 문장이 있을 때, 모든 문장 사이에 적용하세요.
- JSON.stringify()로 생성한 것처럼 모든 문자열을 적절히 이스케이프하세요.
- 출력 예시: "text": "첫 번째 문장.\\n두 번째 문장.\\n세 번째 문장."

정답 예시:
{{
    "dialogue": "정답에 대한 축하 메시지",
    "tool": {{
        "type": "continuous_quiz_response", 
        "data": {{
            "phase1": {{
                "text": "정답입니다.\\n [왜 맞는지 설명]",
                "delay_ms": 3000
            }},
            "phase2": {{
                "text": "이제 다른 과학 주제로 넘어가볼까요:\\n",
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

오답 예시:
{{
    "dialogue": "답을 공개하지 않는 격려적 피드백",
    "tool": {{
        "type": "continuous_quiz_response",
        "data": {{
            "phase1": {{
                "text": "좋은 시도예요!\\n 관련이 있지만 온도가 빙점 이하로 떨어질 때 어떤 일이 일어나는지 생각해보세요...",
                "delay_ms": 3000
            }},
            "phase2": {{
                "text": "그 문제를 다시 한번 시도해볼까요:\\n",
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


DO NOT USE: "show_selection" 
REQUIRED TOOL: "continuous_quiz_response"

JSON OUTPUT REQUIREMENTS:
- Output valid JSON only, no pretty printing, no extra explanations
- Use literal \\n characters (backslash + n) inside string values for sentence separation
- Do NOT insert actual newline characters inside JSON string values
- Example format: {{"text": "First sentence.\\nSecond sentence."}}
- Produce the JSON as if it was created by JSON.stringify()

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
    
    def _combine_dialogue_and_tool_text(self, dialogue: str, executed_tools: List[Dict]) -> str:
        """
        Combine dialogue text with relevant tool text (like questions) for comprehensive TTS.
        
        Args:
            dialogue: The main dialogue text from LLM
            executed_tools: List of executed tools that may contain additional text
            
        Returns:
            Combined text for TTS processing
        """
        combined_text = dialogue
        
        if not executed_tools:
            return combined_text
        
        for tool in executed_tools:
            tool_type = tool.get('type')
            tool_data = tool.get('data', {})
            
            # Extract text from show_selection tools (questions)
            if tool_type == 'show_selection':
                question = tool_data.get('question')
                if question and question.strip():
                    # Only add if not already present to avoid duplication
                    if question.strip() not in combined_text:
                        combined_text += f"\n{question}"
                        logger.info(f"🔗 Added question to TTS: '{question[:30]}...'")
                    else:
                        logger.info(f"🛑 Skipped duplicate question in TTS: '{question[:30]}...'")
            
            # Extract text from continuous_quiz_response tools (already handled separately above)
            elif tool_type == 'continuous_quiz_response':
                # These are handled in the phase-based processing above
                pass
            
            # Add other tool types as needed
            else:
                # For future tool types that might have speakable text
                if 'text' in tool_data and tool_data['text']:
                    # Only add if not already present to avoid duplication
                    if tool_data['text'] not in combined_text:
                        combined_text += f"\n{tool_data['text']}"
                        logger.info(f"🔗 Added {tool_type} text to TTS")
                    else:
                        logger.info(f"🛑 Skipped duplicate {tool_type} text in TTS")
        
        logger.info(f"📝 Combined text: dialogue({len(dialogue)}) + tool_text({len(combined_text) - len(dialogue)}) = {len(combined_text)} total")
        return combined_text
    
    async def _generate_parallel_sentence_tts(self, text: str, timeout_seconds: float = 15.0) -> Optional[str]:
        """
        Generate TTS for text by splitting into sentences and processing in parallel,
        then combining the audio data for seamless playback.
        
        Args:
            text: Text to synthesize (may contain multiple sentences separated by \\n)
            timeout_seconds: Timeout for each TTS request
            
        Returns:
            Combined base64 audio data or None if failed
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for parallel sentence TTS")
            return None
        
        # Split text by newlines (handle both actual \n and escaped \\n from LLM)
        # First, convert escaped newlines to actual newlines
        normalized_text = text.replace('\\n', '\n')
        sentences = [s.strip() for s in normalized_text.split('\n') if s.strip()]
        
        # If only one sentence, use direct TTS
        if len(sentences) <= 1:
            logger.info(f"🔤 Single sentence TTS: {text[:50]}...")
            return await self.seol_tts_service.generate_tts(
                text=text, use_hd=True, language="auto", timeout_seconds=timeout_seconds
            )
        
        logger.info(f"🔀 Parallel sentence TTS: {len(sentences)} sentences")
        print(f"🔀 Processing {len(sentences)} sentences in parallel:")
        for i, sentence in enumerate(sentences):
            print(f"   {i+1}. {sentence[:30]}...")
        
        # Generate TTS for each sentence in parallel using shared HTTP client
        try:
            # Execute all TTS requests in parallel with shared client for true parallelism
            start_time = time.time()
            
            # Use properly configured shared client for true parallelism
            limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
            timeout = httpx.Timeout(timeout_seconds, connect=5.0)
            
            async with httpx.AsyncClient(limits=limits, timeout=timeout) as shared_client:
                tts_tasks = []
                for sentence in sentences:
                    tts_tasks.append(self.seol_tts_service.generate_tts(
                        text=sentence,
                        use_hd=True,
                        language="auto", 
                        timeout_seconds=timeout_seconds,
                        client=shared_client  # Use shared client for true parallelism
                    ))
                
                # Execute all TTS requests truly in parallel
                tts_results = await asyncio.gather(*tts_tasks, return_exceptions=True)
            
            end_time = time.time()
            print(f"⏱️ TTS execution (API rate-limited): {int((end_time - start_time) * 1000)}ms for {len(sentences)} sentences")
            
            # Extract successful audio data and combine
            audio_segments = []
            failed_count = 0
            
            for i, result in enumerate(tts_results):
                if isinstance(result, str) and result.startswith("data:audio/wav;base64,"):
                    # Extract base64 data (remove the data URI prefix)
                    base64_data = result.split(",", 1)[1]
                    audio_segments.append(base64_data)
                    logger.info(f"✅ Sentence {i+1} TTS successful")
                else:
                    failed_count += 1
                    logger.warning(f"❌ Sentence {i+1} TTS failed: {result}")
            
            if not audio_segments:
                logger.error("All sentence TTS requests failed")
                return None
            
            if failed_count > 0:
                logger.warning(f"⚠️ {failed_count}/{len(sentences)} sentences failed TTS")
            
            # Combine audio segments into single base64 data
            combined_audio = self._combine_audio_segments(audio_segments)
            
            if combined_audio:
                logger.info(f"🎵 Successfully combined {len(audio_segments)} audio segments")
                return f"data:audio/wav;base64,{combined_audio}"
            else:
                logger.error("Failed to combine audio segments")
                return None
                
        except Exception as e:
            logger.error(f"Parallel sentence TTS failed: {e}")
            # Fallback to single TTS
            logger.info("🔄 Falling back to single TTS request")
            return await self.seol_tts_service.generate_tts(
                text=text, use_hd=True, language="auto", timeout_seconds=timeout_seconds
            )
    
    def _combine_audio_segments(self, base64_segments: List[str]) -> Optional[str]:
        """
        Combine multiple base64-encoded WAV audio segments into a single audio file.
        
        Args:
            base64_segments: List of base64-encoded WAV audio data
            
        Returns:
            Combined base64-encoded WAV audio data or None if failed
        """
        try:
            import base64
            import io
            import wave
            
            if not base64_segments:
                return None
            
            if len(base64_segments) == 1:
                return base64_segments[0]
            
            # Decode all segments and extract audio data
            audio_data_segments = []
            sample_rate = None
            channels = None
            sample_width = None
            
            for i, b64_data in enumerate(base64_segments):
                try:
                    # Decode base64 to WAV bytes
                    wav_bytes = base64.b64decode(b64_data)
                    wav_buffer = io.BytesIO(wav_bytes)
                    
                    # Read WAV file properties and audio data
                    with wave.open(wav_buffer, 'rb') as wav_file:
                        if sample_rate is None:
                            sample_rate = wav_file.getframerate()
                            channels = wav_file.getnchannels()
                            sample_width = wav_file.getsampwidth()
                        
                        # Verify all segments have same properties
                        if (wav_file.getframerate() != sample_rate or 
                            wav_file.getnchannels() != channels or 
                            wav_file.getsampwidth() != sample_width):
                            logger.warning(f"Audio segment {i} has different properties, skipping")
                            continue
                        
                        # Extract raw audio frames
                        frames = wav_file.readframes(wav_file.getnframes())
                        audio_data_segments.append(frames)
                        
                except Exception as e:
                    logger.warning(f"Failed to process audio segment {i}: {e}")
                    continue
            
            if not audio_data_segments:
                logger.error("No valid audio segments to combine")
                return None
            
            # Combine all audio data
            combined_frames = b''.join(audio_data_segments)
            
            # Create new WAV file with combined data
            output_buffer = io.BytesIO()
            with wave.open(output_buffer, 'wb') as output_wav:
                output_wav.setnchannels(channels)
                output_wav.setsampwidth(sample_width)
                output_wav.setframerate(sample_rate)
                output_wav.writeframes(combined_frames)
            
            # Encode combined WAV to base64
            output_buffer.seek(0)
            combined_wav_bytes = output_buffer.read()
            combined_base64 = base64.b64encode(combined_wav_bytes).decode('utf-8')
            
            logger.info(f"🔗 Combined {len(audio_data_segments)} segments into {len(combined_base64)} chars")
            return combined_base64
            
        except Exception as e:
            logger.error(f"Audio combination failed: {e}")
            return None