"""
Simple test suite for temperature feature - focusing on core functionality
Following TDD approach: RED → GREEN → REFACTOR
"""

import pytest
from unittest.mock import patch, Mock
from main import generate_ai_response, generate_enhanced_ai_response


@patch('main.azure_client')
def test_llm_uses_character_temperature(mock_azure_client):
    """Test 3: LLM calls use character-specific temperature"""
    # Setup mock
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"character": "Test", "dialogue": "Hello", "emotion": "happy", "speed": 1.0}'
    mock_azure_client.chat.completions.create.return_value = mock_response
    
    import asyncio
    
    # Call with specific temperature
    response = asyncio.run(generate_ai_response(
        character_prompt="<character>Test</character>",
        history=[],
        user_message="Hello",
        character_temperature=0.9  # Pass temperature parameter
    ))
    
    # Verify the LLM was called with correct temperature
    mock_azure_client.chat.completions.create.assert_called()
    call_args = mock_azure_client.chat.completions.create.call_args
    
    assert 'temperature' in call_args.kwargs, "Temperature should be passed to LLM"
    assert call_args.kwargs['temperature'] == 0.9, "Should use character-specific temperature"


@patch('main.azure_client')
def test_enhanced_ai_response_uses_temperature(mock_azure_client):
    """Test 5: Enhanced AI response function also uses temperature"""
    # Setup mock
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"character": "Test", "dialogue": "Hello", "emotion": "happy", "speed": 1.0}'
    mock_azure_client.chat.completions.create.return_value = mock_response
    
    import asyncio
    
    # Create AI context with temperature
    ai_context = {
        "character_temperature": 0.85,
        "knowledge": [],
        "memory": {}
    }
    
    # Call enhanced function
    response = asyncio.run(generate_enhanced_ai_response(
        character_prompt="<character>Test</character>",
        ai_context=ai_context,
        user_message="Hello"
    ))
    
    # Verify temperature was used
    call_args = mock_azure_client.chat.completions.create.call_args
    assert call_args.kwargs.get('temperature') == 0.85, "Enhanced function should use temperature from context"


@patch('main.azure_client')
def test_default_temperature_used_when_none_provided(mock_azure_client):
    """Test: Default temperature (0.7) is used when none provided"""
    # Setup mock
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"character": "Test", "dialogue": "Hello", "emotion": "happy", "speed": 1.0}'
    mock_azure_client.chat.completions.create.return_value = mock_response
    
    import asyncio
    
    # Call without temperature parameter
    response = asyncio.run(generate_ai_response(
        character_prompt="<character>Test</character>",
        history=[],
        user_message="Hello"
        # No temperature parameter
    ))
    
    # Verify default temperature was used
    call_args = mock_azure_client.chat.completions.create.call_args
    assert call_args.kwargs.get('temperature') == 0.7, "Should use default temperature of 0.7"


def test_temperature_validation():
    """Test: Temperature validation in character service"""
    from services.character_service import CharacterService
    from services.database_service import DatabaseService
    
    # Mock database service
    mock_db = Mock()
    char_service = CharacterService(mock_db)
    
    import asyncio
    
    # Test invalid low temperature
    with pytest.raises(ValueError, match="Temperature must be between 0.0 and 1.0"):
        character_data = {
            "character_id": "test_invalid_low",
            "name": "Invalid Low",
            "temperature": -0.1
        }
        # This should raise an error during validation
        try:
            asyncio.run(char_service.create_character(character_data))
        except Exception as e:
            if "Temperature must be between 0.0 and 1.0" in str(e):
                raise ValueError("Temperature must be between 0.0 and 1.0")
            raise
    
    # Test invalid high temperature
    with pytest.raises(ValueError, match="Temperature must be between 0.0 and 1.0"):
        character_data = {
            "character_id": "test_invalid_high", 
            "name": "Invalid High",
            "temperature": 1.1
        }
        # This should raise an error during validation
        try:
            asyncio.run(char_service.create_character(character_data))
        except Exception as e:
            if "Temperature must be between 0.0 and 1.0" in str(e):
                raise ValueError("Temperature must be between 0.0 and 1.0")
            raise


if __name__ == "__main__":
    print("Running temperature feature tests (simple version)...")
    pytest.main([__file__, "-v"])