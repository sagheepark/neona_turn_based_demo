"""
Test suite for Greeting Suggestions System - handles contextual greeting suggestions
Following TDD methodology: Red -> Green -> Refactor
"""
import pytest
from services.greeting_suggestion_generator import GreetingSuggestionGenerator


class TestGreetingSuggestions:
    """Test Group 9: Contextual Greeting Suggestions System"""
    
    def test_should_generate_contextual_greeting_suggestions(self):
        """
        Test 9.1: shouldGenerateContextualGreetingSuggestions
        Red phase: This test should fail because GreetingSuggestionGenerator doesn't exist yet
        """
        # Arrange
        generator = GreetingSuggestionGenerator()
        greeting_context = {
            "character_id": "seol_min_seok_quiz",
            "greeting_message": "안녕하세요! 한국사 퀴즈를 함께 풀어볼까요?",
            "character_personality": "교육적이고 친근한 역사 튜터",
            "suggestions_enabled": True
        }
        
        # Act
        suggestions = generator.generate_greeting_suggestions(greeting_context)
        
        # Assert
        assert len(suggestions) >= 3
        assert "조선시대 퀴즈" in suggestions
        assert "근현대사 문제" in suggestions
        assert any("난이도" in suggestion for suggestion in suggestions)
    
    def test_should_respect_character_suggestion_settings(self):
        """
        Test 9.2: shouldRespectCharacterSuggestionSettings
        Red phase: This test checks if per-character on/off settings are respected
        """
        # Arrange
        generator = GreetingSuggestionGenerator()
        
        enabled_context = {
            "character_id": "seol_min_seok_quiz", 
            "greeting_message": "안녕하세요!",
            "suggestions_enabled": True
        }
        
        disabled_context = {
            "character_id": "regular_character",
            "greeting_message": "안녕하세요!",
            "suggestions_enabled": False
        }
        
        # Act
        enabled_suggestions = generator.generate_greeting_suggestions(enabled_context)
        disabled_suggestions = generator.generate_greeting_suggestions(disabled_context)
        
        # Assert
        assert len(enabled_suggestions) > 0
        assert len(disabled_suggestions) == 0
    
    def test_should_integrate_with_tool_calling_system(self):
        """
        Test 9.3: shouldIntegrateWithToolCallingSystem
        Red phase: This test verifies greeting suggestions work with existing tool system
        """
        import asyncio
        # Arrange
        from main import interactive_chat, InteractiveChatRequest
        
        request = InteractiveChatRequest(
            message="안녕하세요",  # Initial greeting trigger
            character_id="seol_min_seok_quiz",
            session_id="greeting_test_session"
        )
        
        # Act
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(interactive_chat(request))
            
            # Assert
            assert "tools" in response
            tools = response["tools"]
            show_selection_tool = next((tool for tool in tools if tool.get("type") == "show_selection"), None)
            assert show_selection_tool is not None
            assert "items" in show_selection_tool["data"]
            assert len(show_selection_tool["data"]["items"]) >= 3
            
        finally:
            loop.close()