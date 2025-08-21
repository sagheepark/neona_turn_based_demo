import pytest
import sys
from pathlib import Path
import os
import json
import tempfile
import shutil

# Add parent directory to path to import services
sys.path.append(str(Path(__file__).parent.parent))

from services.persona_service import PersonaService


class TestPersonaService:
    def setup_method(self):
        """Setup test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_shouldCreateNewUserPersona(self):
        """
        RED PHASE: Write failing test for persona creation
        
        Test that persona service can create new user personas with unique IDs
        and proper attribute storage for different user personalities.
        """
        # Given: Persona service
        service = PersonaService()
        
        # When: Create new persona with student attributes
        persona_data = {
            "name": "대학생 페르소나",
            "description": "스트레스 받는 대학생",
            "attributes": {
                "age": "20대 초반",
                "occupation": "대학생",
                "personality": "내향적, 완벽주의",
                "interests": ["공부", "게임", "음악"],
                "speaking_style": "존댓말, 조심스러움",
                "background": "시험 스트레스, 진로 고민"
            }
        }
        
        persona = service.create_persona("user_123", persona_data)
        
        # Then: Returns persona with unique ID and proper structure
        assert persona is not None, "Should return a persona object"
        assert isinstance(persona, dict), "Persona should be a dictionary"
        
        # Check required fields
        assert "id" in persona, "Persona should have unique ID"
        assert "name" in persona, "Persona should have name"
        assert "description" in persona, "Persona should have description"
        assert "attributes" in persona, "Persona should have attributes"
        assert "created_at" in persona, "Persona should have creation timestamp"
        assert "is_active" in persona, "Persona should have active status"
        
        # Verify field values
        assert persona["id"] is not None, "Persona ID should not be None"
        assert len(persona["id"]) > 0, "Persona ID should not be empty"
        assert persona["id"].startswith("persona_"), "Persona ID should start with 'persona_'"
        assert persona["name"] == "대학생 페르소나", "Name should match input"
        assert persona["description"] == "스트레스 받는 대학생", "Description should match input"
        assert persona["is_active"] == False, "New persona should not be active by default"
        
        # Verify attributes preservation
        attributes = persona["attributes"]
        assert attributes["age"] == "20대 초반", "Age attribute should be preserved"
        assert attributes["occupation"] == "대학생", "Occupation should be preserved"
        assert attributes["personality"] == "내향적, 완벽주의", "Personality should be preserved"
        assert "공부" in attributes["interests"], "Interests should be preserved as list"
        assert attributes["speaking_style"] == "존댓말, 조심스러움", "Speaking style should be preserved"
        assert attributes["background"] == "시험 스트레스, 진로 고민", "Background should be preserved"
        
        # Verify persona ID format (should be unique and follow pattern)
        assert len(persona["id"]) > 10, "Persona ID should be reasonably long for uniqueness"
        
        # Verify creation timestamp format
        created_at = persona["created_at"]
        assert "T" in created_at, "Created timestamp should be ISO format"
        assert len(created_at) > 15, "Timestamp should be reasonably detailed"
    
    def test_shouldPersistPersonaToFile(self):
        """
        Test that created personas are persisted to the file system
        """
        # Given: Persona service
        service = PersonaService()
        
        # When: Create persona for user
        persona_data = {
            "name": "직장인 페르소나",
            "description": "바쁜 직장인",
            "attributes": {"occupation": "개발자"}
        }
        
        persona = service.create_persona("user_456", persona_data)
        
        # Then: Persona file should exist
        expected_path = Path("personas/user_456.json")
        assert expected_path.exists(), f"Persona file should exist at {expected_path}"
        
        # Verify file contents
        with open(expected_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert "personas" in saved_data, "File should contain personas array"
        assert "active_persona_id" in saved_data, "File should contain active persona ID"
        assert len(saved_data["personas"]) == 1, "Should have one persona"
        
        saved_persona = saved_data["personas"][0]
        assert saved_persona["id"] == persona["id"], "Saved persona should match created persona"
        assert saved_persona["name"] == "직장인 페르소나", "Saved persona should have correct name"
    
    def test_shouldSetActivePersonaForUser(self):
        """
        RED PHASE: Write failing test for persona activation
        
        Test that persona service can set active persona for users,
        ensuring only one persona is active at a time.
        """
        # Given: Persona service with multiple personas for user
        service = PersonaService()
        
        # Create multiple personas
        persona1_data = {
            "name": "학생 페르소나",
            "description": "대학생",
            "attributes": {"occupation": "student"}
        }
        persona1 = service.create_persona("user_789", persona1_data)
        
        persona2_data = {
            "name": "개발자 페르소나", 
            "description": "주니어 개발자",
            "attributes": {"occupation": "developer"}
        }
        persona2 = service.create_persona("user_789", persona2_data)
        
        # When: Set persona2 as active
        updated_personas = service.set_active_persona("user_789", persona2["id"])
        
        # Then: persona2 should be active, persona1 should be inactive
        assert updated_personas is not None, "Should return updated personas data"
        assert isinstance(updated_personas, dict), "Should return dictionary"
        
        # Check active persona ID
        assert "active_persona_id" in updated_personas, "Should have active persona ID"
        assert updated_personas["active_persona_id"] == persona2["id"], "Active ID should match persona2"
        
        # Check personas list
        personas = updated_personas["personas"]
        assert len(personas) == 2, "Should have both personas"
        
        # Find and verify each persona's active status
        persona1_found = False
        persona2_found = False
        
        for persona in personas:
            if persona["id"] == persona1["id"]:
                persona1_found = True
                assert persona["is_active"] == False, "Persona1 should be inactive"
            elif persona["id"] == persona2["id"]:
                persona2_found = True
                assert persona["is_active"] == True, "Persona2 should be active"
        
        assert persona1_found, "Persona1 should be found in personas list"
        assert persona2_found, "Persona2 should be found in personas list"
        
        # Verify persistence: Load from file and check
        user_file = Path("personas/user_789.json")
        assert user_file.exists(), "User personas file should exist"
        
        with open(user_file, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
        
        assert file_data["active_persona_id"] == persona2["id"], "File should have correct active persona ID"
        
        # Test switching to persona1
        service.set_active_persona("user_789", persona1["id"])
        active_persona = service.get_active_persona("user_789")
        
        assert active_persona is not None, "Should have active persona"
        assert active_persona["id"] == persona1["id"], "Should switch to persona1"
        assert active_persona["name"] == "학생 페르소나", "Active persona should have correct name"
    
    def test_shouldIncludePersonaContextInChatPrompt(self):
        """
        RED PHASE: Write failing test for persona context injection
        
        Test that persona service can generate context string for chat prompts,
        allowing characters to respond appropriately to user's persona.
        """
        # Given: Persona service with active persona
        service = PersonaService()
        
        # Create and activate a detailed persona
        persona_data = {
            "name": "스트레스 받는 대학생",
            "description": "시험 기간 중인 컴퓨터공학과 학생",
            "attributes": {
                "age": "21세",
                "occupation": "대학생 (컴퓨터공학과 3학년)",
                "personality": "내향적, 완벽주의, 걱정이 많음",
                "interests": ["프로그래밍", "게임", "카페"],
                "speaking_style": "존댓말, 조심스럽게 질문",
                "background": "중간고사 스트레스, Python 과제 걱정",
                "current_mood": "불안하고 압박감을 느낌"
            }
        }
        
        persona = service.create_persona("user_student", persona_data)
        service.set_active_persona("user_student", persona["id"])
        
        # When: Generate persona context for chat prompt
        context = service.generate_persona_context("user_student")
        
        # Then: Context should include key persona information for AI character
        assert context is not None, "Should return persona context"
        assert isinstance(context, str), "Context should be a string"
        assert len(context) > 0, "Context should not be empty"
        
        # Check that key persona elements are included in context
        assert "21세" in context, "Context should include age"
        assert "대학생" in context, "Context should include occupation"
        assert "컴퓨터공학과" in context, "Context should include specific major"
        assert "내향적" in context, "Context should include personality traits"
        assert "완벽주의" in context, "Context should include personality traits"
        assert "존댓말" in context, "Context should include speaking style"
        assert "Python" in context, "Context should include current concerns"
        assert "스트레스" in context, "Context should include emotional state"
        
        # Verify context is formatted for AI consumption
        assert "사용자" in context or "user" in context.lower(), "Context should reference the user"
        assert "상황" in context or "배경" in context, "Context should provide situational background"
        
        # Test with no active persona
        context_none = service.generate_persona_context("nonexistent_user")
        assert context_none == "", "Should return empty string when no active persona"
        
        # Test persona context formatting includes instructions for character
        assert len(context.split(".")) >= 3, "Context should have multiple sentences for rich information"
        
        # Verify context helps character understand how to respond
        context_lower = context.lower()
        persona_indicators = ["학생", "프로그래밍", "불안", "걱정"]
        found_indicators = sum(1 for indicator in persona_indicators if indicator in context_lower)
        assert found_indicators >= 2, "Context should contain multiple persona indicators for character understanding"