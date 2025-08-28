"""
Test Suite for Memory Cache Integration
Testing the integration of IncrementalKnowledgeCache + OptimizedPromptBuilder into chat endpoint
Following TDD: Red → Green → Refactor
"""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.incremental_knowledge_cache import IncrementalKnowledgeCache
from services.optimized_prompt_builder import OptimizedPromptBuilder
from services.conversation_service import ConversationService


class TestMemoryCacheIntegration:
    """Test suite for integrated memory cache system"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.cache = IncrementalKnowledgeCache()
        self.prompt_builder = OptimizedPromptBuilder()
        self.conversation_service = ConversationService()
        
        # Test request data (not using the model since it's defined in main.py)
        self.test_request_data = {
            "user_id": "test_user",
            "character_id": "seol_min_seok", 
            "message": "3·1 운동은 언제 일어났나요?",
            "character_prompt": "You are 설민석, Korean history teacher.",
            "voice_id": "test_voice",
            "persona_id": "default"
        }
        
    def test_greeting_workflow_integration(self):
        """Test 1: Complete greeting workflow with knowledge caching and prompt building"""
        # Given: Predefined greeting request
        greeting_message = "__PREDEFINED_GREETING__:안녕하세요, 역사 여행 가이드 설민석입니다! 오늘은 3·1 운동 이야기로 함께 떠나볼까요?"
        session_id = "test_session_123"
        
        # When: Processing greeting (simulate the cache seeding)
        cached_knowledge = self.cache.cache_greeting_knowledge(
            session_id,
            "안녕하세요, 역사 여행 가이드 설민석입니다! 오늘은 3·1 운동 이야기로 함께 떠나볼까요?",
            "seol_min_seok"
        )
        
        # When: Building prompt with cached knowledge
        prompt = self.prompt_builder.build_llm_prompt(
            character_prompt="You are 설민석, Korean history teacher.",
            cached_knowledge=cached_knowledge,
            conversation_history=[],
            current_user_input="안녕하세요"
        )
        
        # Then: Should cache knowledge and build proper prompt
        assert session_id in self.cache.session_cache
        assert "3·1 운동" in self.cache.session_cache[session_id].knowledge_base
        assert "CHARACTER IDENTITY:" in prompt
        assert "AVAILABLE KNOWLEDGE:" in prompt
        assert "3·1 운동" in prompt
        
    def test_incremental_knowledge_workflow(self):
        """Test 2: User message adds incremental knowledge and builds optimized prompt"""
        # Given: Existing session with cached greeting knowledge
        session_id = "test_session_456"
        self.cache.cache_greeting_knowledge(
            session_id,
            "안녕하세요, 역사를 공부해봅시다.",
            "seol_min_seok"
        )
        
        conversation_history = [
            {"role": "assistant", "content": "안녕하세요, 역사를 공부해봅시다."}
        ]
        
        # When: User asks about new topic
        user_message = "유관순은 누구인가요?"
        cached_knowledge = self.cache.add_knowledge_incrementally(
            session_id,
            user_message,
            "seol_min_seok"
        )
        
        # When: Building optimized prompt
        prompt = self.prompt_builder.build_llm_prompt(
            character_prompt="You are 설민석, Korean history teacher.",
            cached_knowledge=cached_knowledge,
            conversation_history=conversation_history,
            current_user_input=user_message
        )
        
        # Then: Should have both existing and new knowledge
        session_knowledge = self.cache.session_cache[session_id]
        assert "유관순" in session_knowledge.knowledge_base
        assert len(cached_knowledge) > 0
        
        # Then: Prompt should include all relevant knowledge
        assert "AVAILABLE KNOWLEDGE:" in prompt
        assert "유관순" in prompt
        assert "CONVERSATION HISTORY:" in prompt
        assert "CURRENT USER MESSAGE:" in prompt
        assert user_message in prompt
        
    def test_prompt_structure_optimization(self):
        """Test 3: Integrated system should produce optimally structured prompts"""
        # Given: Session with multiple topics cached
        session_id = "test_session_789"
        self.cache.cache_greeting_knowledge(
            session_id,
            "3·1 운동과 독립운동에 대해 이야기해봅시다.",
            "seol_min_seok"
        )
        
        # Add more knowledge
        self.cache.add_knowledge_incrementally(
            session_id,
            "유관순의 활동에 대해 알려주세요",
            "seol_min_seok"
        )
        
        conversation_history = [
            {"role": "assistant", "content": "3·1 운동과 독립운동에 대해 이야기해봅시다."},
            {"role": "user", "content": "유관순의 활동에 대해 알려주세요"},
            {"role": "assistant", "content": "유관순은 학생 독립운동가였습니다."}
        ]
        
        # When: Getting knowledge and building prompt
        cached_knowledge = self.cache.get_relevant_cached_knowledge(
            session_id,
            "3·1 운동은 언제 일어났나요?"
        )
        
        prompt = self.prompt_builder.build_llm_prompt(
            character_prompt="You are 설민석, Korean history teacher.",
            cached_knowledge=cached_knowledge,
            conversation_history=conversation_history,
            current_user_input="3·1 운동은 언제 일어났나요?"
        )
        
        # Then: Should have properly ordered sections
        sections = prompt.split('\n\n')
        
        # Find section positions
        character_section_found = any("CHARACTER IDENTITY:" in section for section in sections)
        knowledge_section_found = any("AVAILABLE KNOWLEDGE:" in section for section in sections)
        history_section_found = any("CONVERSATION HISTORY:" in section for section in sections)
        current_section_found = any("CURRENT USER MESSAGE:" in section for section in sections)
        
        assert character_section_found
        assert knowledge_section_found
        assert history_section_found  
        assert current_section_found
        
        # Verify order (stable → history → current)
        prompt_lines = prompt.split('\n')
        character_pos = next(i for i, line in enumerate(prompt_lines) if "CHARACTER IDENTITY:" in line)
        history_pos = next(i for i, line in enumerate(prompt_lines) if "CONVERSATION HISTORY:" in line)  
        current_pos = next(i for i, line in enumerate(prompt_lines) if "CURRENT USER MESSAGE:" in line)
        
        assert character_pos < history_pos < current_pos
        
    def test_knowledge_relevance_filtering(self):
        """Test 4: System should filter knowledge by relevance"""
        # Given: Session with multiple unrelated topics
        session_id = "test_session_relevance"
        
        # Cache diverse knowledge
        self.cache.cache_greeting_knowledge(
            session_id,
            "조선시대와 3·1 운동, 그리고 현대사에 대해 배워봅시다.",
            "seol_min_seok"
        )
        
        # When: Asking specific question
        user_message = "3·1 운동의 주요 인물은 누구인가요?"
        relevant_knowledge = self.cache.get_relevant_cached_knowledge(
            session_id,
            user_message  
        )
        
        # Then: Should prioritize 3·1 운동 related knowledge
        assert len(relevant_knowledge) > 0
        
        # Most relevant items should be related to 3·1 운동
        for item in relevant_knowledge[:3]:  # Top 3 items
            assert item['relevance_score'] > 0.3
        
    def test_cache_memory_efficiency(self):
        """Test 5: Cache should not grow unbounded"""
        # Given: Session with multiple knowledge additions
        session_id = "test_session_memory"
        
        # Simulate multiple topic additions
        topics = ["3·1 운동", "유관순", "임시정부", "독립운동", "조선시대", "고구려"]
        
        for topic in topics:
            self.cache.add_knowledge_incrementally(
                session_id,
                f"{topic}에 대해 알려주세요",
                "seol_min_seok"
            )
        
        session_knowledge = self.cache.session_cache[session_id]
        
        # Then: Should limit cached knowledge reasonably
        assert session_knowledge.total_items < 50  # Reasonable limit
        assert len(session_knowledge.knowledge_base) <= len(topics)  # One topic per addition max
        
    def test_session_independence(self):
        """Test 6: Different sessions should have independent caches"""
        # Given: Two different sessions
        session1 = "session_1"
        session2 = "session_2"
        
        # When: Each session caches different knowledge
        self.cache.cache_greeting_knowledge(
            session1,
            "3·1 운동에 대해 배워봅시다.",
            "seol_min_seok"
        )
        
        self.cache.cache_greeting_knowledge(
            session2,
            "조선시대에 대해 배워봅시다.",
            "seol_min_seok"
        )
        
        # Then: Sessions should have independent knowledge
        session1_topics = list(self.cache.session_cache[session1].knowledge_base.keys())
        session2_topics = list(self.cache.session_cache[session2].knowledge_base.keys())
        
        assert session1 in self.cache.session_cache
        assert session2 in self.cache.session_cache
        assert session1_topics != session2_topics
        
    def test_empty_knowledge_handling(self):
        """Test 7: System should handle empty knowledge gracefully"""
        # Given: Session with no cached knowledge
        session_id = "empty_session"
        
        # When: Getting knowledge for non-existent session
        relevant_knowledge = self.cache.get_relevant_cached_knowledge(
            session_id,
            "아무 질문이나"
        )
        
        # When: Building prompt with empty knowledge
        prompt = self.prompt_builder.build_llm_prompt(
            character_prompt="You are a teacher.",
            cached_knowledge=relevant_knowledge,  # Empty list
            conversation_history=[],
            current_user_input="Hello"
        )
        
        # Then: Should handle gracefully
        assert relevant_knowledge == []
        assert "CHARACTER IDENTITY:" in prompt
        assert "AVAILABLE KNOWLEDGE:" not in prompt  # No knowledge section
        assert "CURRENT USER MESSAGE:" in prompt
        
    def test_performance_characteristics(self):
        """Test 8: Integrated system should be reasonably performant"""
        # Given: Realistic session scenario
        session_id = "performance_test"
        
        # Simulate greeting
        start_time = pytest.current_time = getattr(pytest, 'current_time', 0)
        
        cached_knowledge = self.cache.cache_greeting_knowledge(
            session_id,
            "안녕하세요, 역사 여행 가이드입니다! 3·1 운동과 독립운동에 대해 이야기해봅시다.",
            "seol_min_seok"
        )
        
        # Simulate conversation
        for i in range(5):
            user_message = f"질문 {i+1}: 역사적 사실을 알려주세요"
            self.cache.add_knowledge_incrementally(
                session_id,
                user_message,
                "seol_min_seok"
            )
            
            prompt = self.prompt_builder.build_llm_prompt(
                character_prompt="You are 설민석.",
                cached_knowledge=cached_knowledge,
                conversation_history=[{"role": "user", "content": user_message}],
                current_user_input=user_message
            )
        
        # Then: Should maintain reasonable performance characteristics
        session_knowledge = self.cache.session_cache[session_id]
        assert session_knowledge.total_items > 0  # Should have cached items
        assert len(prompt) > 100  # Should generate meaningful prompts
        assert len(prompt) < 5000  # But not excessively long


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])