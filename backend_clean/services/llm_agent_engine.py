"""
LLM Agent Engine - Core LLM processing with tool understanding

This engine processes user interactions using LLM intelligence based on
character prompts and available tools. NO FALLBACK METHODS - must work with real LLM.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

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
        """Initialize with Azure OpenAI client"""
        if not azure_client:
            try:
                from openai import AsyncAzureOpenAI
                import os
                
                # Initialize Azure OpenAI client
                self.azure_client = AsyncAzureOpenAI(
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    api_version="2024-02-15-preview", 
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                )
                logger.info("✅ LLMAgentEngine initialized with Azure OpenAI")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Azure OpenAI: {e}")
                raise RuntimeError("Cannot initialize LLM Agent without Azure OpenAI")
        else:
            self.azure_client = azure_client
    
    async def process_with_tools(self, 
                                 user_input: str,
                                 character_prompt: str,
                                 chat_history: List[Dict],
                                 available_tools: Dict) -> Dict:
        """
        Process user input using LLM with tool understanding
        
        Args:
            user_input: User's message or selection
            character_prompt: Character behavior instructions
            chat_history: Previous conversation context
            available_tools: Dictionary of available tools
            
        Returns:
            Dictionary with dialogue and tool (if specified)
        """
        
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

IMPORTANT TOOL USAGE:
- When user answers quiz: Use 'continuous_quiz_response' tool
- Phase1: Review their answer (correct/wrong feedback)  
- Phase2: Present next question with show_selection tool
- For topic selection: Use 'show_selection' tool
- For initial greeting: Use 'show_selection' tool to offer topics

RESPONSE GUIDELINES:
- Always be in character as defined above
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
        
        logger.info(f"🧠 Processing with Azure GPT-4o: user_input='{user_input[:50]}...'")
        
        try:
            # Call Azure GPT-4o with JSON mode
            response = await self.azure_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse JSON response
            response_content = response.choices[0].message.content
            logger.info(f"🔍 Raw LLM response: {response_content}")
            
            parsed_response = json.loads(response_content)
            logger.info(f"🔍 Parsed LLM response: {parsed_response}")
            
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
            logger.error(f"❌ Azure OpenAI API error: {e}")
            raise RuntimeError(f"LLM processing failed: {e}")