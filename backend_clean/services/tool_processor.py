"""
Tool Processor Service - Handles LLM response tool parsing
Minimal implementation following TDD principles
"""
import json
from typing import Dict, Any


class ValidationError(Exception):
    """Raised when tool data validation fails"""
    pass


class ToolProcessor:
    """Processes LLM responses and extracts tool information"""
    
    # Valid tool types
    VALID_TOOL_TYPES = [
        "show_selection",
        "continue_output", 
        "show_image"
    ]
    
    def parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response JSON and return structured data with tools
        
        Args:
            response_text: JSON string from LLM
            
        Returns:
            Dictionary with parsed response including tools if present
            
        Raises:
            ValidationError: If JSON is invalid or tool types are invalid
        """
        try:
            # Parse JSON response
            result = json.loads(response_text.strip())
            
            # Validate tools if present
            if "tools" in result and result["tools"]:
                self._validate_tools(result["tools"])
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in response: {e}")
    
    def _validate_tools(self, tools: list) -> None:
        """
        Validate tool data
        
        Args:
            tools: List of tool dictionaries
            
        Raises:
            ValidationError: If any tool has invalid type
        """
        for tool in tools:
            if "type" not in tool:
                raise ValidationError("Tool missing 'type' field")
            
            tool_type = tool["type"]
            if tool_type not in self.VALID_TOOL_TYPES:
                raise ValidationError(f"Invalid tool type: {tool_type}. Valid types: {self.VALID_TOOL_TYPES}")