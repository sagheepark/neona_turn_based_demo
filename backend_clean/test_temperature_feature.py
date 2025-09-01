"""
Test suite for character-specific temperature settings
Following TDD approach: RED → GREEN → REFACTOR
"""

import pytest
import asyncio
from unittest.mock import patch, Mock, MagicMock
from services.character_service import CharacterService
from services.database_service import DatabaseService
from main import generate_ai_response, generate_enhanced_ai_response

# Initialize services
database_service = None
character_service = None

@pytest.fixture
async def setup_services():
    """Setup test services with database connection"""
    global database_service, character_service
    database_service = DatabaseService()
    character_service = CharacterService(database_service)
    await database_service.connect()
    yield database_service, character_service
    await database_service.disconnect()

@pytest.mark.asyncio
async def test_character_has_temperature_field(setup_services):
    """Test 1: Character schema includes temperature field"""
    db_service, char_service = await setup_services.__anext__()
    
    # Create a test character with temperature
    character_data = {
        "character_id": "test_temp_char",
        "name": "Temperature Test Character",
        "prompt": "<character>Test Character</character>",
        "greetings": ["Hello!"],
        "voice_id": "test_voice",
        "temperature": 0.8  # This is what we're testing
    }
    
    # Save character
    await char_service.create_character(character_data)
    
    # Retrieve character
    character = await char_service.get_character("test_temp_char")
    
    # Assert temperature field exists and is valid
    assert "temperature" in character, "Character should have temperature field"
    assert character["temperature"] == 0.8, "Temperature should be 0.8"
    assert 0.0 <= character["temperature"] <= 1.0, "Temperature should be between 0 and 1"
    
    # Cleanup
    await char_service.delete_character("test_temp_char")

def test_temperature_persists_in_database():
    """Test 2: Temperature is saved and retrieved correctly from database"""
    character_data = {
        "character_id": "test_persist_char",
        "name": "Persistence Test Character",
        "prompt": "<character>Persistent</character>",
        "greetings": ["Hi there!"],
        "voice_id": "test_voice_2",
        "temperature": 0.6
    }
    
    # Create character
    asyncio.run(character_service.create_character(character_data))
    
    # Retrieve from database (not cache)
    character_service._invalidate_cache()  # Clear any cache
    retrieved = asyncio.run(character_service.get_character("test_persist_char"))
    
    assert retrieved["temperature"] == 0.6, "Temperature should persist in database"
    
    # Update temperature
    asyncio.run(character_service.update_character("test_persist_char", {"temperature": 0.9}))
    
    # Retrieve again
    character_service._invalidate_cache()
    updated = asyncio.run(character_service.get_character("test_persist_char"))
    
    assert updated["temperature"] == 0.9, "Updated temperature should persist"
    
    # Cleanup
    asyncio.run(character_service.delete_character("test_persist_char"))

@patch('main.azure_client')
def test_llm_uses_character_temperature(mock_azure_client):
    """Test 3: LLM calls use character-specific temperature"""
    # Setup mock
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"character": "Test", "dialogue": "Hello", "emotion": "happy", "speed": 1.0}'
    mock_azure_client.chat.completions.create.return_value = mock_response
    
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

def test_default_temperature_when_not_specified():
    """Test 4: Default temperature (0.7) is used when not specified"""
    character_data = {
        "character_id": "test_no_temp_char",
        "name": "No Temperature Character",
        "prompt": "<character>Default</character>",
        "greetings": ["Hey!"],
        "voice_id": "test_voice_3"
        # Note: No temperature field
    }
    
    # Create character without temperature
    asyncio.run(character_service.create_character(character_data))
    
    # Retrieve character
    character = asyncio.run(character_service.get_character("test_no_temp_char"))
    
    # Should have default temperature
    temperature = character.get("temperature", 0.7)
    assert temperature == 0.7, "Should use default temperature of 0.7"
    
    # Cleanup
    asyncio.run(character_service.delete_character("test_no_temp_char"))

@patch('main.azure_client')
def test_enhanced_ai_response_uses_temperature(mock_azure_client):
    """Test 5: Enhanced AI response function also uses temperature"""
    # Setup mock
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"character": "Test", "dialogue": "Hello", "emotion": "happy", "speed": 1.0}'
    mock_azure_client.chat.completions.create.return_value = mock_response
    
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

def test_temperature_validation():
    """Test 6: Temperature values are validated (0.0 to 1.0)"""
    # Test invalid low temperature
    with pytest.raises(ValueError, match="Temperature must be between 0.0 and 1.0"):
        character_data = {
            "character_id": "test_invalid_low",
            "name": "Invalid Low",
            "temperature": -0.1
        }
        asyncio.run(character_service.create_character(character_data))
    
    # Test invalid high temperature
    with pytest.raises(ValueError, match="Temperature must be between 0.0 and 1.0"):
        character_data = {
            "character_id": "test_invalid_high",
            "name": "Invalid High",
            "temperature": 1.1
        }
        asyncio.run(character_service.create_character(character_data))

def test_existing_characters_get_default_temperature():
    """Test 7: Existing characters without temperature get default value"""
    # Simulate an existing character without temperature field
    old_character_data = {
        "character_id": "old_character",
        "name": "Old Character",
        "prompt": "<character>Old</character>",
        "greetings": ["Greetings!"],
        "voice_id": "old_voice"
    }
    
    # Directly insert without temperature field (simulating old data)
    asyncio.run(database_service.characters.insert_one(old_character_data))
    
    # Retrieve through service
    character = asyncio.run(character_service.get_character("old_character"))
    
    # Should have default temperature added
    assert "temperature" in character, "Service should add default temperature"
    assert character["temperature"] == 0.7, "Default should be 0.7"
    
    # Cleanup
    asyncio.run(database_service.characters.delete_one({"character_id": "old_character"}))

if __name__ == "__main__":
    print("Running temperature feature tests...")
    print("Following TDD: These tests should FAIL first (RED phase)")
    print("-" * 50)
    
    # Run tests
    pytest.main([__file__, "-v"])