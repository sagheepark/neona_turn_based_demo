"""
Continuous Answer Tool (Clean Version) - Tool-Driven Multi-Step Interactions

This clean version removes all hardcoded logic and relies entirely on LLM + prompts
to control behavior. It only orchestrates the flow, not the content.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ContinuousFlowContext:
    """Context for continuous flow execution"""
    session_id: str
    character_id: str
    user_input: str
    quiz_context: Optional[Dict[str, Any]] = None
    
class ContinuousAnswerToolClean:
    """
    Clean implementation of continuous answer tool
    All logic is driven by LLM and character prompts, not code
    """
    
    def __init__(self):
        # Import dependencies
        from .llm_agent_engine import LLMAgentEngine
        from .character_prompt_manager import CharacterPromptManager
        from .platform_tool_handler import PlatformToolHandler
        from .tts_service import tts_service
        
        self.llm_agent = LLMAgentEngine()
        self.prompt_manager = CharacterPromptManager()
        self.tool_handler = PlatformToolHandler()
        self.tts_service = tts_service
        
        logger.info("✅ Clean Continuous Answer Tool initialized")
    
    async def process_quiz_answer(self, context: ContinuousFlowContext) -> Dict[str, Any]:
        """
        Process quiz answer and generate continuous two-phase response
        
        Args:
            context: Flow context with session, character, and quiz data
            
        Returns:
            Two-phase response with feedback and next question
        """
        print(f"🔥🔥🔥 CONTINUOUS_ANSWER_TOOL_CLEAN.process_quiz_answer() CALLED! 🔥🔥🔥")
        print(f"   User input: {context.user_input}")
        print(f"   Quiz question: {context.quiz_context.get('question', 'MISSING')}")
        print(f"   Correct answer: {context.quiz_context.get('correct_answer', 'MISSING')}")
        print(f"   Is correct: {context.user_input == context.quiz_context.get('correct_answer', '')}")
        # Get character prompt
        character_prompt = await self.prompt_manager.get_prompt(context.character_id)
        
        # Build LLM prompt with tool definitions
        tool_definitions = self.tool_handler.get_tool_definitions_for_llm()
        
        # Determine if answer is correct
        is_correct = context.user_input == context.quiz_context.get('correct_answer', '')
        
        # Prepare the exact values for the template
        current_question = context.quiz_context.get('question', '')
        current_options = context.quiz_context.get('options', [])
        current_correct = context.quiz_context.get('correct_answer', '')
        
        if is_correct:
            # For correct answers, LLM creates new question
            template_question = "CREATE_NEW_QUESTION"
            template_options = "CREATE_NEW_OPTIONS"
            template_correct = "CREATE_NEW_CORRECT_ANSWER"
            phase_text = "Introduction to next question"
        else:
            # For wrong answers, use EXACT same values
            template_question = current_question
            template_options = str(current_options)
            template_correct = current_correct
            phase_text = "Let's try again"
        
        full_prompt = f"""
{character_prompt}

AVAILABLE TOOLS:
{tool_definitions}

CURRENT QUIZ CONTEXT:
Question: {current_question}
User Answer: {context.user_input}
Correct Answer: {current_correct}
Answer is: {"CORRECT" if is_correct else "WRONG"}

CRITICAL INSTRUCTION FOR WRONG ANSWERS:
If the user answer is WRONG, you MUST use the EXACT values provided in the JSON template below.
Do NOT change the question, options, or correct_answer fields.

CRITICAL INSTRUCTION FOR CORRECT ANSWERS:
If the user answer is CORRECT, replace the template placeholders with new values.

TASK: Generate a continuous_quiz_response tool with:
1. Phase1: Feedback about the answer (correct/wrong)
2. Phase2: {"NEW question if correct" if is_correct else "EXACT SAME question for retry"}

Respond with JSON format:
{{
    "tool": "continuous_quiz_response",
    "data": {{
        "phase1": {{
            "text": "Your feedback here",
            "delay_ms": 3000
        }},
        "phase2": {{
            "text": "{phase_text}",
            "tool": {{
                "type": "show_selection",
                "data": {{
                    "question": "{template_question}",
                    "options": {template_options},
                    "correct_answer": "{template_correct}",
                    "selection_mode": "quiz_question"
                }}
            }}
        }}
    }}
}}
"""
        
        # Call LLM to generate response
        from .llm_agent_engine import InteractionContext
        
        llm_context = InteractionContext(
            question=context.quiz_context.get('question', ''),
            user_answer=context.user_input,
            correct_answer=context.quiz_context.get('correct_answer', ''),
            options=context.quiz_context.get('options', []),
            session_id=context.session_id,
            character_id=context.character_id
        )
        
        # Define available tools
        available_tools = {
            "continuous_quiz_response": {
                "description": "Provide two-phase continuous quiz response",
                "parameters": ["phase1", "phase2"]
            }
        }
        
        agent_response = await self.llm_agent.process_with_tools(
            user_input=context.user_input,
            character_prompt=full_prompt,
            chat_history=[],  # Add chat history if available
            available_tools=available_tools
        )
        
        # Parse LLM response to get tool data
        print(f"🔍 DEBUG: LLM agent_response type: {type(agent_response)}")
        print(f"🔍 DEBUG: LLM agent_response keys: {list(agent_response.keys()) if isinstance(agent_response, dict) else 'Not a dict'}")
        print(f"🔍 DEBUG: LLM agent_response: {str(agent_response)[:200]}...")
        
        try:
            # New format: agent_response is a dict with 'tool' key
            if agent_response.get('tool'):
                tool_data = agent_response['tool']
                print(f"✅ Using agent_response['tool'] format")
            else:
                # Try parsing dialogue as JSON
                dialogue_text = agent_response.get('dialogue', '{}')
                print(f"🔍 Parsing dialogue as JSON: {dialogue_text[:100]}...")
                tool_data = json.loads(dialogue_text)
                print(f"✅ Parsed dialogue as JSON successfully")
                
            # Validate that the parsed structure has the required tool in phase2
            if (not tool_data.get('data') or 
                not tool_data['data'].get('phase2') or 
                not tool_data['data']['phase2'].get('tool')):
                print(f"❌ LLM response missing required phase2 tool structure:")
                print(f"   has data: {bool(tool_data.get('data'))}")
                print(f"   has phase2: {bool(tool_data.get('data', {}).get('phase2'))}")
                print(f"   has phase2.tool: {bool(tool_data.get('data', {}).get('phase2', {}).get('tool'))}")
                print(f"   using fallback structure instead")
                raise ValueError("Missing phase2 tool structure")
            else:
                print(f"✅ LLM response has valid phase2 tool structure")
                
        except Exception as e:
            print(f"Error parsing agent response or missing tool structure: {e}")
            # Fallback structure if parsing fails OR tool structure is incomplete
            is_correct = context.user_input == context.quiz_context.get('correct_answer', '')
            tool_data = {
                "tool": "continuous_quiz_response",
                "data": {
                    "phase1": {
                        "text": agent_response.get('dialogue') or ("정답입니다!" if is_correct else "다시 생각해보세요."),
                        "delay_ms": 3000
                    },
                    "phase2": {
                        "text": "다시 한 번 생각해보세요." if not is_correct else "다음 문제입니다.",
                        "tool": {
                            "type": "show_selection",
                            "data": {
                                "question": context.quiz_context.get('question', ''),
                                "options": context.quiz_context.get('options', context.quiz_context.get('items', [])),
                                "correct_answer": context.quiz_context.get('correct_answer', ''),
                                "selection_mode": "quiz_question"
                            }
                        }
                    }
                }
            }
        
        # Generate TTS for both phases
        phase1_audio = await self._generate_tts(
            tool_data["data"]["phase1"]["text"],
            context.character_id
        )
        
        # Generate TTS for Phase 2 text (already contains question - don't duplicate)
        phase2_text = tool_data["data"]["phase2"]["text"]
        # Note: phase2_text already includes the quiz question from LLM generation
        # No need to append it again to avoid duplication
        
        phase2_audio = await self._generate_tts(phase2_text, context.character_id)
        
        # Return formatted response
        return {
            "type": "continuous_quiz_response",
            "data": {
                "phase1": {
                    "text": tool_data["data"]["phase1"]["text"],
                    "audio": phase1_audio,
                    "delay_ms": tool_data["data"]["phase1"].get("delay_ms", 3000)
                },
                "phase2": {
                    "text": tool_data["data"]["phase2"]["text"],
                    "audio": phase2_audio,
                    "tool": tool_data["data"]["phase2"]["tool"]
                }
            }
        }
    
    async def _generate_tts(self, text: str, character_id: str) -> Optional[str]:
        """Generate TTS for text based on character"""
        try:
            if character_id in ['seol_min_seok_quiz', 'seolminseok_korean_history_chat', 'dr_genie_science_quiz']:
                # Use special TTS for quiz characters
                from .seolminseok_tts_service import seolminseok_tts_service
                return await seolminseok_tts_service.generate_tts(text)
            else:
                # Use default TTS
                result = await self.tts_service.generate_speech(text)
                return result.get("audio")
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None

# Global instance
continuous_answer_tool_clean = ContinuousAnswerToolClean()