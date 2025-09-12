#!/usr/bin/env python3
"""
Test 14.1: shouldLoadCharacterContentConfiguration
RED phase: Character should be able to define custom content types
Purpose: Provider-Controllable Character Configuration System
"""

import pytest
from typing import Dict, List, Any


class TestProviderControllableConfiguration:
    """Test provider-controllable character configuration system"""
    
    def test_should_load_character_content_configuration(self):
        """
        Test that characters can define custom content types with configuration
        """
        # Arrange & Act
        try:
            from services.character_config_manager import CharacterConfigManager
            config_manager = CharacterConfigManager()
            
            # Get character configuration
            config = config_manager.get_character_config("seol_min_seok_quiz")
            
        except ImportError:
            # Expected to fail initially
            assert False, "CharacterConfigManager service should exist"
        
        # Assert - Should have content type configuration
        assert config is not None, "Character configuration should exist"
        assert hasattr(config, 'content_types'), "Config should have content_types"
        assert "quiz" in config.content_types, "Should have quiz content type defined"
        
        # Verify quiz content type structure
        quiz_config = config.content_types["quiz"]
        assert hasattr(quiz_config, 'confidence_threshold'), "Quiz should have confidence threshold"
        assert quiz_config.confidence_threshold == 0.8, "Quiz confidence threshold should be 0.8"
        assert hasattr(quiz_config, 'required_tools'), "Quiz should have required_tools list"
        assert "show_selection" in quiz_config.required_tools, "Quiz should require show_selection tool"
        
        print(f"✅ Character content configuration loaded: {config.content_types}")

    def test_should_validate_provider_content_type_schema(self):
        """
        Test that content type definitions are properly validated
        """
        try:
            from services.character_config_manager import CharacterConfigManager
            config_manager = CharacterConfigManager()
            
            # Test valid schema validation
            valid_schema = {
                "quiz": {
                    "confidence_threshold": 0.8,
                    "required_tools": ["show_selection"],
                    "triggers": ["퀴즈", "질문", "문제"]
                }
            }
            
            is_valid = config_manager.validate_content_type_schema(valid_schema)
            assert is_valid, "Valid schema should pass validation"
            
            # Test invalid schema validation
            invalid_schema = {
                "quiz": {
                    "confidence_threshold": "invalid",  # Should be float
                    "required_tools": "not_a_list"      # Should be list
                }
            }
            
            is_invalid = config_manager.validate_content_type_schema(invalid_schema)
            assert not is_invalid, "Invalid schema should fail validation"
            
            print(f"✅ Content type schema validation working properly")
            
        except ImportError:
            assert False, "CharacterConfigManager should be implemented with validation"

    def test_should_enforce_content_type_constraints(self):
        """
        Test that content type constraints are enforced during runtime
        """
        try:
            from services.character_config_manager import CharacterConfigManager
            config_manager = CharacterConfigManager()
            
            # Test constraint enforcement
            config = config_manager.get_character_config("seol_min_seok_quiz")
            
            # Should enforce confidence threshold
            test_classification = {
                "content_type": "quiz",
                "confidence": 0.7  # Below 0.8 threshold
            }
            
            meets_threshold = config_manager.meets_confidence_threshold(
                "seol_min_seok_quiz", 
                test_classification
            )
            
            assert not meets_threshold, "Should not meet threshold when confidence is too low"
            
            # Should pass when confidence is high enough
            test_classification["confidence"] = 0.9
            meets_threshold = config_manager.meets_confidence_threshold(
                "seol_min_seok_quiz", 
                test_classification
            )
            
            assert meets_threshold, "Should meet threshold when confidence is high enough"
            
            print(f"✅ Content type constraints properly enforced")
            
        except ImportError:
            assert False, "CharacterConfigManager should implement constraint enforcement"


if __name__ == "__main__":
    # Run the tests
    test_instance = TestProviderControllableConfiguration()
    
    try:
        print("🔴 Running Test 14.1: shouldLoadCharacterContentConfiguration")
        print("-" * 50)
        
        # Test 1: Basic character content configuration
        test_instance.test_should_load_character_content_configuration()
        print("✅ Test 1 passed: Character content configuration loaded")
        
        # Test 2: Content type schema validation
        test_instance.test_should_validate_provider_content_type_schema()
        print("✅ Test 2 passed: Content type schema validation working")
        
        # Test 3: Constraint enforcement
        test_instance.test_should_enforce_content_type_constraints()
        print("✅ Test 3 passed: Content type constraints enforced")
        
        print("-" * 50)
        print("🟢 All tests passed!")
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        print("This is expected in RED phase - CharacterConfigManager not implemented yet")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")