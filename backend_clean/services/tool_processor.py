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
    
    def parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response JSON and return structured data with tools
        
        Args:
            response_text: JSON string from LLM
            
        Returns:
            Dictionary with parsed response including tools if present
        """
        try:
            # Parse JSON response
            result = json.loads(response_text.strip())
            
            # Return as-is for now (minimal implementation)
            return result
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in response: {e}")