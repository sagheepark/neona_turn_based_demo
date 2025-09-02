"""
Tests for Character Configuration Manager
Test Group 14: Provider-Controllable Character Configuration
Following TDD RED-GREEN-REFACTOR methodology
"""
import pytest
from typing import Dict, Any


class TestCharacterConfigManager:
    """Test Group 14: Provider-Controllable Character Configuration"""
    
    def test_should_load_character_content_configuration(self):
        """
        Test 14.1: shouldLoadCharacterContentConfiguration
        RED phase: Character should be able to define custom content types
        """
        # Arrange
        from services.character_config_manager import CharacterConfigManager
        config_manager = CharacterConfigManager()
        
        # Act
        config = config_manager.get_character_config("seol_min_seok_quiz")
        
        # Assert
        assert config is not None
        assert "quiz" in config.content_types
        assert config.content_types["quiz"].confidence_threshold == 0.8
        assert "show_selection" in config.content_types["quiz"].required_tools
        assert config.content_types["quiz"].llm_classification_prompt is not None
        assert len(config.content_types["quiz"].detection_patterns) > 0
    
    def test_should_validate_provider_content_type_schema(self):
        """
        Test 14.2: shouldValidateProviderContentTypeSchema
        RED phase: Content type definitions should be validated
        """
        # Arrange
        from services.character_config_manager import ContentTypeDefinition
        
        # Valid content type
        valid_quiz_config = {
            "name": "quiz",
            "detection_patterns": ["(.+?)\\?\\s*([A-D]\\)[^A-D]*)+"],
            "llm_classification_prompt": "Detect Korean quiz questions",
            "required_tools": ["show_selection"],
            "confidence_threshold": 0.8
        }
        
        # Invalid content type - empty name
        invalid_name_config = {
            "name": "",  # Empty name should fail
            "confidence_threshold": 0.8
        }
        
        # Invalid content type - bad threshold
        invalid_threshold_config = {
            "name": "test",
            "confidence_threshold": 1.5  # Invalid threshold should fail
        }
        
        # Act & Assert
        # Valid definition should work
        valid_definition = ContentTypeDefinition(**valid_quiz_config)
        assert valid_definition.name == "quiz"
        assert valid_definition.confidence_threshold == 0.8
        
        # Invalid definitions should raise ValueError
        with pytest.raises(ValueError):
            ContentTypeDefinition(**invalid_name_config)
        
        with pytest.raises(ValueError):
            ContentTypeDefinition(**invalid_threshold_config)
    
    def test_should_get_default_config_for_unknown_character(self):
        """
        Test 14.3: shouldGetDefaultConfigForUnknownCharacter
        RED phase: Unknown characters should get sensible defaults
        """
        # Arrange
        from services.character_config_manager import CharacterConfigManager
        config_manager = CharacterConfigManager()
        
        # Act
        config = config_manager.get_character_config("unknown_character_id")
        
        # Assert
        assert config is not None
        assert config.character_id == "unknown_character_id"
        assert config.classification_strategy == "hybrid"  # Default strategy
        assert config.global_confidence_threshold == 0.7  # Default threshold
        assert len(config.content_types) == 0  # No custom content types
        assert config.fallback_strategy == "conservative"  # Safe default