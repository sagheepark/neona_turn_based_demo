"""
Test suite for Interactive Chat API - handles tool-based chat endpoints
Following TDD methodology: Red -> Green -> Refactor
"""
import pytest
import asyncio
import json


class TestInteractiveChatAPI:
    """Test Group 6: Backend API Integration"""
    
    def test_should_create_interactive_chat_endpoint(self):
        """
        Test 6.1: shouldCreateInteractiveChatEndpoint
        Tests that the interactive chat endpoint exists and returns expected response structure
        """
        from main import app, InteractiveChatRequest
        
        # Simulate calling the endpoint directly
        request_data = InteractiveChatRequest(
            message="퀴즈를 시작해주세요",
            character_id="seol_min_seok",
            session_id="test_session"
        )
        
        # Check that we can import and call the function
        from main import interactive_chat
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(interactive_chat(request_data))
            
            # Assert response structure
            assert isinstance(response, dict)
            assert "tools" in response or "dialogue" in response
            assert "character" in response
            
            # Check for expected content  
            if "tools" in response:
                tools = response["tools"]
                assert isinstance(tools, list)
                assert len(tools) > 0
            
            if "dialogue" in response:
                assert isinstance(response["dialogue"], str)
                assert len(response["dialogue"]) > 0
                
        finally:
            loop.close()
        
    def test_should_handle_continuation_request(self):
        """
        Test 6.2: shouldHandleContinuationRequest
        Tests that the continuation endpoint exists and returns expected response
        """
        from main import app, ContinuationRequest
        
        # Simulate calling the endpoint directly
        request_data = ContinuationRequest(
            session_id="test_session",
            context={
                "last_response": "정답입니다!",
                "continuation_type": "quiz"
            }
        )
        
        # Check that we can import and call the function
        from main import handle_continuation
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(handle_continuation(request_data))
            
            # Assert response structure
            assert isinstance(response, dict)
            assert "dialogue" in response
            assert "character" in response
            assert isinstance(response["dialogue"], str)
            assert len(response["dialogue"]) > 0
            
        finally:
            loop.close()