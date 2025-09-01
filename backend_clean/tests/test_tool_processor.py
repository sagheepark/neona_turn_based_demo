"""
Test suite for ToolProcessor - handles LLM response tool parsing
Following TDD methodology: Red -> Green -> Refactor
"""
import pytest
import json
from services.tool_processor import ToolProcessor, ValidationError


class TestToolProcessor:
    """Test Group 1: Basic Tool System Foundation"""
    
    def test_should_parse_basic_tool_from_llm_response(self):
        """
        Test 1.1: shouldParseBasicToolFromLLMResponse
        Red phase: This test should fail because ToolProcessor doesn't exist yet
        """
        # Arrange
        response_text = '''
        {
            "character": "test_char",
            "dialogue": "Choose an option",
            "emotion": "normal",
            "speed": 1.0,
            "tools": [
                {
                    "type": "show_selection",
                    "data": {
                        "items": ["Option 1", "Option 2"],
                        "mode": "chip"
                    }
                }
            ]
        }
        '''
        
        # Act
        processor = ToolProcessor()
        result = processor.parse_llm_response(response_text)
        
        # Assert
        assert result["tools"] is not None
        assert len(result["tools"]) == 1
        assert result["tools"][0]["type"] == "show_selection"
        assert result["tools"][0]["data"]["items"] == ["Option 1", "Option 2"]
        assert result["tools"][0]["data"]["mode"] == "chip"