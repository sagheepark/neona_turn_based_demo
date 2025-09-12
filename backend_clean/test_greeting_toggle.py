#!/usr/bin/env python3
"""
Test 12.2: shouldRespectToggleInBackend
RED phase: Backend should respect per-character greeting suggestions toggle
Purpose: Ensure backend only shows greeting suggestions when enabled for character
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from services.greeting_suggestion_generator import GreetingSuggestionGenerator


class TestGreetingToggleBackend:
    """Test that backend respects per-character greeting suggestions toggle"""
    
    def test_should_respect_greeting_suggestions_enabled_flag(self):
        """
        Backend should only generate suggestions when character has 
        greeting_suggestions_enabled = True
        """
        # Arrange
        generator = GreetingSuggestionGenerator()
        
        # Character with greeting suggestions disabled
        character_disabled = {
            "id": "test_char_1",
            "name": "Test Character",
            "greeting_suggestions_enabled": False,
            "greetings": ["Hello!"]
        }
        
        # Character with greeting suggestions enabled
        character_enabled = {
            "id": "test_char_2", 
            "name": "Test Character 2",
            "greeting_suggestions_enabled": True,
            "greetings": ["Hi there!"]
        }
        
        # Act
        suggestions_disabled = generator.generate_for_character(character_disabled)
        suggestions_enabled = generator.generate_for_character(character_enabled)
        
        # Assert
        assert suggestions_disabled is None or suggestions_disabled == [], \
            "Should not generate suggestions when disabled"
        assert suggestions_enabled is not None and len(suggestions_enabled) > 0, \
            "Should generate suggestions when enabled"
    
    def test_should_default_to_disabled_when_flag_missing(self):
        """
        When greeting_suggestions_enabled is not present,
        should default to disabled (no suggestions)
        """
        # Arrange
        generator = GreetingSuggestionGenerator()
        
        # Character without the flag
        character_no_flag = {
            "id": "test_char_3",
            "name": "Legacy Character",
            "greetings": ["Welcome!"]
            # Note: no greeting_suggestions_enabled field
        }
        
        # Act
        suggestions = generator.generate_for_character(character_no_flag)
        
        # Assert
        assert suggestions is None or suggestions == [], \
            "Should default to disabled when flag is missing"
    
    def test_generator_handles_edge_cases(self):
        """
        Test edge cases like None values and missing fields
        """
        generator = GreetingSuggestionGenerator()
        
        # Test with None character
        suggestions_none = generator.generate_for_character({})
        assert suggestions_none == [], "Should handle empty character dict"
        
        # Test with character that explicitly sets False
        char_explicit_false = {
            "id": "test_char",
            "greeting_suggestions_enabled": False
        }
        suggestions_false = generator.generate_for_character(char_explicit_false)
        assert suggestions_false == [], "Should respect explicit False setting"
        
        # Test with character that explicitly sets True
        char_explicit_true = {
            "id": "test_char",
            "greeting_suggestions_enabled": True,
            "greetings": ["Hello!"]
        }
        suggestions_true = generator.generate_for_character(char_explicit_true)
        assert len(suggestions_true) > 0, "Should generate suggestions when explicitly enabled"


if __name__ == "__main__":
    # Run the tests
    test_instance = TestGreetingToggleBackend()
    
    try:
        print("🔴 Running Test 12.2: shouldRespectToggleInBackend")
        print("-" * 50)
        
        # Test 1: Respect enabled flag
        test_instance.test_should_respect_greeting_suggestions_enabled_flag()
        print("✅ Test 1 passed: Respects greeting_suggestions_enabled flag")
        
        # Test 2: Default to disabled
        test_instance.test_should_default_to_disabled_when_flag_missing()
        print("✅ Test 2 passed: Defaults to disabled when flag missing")
        
        # Test 3: Edge cases
        test_instance.test_generator_handles_edge_cases()
        print("✅ Test 3 passed: Generator handles edge cases")
        
        print("-" * 50)
        print("🟢 All tests passed!")
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        print("This is expected in RED phase - backend doesn't respect toggle yet")