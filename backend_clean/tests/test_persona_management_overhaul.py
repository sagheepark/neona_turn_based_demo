"""
TDD Tests for Persona Management Overhaul
RED PHASE: Write failing tests for the persona management requirements
Following TDD methodology: Red → Green → Refactor
"""

import pytest
import json
from services.persona_service import PersonaService

class TestPersonaManagementOverhaul:
    def setup_method(self):
        self.persona_service = PersonaService()
        self.test_user_id = "test_user_global_persona"
        
    def test_should_manage_personas_globally_not_per_character(self):
        """
        Test 12.1: Global persona storage and retrieval
        
        RED PHASE: This test fails because personas are currently character-specific
        Personas should be global and available across all characters
        """
        # Given: User creates a global persona
        persona_data = {
            "name": "글로벌 학생 페르소나",
            "description": "모든 캐릭터에서 사용할 수 있는 학생 페르소나",
            "attributes": {
                "age": "22세",
                "occupation": "대학생",
                "name": "김민수",
                "personality": "내향적, 학구적",
                "interests": ["독서", "영화감상"],
                "speaking_style": "존댓말 사용"
            }
        }
        
        # When: Persona is created (should be global, not character-specific)
        created_persona = self.persona_service.create_persona(self.test_user_id, persona_data)
        # Set as active persona for testing
        self.persona_service.set_active_persona(self.test_user_id, created_persona["id"])
        
        # Then: Persona should be accessible globally, not tied to specific character
        user_personas = self.persona_service.get_user_personas(self.test_user_id)
        assert len(user_personas) > 0, "Should have created global persona"
        
        # And: Persona should be available for any character (not character-specific)
        global_persona = next((p for p in user_personas if p["id"] == created_persona["id"]), None)
        assert global_persona is not None, "Persona should exist globally"
        assert "character_id" not in global_persona, "Persona should NOT be tied to specific character"
        
        # EXPECTED FAILURE: Current system may tie personas to characters
        # This test documents the requirement for global persona management
        print("🔴 RED PHASE: Personas should be global, not character-specific")
        
    def test_should_allow_customizable_persona_fields(self):
        """
        Test 12.2: Persona field customization system
        
        RED PHASE: This test fails because all persona fields are currently forced into context
        Characters should be able to select which persona fields to use
        """
        # Given: Character creator defines which persona fields to use
        character_persona_preferences = {
            "character_id": "selective_character",
            "required_fields": ["age", "occupation", "name"],  # Always included
            "optional_fields": ["personality"],  # Character chooses to include
            "excluded_fields": ["interests", "speaking_style"]  # Character chooses to exclude
        }
        
        # And: User has a persona with all fields
        persona_data = {
            "name": "완전한 페르소나",
            "description": "모든 필드를 가진 페르소나",
            "attributes": {
                "age": "25세",
                "occupation": "개발자",
                "name": "이철수",
                "personality": "외향적, 적극적",
                "interests": ["게임", "스포츠"],
                "speaking_style": "반말 사용",
                "background": "IT 회사 재직"
            }
        }
        
        created_persona = self.persona_service.create_persona(self.test_user_id, persona_data)
        # Set as active persona for testing
        self.persona_service.set_active_persona(self.test_user_id, created_persona["id"])
        
        # When: Generate persona context with field customization
        try:
            # This method doesn't exist yet - will be implemented in GREEN phase
            selective_context = self.persona_service.generate_selective_persona_context(
                self.test_user_id, 
                character_persona_preferences
            )
            
            # Then: Context should only include selected fields (check actual values, not field names)
            assert "25세" in selective_context, "Required field 'age' value should be included"
            assert "개발자" in selective_context, "Required field 'occupation' value should be included"
            assert "이철수" in selective_context, "Required field 'name' value should be included"
            assert "외향적, 적극적" in selective_context, "Selected optional field should be included"
            
            # And: Excluded fields should not be in context (check actual values)
            assert "게임" not in selective_context, "Excluded field 'interests' values should NOT be included"
            assert "반말 사용" not in selective_context, "Excluded field 'speaking_style' should NOT be included"
            
            print("✅ GREEN PHASE: Selective persona context working correctly")
            return  # Test passes, no need for the assert False
            
        except AttributeError:
            # Expected failure - method doesn't exist yet
            print("🔴 RED PHASE: generate_selective_persona_context method not implemented")
            
        # EXPECTED FAILURE: Current system includes all persona fields
        # This test documents the requirement for customizable field selection
        assert False, "Current system forces all persona fields into context - need selective inclusion"
        
    def test_should_preserve_character_identity_with_selective_persona(self):
        """
        Test 12.3: Character identity preservation
        
        RED PHASE: This test fails because characters lose identity due to persona overload
        Characters should maintain their core identity with selective persona application
        """
        # Given: Character has strong identity
        character_identity = {
            "name": "김파이썬",
            "personality": "열정적이고 체계적인 성격의 프로그래밍 교육 전문가",
            "role": "Python 프로그래밍 튜터",
            "speaking_style": "친근하면서도 전문적인 말투"
        }
        
        # And: User persona has different characteristics
        user_persona_data = {
            "name": "사용자 페르소나",
            "description": "학습자 페르소나",
            "attributes": {
                "age": "20세",
                "occupation": "학생",
                "name": "박학생",  # Different name
                "personality": "수줍고 조용한 성격",  # Different personality
                "interests": ["게임", "음악"]
            }
        }
        
        created_persona = self.persona_service.create_persona(self.test_user_id, user_persona_data)
        # Set as active persona for testing
        self.persona_service.set_active_persona(self.test_user_id, created_persona["id"])
        
        # When: Generate context with character identity preservation
        try:
            # This method should preserve character identity while adding user context
            preserved_context = self.persona_service.generate_identity_preserving_context(
                self.test_user_id,
                character_identity,
                ["age", "occupation"]  # Only use these fields from user persona
            )
            
            # Then: Character identity should be preserved
            assert character_identity["name"] in preserved_context, "Character name should be preserved"
            assert character_identity["personality"] in preserved_context, "Character personality should be preserved"
            
            # And: Only selected user persona fields should be added
            assert "20세" in preserved_context, "User age should be included"
            assert "학생" in preserved_context, "User occupation should be included"
            
            # But: User name and personality should NOT override character
            assert "박학생" not in preserved_context, "User name should NOT override character name"
            assert "수줍고 조용한" not in preserved_context, "User personality should NOT override character"
            
            print("✅ GREEN PHASE: Character identity preservation working correctly")
            return  # Test passes, no need for the assert False
            
        except AttributeError:
            # Expected failure - method doesn't exist yet
            print("🔴 RED PHASE: generate_identity_preserving_context method not implemented")
            
        # EXPECTED FAILURE: Current system may override character identity with user persona
        # This test documents the requirement for character identity preservation
        assert False, "Current system may override character identity - need identity preservation"