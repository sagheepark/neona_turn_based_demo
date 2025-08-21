"""
TDD Tests for Knowledge Management UI Integration
RED PHASE: Write failing tests for frontend knowledge management in create/edit pages
Following TDD methodology: Red → Green → Refactor
"""

import pytest
import json
from pathlib import Path
from typing import Dict, List

class TestKnowledgeUIIntegration:
    """
    Test knowledge management UI integration with backend services
    Ensuring frontend can properly interact with enhanced knowledge services
    """
    
    def test_should_support_knowledge_items_api_for_ui(self):
        """
        Test 17.1: Backend should provide API endpoints for knowledge management UI
        
        RED PHASE: This test will fail until we add REST API endpoints
        """
        from services.knowledge_service import KnowledgeService
        
        # Given: Knowledge service with character data
        service = KnowledgeService()
        character_id = "dr_python"
        
        # When: UI requests character's knowledge items
        knowledge_items = service.get_character_knowledge(character_id)
        
        # Then: Should return list of knowledge items suitable for UI display
        assert isinstance(knowledge_items, list), "Should return list of knowledge items"
        assert len(knowledge_items) > 0, "Should have knowledge items for dr_python"
        
        # And: Each item should have UI-required fields
        for item in knowledge_items:
            assert "id" in item, "Each item should have unique ID for UI tracking"
            assert "title" in item, "Each item should have title for UI display"
            assert "content" in item, "Each item should have content for editing"
            # Support both simplified and legacy keyword formats
            has_keywords = ("keywords" in item or 
                          ("trigger_keywords" in item and "context_keywords" in item))
            assert has_keywords, "Each item should have keywords (simplified or legacy format)"
    
    def test_should_add_knowledge_item_via_api(self):
        """
        Test 17.2: Backend should support adding knowledge items via API calls
        
        RED PHASE: Tests API integration for UI knowledge creation
        """
        from services.knowledge_service import KnowledgeService
        
        # Given: Knowledge service and new knowledge item data
        service = KnowledgeService()
        character_id = "test_character_ui"
        new_item = {
            "title": "Test Knowledge for UI",
            "content": "This is test content for UI integration",
            "keywords": ["test", "ui", "integration", "knowledge"],
            "category": "testing"
        }
        
        # When: UI creates knowledge item via API
        result = service.create_knowledge_item(character_id, new_item)
        
        # Then: Should successfully create item with ID
        assert result["success"] is True, "Should successfully create knowledge item"
        assert "knowledge_id" in result, "Should return generated knowledge ID"
        
        # And: Item should be retrievable for UI display
        created_id = result["knowledge_id"]
        retrieved_item = service.get_knowledge_item(character_id, created_id)
        assert retrieved_item is not None, "Should retrieve created item"
        assert retrieved_item["title"] == new_item["title"], "Should preserve title"
        assert retrieved_item["keywords"] == new_item["keywords"], "Should preserve keywords"
    
    def test_should_update_knowledge_item_via_api(self):
        """
        Test 17.3: Backend should support updating knowledge items for UI edits
        
        RED PHASE: Tests API integration for UI knowledge editing
        """
        from services.knowledge_service import KnowledgeService
        
        # Given: Knowledge service with existing item
        service = KnowledgeService()
        character_id = "test_character_ui"
        
        # Create item first
        original_item = {
            "title": "Original Title",
            "content": "Original content",
            "keywords": ["original", "test"],
            "category": "testing"
        }
        create_result = service.create_knowledge_item(character_id, original_item)
        knowledge_id = create_result["knowledge_id"]
        
        # When: UI updates knowledge item
        updated_data = {
            "title": "Updated Title",
            "keywords": ["updated", "test", "modified"],
            "content": "Updated content with changes"
        }
        update_result = service.update_knowledge_item(character_id, knowledge_id, updated_data)
        
        # Then: Should successfully update item
        assert update_result["success"] is True, "Should successfully update knowledge item"
        
        # And: Changes should be reflected in retrieved item
        updated_item = service.get_knowledge_item(character_id, knowledge_id)
        assert updated_item["title"] == "Updated Title", "Should update title"
        assert "modified" in updated_item["keywords"], "Should update keywords"
        assert updated_item["content"] == "Updated content with changes", "Should update content"
    
    def test_should_delete_knowledge_item_via_api(self):
        """
        Test 17.4: Backend should support deleting knowledge items for UI management
        
        RED PHASE: Tests API integration for UI knowledge deletion
        """
        from services.knowledge_service import KnowledgeService
        
        # Given: Knowledge service with existing item
        service = KnowledgeService()
        character_id = "test_character_ui"
        
        # Create item to delete
        item_to_delete = {
            "title": "Item to Delete",
            "content": "This item will be deleted",
            "keywords": ["delete", "test"],
            "category": "testing"
        }
        create_result = service.create_knowledge_item(character_id, item_to_delete)
        knowledge_id = create_result["knowledge_id"]
        
        # Verify item exists
        assert service.get_knowledge_item(character_id, knowledge_id) is not None
        
        # When: UI deletes knowledge item
        delete_result = service.delete_knowledge_item(character_id, knowledge_id)
        
        # Then: Should successfully delete item
        assert delete_result["success"] is True, "Should successfully delete knowledge item"
        
        # And: Item should no longer be retrievable
        deleted_item = service.get_knowledge_item(character_id, knowledge_id)
        assert deleted_item is None, "Should not find deleted item"
    
    def test_should_support_simplified_keywords_processing(self):
        """
        Test 17.5: Backend should process simplified keywords for UI compatibility
        
        RED PHASE: Tests simplified keyword processing for UI simplicity
        """
        from services.knowledge_service import KnowledgeService
        
        # Given: Knowledge service and simplified keyword input
        service = KnowledgeService()
        
        # When: UI provides keywords as comma-separated string
        knowledge_item_string = {
            "title": "String Keywords Test",
            "content": "Testing string keyword input",
            "keywords": "python, programming, variables, data types",  # String format
            "category": "testing"
        }
        processed_string = service.process_simplified_keywords(knowledge_item_string)
        
        # Then: Should convert string to list
        assert isinstance(processed_string["keywords"], list), "Should convert string to list"
        assert "python" in processed_string["keywords"], "Should include python keyword"
        assert "data types" in processed_string["keywords"], "Should handle spaces correctly"
        
        # When: UI provides keywords as list (already processed)
        knowledge_item_list = {
            "title": "List Keywords Test", 
            "content": "Testing list keyword input",
            "keywords": ["python", "programming", "variables"],  # List format
            "category": "testing"
        }
        processed_list = service.process_simplified_keywords(knowledge_item_list)
        
        # Then: Should maintain list format
        assert isinstance(processed_list["keywords"], list), "Should maintain list format"
        assert len(processed_list["keywords"]) == 3, "Should preserve all keywords"