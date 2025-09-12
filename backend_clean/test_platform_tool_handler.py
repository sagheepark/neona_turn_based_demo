#!/usr/bin/env python3
"""
Test Group 2: Platform Tool Handlers
Testing platform handlers for tool execution following TDD methodology
"""

import pytest
import asyncio
from services.platform_tool_handler import PlatformToolHandler


class TestPlatformToolHandler:
    """Test suite for platform tool execution system"""

    def test_should_execute_quiz_tool(self):
        """
        Test 2.1: shouldExecuteQuizTool
        RED phase: This test should fail because PlatformToolHandler doesn't exist yet
        """
        # Arrange
        handler = PlatformToolHandler()
        tool_data = {
            "type": "topic_selection",
            "items": ["조선시대", "근현대사"]
        }
        
        # Act
        result = handler.handle_quiz_tool(tool_data)
        
        # Assert
        assert result["ui_type"] == "selection"
        assert len(result["options"]) == 2
        assert "조선시대" in result["options"]
        assert "근현대사" in result["options"]

    @pytest.mark.asyncio
    async def test_should_execute_continuous_tool(self):
        """
        Test 2.2: shouldExecuteContinuousTool
        RED phase: Test continuous flow orchestration
        """
        # Arrange
        handler = PlatformToolHandler()
        session_id = "test_session_123"
        
        # Act
        result = await handler.handle_continuous_tool(session_id)
        
        # Assert
        assert result["next_response"] is not None
        assert result["conversation_continued"] == True
        assert result["session_id"] == session_id

    def test_should_execute_show_selection_tool(self):
        """
        Test 2.3: shouldExecuteShowSelectionTool
        RED phase: Test show_selection tool handler
        """
        # Arrange
        handler = PlatformToolHandler()
        tool_data = {
            "type": "quiz_question",
            "question": "다음 중 세종대왕의 업적은?",
            "items": ["한글 창제", "불교 장려", "몽골 침입", "일제강점"],
            "correct_answer": "한글 창제"
        }
        
        # Act
        result = handler.handle_show_selection_tool(tool_data)
        
        # Assert
        assert result["ui_type"] == "quiz"
        assert result["question"] == "다음 중 세종대왕의 업적은?"
        assert len(result["options"]) == 4
        assert result["correct_answer"] == "한글 창제"

    def test_should_handle_unknown_tool_type(self):
        """
        Test 2.4: shouldHandleUnknownToolType
        RED phase: Test error handling for unsupported tools
        """
        # Arrange
        handler = PlatformToolHandler()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported tool type"):
            handler.execute_tool("unknown_tool", {})

    def test_should_validate_tool_data(self):
        """
        Test 2.5: shouldValidateToolData
        RED phase: Test validation of tool-specific data
        """
        # Arrange
        handler = PlatformToolHandler()
        invalid_data = {}  # Missing required fields
        
        # Act & Assert
        with pytest.raises(ValueError, match="Missing required data"):
            handler.handle_quiz_tool(invalid_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])