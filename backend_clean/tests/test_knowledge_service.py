import pytest
import sys
from pathlib import Path

# Add parent directory to path to import services
sys.path.append(str(Path(__file__).parent.parent))

from services.knowledge_service import KnowledgeService


class TestKnowledgeService:
    def test_shouldFindRelevantKnowledgeByKeyword(self):
        """
        RED PHASE: Write failing test first
        
        Test that knowledge service can find relevant Python programming knowledge
        when searching with keywords that should match Dr. Python's knowledge base.
        """
        # Given: Knowledge service with Dr. Python's knowledge
        service = KnowledgeService()
        
        # When: Search for Python-related keyword
        results = service.search_relevant_knowledge("변수", "dr_python", max_results=3)
        
        # Then: Returns Python variable-related knowledge
        assert len(results) > 0, "Should find at least one relevant knowledge item"
        assert any("변수" in item.get("title", "") or "변수" in item.get("trigger_keywords", []) 
                  for item in results), "Should contain variable-related knowledge"
        assert any("Python" in item.get("title", "") or "python" in str(item.get("tags", [])).lower() 
                  for item in results), "Should contain Python-related knowledge"
    
    def test_shouldFindFunctionKnowledge(self):
        """
        Additional test for Dr. Python's function knowledge
        """
        # Given: Knowledge service
        service = KnowledgeService()
        
        # When: Search for function-related terms
        results = service.search_relevant_knowledge("함수", "dr_python", max_results=3)
        
        # Then: Returns function-related knowledge
        assert len(results) > 0, "Should find function-related knowledge"
        assert any("함수" in item.get("trigger_keywords", []) 
                  for item in results), "Should match function keywords"
    
    def test_shouldFindDebuggingKnowledge(self):
        """
        Test for Dr. Python's debugging knowledge
        """
        # Given: Knowledge service
        service = KnowledgeService()
        
        # When: Search for debugging terms
        results = service.search_relevant_knowledge("오류", "dr_python", max_results=3)
        
        # Then: Returns debugging-related knowledge
        assert len(results) > 0, "Should find debugging-related knowledge"
        assert any("오류" in item.get("trigger_keywords", []) or "디버깅" in item.get("tags", [])
                  for item in results), "Should match debugging keywords"
    
    def test_shouldRankKnowledgeByRelevanceScore(self):
        """
        RED PHASE: Write failing test for relevance ranking
        
        Test that knowledge items are returned in order of relevance score,
        with items matching trigger keywords ranked higher than tag matches.
        """
        # Given: Knowledge service with Dr. Python's knowledge
        service = KnowledgeService()
        
        # When: Search with term that matches both trigger keywords and tags
        # "Python" should match trigger keywords (high score) and tags (lower score)
        results = service.search_relevant_knowledge("Python 기본", "dr_python", max_results=5)
        
        # Then: Results should be ranked by relevance score
        assert len(results) >= 2, "Should find multiple relevant items"
        
        # Extract relevance scores for verification
        scores = []
        for item in results:
            score = service._calculate_relevance_score("Python 기본", item)
            scores.append(score)
        
        # Verify results are in descending order of relevance
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], f"Results should be ranked by score: {scores[i]} >= {scores[i + 1]}"
        
        # Verify that items with trigger keyword matches rank higher than tag-only matches
        first_item = results[0]
        first_score = service._calculate_relevance_score("Python 기본", first_item)
        
        # First result should have a reasonably high score (trigger keyword or title match)
        assert first_score >= 5, f"Top result should have high relevance score, got: {first_score}"
    
    def test_shouldReturnOnlyCharacterSpecificKnowledge(self):
        """
        RED PHASE: Write failing test for character-specific knowledge isolation
        
        Test that search returns knowledge only for the specified character,
        not mixing knowledge from different characters.
        """
        # Given: Knowledge service with multiple characters' knowledge
        service = KnowledgeService()
        
        # When: Search for dr_python's knowledge with programming terms
        python_results = service.search_relevant_knowledge("변수", "dr_python", max_results=3)
        
        # Then: Should return only dr_python's knowledge
        assert len(python_results) > 0, "Should find dr_python's programming knowledge"
        
        # All results should be from dr_python's knowledge base (programming-focused)
        # We'll verify by checking that knowledge items contain programming concepts
        for item in python_results:
            # dr_python's knowledge should contain programming/development content
            # Check that it's educational programming content (not ASMR or debate content)
            content = item.get('content', '').lower()
            title = item.get('title', '').lower()
            tags = [tag.lower() for tag in item.get('tags', [])]
            
            # Should be programming/educational content, not other domains
            is_programming_content = (
                'python' in content or 'python' in title or
                any(prog_term in content for prog_term in ['def ', 'class ', 'import ', 'function', '변수', '함수', '코딩']) or
                any(prog_term in title for prog_term in ['python', '변수', '함수', '클래스', '프로그래밍']) or
                any(tag in ['변수', 'python', '함수', '클래스', 'oop', '프로그래밍'] for tag in tags)
            )
            
            # Should not be ASMR or debate content
            is_other_domain = (
                any(other_term in content for other_term in ['asmr', '귓속말', '논쟁', '분노']) or
                any(other_term in title for other_term in ['asmr', '논쟁', '분노'])
            )
            
            assert is_programming_content and not is_other_domain, \
                   f"Should be programming content from dr_python: {item.get('title')}"
        
        # When: Search for non-existent character
        invalid_results = service.search_relevant_knowledge("anything", "non_existent_character", max_results=5)
        
        # Then: Should return empty list for character that doesn't exist
        assert len(invalid_results) == 0, "Should return empty list for non-existent character"
    
    def test_shouldReturnEmptyArrayWhenNoKnowledgeFound(self):
        """
        RED PHASE: Write test for empty search results
        
        Test that search returns empty array when no knowledge matches the query.
        """
        # Given: Knowledge service with dr_python's knowledge
        service = KnowledgeService()
        
        # When: Search with completely irrelevant terms that won't match any programming knowledge
        irrelevant_results = service.search_relevant_knowledge("화성여행우주선", "dr_python", max_results=5)
        
        # Then: Should return empty array
        assert len(irrelevant_results) == 0, "Should return empty array for irrelevant search terms"
        assert isinstance(irrelevant_results, list), "Should return a list (even if empty)"
        
        # When: Search with empty string
        empty_results = service.search_relevant_knowledge("", "dr_python", max_results=5)
        
        # Then: Should return empty array for empty query
        assert len(empty_results) == 0, "Should return empty array for empty search string"
        
        # When: Search for character with no knowledge base (simulate empty knowledge)
        # We'll test this by searching in a character that exists but might have no matching content
        no_match_results = service.search_relevant_knowledge("완전히다른주제", "dr_python", max_results=5)
        
        # Then: Should return empty array when no content matches
        assert len(no_match_results) == 0, "Should return empty array when no knowledge matches"