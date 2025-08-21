"""
TDD Test for Visual Knowledge Feedback
RED PHASE: Write failing test for visual feedback when knowledge is used
Following TDD methodology: Red → Green → Refactor
"""

import pytest
import json
from services.chat_orchestrator import ChatOrchestrator

class TestVisualKnowledgeFeedback:
    def setup_method(self):
        self.chat_orchestrator = ChatOrchestrator()
        self.test_user_id = "test_user_knowledge_feedback"
        self.test_character_id = "dr_python"  # Character with known knowledge base
        
    def test_should_indicate_when_knowledge_is_used_in_response(self):
        """
        Test for visual knowledge feedback requirement
        
        RED PHASE: This test fails because chat responses don't include 
        knowledge usage indicators for frontend display
        """
        # Given: User asks a question that should trigger knowledge usage
        user_message = "파이썬에서 변수는 어떻게 만드나요?"  # This should match Dr. Python's knowledge
        
        # When: Generate chat response
        try:
            response = self.chat_orchestrator.generate_response(
                user_id=self.test_user_id,
                character_id=self.test_character_id,
                message=user_message,
                character_prompt="당신은 Python 프로그래밍 전문가입니다."
            )
            
            # Then: Response should include knowledge usage indicators
            assert "knowledge_used" in response, "Response should include knowledge_used field for visual feedback"
            assert isinstance(response["knowledge_used"], list), "knowledge_used should be a list of knowledge items"
            
            if response["knowledge_used"]:
                # Verify knowledge items have required fields for frontend display
                knowledge_item = response["knowledge_used"][0]
                assert "id" in knowledge_item, "Knowledge item should have ID for tracking"
                assert "title" in knowledge_item, "Knowledge item should have title for display"
                assert "relevance_score" in knowledge_item, "Knowledge item should have relevance score"
                
                print("✅ GREEN PHASE: Knowledge usage feedback working correctly")
                return  # Test passes
            
        except Exception as e:
            print(f"🔴 RED PHASE: Knowledge feedback not implemented - {str(e)}")
        
        # EXPECTED FAILURE: Current system doesn't provide knowledge usage feedback
        # This test documents the requirement for visual knowledge indicators
        assert False, "Chat responses should include knowledge_used field with knowledge items for visual feedback"
        
    def test_should_provide_empty_knowledge_when_none_used(self):
        """
        Test for handling cases when no knowledge is used
        
        RED PHASE: This test fails because response format doesn't include 
        knowledge_used field even when empty
        """
        # Given: User asks a question that shouldn't trigger knowledge usage
        user_message = "안녕하세요"  # Simple greeting, shouldn't use specific knowledge
        
        # When: Generate chat response
        try:
            response = self.chat_orchestrator.generate_response(
                user_id=self.test_user_id,
                character_id=self.test_character_id,
                message=user_message,
                character_prompt="당신은 Python 프로그래밍 전문가입니다."
            )
            
            # Then: Response should include empty knowledge_used field
            assert "knowledge_used" in response, "Response should always include knowledge_used field"
            assert isinstance(response["knowledge_used"], list), "knowledge_used should be a list"
            assert len(response["knowledge_used"]) == 0, "knowledge_used should be empty when no knowledge is used"
            
            print("✅ GREEN PHASE: Empty knowledge feedback working correctly")
            return  # Test passes
            
        except Exception as e:
            print(f"🔴 RED PHASE: Knowledge feedback structure not implemented - {str(e)}")
        
        # EXPECTED FAILURE: Current system doesn't provide knowledge_used field structure
        # This test documents the requirement for consistent response format
        assert False, "Chat responses should always include knowledge_used field, even when empty"