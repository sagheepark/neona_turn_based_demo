"""
Continuous Answer Tool: Proactive Multi-Step Character Interactions

Enables characters to conduct intelligent multi-step conversations where user actions 
trigger continuous, proactive responses without manual prompts.
"""

import json
import asyncio
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from services.optimized_prompt_builder import OptimizedPromptBuilder
from services.tts_service import tts_service


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
    
    def _load_flow_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load flow configuration from JSON files"""
        configs = {}
        
        # Quiz continuous flow configuration
        quiz_flow = {
            "flow_id": "quiz_continuous_v1",
            "character_types": ["seol_min_seok_quiz", "history_teacher"],
            "trigger": {
                "tool_type": "show_selection",
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
                        "question": "${trigger_data.question}"
                    },
                    "audio_enabled": True,
                    "next_trigger": "audio_completion"
                },
                {
                    "step_id": "next_action_decision",
                    "type": "llm_response", 
                    "condition": "audio_completion",
                    "prompt_template": "quiz_next_step_prompt",
                    "context": {
                        "was_correct": "${step_0.result.was_correct}",
                        "character_personality": "${character.proactive_level}"
                    },
                    "audio_enabled": True,
                    "next_trigger": None  # End of flow
                }
            ],
            "prompts": {
                "quiz_feedback_prompt": """당신은 {character_name}입니다. 사용자가 방금 다음과 같이 답했습니다: "{user_answer}"
정답은: "{correct_answer}"이었습니다.

{is_correct}
- 정답이면: 열정적으로 축하하고 간단한 설명을 제공하세요.
- 오답이면: 격려하며 정답을 알려주고 왜 그런지 설명하세요.

그 다음, 자연스럽게 다음 문제를 준비한다고 말하면서 관련된 새로운 퀴즈 문제를 만들어 제시하세요.
사용자에게 준비되었는지 묻지 말고, 바로 다음 문제로 이어가세요.""",

                "quiz_next_step_prompt": """이전 단계에서 사용자가 {was_correct}했습니다. 
당신의 성격은 {character_personality}입니다.

다음 행동을 결정하세요:
- 정답이었다면: 더 도전적인 문제를 제시
- 오답이었다면: 관련된 쉬운 문제로 자신감을 회복시키기

주도적으로 다음 퀴즈를 제시하세요. "준비되었나요?" 같은 질문은 하지 말고 자연스럽게 이어가세요."""
            }
        }
        
        configs["quiz_continuous_v1"] = quiz_flow
        return configs
    
    async def trigger_flow(self, trigger_event: ToolTriggerEvent) -> Optional[FlowExecution]:
        """
        Main entry point for continuous flows
        """
        print(f"🔄 ContinuousAnswerTool: Triggering flow for {trigger_event.character_id}")
        
        # Find matching flow configuration
        flow_config = self._get_flow_config(trigger_event.character_id, trigger_event.tool_type)
        
        if not flow_config:
            print(f"❌ No flow config found for character {trigger_event.character_id}, tool {trigger_event.tool_type}")
            return None
            
        # Initialize flow state
        flow_state = FlowState(
            session_id=trigger_event.session_id,
            character_id=trigger_event.character_id,
            flow_config=flow_config,
            trigger_data=trigger_event.data
        )
        
        self.active_flows[trigger_event.session_id] = flow_state
        print(f"✅ Flow initialized for session {trigger_event.session_id}")
        
        # Execute first step
        return await self._execute_flow_step(flow_state, step_index=0)
    
    def _get_flow_config(self, character_id: str, tool_type: str) -> Optional[Dict[str, Any]]:
        """Get flow configuration for character and tool type"""
        for flow_id, config in self.flow_definitions.items():
            if (character_id in config.get("character_types", []) and 
                config.get("trigger", {}).get("tool_type") == tool_type):
                return config
        return None
    
    async def _execute_flow_step(self, flow_state: FlowState, step_index: int) -> FlowExecution:
        """Execute a single step in the continuous flow"""
        print(f"🎯 Executing step {step_index} for session {flow_state.session_id}")
        
        if step_index >= len(flow_state.flow_config["steps"]):
            print("❌ Step index out of range")
            return FlowExecution(
                session_id=flow_state.session_id,
                step_result=StepResult("error", "error", error="Step index out of range"),
                flow_continues=False
            )
        
        step_config = flow_state.flow_config["steps"][step_index]
        flow_state.current_step = step_index
        
        if step_config["type"] == "llm_response":
            step_result = await self._execute_llm_step(flow_state, step_config)
        else:
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
        
        if step_result.next_trigger and step_index + 1 < len(flow_state.flow_config["steps"]):
            next_step_index = step_index + 1
            flow_continues = True
        
        return FlowExecution(
            session_id=flow_state.session_id,
            step_result=step_result,
            flow_continues=flow_continues,
            next_step_index=next_step_index
        )
    
    async def _execute_llm_step(self, flow_state: FlowState, step_config: Dict[str, Any]) -> StepResult:
        """Execute LLM generation step with context injection"""
        try:
            # Build context from previous steps and trigger data
            context = self._build_step_context(flow_state, step_config.get("context", {}))
            
            # Get prompt template and inject context
            prompt_template = flow_state.flow_config["prompts"][step_config["prompt_template"]]
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
                    audio_data = await self.tts_service.generate_speech(
                        text=response["dialogue"],
                        voice_id=None  # Will use character default
                    )
                except Exception as tts_error:
                    print(f"❌ TTS generation failed: {tts_error}")
                    # Continue without audio
            
            return StepResult(
                step_id=step_config["step_id"],
                step_type="llm_response",
                response=response,
                audio=audio_data,
                next_trigger=step_config.get("next_trigger"),
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
    
    def _build_step_context(self, flow_state: FlowState, context_config: Dict[str, str]) -> Dict[str, Any]:
        """Build context for step execution from templates"""
        context = {}
        base_data = {
            "trigger_data": flow_state.trigger_data,
            "step_results": flow_state.step_results,
            "character_id": flow_state.character_id,
            "session_id": flow_state.session_id
        }
        
        for key, template in context_config.items():
            try:
                # Simple template substitution
                value = self._resolve_template(template, base_data)
                context[key] = value
            except Exception as e:
                print(f"❌ Error resolving template {template}: {e}")
                context[key] = template  # Fallback to original template
        
        return context
    
    def _resolve_template(self, template: str, data: Dict[str, Any]) -> str:
        """Resolve template variables like ${trigger_data.selection}"""
        if not template.startswith("${") or not template.endswith("}"):
            return template
            
        path = template[2:-1]  # Remove ${ and }
        parts = path.split(".")
        
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                idx = int(part)
                current = current[idx] if idx < len(current) else None
            else:
                current = None
                break
        
        return str(current) if current is not None else template
    
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
            "history_teacher": "역사 선생님"
        }
        return name_mapping.get(character_id, "AI 캐릭터")
    
    async def _generate_character_response(self, character_id: str, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate character response using existing systems"""
        try:
            character_name = self._get_character_name(character_id)
            
            # Generate meaningful dialogue based on context
            user_answer = context.get("user_answer", "")
            correct_answer = context.get("correct_answer", "")
            question = context.get("question", "")
            
            # Simple feedback logic based on answer correctness
            is_correct = user_answer.lower().strip() in correct_answer.lower().strip()
            
            if is_correct:
                dialogue = f"정답입니다! 훌륭해요! '{user_answer}'가 맞습니다. 다음 문제로 넘어가겠습니다. 조선시대의 또 다른 중요한 사건인 임진왜란은 언제 일어났을까요? A) 1592년 B) 1598년 C) 1587년 D) 1605년"
            else:
                dialogue = f"아쉽게도 틀렸습니다. 정답은 '{correct_answer}'입니다. 하지만 괜찮아요! 다시 한번 관련 문제로 연습해보겠습니다. 세종대왕과 관련된 다른 업적은 무엇일까요? A) 측우기 발명 B) 거중기 발명 C) 화차 제작 D) 앙부일구 제작"
            
            response = {
                "character": character_name,
                "dialogue": dialogue,
                "emotion": "excited" if is_correct else "encouraging",
                "speed": 1.0,
                "was_correct": is_correct
            }
            
            return response
            
        except Exception as e:
            print(f"❌ Error generating character response: {e}")
            return {
                "character": "AI",
                "dialogue": "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다.",
                "emotion": "neutral",
                "speed": 1.0,
                "was_correct": False
            }
    
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