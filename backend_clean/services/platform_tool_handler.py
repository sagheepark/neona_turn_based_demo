"""
Platform Tool Handler - Central tool management for LLM-driven platform

This module defines all available tools that LLM agents can use based on prompts.
NO HARDCODED LOGIC - only tool definitions and execution handlers.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ToolDefinition:
    """Definition of a tool available to LLM agents"""
    name: str
    description: str
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for LLM prompt injection"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

class PlatformToolHandler:
    """
    Central tool handler that LLM uses based on prompts
    NO HARDCODED LOGIC - only tool execution
    """
    
    def __init__(self, tts_service=None):
        self.tools = self._initialize_tools()
        self.tts_service = tts_service
        logger.info(f"✅ Platform Tool Handler initialized with {len(self.tools)} tools")
    
    def _initialize_tools(self) -> Dict[str, ToolDefinition]:
        """Initialize all available tools with their definitions"""
        tools = {}
        
        # Tool 1: show_selection - for topic selection and single quiz questions
        tools["show_selection"] = ToolDefinition(
            name="show_selection",
            description="Display options for user to select (for topics or quiz questions)",
            parameters={
                "question": "string - The question or prompt to display",
                "options": "array[string] - List of options to choose from",
                "correct_answer": "string (optional) - For quiz questions only",
                "selection_mode": "string - Either 'topic' or 'quiz_question'"
            }
        )
        
        # Tool 2: continuous_quiz_response - for two-phase quiz feedback + next question
        tools["continuous_quiz_response"] = ToolDefinition(
            name="continuous_quiz_response",
            description="Two-phase response for quiz: review answer then present next question",
            parameters={
                "phase1": {
                    "text": "string - Review/feedback about the user's answer",
                    "delay_ms": "number - Delay before phase2 (default: 3000)"
                },
                "phase2": {
                    "text": "string - Introduction to next question",
                    "tool": "object - show_selection tool with quiz question"
                }
            }
        )
        
        return tools
    
    def get_tool_definitions_for_llm(self, character_type: Optional[str] = None) -> str:
        """
        Get tool definitions formatted for LLM prompt
        
        Args:
            character_type: Optional filter for character-specific tools
            
        Returns:
            Formatted string describing available tools
        """
        tool_descriptions = []
        
        for tool_name, tool_def in self.tools.items():
            # In future, filter by character_type if needed
            tool_descriptions.append(f"""
Tool: {tool_def.name}
Purpose: {tool_def.description}
Parameters: {json.dumps(tool_def.parameters, indent=2)}
""")
        
        return "\n".join(tool_descriptions)
    
    def get_tool_definitions_json(self) -> Dict[str, Any]:
        """Get tool definitions as JSON for structured prompts"""
        return {
            name: tool.to_dict() 
            for name, tool in self.tools.items()
        }
    
    async def execute_tool(self, tool_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool based on LLM response
        
        Args:
            tool_type: Name of the tool to execute
            data: Parameters for the tool
            
        Returns:
            Tool execution result formatted for frontend
        """
        if tool_type not in self.tools:
            logger.error(f"❌ Unknown tool requested: {tool_type}")
            raise ValueError(f"Unknown tool: {tool_type}")
        
        logger.info(f"🔧 Executing tool: {tool_type}")
        
        # Format tool response for frontend
        if tool_type == "show_selection":
            return await self._execute_show_selection(data)
        
        elif tool_type == "continuous_quiz_response":
            return await self._execute_continuous_quiz_response(data)
        
        return {
            "type": tool_type,
            "data": data
        }
    
    async def _execute_show_selection(self, data: Dict) -> Dict:
        """Execute show_selection tool - returns data as-is since frontend handles UI"""
        required_fields = ["question", "options", "selection_mode"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field for show_selection: {field}")
        
        # Validate selection_mode
        valid_modes = ["topic", "quiz_question"]
        if data["selection_mode"] not in valid_modes:
            raise ValueError(f"Invalid selection_mode: {data['selection_mode']}")
        
        logger.info(f"Show selection: {data['selection_mode']} with {len(data['options'])} options")
        
        return {
            "type": "show_selection",
            "data": data
        }
    
    async def _execute_continuous_quiz_response(self, data: Dict) -> Dict:
        """
        Execute continuous_quiz_response tool
        Generates TTS for both phases and validates structure
        """
        # Validate structure
        if "phase1" not in data or "phase2" not in data:
            raise ValueError("continuous_quiz_response must have phase1 and phase2")
        
        phase1 = data["phase1"]
        phase2 = data["phase2"]
        
        # Validate phase1 structure
        if "text" not in phase1:
            raise ValueError("Phase1 must have 'text' field")
        
        # Validate phase2 structure  
        if "text" not in phase2 or "tool" not in phase2:
            raise ValueError("Phase2 must have 'text' and 'tool' fields")
        
        # Validate phase2 tool is show_selection
        phase2_tool = phase2["tool"]
        if phase2_tool.get("type") != "show_selection":
            raise ValueError("Phase2 tool must be show_selection type")
        
        # Build result with proper structure
        result_data = {
            "phase1": {
                "text": phase1["text"],
                "delay_ms": phase1.get("delay_ms", 3000)
            },
            "phase2": {
                "text": phase2["text"],
                "tool": phase2_tool
            }
        }
        
        # Generate TTS for both phases if service available
        if self.tts_service:
            try:
                # Generate TTS for phase1
                phase1_audio = await self.tts_service.generate_speech(
                    phase1["text"], 
                    character_id="seolminseok_korean_history_chat"
                )
                result_data["phase1"]["audio_url"] = phase1_audio
                
                # Generate TTS for phase2
                phase2_audio = await self.tts_service.generate_speech(
                    phase2["text"],
                    character_id="seolminseok_korean_history_chat"
                )
                result_data["phase2"]["audio_url"] = phase2_audio
                
                logger.info("Generated TTS for both phases of continuous quiz response")
                
            except Exception as e:
                logger.warning(f"TTS generation failed: {e}")
                # Continue without audio
        
        logger.info("Continuous quiz response prepared with review and next question")
        
        return {
            "type": "continuous_quiz_response",
            "data": result_data
        }
    
    def validate_tool_response(self, tool_name: str, tool_data: Dict) -> bool:
        """
        Validate that tool data matches expected format
        
        Args:
            tool_name: Name of the tool
            tool_data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if tool_name not in self.tools:
            return False
        
        # Basic validation - in production, use jsonschema
        if tool_name == "show_selection":
            required = ["question", "options", "selection_mode"]
            return all(key in tool_data for key in required)
        
        elif tool_name == "continuous_quiz_response":
            if "phase1" not in tool_data or "phase2" not in tool_data:
                return False
            if "text" not in tool_data["phase1"]:
                return False
            if "text" not in tool_data["phase2"] or "tool" not in tool_data["phase2"]:
                return False
            return True
        
        return False