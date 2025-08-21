"""
TDD Tests for Knowledge Management UI Components
RED PHASE: Write failing tests for frontend UI components that don't exist yet
Following TDD methodology: Red → Green → Refactor
"""

import pytest
import json
from pathlib import Path

class TestKnowledgeUIComponents:
    """
    Test knowledge management UI components integration
    These tests will fail until we implement the actual frontend components
    """
    
    def test_should_have_knowledge_management_api_endpoints(self):
        """
        Test 18.1: FastAPI should provide REST endpoints for knowledge management
        
        RED PHASE: This test will fail until we add API endpoints to main.py
        """
        # This test simulates what the frontend will need
        # We need to verify that the API endpoints exist for the UI to consume
        
        # Test data that UI will send
        character_id = "dr_python"
        new_knowledge = {
            "title": "New Test Knowledge",
            "content": "Test content for UI",
            "keywords": ["test", "ui", "knowledge"],
            "category": "testing"
        }
        
        # The UI will need these API endpoints:
        expected_endpoints = [
            f"/api/characters/{character_id}/knowledge",      # GET - list knowledge
            f"/api/characters/{character_id}/knowledge",      # POST - create knowledge
            f"/api/knowledge/{{knowledge_id}}",              # PUT - update knowledge  
            f"/api/knowledge/{{knowledge_id}}",              # DELETE - delete knowledge
        ]
        
        # For now, we'll test the service layer that these endpoints will use
        from services.knowledge_service import KnowledgeService
        service = KnowledgeService()
        
        # Simulate GET /api/characters/{character_id}/knowledge
        knowledge_list = service.get_character_knowledge(character_id)
        assert isinstance(knowledge_list, list), "API should return list of knowledge items"
        
        # Simulate POST /api/characters/{character_id}/knowledge
        create_result = service.create_knowledge_item(character_id, new_knowledge)
        assert create_result["success"] is True, "API should create knowledge successfully"
        knowledge_id = create_result["knowledge_id"]
        
        # Simulate PUT /api/knowledge/{knowledge_id}
        update_data = {"title": "Updated Title"}
        update_result = service.update_knowledge_item(character_id, knowledge_id, update_data)
        assert update_result["success"] is True, "API should update knowledge successfully"
        
        # Simulate DELETE /api/knowledge/{knowledge_id}
        delete_result = service.delete_knowledge_item(character_id, knowledge_id)
        assert delete_result["success"] is True, "API should delete knowledge successfully"
    
    def test_should_validate_frontend_component_requirements(self):
        """
        Test 18.2: Validate that backend provides all data needed for frontend components
        
        RED PHASE: This test defines what frontend components will need
        """
        from services.knowledge_service import KnowledgeService
        
        # Given: Knowledge service with character data
        service = KnowledgeService()
        character_id = "dr_python"
        
        # When: Frontend requests knowledge data
        knowledge_items = service.get_character_knowledge(character_id)
        
        # Then: Each item should have all fields needed by UI components
        if knowledge_items:  # Only test if items exist
            sample_item = knowledge_items[0]
            
            # Required fields for KnowledgeRow component
            ui_required_fields = ["id", "title", "content", "category"]
            for field in ui_required_fields:
                assert field in sample_item, f"UI component needs '{field}' field"
            
            # Keywords field (simplified or legacy)
            has_keywords = ("keywords" in sample_item or 
                          ("trigger_keywords" in sample_item and "context_keywords" in sample_item))
            assert has_keywords, "UI component needs keywords in some format"
            
            # Optional fields that UI might use
            optional_fields = ["created_at", "updated_at", "priority"]
            # These are optional, so we just check they don't break if present
            for field in optional_fields:
                if field in sample_item:
                    assert sample_item[field] is not None, f"If present, '{field}' should not be None"
    
    def test_should_support_character_creation_with_knowledge(self):
        """
        Test 18.3: Character creation should include knowledge base initialization
        
        RED PHASE: This test will guide the integration with character creation UI
        """
        from services.knowledge_service import KnowledgeService
        
        # Given: New character creation scenario
        service = KnowledgeService()
        new_character_id = "new_test_character"
        
        # When: Character is created with initial knowledge items
        initial_knowledge = [
            {
                "title": "Character Introduction",
                "content": "Basic information about this character",
                "keywords": ["introduction", "basic", "character"],
                "category": "fundamentals"
            },
            {
                "title": "Character Expertise",
                "content": "What this character specializes in",
                "keywords": ["expertise", "specialization", "skills"],
                "category": "expertise"
            }
        ]
        
        # Character creation process should be able to add multiple knowledge items
        created_items = []
        for knowledge_data in initial_knowledge:
            result = service.create_knowledge_item(new_character_id, knowledge_data)
            assert result["success"] is True, "Should create each knowledge item"
            created_items.append(result["knowledge_id"])
        
        # Then: Character should have all knowledge items
        character_knowledge = service.get_character_knowledge(new_character_id)
        assert len(character_knowledge) >= len(initial_knowledge), "Should have all created items"
        
        # And: Each created item should be retrievable
        for knowledge_id in created_items:
            item = service.get_knowledge_item(new_character_id, knowledge_id)
            assert item is not None, f"Should retrieve knowledge item {knowledge_id}"
    
    def test_should_support_knowledge_search_for_ui(self):
        """
        Test 18.4: Backend should support knowledge search functionality for UI
        
        RED PHASE: This test ensures search functionality works for UI filtering
        """
        from services.enhanced_knowledge_service import EnhancedKnowledgeService
        
        # Given: Enhanced knowledge service for smart search
        service = EnhancedKnowledgeService()
        character_id = "dr_python"
        
        # When: UI performs search (what a search box would do)
        search_queries = ["variables", "functions", "programming"]
        
        for query in search_queries:
            # UI search functionality
            search_results = service.smart_search(query, character_id)
            
            # Then: Should return relevant results for UI display
            assert isinstance(search_results, list), f"Search for '{query}' should return list"
            
            # If results found, they should have relevance scores for UI sorting
            if search_results:
                for result in search_results:
                    assert "relevance_score" in result, "UI needs relevance scores for ranking"
                    assert result["relevance_score"] > 0, "Relevance score should be positive"
                    
                # Results should be sorted by relevance (highest first)
                scores = [r["relevance_score"] for r in search_results]
                assert scores == sorted(scores, reverse=True), "Results should be sorted by relevance"
    
    def test_should_validate_character_mood_system_integration(self):
        """
        Test 18.5: Character mood system should integrate with knowledge management
        
        RED PHASE: This test prepares for character expression UI integration  
        """
        from services.character_mood_service import CharacterMoodService
        
        # Given: Character mood service
        mood_service = CharacterMoodService()
        character_id = "test_character_moods"
        
        # When: UI creates character with mood system
        character_moods = {
            "default": {
                "image": "/images/character_default.png",
                "description": "Normal conversation state"
            },
            "teaching": {
                "image": "/images/character_teaching.png", 
                "trigger_keywords": ["explain", "learn", "understand"],
                "description": "When explaining concepts"
            },
            "helpful": {
                "image": "/images/character_helpful.png",
                "trigger_keywords": ["help", "assist", "support"],
                "description": "When providing assistance"
            }
        }
        
        # Character creation UI should be able to set up moods
        result = mood_service.set_character_moods(character_id, character_moods)
        assert result["success"] is True, "Should successfully set character moods"
        
        # Then: Mood detection should work for knowledge-based conversations
        test_phrases = [
            ("Let me explain this concept", "teaching"),
            ("I can help you with that", "helpful"), 
            ("How are you today?", "default")
        ]
        
        for phrase, expected_mood in test_phrases:
            detected_mood = mood_service.detect_mood(character_id, phrase)
            assert detected_mood == expected_mood, f"Should detect '{expected_mood}' for '{phrase}'"
        
        # And: UI should be able to retrieve mood data for display
        all_moods = mood_service.get_character_moods(character_id)
        assert len(all_moods) == len(character_moods), "Should retrieve all moods"
        assert "teaching" in all_moods, "Should include teaching mood"
        assert "image" in all_moods["teaching"], "Mood should include image for UI display"