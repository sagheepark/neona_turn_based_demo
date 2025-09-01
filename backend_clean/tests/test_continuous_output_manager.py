"""
Test suite for ContinuousOutputManager - handles multi-turn character responses
Following TDD methodology: Red -> Green -> Refactor
"""
import pytest
from services.continuous_output_manager import ContinuousOutputManager


class TestContinuousOutputManager:
    """Test Group 4: Continuous Output System"""
    
    def test_should_detect_continuation_tool(self):
        """
        Test 4.1: shouldDetectContinuationTool
        Red phase: This test should fail because ContinuousOutputManager doesn't exist yet
        """
        # Arrange
        response_data = {
            "character": "seol_min_seok",
            "dialogue": "정답입니다!",
            "emotion": "happy",
            "speed": 1.0,
            "tools": [
                {
                    "type": "continue_output",
                    "data": {
                        "reason": "quiz_continuation"
                    }
                }
            ]
        }
        
        # Act
        continuator = ContinuousOutputManager()
        should_continue = continuator.should_continue(response_data)
        
        # Assert
        assert should_continue == True
        
    def test_should_handle_response_without_continuation_tool(self):
        """
        Test 4.1b: Handle responses without continuation tools
        """
        # Arrange
        response_data = {
            "character": "seol_min_seok",
            "dialogue": "안녕하세요!",
            "emotion": "normal",
            "speed": 1.0,
            "tools": [
                {
                    "type": "show_selection",
                    "data": {
                        "items": ["Option 1", "Option 2"]
                    }
                }
            ]
        }
        
        # Act
        continuator = ContinuousOutputManager()
        should_continue = continuator.should_continue(response_data)
        
        # Assert
        assert should_continue == False
    
    def test_should_prevent_infinite_loops(self):
        """
        Test 4.2: shouldPreventInfiniteLoops  
        Red phase: This test should fail because we don't have loop prevention yet
        """
        # Arrange - response with continue_output tool but at continuation limit
        response_data = {
            "character": "seol_min_seok", 
            "dialogue": "다음 문제입니다!",
            "tools": [
                {
                    "type": "continue_output",
                    "data": {"reason": "quiz_continuation"}
                }
            ],
            # Context indicating we're at the limit
            "continuation_count": 3,  # At max limit
            "max_continuations": 3
        }
        
        # Act
        continuator = ContinuousOutputManager()
        should_continue = continuator.should_continue(response_data)
        
        # Assert - should prevent continuation despite continue_output tool
        assert should_continue == False