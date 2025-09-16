"""
Continuous Answer Tool: Proactive Multi-Step Character Interactions

Enables characters to conduct intelligent multi-step conversations where user actions 
trigger continuous, proactive responses without manual prompts.
"""

import json
import asyncio
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from services.optimized_prompt_builder import OptimizedPromptBuilder
from services.tts_service import tts_service
from services.seolminseok_tts_service import seolminseok_tts_service
from services.conversation_service import ConversationService


@dataclass
class ToolTriggerEvent:
    """Event that triggers a continuous flow"""
    session_id: str
    character_id: str
    tool_type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FlowState:
    """State management for continuous flows"""
    session_id: str
    character_id: str
    flow_config: Dict[str, Any]
    current_step: int = 0
    step_results: List[Dict[str, Any]] = field(default_factory=list)
    trigger_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_context(self) -> Dict[str, Any]:
        """Build context from all previous steps and trigger data"""
        return {
            "trigger_data": self.trigger_data,
            "step_results": self.step_results,
            "character_id": self.character_id,
            "session_id": self.session_id
        }


@dataclass
class StepResult:
    """Result of executing a flow step"""
    step_id: str
    step_type: str
    response: Optional[Dict[str, Any]] = None
    audio: Optional[str] = None
    error: Optional[str] = None
    next_trigger: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowExecution:
    """Result of flow execution"""
    session_id: str
    step_result: StepResult
    flow_continues: bool
    next_step_index: Optional[int] = None


class ContinuousAnswerTool:
    """
    Orchestrates multi-step character interactions triggered by user actions
    """
    
    def __init__(self):
        self.flow_definitions = self._load_flow_configs()
        self.active_flows: Dict[str, FlowState] = {}  # session_id -> FlowState
        self.prompt_builder = OptimizedPromptBuilder()
        self.tts_service = tts_service
        self.seol_tts_service = seolminseok_tts_service  # Add correct service for quiz characters
        self.conversation_service = ConversationService()
    
    def _load_flow_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load flow configuration from JSON files"""
        configs = {}
        
        # Quiz continuous flow configuration
        quiz_flow = {
            "flow_id": "quiz_continuous_v1",
            "character_types": ["seol_min_seok_quiz", "seolminseok_korean_history_chat", "kim_daehyun_history", "history_teacher", "dr_genie_science_quiz"],
            "trigger": {
                "tool_type": "continuous_answer",
                "event": "user_selection"
            },
            "steps": [
                {
                    "step_id": "feedback_generation",
                    "type": "llm_response",
                    "prompt_template": "quiz_feedback_prompt",
                    "context": {
                        "user_answer": "${trigger_data.selection}",
                        "correct_answer": "${trigger_data.correct_answer}",
                        "question": "${trigger_data.question}",
                        "options": "${trigger_data.items}"
                    },
                    "audio_enabled": True,
                    "next_trigger": "immediate"  # Immediately proceed to next step
                },
                {
                    "step_id": "quiz_presentation",
                    "type": "llm_response_with_tools",
                    "prompt_template": "quiz_presentation_prompt",
                    "context": {
                        "user_answer": "${trigger_data.selection}",
                        "correct_answer": "${trigger_data.correct_answer}",
                        "question": "${trigger_data.question}",
                        "options": "${trigger_data.items}",
                        "was_correct": "${step_0.was_correct}"
                    },
                    "audio_enabled": True,
                    "next_trigger": None  # End of flow
                }
            ],
            "prompts": {
                "quiz_feedback_prompt": """당신은 설민석 선생님입니다. 따뜻하고 격려적인 한국사 선생님으로서 답변해주세요.

사용자 답변: "{user_answer}"
정답: "{correct_answer}"

**중요: 이것은 첫 번째 단계입니다. 피드백만 제공하고, 퀴즈나 도구는 사용하지 마세요.**

정답인 경우:
- "정답입니다!" 등으로 축하하고 격려
- 해당 역사적 사건에 대한 흥미로운 추가 정보 제공
- 간단한 역사적 맥락이나 흥미로운 사실 추가

오답인 경우:
- "아쉽지만 정답이 아니에요" 등으로 부드럽게 피드백
- 정답을 바로 알려주지 말고, 힌트나 역사적 맥락 제공
- "다시 한번 도전해보시겠어요?" 등으로 격려

**절대 하지 말 것:**
- 새로운 퀴즈 문제 제시
- "다음 문제입니다" 같은 표현
- 도구(tool) 사용 요청
- 정답을 바로 공개 (오답인 경우)

따뜻하고 교육적인 톤으로 2-3문장 정도로 답변해주세요.""",

                "quiz_retry_prompt": """당신은 설민석 역사 선생님입니다.

사용자가 틀린 답변을 했습니다:
- 사용자 답변: "{user_answer}"  
- 정답: "{correct_answer}"
- 원래 문제: "{question}"
- 원래 선택지: {options}

🚨 중요: 새로운 문제를 만들지 마세요! 원래 문제를 그대로 재사용해야 합니다!

🔴 RETRY LOGIC - 틀린 답변 처리:
1. 격려하는 피드백 제공 (정답은 아직 알려주지 말기)
2. 힌트나 관련 역사적 맥락 제공
3. **정확히 동일한 문제와 선택지를 다시 제시** (새 문제 금지!)

반드시 JSON으로 응답하세요:
{{
    "dialogue": "격려 피드백 + 힌트 제공 (정답 공개 금지)",
    "tools": [{{
        "type": "show_selection",
        "data": {{
            "question": "{question}",
            "options": {options},
            "correct_answer": "{correct_answer}",
            "selection_mode": "quiz_question",
            "retry_mode": true
        }}
    }}]
}}

⚠️ 절대 금지사항:
- 새로운 문제 생성하지 말 것
- 다른 선택지 만들지 말 것  
- 정답을 바로 알려주지 말 것
- 반드시 위 JSON 형식 그대로 사용할 것""",

                "quiz_progress_prompt": """당신은 설민석 역사 선생님입니다.

사용자가 정답을 맞혔습니다!
- 사용자 답변: "{user_answer}"  
- 정답: "{correct_answer}"
- 이전 문제: "{question}"

🟢 PROGRESS LOGIC - 정답 처리:
1. 정답을 축하하고 구체적으로 칭찬
2. 해당 역사적 사실에 대한 흥미로운 배경 설명
3. 새로운 한국사 문제 생성 (이전과 다른 주제/시대)

새 문제 생성 가이드라인:
- 조선시대의 다른 왕, 사건, 제도에 관한 문제
- 4개의 선택지 중 1개가 정답
- 교육적 가치가 높은 내용

반드시 JSON으로 응답하세요:
{{
    "dialogue": "축하 메시지 + 새로운 문제 텍스트 포함",
    "tools": [{{
        "type": "show_selection",
        "data": {{
            "question": "새로운 한국사 문제",
            "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
            "correct_answer": "정답 선택지",
            "selection_mode": "quiz_question",
            "retry_mode": false
        }}
    }}]
}}""",

                "quiz_next_step_prompt": """당신은 설민석 선생님입니다. 

**중요: 채팅 기록을 확인하여 이미 출제한 문제를 피하세요**

**교육적 퀴즈 로직 - 2단계:**
- 이전 피드백이 끝났으므로 이제 문제를 제시할 차례입니다
- 정답이었다면: 이전 채팅 기록을 확인하고 아직 출제하지 않은 새로운 조선시대 관련 문제 제시
- 오답이었다면: 동일한 문제를 다시 제시하여 재도전 기회 제공

**새로운 문제 생성 시 고려사항:**
- 채팅 기록에 이미 나온 문제와 동일하지 않은 문제 생성
- 조선시대의 다른 시기, 다른 왕, 다른 사건에 관한 문제
- 예: 세종대왕 → 태조 이성계, 정조, 선조 등 다른 왕으로 변경
- 예: 한글 창제 → 임진왜란, 정유재란, 갑신정변 등 다른 역사적 사건

**!!! CRITICAL WARNING - 반드시 준수하세요 !!!**
대화(dialogue)에 문제를 포함하지 않으면 사용자가 문제를 볼 수 없습니다!

**절대적 필수 규칙:**
1. 먼저 피드백을 제공하세요 (축하 또는 격려)
2. 그 다음 반드시 "자, 다음 문제입니다." 라고 말하세요
3. 그 다음 줄에 반드시 문제 전체 내용을 포함하세요
4. 마지막에 show_selection 도구를 사용하세요

**EXACT FORMAT을 따르세요:**
정답인 경우:
"축하 메시지... 자, 다음 문제입니다. [문제 전체 내용]"

오답인 경우: 
"격려 메시지... 자, 다시 한번 도전해보세요! [문제 전체 내용]"

**예시 - 반드시 이 형태로 작성하세요:**
"정답입니다! 잘하셨어요! 자, 다음 문제입니다. 다음 중 조선 후기 실학자는?"

**절대 하지 마세요:**
- show_selection 도구에만 문제를 넣고 대화에서 빼먹기
- "문제를 드리겠습니다" 같은 말만 하기
- 문제 내용 없이 끝내기

설민석 선생님다운 열정적이고 교육적인 말투로 문제를 제시하세요."""
            }
        }
        
        configs["quiz_continuous_v1"] = quiz_flow
        
        # 🆕 Feedback-triggered continuous flow (for our corrected detection)
        feedback_flow = {
            "flow_id": "quiz_feedback_continuous_v1",
            "character_types": ["seol_min_seok_quiz", "seolminseok_korean_history_chat", "kim_daehyun_history", "history_teacher", "dr_genie_science_quiz"],
            "trigger": {
                "tool_type": "continue_feedback_flow",
                "event": "quiz_feedback"
            },
            "steps": [
                {
                    "step_id": "detailed_feedback_generation",
                    "type": "llm_response",
                    "prompt_template": "detailed_feedback_prompt",
                    "context": {
                        "user_message": "${trigger_data.user_message}",
                        "feedback_response": "${trigger_data.feedback_response}"
                    },
                    "audio_enabled": True,
                    "next_trigger": "audio_completion"
                },
                {
                    "step_id": "next_question_generation",
                    "type": "llm_response", 
                    "condition": "audio_completion",
                    "prompt_template": "next_question_prompt",
                    "context": {
                        "previous_feedback": "${step_0.result.response}",
                        "user_message": "${trigger_data.user_message}"
                    },
                    "audio_enabled": True,
                    "next_trigger": None  # End of flow
                }
            ],
            "prompts": {
                "detailed_feedback_prompt": """당신은 설민석 선생님입니다. 
사용자가 방금 답변했습니다: "{user_message}"

이미 간단한 피드백을 했지만, 이제 더 자세하고 교육적인 피드백을 제공하세요:
- 답변에 대한 구체적인 설명
- 관련된 역사적 배경이나 흥미로운 사실
- 격려의 말

다음 문제 언급은 하지 마세요. 오직 이번 답변에 대한 피드백만 하세요.""",

                "next_question_prompt": """이제 다음 한국사 퀴즈 문제를 제시할 차례입니다.

이전 문제와 연관되면서도 새로운 주제의 문제를 만들어주세요:
- 4지선다 형태
- 적절한 난이도
- 교육적 가치가 있는 내용

"준비되었나요?" 같은 질문 없이 바로 문제를 제시하세요."""
            }
        }
        
        configs["quiz_feedback_continuous_v1"] = feedback_flow
        
        # 🆕 Add flow configuration for show_selection tool (for greeting and initial quiz presentation)
        show_selection_flow = {
            "flow_id": "show_selection_v1",
            "character_types": ["seol_min_seok_quiz", "seolminseok_korean_history_chat", "kim_daehyun_history", "history_teacher", "dr_genie_science_quiz"],
            "trigger": {
                "tool_type": "show_selection",
                "event": "quiz_presentation"
            },
            "steps": [
                {
                    "step_id": "present_quiz",
                    "type": "llm_response_with_tools",
                    "prompt_template": "quiz_presentation_prompt",
                    "context": {
                        "greeting_message": "${trigger_data.greeting}",
                        "character_name": "${character_id}"
                    },
                    "audio_enabled": True,
                    "next_trigger": None  # End of flow - wait for user selection
                }
            ],
            "prompts": {
                "quiz_retry_prompt": """당신은 설민석 역사 선생님입니다.

사용자가 틀린 답변을 했습니다:
- 사용자 답변: "{user_answer}"  
- 정답: "{correct_answer}"
- 원래 문제: "{question}"
- 원래 선택지: {options}

🚨 중요: 새로운 문제를 만들지 마세요! 원래 문제를 그대로 재사용해야 합니다!

🔴 RETRY LOGIC - 틀린 답변 처리:
1. 격려하는 피드백 제공 (정답은 아직 알려주지 말기)
2. 힌트나 관련 역사적 맥락 제공
3. **정확히 동일한 문제와 선택지를 다시 제시** (새 문제 금지!)

반드시 JSON으로 응답하세요:
{{
    "dialogue": "격려 피드백 + 힌트 제공 (정답 공개 금지)",
    "tools": [{{
        "type": "show_selection",
        "data": {{
            "question": "{question}",
            "options": {options},
            "correct_answer": "{correct_answer}",
            "selection_mode": "quiz_question",
            "retry_mode": true
        }}
    }}]
}}

⚠️ 절대 금지사항:
- 새로운 문제 생성하지 말 것
- 다른 선택지 만들지 말 것  
- 정답을 바로 알려주지 말 것
- 반드시 위 JSON 형식 그대로 사용할 것""",

                "quiz_progress_prompt": """당신은 설민석 역사 선생님입니다.

사용자가 정답을 맞혔습니다!
- 사용자 답변: "{user_answer}"  
- 정답: "{correct_answer}"
- 이전 문제: "{question}"

🟢 PROGRESS LOGIC - 정답 처리:
1. 정답을 축하하고 구체적으로 칭찬
2. 해당 역사적 사실에 대한 흥미로운 배경 설명
3. 새로운 한국사 문제 생성 (이전과 다른 주제/시대)

새 문제 생성 가이드라인:
- 조선시대의 다른 왕, 사건, 제도에 관한 문제
- 4개의 선택지 중 1개가 정답
- 교육적 가치가 높은 내용

반드시 JSON으로 응답하세요:
{{
    "dialogue": "축하 메시지 + 새로운 문제 텍스트 포함",
    "tools": [{{
        "type": "show_selection",
        "data": {{
            "question": "새로운 한국사 문제",
            "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
            "correct_answer": "정답 선택지",
            "selection_mode": "quiz_question",
            "retry_mode": false
        }}
    }}]
}}""",

                "quiz_presentation_prompt": """당신은 {character_name} 선생님입니다.

⚠️  CRITICAL QUIZ RETRY LOGIC (Following plan_new.md):

THE CURRENT QUESTION USER JUST ANSWERED:
QUESTION: "{question}"
OPTIONS: {options}
USER'S ANSWER: "{user_answer}"
CORRECT ANSWER: "{correct_answer}"
WAS USER CORRECT: {was_correct}

🎯 MANDATORY DECISION LOGIC:

IF USER WAS WRONG (was_correct = False):
- Present the EXACT SAME QUESTION for retry
- DO NOT generate a new question
- DO NOT progress to next topic
- Use show_selection with same question, same options, same correct_answer
- Add "retry_mode": true to the tool

IF USER WAS CORRECT (was_correct = True):
- Generate a NEW, DIFFERENT question on a different topic
- DO progress to next topic 
- Use show_selection with completely new question and options
- Add "retry_mode": false to the tool

RESPONSE FORMAT:
{{
  "dialogue": "Your encouraging response based on correct/wrong answer",
  "tool": {{
    "type": "show_selection",
    "data": {{
      "question": "[SAME question if wrong, NEW question if correct]",
      "options": ["option1", "option2", "option3", "option4"],
      "correct_answer": "[appropriate correct answer]",
      "selection_mode": "quiz_question",
      "retry_mode": [true if wrong, false if correct]
    }}
  }}
}}

반드시 이 로직을 정확히 따르세요. 틀린 답변에는 같은 문제를 다시 제시하고, 맞은 답변에는 새로운 문제를 제시하세요."""
            }
        }
        
        configs["show_selection_v1"] = show_selection_flow
        return configs
    
    async def trigger_flow(self, trigger_event: ToolTriggerEvent) -> Optional[FlowExecution]:
        """
        Main entry point for continuous flows
        """
        print(f"🔄 ContinuousAnswerTool: Triggering flow for {trigger_event.character_id}")
        print(f"🔍 RECEIVED TOOL_TYPE: '{trigger_event.tool_type}'")
        print(f"🔍 TRIGGER DATA: {trigger_event.data}")
        
        # Find matching flow configuration
        flow_config = self._get_flow_config(trigger_event.character_id, trigger_event.tool_type)
        
        if not flow_config:
            print(f"❌ No flow config found for character {trigger_event.character_id}, tool {trigger_event.tool_type}")
            return None
        
        print(f"   Flow has {len(flow_config.get('steps', []))} steps")
        for i, step in enumerate(flow_config.get('steps', [])):
            print(f"   Step {i}: {step.get('step_id', 'N/A')} - type: {step.get('type', 'N/A')}")
            if 'prompt_template' in step:
                print(f"     - uses prompt: '{step['prompt_template']}'")
            if 'next_trigger' in step:
                print(f"     - next_trigger: '{step.get('next_trigger', 'None')}'")
        print(f"   Available prompts: {list(flow_config.get('prompts', {}).keys())}")
            
        # Initialize flow state
        flow_state = FlowState(
            session_id=trigger_event.session_id,
            character_id=trigger_event.character_id,
            flow_config=flow_config,
            trigger_data=trigger_event.data
        )
        
        self.active_flows[trigger_event.session_id] = flow_state
        print(f"✅ Flow initialized for session {trigger_event.session_id}")
        
        # Execute first step (feedback)
        first_step_result = await self._execute_flow_step(flow_state, step_index=0)
        
        # ALWAYS execute second step for two-step continuous flow
        total_steps = len(flow_state.flow_config["steps"])
        
        if total_steps > 1:
            print(f"🔄 Executing second step for quiz presentation (two-step architecture)")
            
            # Store was_correct from first step for second step context
            if first_step_result.step_result.response:
                flow_state.step_results[0]["was_correct"] = first_step_result.step_result.response.get("was_correct", False)
            
            # 🚨 CRITICAL FIX: Execute second step immediately but don't wait
            print(f"🚀 Executing second step immediately for background processing...")
            
            # Execute second step asynchronously in background
            asyncio.create_task(self._execute_and_store_second_step(flow_state, first_step_result))
            
            # Return first phase immediately to frontend
            print(f"✅ First phase ready, returning immediately. Second phase will be stored for later retrieval.")
            
            # CRITICAL: Return ONLY first phase data (feedback only) immediately
            if first_step_result.step_result.response:
                feedback_dialogue = first_step_result.step_result.response.get("dialogue", "")
                
                print(f"🎯 Phase 1: Returning ONLY feedback dialogue - no tools, no questions")
                print(f"📝 Feedback dialogue: '{feedback_dialogue}'")
                
                # CRITICAL: Return ONLY first phase data (feedback only)
                first_phase_response = {
                    "dialogue": feedback_dialogue,  # ONLY feedback, NO question
                    "character": first_step_result.step_result.response.get("character"),
                    "emotion": first_step_result.step_result.response.get("emotion"), 
                    "tools": [],  # NO tools in first phase!
                    "was_correct": first_step_result.step_result.response.get("was_correct")
                }
                
                # Use existing first phase audio
                first_phase_audio = first_step_result.step_result.audio
                
                # Return ONLY first phase result (feedback only)
                first_step_result.step_result.response = first_phase_response
                first_step_result.step_result.audio = first_phase_audio
                
                return first_step_result
            
            else:
                print(f"❌ First step response is None, cannot return phase 1")
                return first_step_result

    async def _execute_and_store_second_step(self, flow_state: FlowState, first_step_result) -> None:
        """Execute second step in background and store results"""
        try:
            print(f"🔄 Background: Executing second step for session {flow_state.session_id}")
            
            # Small delay to allow first phase to complete
            await asyncio.sleep(1.0)
            
            second_step_result = await self._execute_flow_step(flow_state, step_index=1)
            
            if second_step_result.step_result.response:
                quiz_dialogue = second_step_result.step_result.response.get("dialogue", "")
                quiz_tools = second_step_result.step_result.response.get("tools", [])
                
                print(f"🗄️ Background: Storing second phase data - dialogue: {len(quiz_dialogue)} chars, tools: {len(quiz_tools)}")
                
                # 🔴 REMOVE DUPLICATE FEEDBACK FROM SECOND PHASE DIALOGUE
                retry_feedback_phrases = [
                    "아쉽지만 정답이 아니에요",
                    "아쉽게도 틀렸습니다", 
                    "정답이 아닙니다",
                    "틀렸습니다"
                ]
                
                # Check if dialogue contains retry feedback that should only be in first phase
                contains_retry_feedback = any(phrase in quiz_dialogue for phrase in retry_feedback_phrases)
                
                if contains_retry_feedback:
                    print(f"🔴 DUPLICATE FEEDBACK DETECTED in second phase: '{quiz_dialogue}'")
                    
                    # Remove retry feedback phrases and keep only educational content
                    clean_dialogue = quiz_dialogue
                    for phrase in retry_feedback_phrases:
                        clean_dialogue = clean_dialogue.replace(phrase, "").strip()
                    
                    # Clean up extra punctuation and spaces
                    clean_dialogue = clean_dialogue.replace(". .", ".").replace("  ", " ").strip()
                    
                    # If dialogue becomes too short, provide minimal encouragement
                    if len(clean_dialogue) < 10:
                        quiz_dialogue = "다시 한번 생각해보세요!"
                    else:
                        quiz_dialogue = clean_dialogue
                        
                    print(f"🔴 SECOND PHASE DIALOGUE CLEANED: '{quiz_dialogue}'")
                
                # Store the second phase data for later frontend retrieval
                await self._store_second_phase_data(flow_state.session_id, {
                    "dialogue": quiz_dialogue,
                    "tools": quiz_tools,
                    "audio": second_step_result.step_result.audio
                })
                print(f"✅ Background: Second phase data stored for session: {flow_state.session_id}")
            else:
                print(f"❌ Background: Second step response is None")
                
        except Exception as e:
            print(f"❌ Background: Error executing second step: {e}")

    async def _store_second_phase_data(self, session_id: str, phase_data: Dict) -> None:
        """Store second phase data for later retrieval"""
        # For now, store in memory - in production, use Redis or session storage
        if not hasattr(self, '_second_phase_storage'):
            self._second_phase_storage = {}
        
        self._second_phase_storage[session_id] = {
            "data": phase_data,
            "timestamp": time.time()
        }
        print(f"🗄️ Stored second phase data for session {session_id}")

    async def check_second_phase_data(self, session_id: str) -> bool:
        """Check if second phase data exists without removing it"""
        if not hasattr(self, '_second_phase_storage'):
            return False
        
        stored = self._second_phase_storage.get(session_id)
        exists = stored is not None
        
        if exists:
            print(f"🔍 Second phase data exists for session {session_id}")
        else:
            print(f"🔍 No second phase data yet for session {session_id}")
        
        return exists

    async def get_second_phase_data(self, session_id: str) -> Optional[Dict]:
        """Retrieve second phase data for frontend (removes after retrieval)"""
        if not hasattr(self, '_second_phase_storage'):
            return None
        
        stored = self._second_phase_storage.get(session_id)
        if stored:
            # Remove after retrieval (one-time use)
            del self._second_phase_storage[session_id]
            print(f"🗄️ Retrieved and removed second phase data for session {session_id}")
            return stored["data"]
        
        print(f"❌ No second phase data found for session {session_id}")
        return None
    
    def _get_flow_config(self, character_id: str, tool_type: str) -> Optional[Dict[str, Any]]:
        """Get flow configuration for character and tool type"""
        print(f"🔍 FLOW SELECTION: Looking for character='{character_id}', tool_type='{tool_type}'")
        
        for flow_id, config in self.flow_definitions.items():
            flow_character_types = config.get("character_types", [])
            flow_tool_type = config.get("trigger", {}).get("tool_type")
            
            print(f"   Checking flow '{flow_id}': character_types={flow_character_types}, tool_type='{flow_tool_type}'")
            
            if (character_id in flow_character_types and flow_tool_type == tool_type):
                print(f"✅ FLOW MATCH: Selected flow '{flow_id}' for character='{character_id}', tool_type='{tool_type}'")
                return config
                
        print(f"❌ NO FLOW MATCH: No flow found for character='{character_id}', tool_type='{tool_type}'")
        return None
    
    async def _execute_flow_step(self, flow_state: FlowState, step_index: int) -> FlowExecution:
        """Execute a single step in the continuous flow"""
        print(f"🎯 Executing step {step_index} for session {flow_state.session_id}")
        
        # Store session_id and character_id locally to avoid scoping issues
        session_id = flow_state.session_id
        character_id = flow_state.character_id
        
        if step_index >= len(flow_state.flow_config["steps"]):
            print("❌ Step index out of range")
            return FlowExecution(
                session_id=session_id,
                step_result=StepResult("error", "error", error="Step index out of range"),
                flow_continues=False
            )
        
        step_config = flow_state.flow_config["steps"][step_index]
        flow_state.current_step = step_index
        
        # CRITICAL DEBUG: Log step execution details
        print(f"   Step index: {step_index}")
        print(f"   Step ID: {step_config.get('step_id', 'N/A')}")
        print(f"   Step type: {step_config.get('type', 'N/A')}")
        print(f"   Full step_config: {step_config}")
        
        if step_config["type"] == "llm_response":
            print(f"🤖 Executing LLM step (no tools)")
            step_result = await self._execute_llm_step(flow_state, step_config)
        elif step_config["type"] == "llm_response_with_tools":
            print(f"🤖🔧 Executing LLM step WITH TOOLS")
            step_result = await self._execute_llm_step_with_tools(flow_state, step_config)
        else:
            print(f"❌ Unknown step type: {step_config['type']}")
            step_result = StepResult(
                step_id=step_config["step_id"],
                step_type=step_config["type"],
                error=f"Unknown step type: {step_config['type']}"
            )
        
        # Store step result
        flow_state.step_results.append({
            "step_index": step_index,
            "step_id": step_result.step_id,
            "result": step_result.__dict__
        })
        
        # Check if flow continues
        next_step_index = None
        flow_continues = False
        
        # Debug logging for flow continuation
        print(f"   step_result.next_trigger: '{step_result.next_trigger}'")
        print(f"   step_index: {step_index}")
        print(f"   total_steps: {len(flow_state.flow_config['steps'])}")
        print(f"   has_next_step: {step_index + 1 < len(flow_state.flow_config['steps'])}")
        
        if (step_result.next_trigger and 
            step_index + 1 < len(flow_state.flow_config["steps"]) and
            (step_result.next_trigger == "immediate" or step_result.next_trigger == "audio_completion")):
            next_step_index = step_index + 1
            flow_continues = True
            print(f"   ✅ Flow will continue to step {next_step_index}")
        else:
            print(f"   ❌ Flow stops here")
            if not step_result.next_trigger:
                print(f"   - Missing next_trigger")
            if not (step_index + 1 < len(flow_state.flow_config["steps"])):
                print(f"   - No more steps available")
            if step_result.next_trigger and step_result.next_trigger not in ["immediate", "audio_completion"]:
                print(f"   - Invalid next_trigger: '{step_result.next_trigger}'")
        
        return FlowExecution(
            session_id=session_id,
            step_result=step_result,
            flow_continues=flow_continues,
            next_step_index=next_step_index
        )
    
    async def _execute_llm_step(self, flow_state: FlowState, step_config: Dict[str, Any]) -> StepResult:
        """Execute LLM generation step with context injection"""
        try:
            # OPTIMIZED: Use shared context and template preparation
            context, template_name = self._prepare_step_context_and_template(flow_state, step_config)
            
            prompt_template = flow_state.flow_config["prompts"][template_name]
            final_prompt = self._inject_context(prompt_template, context)
            
            print(f"🤖 Generated prompt for {step_config['step_id']}: {final_prompt[:100]}...")
            
            # Generate LLM response using existing character service
            response = await self._generate_character_response(
                character_id=flow_state.character_id,
                prompt=final_prompt,
                context=context
            )
            
            # Generate TTS if enabled
            audio_data = None
            if step_config.get("audio_enabled", False) and response.get("dialogue"):
                print(f"🎵 Generating TTS for step {step_config['step_id']}")
                try:
                    # Use same character-specific TTS selection as regular chat
                    if flow_state.character_id in ['seol_min_seok', 'seol_min_seok_quiz', 'kim_daehyun_history', 'seolminseok_korean_history_chat', 'dr_genie_science_quiz']:
                        print(f"🎭 Korean history character detected ({flow_state.character_id}) - using dedicated TTS service")
                        audio_data = await seolminseok_tts_service.generate_tts(
                            text=response["dialogue"],
                            use_hd=True,
                            language="auto",
                            timeout_seconds=3.0  # PHASE 1: Keep fast timeout
                        )
                    else:
                        # Use regular TTS for other characters
                        audio_data = await self.tts_service.generate_speech(
                            text=response["dialogue"],
                            voice_id=None,  # Will use character default
                            timeout_seconds=3.0  # PHASE 1: Keep fast timeout
                        )
                except Exception as tts_error:
                    print(f"❌ TTS generation failed: {tts_error}")
                    # Continue without audio
            
            # CRITICAL DEBUG: Log what we're getting from step_config
            next_trigger_value = step_config.get("next_trigger", None)
            
            return StepResult(
                step_id=step_config["step_id"],
                step_type="llm_response",
                response=response,
                audio=audio_data,
                next_trigger=next_trigger_value,
                metadata={
                    "prompt_length": len(final_prompt),
                    "response_length": len(response.get("dialogue", "")),
                    "audio_generated": audio_data is not None
                }
            )
            
        except Exception as e:
            print(f"❌ Error in LLM step execution: {e}")
            return StepResult(
                step_id=step_config["step_id"],
                step_type="llm_response",
                error=str(e)
            )
    
    async def _execute_llm_step_with_tools(self, flow_state: FlowState, step_config: Dict[str, Any]) -> StepResult:
        """Execute LLM generation step that returns both dialogue and tools"""
        print(f"🚨 _execute_llm_step_with_tools CALLED for step: {step_config.get('step_id', 'N/A')}")
        print(f"🚨 Character ID: {flow_state.character_id}")
        print(f"🚨 Step config: {step_config}")
        try:
            # OPTIMIZED: Use shared context and template preparation
            context, template_name = self._prepare_step_context_and_template(flow_state, step_config)
            
            prompt_template = flow_state.flow_config["prompts"][template_name]
            
            try:
                final_prompt = self._inject_context(prompt_template, context)
            except Exception as e:
                import traceback
                traceback.print_exc()
                raise
            
            
            # Use the proper character generation method with the resolved template
            
            # Call character service with the resolved prompt directly
            response = await self._generate_character_response(
                character_id=flow_state.character_id,
                prompt=final_prompt,  # Use the resolved template as prompt
                context=context
            )
            
            print(f"🔧 LLM raw response: {response}")
            
            # Parse the structured response
            try:
                import json
                if isinstance(response, dict) and "dialogue" in response:
                    # Response is already structured
                    structured_response = response
                else:
                    # Try to parse the dialogue as JSON
                    dialogue_content = response.get("dialogue", "") if isinstance(response, dict) else str(response)
                    if dialogue_content.startswith("{") and dialogue_content.endswith("}"):
                        structured_response = json.loads(dialogue_content)
                    else:
                        # Fallback - create structure manually
                        structured_response = {
                            "dialogue": dialogue_content,
                            "character": flow_state.character_id,
                            "emotion": "normal",
                            "tools": []
                        }
                
                
                
                from .tool_orchestrator import ToolOrchestrator
                
                # Get chat history from session to extract current question
                session_service = getattr(self, 'session_service', None)
                chat_history = []
                if session_service and session_id:
                    try:
                        session_data = await session_service.get_session(session_id)
                        chat_history = session_data.get('messages', [])
                    except Exception as e:
                        print(f"⚠️ Could not fetch chat history: {e}")
                        chat_history = context.get("recent_messages", [])
                else:
                    chat_history = context.get("recent_messages", [])
                
                # Use the proper tool orchestrator method to extract current question
                temp_orchestrator = ToolOrchestrator(None, None, None, None)
                current_question_data = temp_orchestrator._extract_current_question_context(chat_history)
                
                print(f"🔧 TOOL ORCHESTRATOR QUESTION EXTRACTION RESULT:")
                print(f"   Question: {current_question_data.get('question', 'unknown')}")
                print(f"   Options: {current_question_data.get('options', [])}")
                print(f"   Correct: {current_question_data.get('correct_answer', '')}")
                
                # Use extracted data or fallback to trigger_data  
                if current_question_data.get('question') and current_question_data.get('question') != 'unknown question':
                    original_question = current_question_data.get('question', '')
                    original_options = current_question_data.get('options', [])
                    original_correct = current_question_data.get('correct_answer', '')
                    print(f"✅ Using CURRENT question from chat history")
                else:
                    print(f"⚠️ FALLBACK: Using trigger_data (this should only happen for first question)")
                    original_question = context.get("question", "")
                    original_options = context.get("options", [])
                    original_correct = context.get("correct_answer", "")
                
                # 🔧 Handle options parsing - could be string representation of array
                if isinstance(original_options, str):
                    try:
                        import ast
                        original_options = ast.literal_eval(original_options)
                        print(f"🔧 RETRY FIX: Parsed string options into array: {original_options}")
                    except:
                        print(f"🔧 RETRY FIX: Could not parse options string, using as-is: {original_options}")
                
                if template_name == "quiz_retry_prompt" and not is_correct:
                    print("🔴 FORCING CORRECT RETRY BEHAVIOR - LLM tried to generate new question, fixing it")
                    
                    print(f"🔧 RETRY FIX: Using original question='{original_question}'")
                    print(f"🔧 RETRY FIX: Using original options={original_options}")
                    
                    # Force the response to use the same question with retry_mode=true
                    structured_response["tools"] = [{
                        "type": "show_selection",
                        "data": {
                            "question": original_question,
                            "options": original_options,
                            "correct_answer": original_correct,
                            "selection_mode": "quiz_question", 
                            "retry_mode": True
                        }
                    }]
                    
                    print(f"🔴 RETRY BEHAVIOR FORCED: Same question with retry_mode=True")
                elif template_name == "quiz_progress_prompt" and is_correct:
                    print("🟢 PROGRESS BEHAVIOR: Correct answer, allowing new question generation")
                    # Let the LLM generate new questions for correct answers
                    if structured_response.get("tools") and len(structured_response["tools"]) > 0:
                        # Ensure retry_mode is False for new questions
                        for tool in structured_response["tools"]:
                            if tool.get("type") == "show_selection" and "data" in tool:
                                tool["data"]["retry_mode"] = False
                        print(f"🟢 PROGRESS BEHAVIOR CONFIRMED: New question with retry_mode=False")
                
                # 🔧 CRITICAL FIX: Resolve templates in the structured response
                # This fixes the issue where ${trigger_data.selection} appears literally in dialogue and tool data
                structured_response = self._resolve_response_templates(structured_response, {
                    "trigger_data": flow_state.trigger_data,
                    "character_id": flow_state.character_id,
                    "session_id": flow_state.session_id,
                    "step_results": flow_state.step_results
                })
                print(f"🔧 Template-resolved response: {structured_response}")
                
                # 🔴 SYNC DIALOGUE WITH RETRY QUESTION - AFTER template resolution
                if template_name == "quiz_retry_prompt" and not is_correct:
                    retry_dialogue = f"아쉽지만 정답이 아니에요. 다시 한번 생각해보세요!\n\n{original_question}"
                    structured_response["dialogue"] = retry_dialogue
                    print(f"🔴 DIALOGUE SYNCED AFTER TEMPLATES: Updated dialogue to match retry question")
                
            except Exception as parse_error:
                print(f"⚠️ Failed to parse structured response: {parse_error}")
                # Fallback to basic response
                structured_response = {
                    "dialogue": response.get("dialogue", "피드백을 생성하는 중에 오류가 발생했습니다.") if isinstance(response, dict) else str(response),
                    "character": flow_state.character_id,
                    "emotion": "normal",
                    "tools": []
                }
                
            # Generate TTS if enabled
            audio_data = None
            if step_config.get("audio_enabled", False) and structured_response.get("dialogue"):
                print(f"🎵 Generating TTS for step {step_config['step_id']}")
                try:
                    if flow_state.character_id in ['seol_min_seok', 'seol_min_seok_quiz', 'kim_daehyun_history', 'seolminseok_korean_history_chat', 'dr_genie_science_quiz']:
                        print(f"🎭 Korean history character detected ({flow_state.character_id}) - using dedicated TTS service")
                        audio_data = await self.seol_tts_service.generate_tts(
                            text=structured_response["dialogue"],
                            use_hd=True,
                            language="auto",
                            timeout_seconds=3.0  # PHASE 1: Keep fast timeout
                        )
                    else:
                        audio_data = await self.tts_service.generate_tts(structured_response["dialogue"])
                        
                    print(f"🎵 TTS generated successfully for flow step")
                except Exception as tts_error:
                    print(f"❌ TTS generation failed: {tts_error}")
                    audio_data = None
                    
            return StepResult(
                step_id=step_config["step_id"],
                step_type="llm_response_with_tools",
                response=structured_response,  # This includes both dialogue AND tools
                audio=audio_data,
                next_trigger=step_config.get("next_trigger", None)
            )
            
        except Exception as e:
            print(f"❌ Error in LLM step with tools execution: {e}")
            import traceback
            traceback.print_exc()
            
            # ⚠️ NO FALLBACK RESPONSES - RETRY WITH LONGER DELAY TO GET REAL LLM RESPONSE
            print(f"🔄 Retrying LLM call after error with extended delay for rate limiting...")
            
            # Extended delay for Azure OpenAI rate limiting issues
            retry_delay = 15.0
            await asyncio.sleep(retry_delay)
            
            try:
                # Retry using the original context-building system, not bypassing it
                print(f"🔄 RETRY: Using original context system with proper history...")
                retry_response = await self._generate_character_response(
                    character_id=flow_state.character_id,
                    prompt=final_prompt,  # Use the same resolved template as original call
                    context=context      # Use the full context with conversation history
                )
                print(f"✅ RETRY SUCCESS: Got real LLM response: {str(retry_response)[:100]}...")
                
                # Parse the structured response the same way as original
                try:
                    import json
                    if isinstance(retry_response, dict) and "dialogue" in retry_response:
                        structured_response = retry_response
                    else:
                        dialogue_content = retry_response.get("dialogue", str(retry_response)) if isinstance(retry_response, dict) else str(retry_response)
                        if dialogue_content.startswith("{") and dialogue_content.endswith("}"):
                            structured_response = json.loads(dialogue_content)
                        else:
                            structured_response = {
                                "dialogue": dialogue_content,
                                "character": flow_state.character_id,
                                "emotion": "normal",
                                "tools": []
                            }
                    
                    # Resolve templates in the retry response
                    structured_response = self._resolve_response_templates(structured_response, {
                        "trigger_data": flow_state.trigger_data,
                        "character_id": flow_state.character_id,
                        "session_id": flow_state.session_id,
                        "step_results": flow_state.step_results
                    })
                    
                except Exception as parse_error:
                    print(f"⚠️ Failed to parse retry response: {parse_error}")
                    structured_response = {
                        "dialogue": str(retry_response),
                        "character": flow_state.character_id,
                        "emotion": "normal",
                        "tools": []
                    }
                
                # Generate TTS for the retry response
                audio_data = None
                if step_config.get("audio_enabled", False) and structured_response.get("dialogue"):
                    print(f"🎵 Generating TTS for retry response")
                    try:
                        if flow_state.character_id in ['seol_min_seok', 'seol_min_seok_quiz', 'kim_daehyun_history', 'seolminseok_korean_history_chat', 'dr_genie_science_quiz']:
                            audio_data = await self.seol_tts_service.generate_tts(
                                text=structured_response["dialogue"],
                                use_hd=True,
                                language="auto",
                                timeout_seconds=3.0  # PHASE 1: Keep fast timeout
                            )
                        else:
                            audio_data = await self.tts_service.generate_tts(structured_response["dialogue"])
                    except Exception as tts_error:
                        print(f"⚠️ TTS generation failed for retry: {tts_error}")
                
                return StepResult(
                    step_id=step_config["step_id"],
                    step_type="llm_response_with_tools",
                    response=structured_response,
                    audio=audio_data,
                    error=None
                )
                
            except Exception as retry_error:
                print(f"❌ RETRY ALSO FAILED: {retry_error}")
                # Re-raise the original exception - no fallbacks, user needs real LLM responses
                raise e
    
    def _prepare_step_context_and_template(self, flow_state: FlowState, step_config: Dict[str, Any]) -> tuple:
        """OPTIMIZED: Prepare context and resolve template in one operation"""
        # Build context from previous steps and trigger data
        context = self._build_step_context(flow_state, step_config.get("context", {}))
        context["character_id"] = flow_state.character_id
        
        # Get prompt template and apply dynamic selection logic
        template_name = step_config["prompt_template"]
        
        # 🚨 DYNAMIC TEMPLATE SELECTION: Choose correct template based on was_correct
        if template_name == "quiz_presentation_prompt":
            was_correct = False
            
            # Check multiple locations for was_correct value
            if "was_correct" in context:
                was_correct = context["was_correct"]
            elif "step_0" in context and isinstance(context["step_0"], dict):
                step_0_data = context["step_0"]
                if "was_correct" in step_0_data:
                    was_correct = step_0_data["was_correct"]
                elif "result" in step_0_data and "response" in step_0_data["result"]:
                    response_data = step_0_data["result"]["response"]
                    if "was_correct" in response_data:
                        was_correct = response_data["was_correct"]
            
            # Handle string boolean values properly - "False" string should be treated as False
            is_correct = False
            if isinstance(was_correct, str):
                is_correct = was_correct.lower() in ['true', '1', 'yes']
            else:
                is_correct = bool(was_correct)
            
            if is_correct:
                template_name = "quiz_progress_prompt"
            else:
                template_name = "quiz_retry_prompt"
        
        return context, template_name
    
    def _build_step_context(self, flow_state: FlowState, context_config: Dict[str, str]) -> Dict[str, Any]:
        """Build context for step execution from templates"""
        context = {}
        base_data = {
            "trigger_data": flow_state.trigger_data,
            "step_results": flow_state.step_results,
            "character_id": flow_state.character_id,
            "session_id": flow_state.session_id
        }
        
        # Add step-specific data
        if flow_state.step_results:
            for i, step_result in enumerate(flow_state.step_results):
                base_data[f"step_{i}"] = step_result
                # Special handling for was_correct
                if "was_correct" in step_result:
                    base_data[f"step_{i}"]["was_correct"] = step_result["was_correct"]
        
        # 🆕 ADD CHAT HISTORY CONTEXT
        try:
            user_id = self._get_user_id_from_session(flow_state.session_id)
            if user_id:
                chat_context = self.conversation_service.get_enhanced_ai_context(flow_state.session_id, user_id)
                base_data["chat_context"] = chat_context
                base_data["conversation_history"] = chat_context.get("context_prompt", "")
                base_data["recent_messages"] = chat_context.get("recent_messages", [])
                print(f"🗣️ CHAT CONTEXT INTEGRATED: {len(chat_context.get('recent_messages', []))} recent messages loaded")
            else:
                print(f"⚠️ Could not determine user_id for session {flow_state.session_id}")
                base_data["conversation_history"] = ""
                base_data["recent_messages"] = []
        except Exception as e:
            print(f"⚠️ Failed to load chat history: {e}")
            base_data["conversation_history"] = ""
            base_data["recent_messages"] = []
        
        for key, template in context_config.items():
            try:
                # Simple template substitution
                value = self._resolve_template(template, base_data)
                context[key] = value
            except Exception as e:
                print(f"❌ Error resolving template {template}: {e}")
                context[key] = template  # Fallback to original template
        
        # 🔧 ENSURE step_results is always available for step detection
        context["step_results"] = base_data["step_results"]
        context["character_id"] = base_data["character_id"]
        context["session_id"] = base_data["session_id"]
        context["conversation_history"] = base_data.get("conversation_history", "")
        context["recent_messages"] = base_data.get("recent_messages", [])
        
        return context
    
    def _get_user_id_from_session(self, session_id: str) -> Optional[str]:
        """Extract user_id from session_id by finding the session file in conversation directories"""
        try:
            conversations_path = Path("conversations")
            if not conversations_path.exists():
                return None
                
            # Search through user directories to find the session
            for user_dir in conversations_path.iterdir():
                if user_dir.is_dir():
                    for char_dir in user_dir.iterdir():
                        if char_dir.is_dir():
                            session_file = char_dir / f"{session_id}.json"
                            if session_file.exists():
                                # Load session to verify and get user_id
                                with open(session_file, 'r', encoding='utf-8') as f:
                                    session_data = json.load(f)
                                return session_data.get("user_id")
            return None
        except Exception as e:
            print(f"⚠️ Error extracting user_id from session {session_id}: {e}")
            return None
    
    def _resolve_template(self, template: str, data: Dict[str, Any]) -> str:
        """Resolve template variables like ${trigger_data.selection}"""
        if not template.startswith("${") or not template.endswith("}"):
            return template
            
        path = template[2:-1]  # Remove ${ and }
        parts = path.split(".")
        
        if 'trigger_data' in data:
            pass  # Debug logging was removed
        
        current = data
        for i, part in enumerate(parts):
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                idx = int(part)
                current = current[idx] if idx < len(current) else None
            else:
                current = None
                break
        
        result = str(current) if current is not None else template
        return result
    
    def _resolve_response_templates(self, response: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively resolve template variables in LLM response (both dialogue and tools)
        
        This fixes the issue where ${trigger_data.selection} appears literally in responses
        instead of being replaced with actual user selections.
        """
        
        if isinstance(response, dict):
            resolved_response = {}
            for key, value in response.items():
                resolved_response[key] = self._resolve_response_templates(value, data)
            return resolved_response
        elif isinstance(response, list):
            return [self._resolve_response_templates(item, data) for item in response]
        elif isinstance(response, str):
            # This is where the actual template resolution happens
            resolved = self._resolve_template(response, data)
            return resolved
        else:
            return response
    
    def _inject_context(self, prompt_template: str, context: Dict[str, Any]) -> str:
        """Inject context variables into prompt template"""
        prompt = prompt_template
        
        # Add common context variables
        if "character_id" in context:
            character_name = self._get_character_name(context["character_id"])
            prompt = prompt.replace("{character_name}", character_name)
        
        # Inject all context variables
        for key, value in context.items():
            placeholder = "{" + key + "}"
            prompt = prompt.replace(placeholder, str(value))
        
        # Handle quiz-specific logic
        if "user_answer" in context and "correct_answer" in context:
            is_correct = context["user_answer"].lower().strip() == context["correct_answer"].lower().strip()
            correct_text = "정답입니다!" if is_correct else "아쉽게도 틀렸습니다."
            prompt = prompt.replace("{is_correct}", correct_text)
        
        return prompt
    
    def _get_character_name(self, character_id: str) -> str:
        """Get character display name"""
        name_mapping = {
            "seol_min_seok_quiz": "설민석",
            "seolminseok_korean_history_chat": "설민석",
            "kim_daehyun_history": "김대현", 
            "history_teacher": "역사 선생님",
            "dr_genie_science_quiz": "닥터 지니"
        }
        # Force use of mapped character names only - no fallback allowed
        if character_id not in name_mapping:
            raise ValueError(f"Character ID '{character_id}' not found. Must use real character integration.")
        return name_mapping[character_id]
    
    def _extract_quiz_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract quiz-specific context for LLM analysis"""
        
        # IMPORTANT: Check for resolved template variables in trigger_data as fallback
        trigger_data = context.get("trigger_data", {}) if isinstance(context.get("trigger_data"), dict) else {}
        
        return {
            "quiz_question": context.get("question", context.get("quiz_question", trigger_data.get("question", ""))),
            "user_answer": context.get("user_answer", context.get("selection", trigger_data.get("selection", context.get("user_message", "")))),
            "correct_answer": context.get("correct_answer", trigger_data.get("correct_answer", "")),
            "options": context.get("options", context.get("items", trigger_data.get("items", [])))
        }
    
    async def _generate_character_response(self, character_id: str, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate character response using LLM-driven analysis"""
        
        # Define variables outside try block for exception handling
        character_name = self._get_character_name(character_id)
        step_results = context.get("step_results", [])
        current_step = len(step_results)
        quiz_context = self._extract_quiz_context(context)
        
        
        try:
            # Import and initialize LLM Agent system
            from .llm_agent_engine import LLMAgentEngine, InteractionContext
            from .character_prompt_manager import CharacterPromptManager
            
            # Initialize components if not already done (with proper caching)
            if not hasattr(self, 'llm_agent_engine'):
                self.llm_agent_engine = LLMAgentEngine()
                print("✅ Initialized LLM Agent Engine (cached for this ContinuousAnswerTool instance)")
            
            # Always create fresh CharacterPromptManager to ensure prompt updates are loaded
            self.character_prompt_manager = CharacterPromptManager()
            print("✅ Created fresh Character Prompt Manager (allows prompt updates)")
            
            # TWO-STEP PROCESS
            if current_step == 0:
                # FIRST STEP: Answer feedback only
                user_answer = quiz_context.get('user_answer', '')
                correct_answer = quiz_context.get('correct_answer', '')
                is_correct = user_answer == correct_answer
                
                print(f"🔧 STEP 0 FEEDBACK: user='{user_answer}', correct='{correct_answer}', is_correct={is_correct}")
                
                # Use LLM Agent Engine with character prompts instead of hardcoded responses
                interaction_context = InteractionContext(
                    question=quiz_context.get('quiz_question', ''),
                    user_answer=user_answer,
                    correct_answer=correct_answer,
                    options=quiz_context.get('options', [])
                )
                
                # CRITICAL FIX: Use the injected context prompt, not the character prompt manager
                # The 'prompt' parameter already contains the template with context injected
                print(f"🎯 Using context-injected prompt for feedback generation: {prompt[:100]}...")
                
                # Process with LLM Agent Engine using the injected prompt
                try:
                    # Use process_with_tools method with appropriate parameters
                    chat_history = []  # Empty for now, could be enhanced later
                    available_tools = {}  # No tools needed for simple feedback
                    
                    agent_response = await self.llm_agent_engine.process_with_tools(
                        user_input=user_answer,
                        character_prompt=prompt,  # Use the injected template prompt
                        chat_history=chat_history,
                        available_tools=available_tools
                    )
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    raise
                
                print(f"✅ LLM Agent Response: {agent_response.get('dialogue', 'No dialogue')[:100]}...")
                print(f"🔧 LLM Agent Tools: {agent_response.get('tool', None)}")
                
                response = {
                    "character": character_name,
                    "dialogue": agent_response.get('dialogue', 'No dialogue available'),
                    "emotion": agent_response.get('emotion', "sad" if not is_correct else "excited"),
                    "speed": 1.0,
                    "was_correct": is_correct,
                    "llm_tools": agent_response.get('tool', [])  # Store LLM-generated tools for step 1
                }
                
                return response
                
            elif current_step == 1:
                # SECOND STEP: Quiz presentation with LLM-generated tools
                # Get LLM tools from step 0 result
                llm_tools = []
                if step_results and len(step_results) > 0:
                    first_result = step_results[0].get('result', {})
                    if 'response' in first_result and first_result['response'] is not None:
                        llm_tools = first_result['response'].get('llm_tools', [])
                    elif 'llm_tools' in first_result:
                        llm_tools = first_result['llm_tools']
                
                print(f"🔧 STEP 1 QUIZ: Using {len(llm_tools)} LLM-generated tools")
                
                # STEP 1: Generate new quiz question with conversation history from Step 0
                print("📝 STEP 1: Generating new quiz question with full conversation context")
                
                # Build context that includes Step 0 conversation history
                # Extract from context (handle both dict and object forms)
                if isinstance(context, dict):
                    question = context.get('question', '')
                    user_answer = context.get('user_answer', '')
                    correct_answer = context.get('correct_answer', '')
                    attempt_history = context.get('attempt_history', [])
                    conversation_history = context.get('conversation_history', [])
                else:
                    question = getattr(context, 'question', '')
                    user_answer = getattr(context, 'user_answer', '')
                    correct_answer = getattr(context, 'correct_answer', '')
                    attempt_history = getattr(context, 'attempt_history', [])
                    conversation_history = getattr(context, 'conversation_history', [])
                
                step_1_context = InteractionContext(
                    question=question,
                    user_answer=user_answer, 
                    correct_answer=correct_answer,
                    options=[], 
                    attempt_history=attempt_history
                )
                
                # Use default Korean history teacher prompt for Step 1 (new quiz generation)
                character_prompt = "You are 설민석, an enthusiastic Korean history teacher who creates engaging quiz questions."
                
                # Get conversation history safely
                conversation_history_text = str(conversation_history) if conversation_history else "이전 피드백이 제공되었습니다."
                
                # Add Step 1 specific instructions to character prompt
                step_1_prompt = f"""{character_prompt}

STEP 1 CONTEXT - NEW QUIZ GENERATION:
You just provided feedback in Step 0. Now generate a NEW quiz question for the student.

CONVERSATION HISTORY FROM STEP 0:
{conversation_history_text}

INSTRUCTIONS FOR STEP 1:
- Generate a DIFFERENT quiz question (not the same as previous)
- Include the question text in your dialogue for TTS
- Use show_selection tool with new question and options
- Be encouraging and educational in your dialogue
- This is a new question, not a retry of the previous one

Return JSON with:
- dialogue: Include the new question text + introduction
- tools: [show_selection tool with new quiz question]
"""
                
                # Call LLM Agent Engine for Step 1 with full context
                try:
                    print("🤖 Calling LLM Agent Engine for Step 1 quiz generation...")
                    step_1_response = await self.llm_agent_engine.process_with_tools(
                        user_input=step_1_context.user_answer,
                        character_prompt=step_1_prompt,
                        chat_history=[],
                        available_tools={}
                    )
                    
                    if step_1_response and step_1_response.get('dialogue'):
                        dialogue = step_1_response['dialogue']
                        tools = step_1_response.get('tool') or []
                        if isinstance(tools, dict):
                            tools = [tools]  # Convert single tool dict to list
                        
                        print(f"✅ STEP 1 LLM Response: {len(dialogue)} chars dialogue, {len(tools)} tools")
                        print(f"📋 Step 1 Dialogue: {dialogue[:100]}...")
                        print(f"🔧 Step 1 Tools: {[tool.get('type') for tool in tools]}")
                        
                    else:
                        print("❌ STEP 1 LLM returned empty response - re-raising error for debugging")
                        raise Exception("LLM Agent Engine returned empty response for step 1. Check LLM client configuration.")
                        
                except Exception as e:
                    print(f"❌ STEP 1 LLM error: {e}")
                    raise Exception(f"LLM Agent Engine failed for step 1: {e}. No fallback allowed - must debug LLM integration.")
                
                response = {
                    "character": character_name,
                    "dialogue": dialogue,
                    "emotion": "excited",
                    "speed": 1.0,
                    "tools": tools
                }
                
                return response
                
            else:
                # Fallback for unexpected steps
                return {
                    "character": character_name,
                    "dialogue": f"죄송합니다. 예상치 못한 상황이 발생했습니다. 다시 시도해주세요.",
                    "emotion": "normal",
                    "speed": 1.0,
                    "was_correct": True
                }
            
        except Exception as e:
            print(f"❌ Error generating LLM character response: {e}")
            print(f"🚨 REAL LLM INTEGRATION: Re-raising exception to debug LLM issues")
            raise  # Re-raise the exception instead of using fallback mock responses
    
    # LEGACY FEEDBACK METHOD REMOVED - All feedback must come from LLM Agent Engine
    
    # LEGACY METHOD REMOVED - All question generation must come from LLM Agent Engine
    
    # FALLBACK METHODS REMOVED - All responses must come from LLM Agent Engine
    
    # FALLBACK QUIZ METHOD REMOVED - All quiz generation must come from LLM Agent Engine
    
    async def progress_flow(self, session_id: str, trigger_type: str, data: Optional[Dict[str, Any]] = None) -> Optional[FlowExecution]:
        """
        Progress an active flow to the next step
        Called when conditions are met (e.g., audio completion)
        """
        print(f"⏭️  Progressing flow for session {session_id}, trigger: {trigger_type}")
        
        flow_state = self.active_flows.get(session_id)
        if not flow_state:
            print(f"❌ No active flow for session {session_id}")
            return None
        
        # Check if condition is met for progression
        if trigger_type == "audio_completion":
            next_step_index = flow_state.current_step + 1
            
            if next_step_index < len(flow_state.flow_config["steps"]):
                # Execute next step
                return await self._execute_flow_step(flow_state, next_step_index)
            else:
                # Flow completed
                self._complete_flow(session_id)
                return FlowExecution(
                    session_id=session_id,
                    step_result=StepResult("flow_end", "completion"),
                    flow_continues=False
                )
        
        print(f"❌ Invalid trigger type: {trigger_type}")
        return None
    
    def _complete_flow(self, session_id: str):
        """Complete and cleanup flow"""
        if session_id in self.active_flows:
            print(f"✅ Completing flow for session {session_id}")
            del self.active_flows[session_id]
    
    def get_active_flow(self, session_id: str) -> Optional[FlowState]:
        """Get active flow state for session"""
        return self.active_flows.get(session_id)
    
    def has_active_flow(self, session_id: str) -> bool:
        """Check if session has active flow"""
        return session_id in self.active_flows
    

# Global instance
continuous_answer_tool = ContinuousAnswerTool()