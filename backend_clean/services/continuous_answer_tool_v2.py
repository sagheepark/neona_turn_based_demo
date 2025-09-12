"""
Continuous Answer Tool V2 - Single LLM Call Implementation

This implements the CORRECT architecture from plan_new.md:
- Single LLM call generates complete continuous_quiz_response tool
- Two-phase structure returned in ONE response  
- Frontend handles timing and UI rendering
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

# Import LLM and TTS services
from services.llm_agent_engine import LLMAgentEngine
from services.character_prompt_manager import CharacterPromptManager
from services.platform_tool_handler import PlatformToolHandler
from services.tts_service import tts_service
from services.seolminseok_tts_service import seolminseok_tts_service

@dataclass
class ContinuousFlowContext:
    """Context for continuous flow execution"""
    session_id: str
    character_id: str
    user_selection: str
    quiz_context: Dict[str, Any]

class ContinuousAnswerToolV2:
    """
    Single LLM call implementation matching plan_new.md specification
    """
    
    def __init__(self):
        self.llm_agent = LLMAgentEngine()
        self.prompt_manager = CharacterPromptManager()
        self.tool_handler = PlatformToolHandler()
        
        print("✅ ContinuousAnswerToolV2 initialized with single-LLM-call architecture")
    
    async def trigger_continuous_flow(self, context: ContinuousFlowContext) -> Dict[str, Any]:
        """
        Trigger continuous quiz flow with single LLM call
        
        Returns complete continuous_quiz_response tool matching plan specification
        """
        print(f"🚀 TRIGGERING CONTINUOUS FLOW - Single LLM Call Architecture")
        print(f"   Session: {context.session_id}")
        print(f"   Character: {context.character_id}")
        print(f"   User Selection: {context.user_selection}")
        print(f"   Quiz Context: {context.quiz_context}")
        
        # Get character prompt
        character_prompt = await self.prompt_manager.get_prompt(context.character_id)
        
        # Get available tools for LLM
        available_tools = self.tool_handler.get_tool_definitions_for_llm()
        
        # Build user input message
        user_input = f"Quiz answer: {context.user_selection}"
        
        # Build chat history with quiz context
        chat_history = []
        if context.quiz_context.get("question"):
            chat_history.append({
                "role": "assistant", 
                "content": f"Quiz question: {context.quiz_context['question']}"
            })
        
        print(f"🤖 Calling LLM with single call for continuous_quiz_response...")
        
        # Single LLM call to generate complete response
        llm_response = await self.llm_agent.process_with_tools(
            user_input=user_input,
            character_prompt=character_prompt,
            chat_history=chat_history,
            available_tools=available_tools
        )
        
        print(f"🎯 LLM Response Received: {llm_response}")
        
        # Verify we got continuous_quiz_response tool
        tool_type = None
        if llm_response.get("tool"):
            tool_type = llm_response["tool"].get("type", "unknown")
        
        if not llm_response.get("tool") or tool_type != "continuous_quiz_response":
            print(f"⚠️ LLM did not return continuous_quiz_response, got: {tool_type}")
            print(f"🔍 Full tool response: {llm_response.get('tool', {})}")
            
            # Force correct structure if LLM didn't provide it
            llm_response = await self._force_continuous_quiz_structure(context, llm_response)
        
        # Generate TTS for both phases
        tool_data = llm_response["tool"]["data"]
        
        # Phase 1 TTS
        print(f"🎵 Generating Phase 1 TTS...")
        tool_data["phase1"]["audio_url"] = await self._generate_tts(
            tool_data["phase1"]["text"], 
            context.character_id
        )
        
        # Phase 2 TTS  
        print(f"🎵 Generating Phase 2 TTS...")
        tool_data["phase2"]["audio_url"] = await self._generate_tts(
            tool_data["phase2"]["text"], 
            context.character_id
        )
        
        print(f"✅ CONTINUOUS FLOW COMPLETE - Single response with both phases ready")
        
        return {
            "type": "continuous_quiz_response",
            "data": tool_data,
            "dialogue": llm_response.get("dialogue", "Processing your answer..."),
            "session_id": context.session_id
        }
    
    async def _force_continuous_quiz_structure(self, context: ContinuousFlowContext, partial_response: Dict) -> Dict:
        """
        Force correct continuous_quiz_response structure if LLM didn't provide it
        This ensures we always return the expected format from plan_new.md
        """
        print(f"🔧 FORCING CORRECT STRUCTURE for continuous_quiz_response")
        
        # Determine if answer was correct
        user_answer = context.user_selection
        correct_answer = context.quiz_context.get("correct_answer", "")
        is_correct = user_answer == correct_answer
        
        print(f"   User Answer: '{user_answer}'")
        print(f"   Correct Answer: '{correct_answer}'")  
        print(f"   Is Correct: {is_correct}")
        
        # Build phase1 feedback
        if is_correct:
            phase1_text = f"정답입니다! 훌륭해요! {user_answer}이 맞습니다."
        else:
            phase1_text = f"아쉽게도 틀렸습니다. {user_answer}은 정답이 아니에요. 다시 한번 생각해보세요!"
        
        # Build phase2 content
        if is_correct:
            # Generate new question for correct answers
            phase2_text = "자, 이제 다음 문제로 넘어가볼까요?"
            phase2_tool = {
                "type": "show_selection",
                "data": {
                    "question": "세종대왕의 가장 큰 업적은 무엇일까요?",
                    "options": ["한글 창제", "측우기 발명", "거북선 건조", "팔만대장경 제작"],
                    "correct_answer": "한글 창제",
                    "selection_mode": "quiz_question"
                }
            }
        else:
            # Retry same question for wrong answers
            phase2_text = "자, 다시 한번 도전해볼까요?"
            phase2_tool = {
                "type": "show_selection", 
                "data": {
                    "question": context.quiz_context.get("question", ""),
                    "options": context.quiz_context.get("options", []),
                    "correct_answer": context.quiz_context.get("correct_answer", ""),
                    "selection_mode": "quiz_question"
                }
            }
        
        # Return corrected structure
        return {
            "dialogue": partial_response.get("dialogue", f"{user_answer}을 선택하셨습니다!"),
            "tool": {
                "type": "continuous_quiz_response",
                "data": {
                    "phase1": {
                        "text": phase1_text,
                        "delay_ms": 3000
                    },
                    "phase2": {
                        "text": phase2_text,
                        "tool": phase2_tool
                    }
                }
            }
        }
    
    async def _generate_tts(self, text: str, character_id: str) -> Optional[str]:
        """Generate TTS for given text and character"""
        try:
            if character_id in ['seol_min_seok_quiz', 'seolminseok_korean_history_chat']:
                # Use special TTS for Korean history characters
                return await seolminseok_tts_service.generate_tts(text)
            else:
                # Use default TTS service
                result = await tts_service.generate_speech(text)
                return result.get("audio")
        except Exception as e:
            print(f"❌ TTS generation failed: {e}")
            return None

# Global instance
continuous_answer_tool_v2 = ContinuousAnswerToolV2()