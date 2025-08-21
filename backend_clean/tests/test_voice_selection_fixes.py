"""
TDD Tests for Voice Selection System Fixes
Following TDD: Red → Green → Refactor
Testing voice selection issues and requirements
"""

import pytest
import json
import requests
from pathlib import Path

class TestVoiceSelectionFixes:
    """
    Test voice selection functionality for character creation and editing
    These tests verify voice selection works correctly and handles errors gracefully
    """
    
    def test_should_not_crash_when_selecting_voice_in_edit_page(self):
        """
        Test 22.1: Edit page voice selection should not crash
        
        RED PHASE: This test will fail until we fix the voice selection crash
        """
        # Check if edit page exists and has voice selection
        edit_page_path = Path("../frontend/src/app/characters/[id]/edit/page.tsx")
        
        if edit_page_path.exists():
            with open(edit_page_path, 'r', encoding='utf-8') as f:
                edit_content = f.read()
            
            # Check for voice selection implementation
            voice_features = [
                "VoiceSelector",           # Should import VoiceSelector
                "selectedVoiceId",         # Should manage voice state
                "onSelect",               # Should handle voice selection
                "voice_id"                # Should save voice_id
            ]
            
            missing_features = []
            for feature in voice_features:
                if feature not in edit_content:
                    missing_features.append(feature)
            
            # Check if voice selection has error boundaries
            error_handling_features = [
                "try",                    # Should have try-catch blocks
                "catch",                  # Should catch errors
                "Error",                  # Should handle errors
                "loading",                # Should handle loading states
            ]
            
            has_error_handling = any(feature in edit_content for feature in error_handling_features)
            
            assert len(missing_features) == 0, f"Edit page missing voice selection features: {missing_features}"
            assert has_error_handling, "Edit page should have error handling for voice selection"
        else:
            pytest.fail("Character edit page not found")
    
    def test_should_require_voice_selection_for_character_creation(self):
        """
        Test 22.2: Character creation should require voice selection
        
        RED PHASE: This test will fail until we add voice validation
        """
        create_page_path = Path("../frontend/src/app/characters/create/page.tsx")
        
        if create_page_path.exists():
            with open(create_page_path, 'r', encoding='utf-8') as f:
                create_content = f.read()
            
            # Check for voice validation requirements
            validation_features = [
                "voice_id",                # Should have voice_id field
                "required",                # Should mark voice as required
                "validation",              # Should have validation logic
                "error",                   # Should show validation errors
                "VoiceSelector"            # Should use VoiceSelector component
            ]
            
            missing_validation = []
            for feature in validation_features:
                if feature not in create_content:
                    missing_validation.append(feature)
            
            # Check if form prevents submission without voice
            form_validation_indicators = [
                "handleSubmit",            # Should have form submission
                "preventDefault",          # Should prevent invalid submission  
                "voice_id",               # Should check voice_id before submit
            ]
            
            has_form_validation = all(indicator in create_content for indicator in form_validation_indicators)
            
            assert len(missing_validation) == 0, f"Character creation missing voice validation: {missing_validation}"
            assert has_form_validation, "Form should validate voice selection before submission"
        else:
            pytest.fail("Character creation page not found")
    
    def test_should_provide_default_voice_option(self):
        """
        Test 22.3: Default voice should be available
        
        RED PHASE: This test will fail until we implement default voice system
        """
        # Check if VoiceSelector component has default voice support
        voice_selector_path = Path("../frontend/src/components/characters/VoiceSelector.tsx")
        
        if voice_selector_path.exists():
            with open(voice_selector_path, 'r', encoding='utf-8') as f:
                voice_selector_content = f.read()
            
            # Check for default voice implementation
            default_voice_features = [
                "defaultVoice",            # Should have default voice concept
                "isDefault",               # Should mark default voice
                "fallback",                # Should have fallback mechanism
            ]
            
            missing_default_features = []
            for feature in default_voice_features:
                if feature not in voice_selector_content:
                    missing_default_features.append(feature)
            
            # Should fail because default voice system is not implemented
            assert len(missing_default_features) == 0, f"VoiceSelector missing default voice features: {missing_default_features}"
        else:
            pytest.fail("VoiceSelector component not found")
    
    def test_should_handle_voice_api_failures_gracefully(self):
        """
        Test 22.4: Voice selector should handle API failures gracefully
        
        RED PHASE: This test verifies error handling exists
        """
        voice_selector_path = Path("../frontend/src/components/characters/VoiceSelector.tsx")
        
        if voice_selector_path.exists():
            with open(voice_selector_path, 'r', encoding='utf-8') as f:
                voice_selector_content = f.read()
            
            # Check for API error handling
            error_handling_features = [
                "catch",                   # Should catch API errors
                "error",                   # Should handle error states
                "loading",                 # Should handle loading states
                "fallback",                # Should have fallback options
                "try",                     # Should wrap API calls in try-catch
            ]
            
            error_handling_count = sum(1 for feature in error_handling_features if feature in voice_selector_content)
            
            # Check for graceful degradation
            graceful_features = [
                "offline",                 # Should handle offline state
                "cache",                   # Should use cached voices
                "default",                 # Should fallback to default
            ]
            
            graceful_count = sum(1 for feature in graceful_features if feature in voice_selector_content)
            
            assert error_handling_count >= 3, f"VoiceSelector needs better error handling. Found {error_handling_count}/5 features"
            assert graceful_count >= 1, f"VoiceSelector needs graceful degradation. Found {graceful_count}/3 features"
        else:
            pytest.fail("VoiceSelector component not found")
    
    def test_should_have_voice_selection_integration_in_both_pages(self):
        """
        Test 22.5: Both create and edit pages should have complete voice selection
        
        RED PHASE: This test verifies consistent voice selection integration
        """
        create_page = Path("../frontend/src/app/characters/create/page.tsx")
        edit_page = Path("../frontend/src/app/characters/[id]/edit/page.tsx")
        
        pages_to_check = [
            ("create", create_page),
            ("edit", edit_page)
        ]
        
        for page_type, page_path in pages_to_check:
            if page_path.exists():
                with open(page_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Required voice integration features
                required_features = [
                    "VoiceSelector",           # Should import VoiceSelector
                    "voice_id",                # Should manage voice_id state
                    "onSelect",                # Should handle voice selection
                    "selectedVoiceId",         # Should pass selected voice
                ]
                
                missing_features = []
                for feature in required_features:
                    if feature not in content:
                        missing_features.append(feature)
                
                assert len(missing_features) == 0, f"{page_type} page missing voice features: {missing_features}"
            else:
                pytest.fail(f"Character {page_type} page not found")
    
    def test_voice_api_should_be_accessible(self):
        """
        Test 22.6: Voice API endpoint should be working
        
        RED PHASE: This test checks if voice API is causing crashes
        """
        try:
            # Test if voice API endpoint is accessible
            # This is a basic connectivity test
            response = requests.get("http://localhost:8000/api/voices", timeout=5)
            
            # Should either return voices or a proper error response
            assert response.status_code in [200, 404, 500], f"Voice API returned unexpected status: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, (list, dict)), "Voice API should return list or dict"
            
        except requests.exceptions.ConnectionError:
            # API not available - this might be why voice selection crashes
            pytest.fail("Voice API is not accessible - this may cause voice selection crashes")
        except requests.exceptions.Timeout:
            pytest.fail("Voice API timeout - this may cause voice selection to hang")
        except Exception as e:
            pytest.fail(f"Voice API error: {str(e)} - this may cause voice selection crashes")