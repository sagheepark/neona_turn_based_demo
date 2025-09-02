"""
Test suite for Quiz-Focused Character - implementation of quiz-focused 설민석 character
Following TDD methodology: Red -> Green -> Refactor
"""
import pytest
import asyncio


class TestQuizCharacter:
    """Test Group 10: Quiz-Focused Character Implementation"""
    
    def test_should_create_quiz_focused_character(self):
        """
        Test 10.1: shouldCreateQuizFocusedCharacter
        Red phase: This test should fail because quiz character doesn't exist yet
        """
        # Arrange & Act - Test via API endpoint that character exists and responds appropriately
        from main import interactive_chat, InteractiveChatRequest
        
        # Test that seol_min_seok_quiz character returns greeting suggestions 
        request = InteractiveChatRequest(
            message="안녕하세요",
            character_id="seol_min_seok_quiz",
            session_id="character_test"
        )
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(interactive_chat(request))
            
            # Assert character exists and has quiz-focused greeting with suggestions
            assert response["character"] == "seol_min_seok_quiz"
            assert "퀴즈" in response["dialogue"]
            assert "tools" in response
            tools = response["tools"]
            assert any(tool.get("type") == "show_selection" for tool in tools)
            
            # Check that suggestions are quiz-focused
            show_selection_tool = next((tool for tool in tools if tool.get("type") == "show_selection"), None)
            assert show_selection_tool is not None
            items = show_selection_tool["data"]["items"]
            assert any("퀴즈" in item for item in items)
            
        finally:
            loop.close()
    
    def test_should_lead_quiz_session_from_greeting(self):
        """
        Test 10.2: shouldLeadQuizSessionFromGreeting
        Red phase: This test verifies quiz character can lead sessions from first interaction
        """
        # Arrange
        from main import interactive_chat, InteractiveChatRequest
        
        # Initial greeting to quiz character
        greeting_request = InteractiveChatRequest(
            message="안녕하세요",
            character_id="seol_min_seok_quiz", 
            session_id="quiz_session_test"
        )
        
        # Act
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            greeting_response = loop.run_until_complete(interactive_chat(greeting_request))
            
            # Simulate user selecting quiz suggestion
            quiz_request = InteractiveChatRequest(
                message="조선시대 퀴즈",  # User selects from greeting suggestions
                character_id="seol_min_seok_quiz",
                session_id="quiz_session_test"
            )
            
            quiz_response = loop.run_until_complete(interactive_chat(quiz_request))
            
            # Assert
            # Greeting should have suggestions
            assert "tools" in greeting_response
            greeting_tools = greeting_response["tools"]
            assert any(tool.get("type") == "show_selection" for tool in greeting_tools)
            
            # Quiz response should have quiz questions
            assert "tools" in quiz_response  
            quiz_tools = quiz_response["tools"]
            quiz_tool = next((tool for tool in quiz_tools if tool.get("type") == "show_selection"), None)
            assert quiz_tool is not None
            assert "correctAnswer" in quiz_tool["data"]
            
        finally:
            loop.close()