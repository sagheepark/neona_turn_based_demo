"""
TDD Tests for Knowledge Base UI Enhancements
RED PHASE: Write failing tests for simplified knowledge management
Following TDD methodology: Red → Green → Refactor
"""

import pytest
import json
from pathlib import Path
from typing import Dict, List
from services.knowledge_service import KnowledgeService

class TestKnowledgeBaseEnhancements:
    def setup_method(self):
        self.knowledge_service = KnowledgeService()
        
    def test_should_support_simplified_keywords_field(self):
        """
        Test 16.1: Knowledge items should use single 'keywords' field instead of trigger/context
        
        RED PHASE: This test fails because current system uses dual keyword system
        """
        # Given: A knowledge item with simplified keywords
        knowledge_item = {
            "id": "test_001",
            "title": "Python Variables",
            "content": "Variables in Python are used to store data",
            "keywords": ["variables", "data", "storage", "python"],  # Single field
            "category": "fundamentals"
        }
        
        # When: Processing keywords for RAG
        processed_item = self.knowledge_service.process_simplified_keywords(knowledge_item)
        
        # Then: Should handle single keywords field properly
        assert "keywords" in processed_item, "Should maintain keywords field"
        assert isinstance(processed_item["keywords"], list), "Keywords should be a list"
        assert len(processed_item["keywords"]) == 4, "Should preserve all keywords"
        
        # And: Should be searchable with simplified keywords
        results = self.knowledge_service.search_with_simplified_keywords(
            "variables", "test_character", [knowledge_item]
        )
        assert len(results) > 0, "Should find item with simplified keywords"
        
    def test_should_manage_knowledge_items_per_character(self):
        """
        Test 16.2: Characters should have manageable knowledge base collections
        
        RED PHASE: This test fails because knowledge management API doesn't exist
        """
        # Given: A character ID
        character_id = "dr_python"
        
        # When: Adding knowledge items to character
        knowledge_item = {
            "title": "Python Functions",
            "content": "Functions are reusable blocks of code",
            "keywords": ["functions", "def", "return", "parameters"],
            "category": "fundamentals"
        }
        
        result = self.knowledge_service.add_knowledge_item(character_id, knowledge_item)
        
        # Then: Should successfully add knowledge item
        assert result["success"] is True, "Should add knowledge item successfully"
        assert "knowledge_id" in result, "Should return generated knowledge ID"
        
        # And: Should retrieve character's knowledge items
        items = self.knowledge_service.get_character_knowledge(character_id)
        assert len(items) > 0, "Should retrieve knowledge items"
        assert items[-1]["title"] == "Python Functions", "Should include added item"
        
    def test_should_support_character_mood_system(self):
        """
        Test 16.3: Characters should have mood/expression system for dynamic images
        
        RED PHASE: This test fails because mood system doesn't exist
        """
        # Given: Character mood configuration
        from services.character_mood_service import CharacterMoodService
        mood_service = CharacterMoodService()
        
        character_id = "dr_python"
        moods = {
            "default": {
                "image": "/images/dr_python_default.png",
                "description": "Normal conversational state"
            },
            "teaching": {
                "image": "/images/dr_python_teaching.png",
                "trigger_keywords": ["explain", "variables", "functions"],
                "description": "When explaining concepts"
            },
            "encouraging": {
                "image": "/images/dr_python_happy.png",
                "trigger_keywords": ["good", "excellent", "correct"],
                "description": "When praising"
            }
        }
        
        # When: Setting character moods
        result = mood_service.set_character_moods(character_id, moods)
        
        # Then: Should store mood configuration
        assert result["success"] is True, "Should set moods successfully"
        
        # And: Should detect mood from conversation
        detected_mood = mood_service.detect_mood(character_id, "Let me explain variables to you")
        assert detected_mood == "teaching", "Should detect teaching mood"
        
        # And: Should return appropriate image
        mood_data = mood_service.get_mood_data(character_id, detected_mood)
        assert mood_data["image"] == "/images/dr_python_teaching.png", "Should return teaching image"
        
    def test_should_enhance_rag_with_smart_processing(self):
        """
        Test 16.4: RAG should intelligently process simplified keywords
        
        RED PHASE: This test fails because smart RAG processing doesn't exist
        """
        # Given: User query with partial matches
        query = "how to declare vars"
        character_id = "dr_python"
        
        # When: Smart RAG processes query
        from services.enhanced_knowledge_service import EnhancedKnowledgeService
        enhanced_service = EnhancedKnowledgeService()
        
        results = enhanced_service.smart_search(query, character_id)
        
        # Then: Should find relevant content despite partial match
        assert len(results) > 0, "Should find results with smart matching"
        
        # And: Should understand semantic similarity
        # "vars" should match "variables" through semantic understanding
        found_variables = any("variable" in r.get("title", "").lower() for r in results)
        assert found_variables, "Should match 'vars' to 'variables' semantically"
        
        # And: Should rank by enhanced relevance
        if len(results) > 1:
            first_score = results[0].get("relevance_score", 0)
            second_score = results[1].get("relevance_score", 0)
            assert first_score >= second_score, "Should rank by relevance"
            
    def test_should_support_knowledge_crud_operations(self):
        """
        Test 16.5: Should support Create, Read, Update, Delete for knowledge items
        
        RED PHASE: This test fails because CRUD operations don't exist
        """
        character_id = "test_character"
        
        # CREATE
        new_item = {
            "title": "Test Knowledge",
            "content": "Test content",
            "keywords": ["test", "demo"],
            "category": "test"
        }
        created = self.knowledge_service.create_knowledge_item(character_id, new_item)
        assert created["success"] is True, "Should create knowledge item"
        knowledge_id = created["knowledge_id"]
        
        # READ
        item = self.knowledge_service.get_knowledge_item(character_id, knowledge_id)
        assert item is not None, "Should read knowledge item"
        assert item["title"] == "Test Knowledge", "Should have correct title"
        
        # UPDATE
        updated_data = {
            "title": "Updated Knowledge",
            "keywords": ["test", "demo", "updated"]
        }
        updated = self.knowledge_service.update_knowledge_item(character_id, knowledge_id, updated_data)
        assert updated["success"] is True, "Should update knowledge item"
        
        # Verify update
        item = self.knowledge_service.get_knowledge_item(character_id, knowledge_id)
        assert item["title"] == "Updated Knowledge", "Should have updated title"
        assert "updated" in item["keywords"], "Should have updated keywords"
        
        # DELETE
        deleted = self.knowledge_service.delete_knowledge_item(character_id, knowledge_id)
        assert deleted["success"] is True, "Should delete knowledge item"
        
        # Verify deletion
        item = self.knowledge_service.get_knowledge_item(character_id, knowledge_id)
        assert item is None, "Should not find deleted item"