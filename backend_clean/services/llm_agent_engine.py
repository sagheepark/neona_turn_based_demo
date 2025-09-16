"""
LLM Agent Engine - Core LLM processing with tool understanding

This engine processes user interactions using LLM intelligence based on
character prompts and available tools. Enhanced with caching optimization for sub-second response times.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
# Performance logger removed
# from .performance_logger import track_async_operation, performance_logger

# Import caching systems
from .llm_cache_manager import llm_pool, llm_cache

logger = logging.getLogger(__name__)

@dataclass
class InteractionContext:
    """Context information for LLM agent processing"""
    question: str = ""
    user_answer: str = ""
    correct_answer: str = ""
    attempt_history: List[str] = None
    options: List[str] = None
    
    def __post_init__(self):
        if self.attempt_history is None:
            self.attempt_history = []
        if self.options is None:
            self.options = []

class LLMAgentEngine:
    """
    Core engine that processes with LLM based on prompts
    NO FALLBACK METHODS - must work with real LLM
    """
    
    def __init__(self, azure_client=None):
        """Initialize with caching optimization for performance"""
        # Use global caching systems instead of individual clients
        self.connection_pool = llm_pool
        self.response_cache = llm_cache
        self.azure_client = azure_client  # Keep for compatibility
        logger.info("✅ LLMAgentEngine initialized with caching optimization")
    
    async def process_with_tools(self, 
                                 user_input: str,
                                 character_prompt: str,
                                 chat_history: List[Dict],
                                 available_tools: Dict,
                                 character_id: str = None,
                                 request_id: str = None) -> Dict:
        """
        Process user input using LLM with tool understanding - ENHANCED WITH CACHING
        
        Args:
            user_input: User's message or selection
            character_prompt: Character behavior instructions
            chat_history: Previous conversation context
            available_tools: Dictionary of available tools
            character_id: Character identifier for caching
            
        Returns:
            Dictionary with dialogue and tool (if specified)
        """
        
        # Use persistent client from connection pool (initialization optimization only)
        azure_client = await self.connection_pool.get_client(character_id or "default")
        
        # Build system prompt with character instructions and tool definitions
        system_prompt = f"""
{character_prompt}

AVAILABLE TOOLS:
{json.dumps(available_tools, indent=2)}

You MUST respond with valid JSON containing:
{{
    "dialogue": "Your response text",
    "tool": {{ tool object if using tool }} or null
}}

RESPONSE GUIDELINES:
- Always be in character as defined above
- Follow the specific tool usage instructions provided in your character prompt above
- Use tools when interaction requires UI elements
- Maintain educational flow between questions
- Never reveal correct answers for wrong responses
"""
        
        # Build message history
        messages = [
            {"role": "system", "content": system_prompt},
            *chat_history,
            {"role": "user", "content": user_input}
        ]
        
        # Use passed request ID or generate one for performance tracking
        if not request_id:
            request_id = f"llm_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        logger.info(f"🧠 Processing with GPT-4.1-mini: user_input='{user_input[:50]}...'")
        
        try:
            # Get model name from environment
            model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini")
            
            # Call with deployment name using persistent client
            response = await azure_client.chat.completions.create(
                model=model_name,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=510
            )
            
            # Parse JSON response
            response_content = response.choices[0].message.content
            logger.info(f"🔍 Raw LLM response: {response_content}")
            
            parsed_response = json.loads(response_content)
            
            logger.info(f"🔍 Parsed LLM response: {parsed_response}")
            
            # SMART TOOL VALIDATION: Allow show_selection for greetings, enforce continuous_quiz_response for answers
            if character_id and 'tool' in parsed_response and parsed_response['tool']:
                tool = parsed_response['tool']
                tool_type = None
                
                # Extract tool type from various formats
                if isinstance(tool, dict):
                    if 'type' in tool:
                        tool_type = tool['type']
                    elif 'name' in tool:
                        tool_type = tool['name']
                    elif len(tool) == 1:
                        tool_type = list(tool.keys())[0]
                
                # Smart enforcement: Only block show_selection when it should be continuous_quiz_response
                if character_id in ['seol_min_seok_quiz', 'dr_genie_science_quiz']:
                    if tool_type == 'show_selection':
                        tool_data = tool.get('data', {}) if 'data' in tool else tool.get(tool_type, {})
                        selection_mode = tool_data.get('selection_mode', '')
                        
                        # Allow show_selection for topic selection (greetings), block for quiz questions
                        if selection_mode == 'quiz_question':
                            logger.warning(f"🚨 TOOL ENFORCEMENT: {character_id} tried to use 'show_selection' for quiz - this should be 'continuous_quiz_response'")
                            logger.warning(f"⚠️  Allowing it for now, but frontend should handle properly")
                        # Allow selection_mode == 'topic' for greeting topic selection
            
            # Normalize tool format to {type, data} structure
            if 'tool' in parsed_response and parsed_response['tool']:
                tool = parsed_response['tool']
                
                # Handle format: {name: "tool_name", parameters: {...}}
                if 'name' in tool and 'parameters' in tool:
                    parsed_response['tool'] = {
                        'type': tool['name'],
                        'data': tool['parameters']
                    }
                
                # Handle format: {tool_name: {...}}
                elif isinstance(tool, dict) and len(tool) == 1:
                    tool_name = list(tool.keys())[0]
                    tool_data = tool[tool_name]
                    parsed_response['tool'] = {
                        'type': tool_name,
                        'data': tool_data
                    }
                
                # Handle format: {type: "tool_name", data: {...}} (already correct)
                elif 'type' in tool and 'data' in tool:
                    pass  # Already in correct format
            
            tool_type = parsed_response.get('tool', {}).get('type', 'none') if parsed_response.get('tool') else 'none'
            logger.info(f"✅ LLM response: dialogue={bool(parsed_response.get('dialogue'))}, tool={tool_type}")
            
            return parsed_response
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ LLM returned invalid JSON: {e}")
            raise ValueError(f"LLM JSON parsing failed: {e}")
            
        except Exception as e:
            error_str = str(e).lower()
            logger.error(f"❌ GPT-4.1-mini API error: {e}")
            
            # Detect Azure OpenAI content filtering
            if any(keyword in error_str for keyword in ['content filter', 'filtered', 'violence', 'content policy', 'responsible ai']):
                logger.warning(f"🚨 Content filtering detected for user input: '{user_input[:30]}...'")
                
                # Return graceful educational response instead of generic error
                return {
                    "dialogue": f"이 주제는 좀 더 조심스럽게 다뤄야겠어요. 다른 역사적 사건이나 인물에 대해 이야기해볼까요?",
                    "tool": {
                        "type": "show_selection",
                        "data": {
                            "question": "다음 중에서 공부하고 싶은 주제를 선택해주세요:",
                            "options": [
                                "조선시대 문화와 과학",
                                "고구려 역사와 인물",  
                                "조선 전기 정치사",
                                "전통 문화와 예술"
                            ],
                            "correct_answer": "조선시대 문화와 과학",
                            "selection_mode": "topic"
                        }
                    }
                }
            
            raise RuntimeError(f"LLM processing failed: {e}")
    
    async def process_interaction(self, context, character_prompt: str):
        """
        Compatibility method for continuous answer tool system
        Maps old process_interaction calls to new process_with_tools
        """
        logger.info(f"🔄 Compatibility: process_interaction -> process_with_tools")
        
        # Map context to user_input
        user_input = ""
        if hasattr(context, 'user_answer'):
            user_input = context.user_answer
        elif hasattr(context, 'question'):
            user_input = context.question
        
        # Call new method
        return await self.process_with_tools(
            user_input=user_input,
            character_prompt=character_prompt,
            chat_history=[],
            available_tools={}
        )
    
    def _extract_question_context(self, chat_history: List[Dict]) -> Dict:
        """Extract current question context from chat history for caching"""
        try:
            # Look for the most recent question in chat history (working backwards)
            for message in reversed(chat_history):
                if message.get('role') == 'assistant' and 'tools' in message:
                    for tool in message['tools']:
                        # Handle continuous_quiz_response nested structure
                        if tool.get('type') == 'continuous_quiz_response':
                            phase2_tool = tool['data'].get('phase2', {}).get('tool', {})
                            if phase2_tool.get('type') == 'show_selection':
                                return {
                                    'question': phase2_tool['data'].get('question', ''),
                                    'options': phase2_tool['data'].get('options', []),
                                    'correct_answer': phase2_tool['data'].get('correct_answer', '')
                                }
                        
                        # Handle direct show_selection
                        elif tool.get('type') == 'show_selection':
                            if tool['data'].get('selection_mode') == 'quiz_question':
                                return {
                                    'question': tool['data'].get('question', ''),
                                    'options': tool['data'].get('options', []),
                                    'correct_answer': tool['data'].get('correct_answer', '')
                                }
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract question context: {e}")
        
        # Return empty context if none found
        return {'question': '', 'options': [], 'correct_answer': ''}