"""
Test Suite for IncrementalKnowledgeCache
Following TDD: Red → Green → Refactor
Testing incremental knowledge caching for improved RAG performance
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.incremental_knowledge_cache import IncrementalKnowledgeCache, SessionKnowledge
from services.knowledge_service import KnowledgeService


class TestIncrementalKnowledgeCache:
    """Test suite for incremental knowledge caching system"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.cache = IncrementalKnowledgeCache()
        self.test_session_id = "test_session_123"
        self.test_character_id = "seol_min_seok"
        
    def test_cache_initialization(self):
        """Test 1: Cache should initialize empty"""
        # Given: A new cache instance
        # When: Checking initial state
        # Then: Should have empty session cache
        assert len(self.cache.session_cache) == 0
        assert self.cache.knowledge_service is not None
        
    def test_cache_greeting_knowledge(self):
        """Test 2: Should cache knowledge from greeting"""
        # Given: A greeting with specific topics
        greeting = "안녕하세요, 역사 여행 가이드 설민석입니다! 오늘은 3·1 운동 이야기로 함께 떠나볼까요?"
        
        # When: Caching greeting knowledge
        cached_items = self.cache.cache_greeting_knowledge(
            self.test_session_id,
            greeting,
            self.test_character_id
        )
        
        # Then: Should extract topics and cache knowledge
        assert self.test_session_id in self.cache.session_cache
        session_knowledge = self.cache.session_cache[self.test_session_id]
        assert "3·1 운동" in session_knowledge.knowledge_base
        assert len(session_knowledge.topic_history) > 0
        assert session_knowledge.total_items > 0
        
    def test_incremental_knowledge_addition(self):
        """Test 3: Should add new knowledge for uncached topics"""
        # Given: Existing cache with some topics
        greeting = "안녕하세요, 역사 이야기를 들려드리겠습니다."
        self.cache.cache_greeting_knowledge(
            self.test_session_id,
            greeting, 
            self.test_character_id
        )
        initial_count = self.cache.session_cache[self.test_session_id].total_items
        
        # When: User mentions new topic
        user_message = "유관순은 어떤 사람인가요?"
        relevant_knowledge = self.cache.add_knowledge_incrementally(
            self.test_session_id,
            user_message,
            self.test_character_id
        )
        
        # Then: Should add new knowledge for "유관순"
        session_knowledge = self.cache.session_cache[self.test_session_id]
        assert "유관순" in session_knowledge.knowledge_base
        assert session_knowledge.total_items > initial_count
        assert len(relevant_knowledge) > 0
        
    def test_no_duplicate_caching(self):
        """Test 4: Should not cache already cached topics"""
        # Given: Cache with existing topic
        greeting = "3·1 운동에 대해 이야기해봅시다."
        self.cache.cache_greeting_knowledge(
            self.test_session_id,
            greeting,
            self.test_character_id
        )
        initial_3_1_items = len(self.cache.session_cache[self.test_session_id].knowledge_base.get("3·1 운동", []))
        
        # When: User mentions same topic again (without new topics)
        user_message = "3·1 운동에 대해 더 알려주세요"
        self.cache.add_knowledge_incrementally(
            self.test_session_id,
            user_message,
            self.test_character_id
        )
        
        # Then: Should not add duplicate knowledge for same topic
        final_3_1_items = len(self.cache.session_cache[self.test_session_id].knowledge_base.get("3·1 운동", []))
        assert final_3_1_items == initial_3_1_items  # No new items for 3·1 운동
        
    def test_relevance_scoring(self):
        """Test 5: Should score cached knowledge by relevance"""
        # Given: Cache with multiple topics
        self.cache.cache_greeting_knowledge(
            self.test_session_id,
            "3·1 운동과 유관순, 그리고 독립운동에 대해 알아봅시다.",
            self.test_character_id
        )
        
        # When: Getting relevant knowledge for specific query
        relevant_knowledge = self.cache.get_relevant_cached_knowledge(
            self.test_session_id,
            "유관순의 활동에 대해 알려주세요"
        )
        
        # Then: Should prioritize 유관순-related knowledge
        assert len(relevant_knowledge) > 0
        assert len(relevant_knowledge) <= 5  # Max 5 items
        # Most relevant items should have higher scores
        if len(relevant_knowledge) > 1:
            assert relevant_knowledge[0]['relevance_score'] >= relevant_knowledge[-1]['relevance_score']
            
    def test_cache_miss_handling(self):
        """Test 6: Should handle cache miss gracefully"""
        # Given: No cache for session
        # When: Getting knowledge for non-existent session
        relevant_knowledge = self.cache.get_relevant_cached_knowledge(
            "non_existent_session",
            "아무 질문이나"
        )
        
        # Then: Should return empty list
        assert relevant_knowledge == []
        
    def test_topic_extraction(self):
        """Test 7: Should extract meaningful topics from text"""
        # Given: Various text inputs
        test_cases = [
            ("3·1 운동은 언제 일어났나요?", ["3·1 운동", "언제"]),
            ("유관순과 독립운동에 대해", ["유관순", "독립운동"]),
            ("안녕하세요!", []),  # Greeting without specific topics
        ]
        
        # When/Then: Each should extract appropriate topics
        for text, expected_topics in test_cases:
            extracted = self.cache.extract_topics(text)
            for topic in expected_topics:
                assert topic in extracted, f"Expected {topic} in extracted topics from '{text}'"
                
    def test_relevance_calculation(self):
        """Test 8: Should calculate topic relevance correctly"""
        # Given: Cached topics and user query
        cached_topics = ["3·1 운동", "독립운동", "역사"]
        user_topics = ["3·1 운동", "시기"]
        
        # When: Calculating relevance
        relevance = self.cache.calculate_topic_relevance(
            "3·1 운동",
            user_topics,
            "3·1 운동은 언제 일어났나요?"
        )
        
        # Then: Should have high relevance
        assert relevance > 0.7  # High relevance threshold
        
        # When: Unrelated topic
        relevance = self.cache.calculate_topic_relevance(
            "조선시대",
            user_topics,
            "3·1 운동은 언제 일어났나요?"
        )
        
        # Then: Should have low relevance
        assert relevance < 0.3  # Low relevance threshold


class TestSessionKnowledge:
    """Test suite for SessionKnowledge data structure"""
    
    def test_session_knowledge_initialization(self):
        """Test 9: SessionKnowledge should initialize with correct structure"""
        # Given/When: Creating new SessionKnowledge
        session_knowledge = SessionKnowledge()
        
        # Then: Should have proper structure
        assert isinstance(session_knowledge.knowledge_base, dict)
        assert isinstance(session_knowledge.topic_history, list)
        assert session_knowledge.total_items == 0
        assert isinstance(session_knowledge.last_updated, datetime)
        
    def test_add_knowledge_to_session(self):
        """Test 10: Should properly add knowledge to session"""
        # Given: SessionKnowledge instance
        session_knowledge = SessionKnowledge()
        
        # When: Adding knowledge for a topic
        test_knowledge = [
            {"title": "3·1 운동 개요", "content": "1919년 독립운동"},
            {"title": "참여자", "content": "유관순 등"}
        ]
        session_knowledge.knowledge_base["3·1 운동"] = test_knowledge
        session_knowledge.total_items = len(test_knowledge)
        
        # Then: Should store knowledge correctly
        assert "3·1 운동" in session_knowledge.knowledge_base
        assert len(session_knowledge.knowledge_base["3·1 운동"]) == 2
        assert session_knowledge.total_items == 2


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])