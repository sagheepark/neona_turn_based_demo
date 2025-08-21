"""
TDD Tests for Frontend Knowledge Management Components
RED PHASE: Write failing tests for frontend UI components that don't exist yet
Following TDD methodology: Red → Green → Refactor
"""

import pytest
import json
import requests
from pathlib import Path

class TestFrontendKnowledgeComponents:
    """
    Test frontend knowledge management UI components
    These tests define what frontend components need to be implemented
    """
    
    def test_should_have_character_creation_with_knowledge_management(self):
        """
        Test 20.1: Character creation/edit pages should include knowledge management UI
        
        RED PHASE: This test will fail until we add knowledge UI to character pages
        """
        # This test documents what the frontend needs to implement:
        # 1. Character create/edit pages should have knowledge management section
        # 2. Knowledge section should allow adding/editing/deleting knowledge items
        # 3. Each knowledge item should be editable in rows
        # 4. Keywords should be simple input (comma-separated or tag-based)
        
        # For now, we'll test that the API integration is ready for frontend
        import requests
        
        # Test that frontend can create a character with knowledge
        character_data = {
            "name": "Test Character",
            "description": "Character for testing knowledge UI",
            "knowledge_items": [
                {
                    "title": "Character Introduction",
                    "content": "This character specializes in testing",
                    "keywords": ["testing", "character", "demo"],
                    "category": "introduction"
                },
                {
                    "title": "Character Skills", 
                    "content": "Expert in frontend testing and UI development",
                    "keywords": ["frontend", "testing", "ui", "development"],
                    "category": "skills"
                }
            ]
        }
        
        # Frontend should be able to create knowledge items via API
        character_id = "test_ui_character"
        
        try:
            # Test creating multiple knowledge items (what the UI will do)
            for knowledge_item in character_data["knowledge_items"]:
                response = requests.post(
                    f"http://localhost:8000/api/characters/{character_id}/knowledge",
                    json=knowledge_item,
                    timeout=5
                )
                assert response.status_code == 201, f"Should create knowledge item: {knowledge_item['title']}"
                
                data = response.json()
                assert data["success"] is True, "Should return success"
                assert "knowledge_id" in data, "Should return knowledge ID for UI tracking"
                
        except requests.exceptions.ConnectionError:
            pytest.fail("Backend API not available - needed for frontend integration")
    
    def test_should_support_simplified_keyword_input(self):
        """
        Test 20.2: Knowledge UI should support simplified keyword input
        
        RED PHASE: This test defines how the frontend should handle keywords
        """
        # Test that the API supports the simplified keyword formats that UI will send
        
        # Test different keyword input formats that the UI might send
        keyword_formats = [
            {
                "description": "Comma-separated string",
                "keywords": "python, programming, variables, data types",
                "expected": ["python", "programming", "variables", "data types"]
            },
            {
                "description": "Array of strings", 
                "keywords": ["functions", "def", "return", "parameters"],
                "expected": ["functions", "def", "return", "parameters"]
            },
            {
                "description": "Mixed case and spacing",
                "keywords": "API, Rest, JSON , HTTP   ",
                "expected": ["API", "Rest", "JSON", "HTTP"]
            }
        ]
        
        character_id = "test_keyword_formats"
        
        try:
            for i, format_test in enumerate(keyword_formats):
                knowledge_item = {
                    "title": f"Keyword Test {i+1}: {format_test['description']}",
                    "content": f"Testing {format_test['description']} format",
                    "keywords": format_test["keywords"],
                    "category": "testing"
                }
                
                response = requests.post(
                    f"http://localhost:8000/api/characters/{character_id}/knowledge",
                    json=knowledge_item,
                    timeout=5
                )
                
                assert response.status_code == 201, f"Should handle {format_test['description']}"
                
                # Verify the knowledge was stored correctly
                response = requests.get(f"http://localhost:8000/api/characters/{character_id}/knowledge")
                knowledge_items = response.json()
                
                # Find our created item
                created_item = None
                for item in knowledge_items:
                    if item["title"] == knowledge_item["title"]:
                        created_item = item
                        break
                
                assert created_item is not None, "Should find created knowledge item"
                
                # Keywords should be stored as array regardless of input format
                assert isinstance(created_item["keywords"], list), "Keywords should be stored as list"
                
        except requests.exceptions.ConnectionError:
            pytest.fail("Backend API not available - needed for testing keyword formats")
    
    def test_should_support_knowledge_crud_operations_for_ui(self):
        """
        Test 20.3: Frontend should be able to perform all CRUD operations
        
        RED PHASE: This test ensures API supports all UI operations
        """
        character_id = "test_crud_ui"
        
        try:
            # CREATE - UI creates new knowledge item
            create_data = {
                "title": "CRUD Test Knowledge",
                "content": "Testing CRUD operations for UI",
                "keywords": ["crud", "ui", "testing"],
                "category": "testing"
            }
            
            response = requests.post(
                f"http://localhost:8000/api/characters/{character_id}/knowledge",
                json=create_data,
                timeout=5
            )
            assert response.status_code == 201, "UI should be able to create knowledge"
            knowledge_id = response.json()["knowledge_id"]
            
            # READ - UI fetches all knowledge items for editing
            response = requests.get(f"http://localhost:8000/api/characters/{character_id}/knowledge")
            assert response.status_code == 200, "UI should be able to read knowledge"
            knowledge_items = response.json()
            assert len(knowledge_items) > 0, "Should have created knowledge item"
            
            # UPDATE - UI edits existing knowledge item
            update_data = {
                "character_id": character_id,
                "title": "Updated CRUD Test Knowledge",
                "keywords": ["crud", "ui", "testing", "updated"],
                "content": "Updated content from UI"
            }
            
            response = requests.put(
                f"http://localhost:8000/api/knowledge/{knowledge_id}",
                json=update_data,
                timeout=5
            )
            assert response.status_code == 200, "UI should be able to update knowledge"
            assert response.json()["success"] is True, "Update should succeed"
            
            # DELETE - UI removes knowledge item
            response = requests.delete(
                f"http://localhost:8000/api/knowledge/{knowledge_id}",
                json={"character_id": character_id},
                timeout=5
            )
            assert response.status_code == 200, "UI should be able to delete knowledge"
            assert response.json()["success"] is True, "Delete should succeed"
            
        except requests.exceptions.ConnectionError:
            pytest.fail("Backend API not available - needed for UI CRUD operations")
    
    def test_should_validate_character_page_integration_requirements(self):
        """
        Test 20.4: Character pages should integrate knowledge management properly
        
        RED PHASE: This test defines integration requirements for character pages
        """
        # This test documents what the character create/edit pages need:
        
        # 1. Knowledge management section in character form
        # 2. Ability to add multiple knowledge items
        # 3. Row-based editing (each knowledge item as a row)
        # 4. Simple keyword input (not complex dual-field system)
        # 5. Category selection for organization
        
        # Test that the API supports batch operations that the UI will need
        character_id = "test_character_integration"
        
        # Simulate what the character creation UI will do:
        # Create character with multiple knowledge items in one session
        knowledge_items = [
            {
                "title": "Character Personality",
                "content": "This character is friendly and helpful",
                "keywords": ["personality", "friendly", "helpful"],
                "category": "personality"
            },
            {
                "title": "Character Background",
                "content": "Experienced in customer service and support",
                "keywords": ["background", "experience", "support"],
                "category": "background"
            },
            {
                "title": "Character Skills",
                "content": "Expert in problem-solving and communication",
                "keywords": ["skills", "problem-solving", "communication"],
                "category": "skills"
            }
        ]
        
        try:
            created_ids = []
            
            # UI should be able to create multiple knowledge items quickly
            for knowledge_item in knowledge_items:
                response = requests.post(
                    f"http://localhost:8000/api/characters/{character_id}/knowledge",
                    json=knowledge_item,
                    timeout=5
                )
                assert response.status_code == 201, f"Should create {knowledge_item['title']}"
                created_ids.append(response.json()["knowledge_id"])
            
            # UI should be able to retrieve all knowledge for editing
            response = requests.get(f"http://localhost:8000/api/characters/{character_id}/knowledge")
            assert response.status_code == 200, "Should retrieve all knowledge"
            
            all_knowledge = response.json()
            assert len(all_knowledge) >= len(knowledge_items), "Should have all created items"
            
            # Verify each item has the required fields for UI display
            for item in all_knowledge:
                if item["id"] in created_ids:
                    # Required fields for UI components
                    required_fields = ["id", "title", "content", "keywords", "category"]
                    for field in required_fields:
                        assert field in item, f"UI needs '{field}' field in knowledge items"
                    
                    # Keywords should be in a format the UI can work with
                    assert isinstance(item["keywords"], list), "UI expects keywords as list"
                    
        except requests.exceptions.ConnectionError:
            pytest.fail("Backend API not available - needed for character page integration")
    
    def test_should_support_frontend_error_handling(self):
        """
        Test 20.5: API should provide proper error responses for frontend
        
        RED PHASE: This test ensures API provides good error responses for UI
        """
        try:
            # Test invalid knowledge creation (missing required fields)
            invalid_knowledge = {
                "title": "",  # Empty title
                "content": "",  # Empty content
                "keywords": [],  # Empty keywords
                "category": ""  # Empty category
            }
            
            response = requests.post(
                f"http://localhost:8000/api/characters/test_errors/knowledge",
                json=invalid_knowledge,
                timeout=5
            )
            
            # API should handle validation errors gracefully for UI
            assert response.status_code in [400, 422], "Should return validation error"
            
            # Test updating non-existent knowledge
            response = requests.put(
                "http://localhost:8000/api/knowledge/non_existent_id",
                json={
                    "character_id": "test_character",
                    "title": "Updated Title"
                },
                timeout=5
            )
            
            # Should return proper error response for UI to handle
            assert response.status_code in [404, 400], "Should handle non-existent knowledge"
            
            # Test deleting non-existent knowledge
            response = requests.delete(
                "http://localhost:8000/api/knowledge/non_existent_id",
                json={"character_id": "test_character"},
                timeout=5
            )
            
            # Should return proper error response
            assert response.status_code in [404, 400], "Should handle non-existent knowledge deletion"
            
        except requests.exceptions.ConnectionError:
            pytest.fail("Backend API not available - needed for error handling tests")