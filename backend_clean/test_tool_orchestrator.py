#!/usr/bin/env python3
"""
Test Group 1: Core Tool Detection
Testing tool parsing from LLM responses following TDD methodology
"""

import pytest
import json
from services.tool_orchestrator import ToolOrchestrator


class TestToolOrchestrator:
    """Test suite for tool detection and parsing system"""

    def test_should_parse_tool_from_llm_response(self):
        """
        Test 1.1: shouldParseToolFromLLMResponse
        RED phase: This test should fail because ToolOrchestrator doesn't exist yet
        """
        # Arrange
        response_text = '''
        {
            "character": "seol_min_seok_quiz",
            "dialogue": "좋습니다! 퀴즈를 시작해볼까요?",
            "emotion": "enthusiastic",
            "speed": 1.0,
            "tool": "quiz",
            "tool_data": {
                "type": "greeting_suggestion"
            }
        }
        '''
        orchestrator = ToolOrchestrator()
        
        # Act
        result = orchestrator.parse_llm_response(response_text)
        
        # Assert
        assert result["tool"] == "quiz"
        assert result["dialogue"] == "좋습니다! 퀴즈를 시작해볼까요?"
        assert result["tool_data"]["type"] == "greeting_suggestion"
        assert result["character"] == "seol_min_seok_quiz"
        assert result["emotion"] == "enthusiastic"

    def test_should_handle_response_without_tools(self):
        """
        Test 1.2: shouldHandleResponseWithoutTools
        RED phase: Test normal responses without tool fields
        """
        # Arrange
        response_text = '''
        {
            "character": "seol_min_seok_quiz",
            "dialogue": "안녕하세요!",
            "emotion": "friendly",
            "speed": 1.0
        }
        '''
        orchestrator = ToolOrchestrator()
        
        # Act
        result = orchestrator.parse_llm_response(response_text)
        
        # Assert
        assert result.get("tool") is None
        assert result["dialogue"] == "안녕하세요!"
        assert result["character"] == "seol_min_seok_quiz"
        assert result["emotion"] == "friendly"

    def test_should_handle_invalid_json_response(self):
        """
        Test 1.3: shouldHandleInvalidJSONResponse
        RED phase: Test error handling for malformed JSON
        """
        # Arrange
        response_text = "This is not valid JSON"
        orchestrator = ToolOrchestrator()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid JSON in LLM response"):
            orchestrator.parse_llm_response(response_text)

    def test_should_validate_required_fields(self):
        """
        Test 1.4: shouldValidateRequiredFields
        RED phase: Test validation of required response fields
        """
        # Arrange
        response_text = '''
        {
            "tool": "quiz",
            "tool_data": {"type": "greeting"}
        }
        '''
        orchestrator = ToolOrchestrator()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Missing required fields"):
            orchestrator.parse_llm_response(response_text)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])