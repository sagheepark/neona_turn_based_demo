"""
Test suite for Quiz Flow Integration - End-to-end quiz interaction testing
Following TDD methodology: Red -> Green -> Refactor
"""
import pytest
import asyncio


class TestQuizIntegration:
    """Test Group 8: Integration Tests"""
    
    def test_should_complete_quiz_flow_end_to_end(self):
        """
        Test 8.1: shouldCompleteQuizFlowEndToEnd
        Red phase: This test should fail because full integration doesn't exist yet
        """
        from main import app, InteractiveChatRequest
        from main import interactive_chat
        
        # 1. Start quiz
        start_request = InteractiveChatRequest(
            message="퀴즈를 시작해주세요",
            character_id="seol_min_seok",
            session_id="test_session_integration"
        )
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            start_response = loop.run_until_complete(interactive_chat(start_request))
            
            # Verify quiz started with tools
            assert isinstance(start_response, dict)
            assert len(start_response.get("tools", [])) > 0
            
            # Check for quiz structure
            tools = start_response.get("tools", [])
            show_selection_tool = next((tool for tool in tools if tool.get("type") == "show_selection"), None)
            assert show_selection_tool is not None
            assert "correctAnswer" in show_selection_tool.get("data", {})
            
            # 2. Answer question correctly (simulate selecting correct answer)
            correct_answer = show_selection_tool["data"]["correctAnswer"]
            answer_request = InteractiveChatRequest(
                message=correct_answer,
                character_id="seol_min_seok", 
                session_id="test_session_integration"
            )
            
            answer_response = loop.run_until_complete(interactive_chat(answer_request))
            
            # 3. Verify continuation happens or positive feedback
            assert isinstance(answer_response, dict)
            assert "dialogue" in answer_response
            
            # Should have either continuation tool or positive dialogue
            answer_tools = answer_response.get("tools", [])
            has_continuation = any(tool.get("type") == "continue_output" for tool in answer_tools)
            has_positive_feedback = "정답" in answer_response.get("dialogue", "")
            
            assert has_continuation or has_positive_feedback
            
        finally:
            loop.close()