"""
TDD Tests for Knowledge Management REST API Endpoints
RED PHASE: Write failing tests for API endpoints that don't exist yet
Following TDD methodology: Red → Green → Refactor
"""

import pytest
import requests
import json
from pathlib import Path

class TestKnowledgeAPIEndpoints:
    """
    Test REST API endpoints for knowledge management
    These tests will fail until we implement the actual API endpoints in main.py
    """
    
    BASE_URL = "http://localhost:8000"
    
    def test_should_have_get_character_knowledge_endpoint(self):
        """
        Test 19.1: GET /api/characters/{character_id}/knowledge endpoint
        
        RED PHASE: This test will fail until we add the endpoint to main.py
        """
        # Given: Character with knowledge items
        character_id = "dr_python"
        
        # When: Frontend requests character's knowledge via API
        try:
            response = requests.get(f"{self.BASE_URL}/api/characters/{character_id}/knowledge")
            
            # Then: Should return 200 with knowledge items
            assert response.status_code == 200, "Should return success status"
            
            data = response.json()
            assert isinstance(data, list), "Should return list of knowledge items"
            
            # Each item should have required fields for UI
            if data:  # If knowledge items exist
                sample_item = data[0]
                required_fields = ["id", "title", "content", "category"]
                for field in required_fields:
                    assert field in sample_item, f"Knowledge item should have '{field}' field"
                
        except requests.exceptions.ConnectionError:
            # Expected to fail in RED phase - endpoint doesn't exist yet
            pytest.fail("API endpoint /api/characters/{character_id}/knowledge not implemented yet")
    
    def test_should_have_create_knowledge_endpoint(self):
        """
        Test 19.2: POST /api/characters/{character_id}/knowledge endpoint
        
        RED PHASE: This test will fail until we add the endpoint to main.py
        """
        # Given: New knowledge item data
        character_id = "test_character"
        new_knowledge = {
            "title": "API Test Knowledge",
            "content": "Testing knowledge creation via API",
            "keywords": ["api", "test", "knowledge"],
            "category": "testing"
        }
        
        # When: Frontend creates knowledge via API
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/characters/{character_id}/knowledge",
                json=new_knowledge
            )
            
            # Then: Should return 201 with created knowledge ID
            assert response.status_code == 201, "Should return created status"
            
            data = response.json()
            assert "success" in data, "Should return success status"
            assert data["success"] is True, "Should indicate successful creation"
            assert "knowledge_id" in data, "Should return generated knowledge ID"
            
        except requests.exceptions.ConnectionError:
            # Expected to fail in RED phase - endpoint doesn't exist yet
            pytest.fail("API endpoint POST /api/characters/{character_id}/knowledge not implemented yet")
    
    def test_should_have_update_knowledge_endpoint(self):
        """
        Test 19.3: PUT /api/knowledge/{knowledge_id} endpoint
        
        GREEN PHASE: Test with actual knowledge item creation first
        """
        # Given: Create a knowledge item first
        character_id = "test_character_update"
        
        # Create knowledge item
        create_data = {
            "title": "Original API Test Knowledge",
            "content": "Original testing content",
            "keywords": ["api", "test", "original"],
            "category": "testing"
        }
        
        try:
            # First create the item
            create_response = requests.post(
                f"{self.BASE_URL}/api/characters/{character_id}/knowledge",
                json=create_data,
                timeout=5
            )
            assert create_response.status_code == 201, "Should create knowledge item first"
            create_data_result = create_response.json()
            knowledge_id = create_data_result["knowledge_id"]
            
            # Now test update
            update_data = {
                "title": "Updated API Test Knowledge",
                "keywords": ["api", "test", "updated"],
                "content": "Updated content via API"
            }
            
            # When: Frontend updates knowledge via API
            response = requests.put(
                f"{self.BASE_URL}/api/knowledge/{knowledge_id}",
                json={
                    "character_id": character_id,  # Need character_id for context
                    **update_data
                },
                timeout=5
            )
            
            # Then: Should return 200 with success status
            assert response.status_code == 200, "Should return success status"
            
            data = response.json()
            assert "success" in data, "Should return success status"
            assert data["success"] is True, "Should indicate successful update"
            
        except requests.exceptions.ConnectionError:
            pytest.fail("API server not running - start backend server to test endpoints")
    
    def test_should_have_delete_knowledge_endpoint(self):
        """
        Test 19.4: DELETE /api/knowledge/{knowledge_id} endpoint
        
        GREEN PHASE: Test with actual knowledge item creation first
        """
        # Given: Create a knowledge item first to delete
        character_id = "test_character_delete"
        
        # Create knowledge item
        create_data = {
            "title": "Knowledge to Delete",
            "content": "This will be deleted",
            "keywords": ["api", "test", "delete"],
            "category": "testing"
        }
        
        try:
            # First create the item
            create_response = requests.post(
                f"{self.BASE_URL}/api/characters/{character_id}/knowledge",
                json=create_data,
                timeout=5
            )
            assert create_response.status_code == 201, "Should create knowledge item first"
            create_data_result = create_response.json()
            knowledge_id = create_data_result["knowledge_id"]
            
            # When: Frontend deletes knowledge via API
            response = requests.delete(
                f"{self.BASE_URL}/api/knowledge/{knowledge_id}",
                json={"character_id": character_id},  # Need character_id for context
                timeout=5
            )
            
            # Then: Should return 200 with success status
            assert response.status_code == 200, "Should return success status"
            
            data = response.json()
            assert "success" in data, "Should return success status"
            assert data["success"] is True, "Should indicate successful deletion"
            
        except requests.exceptions.ConnectionError:
            pytest.fail("API server not running - start backend server to test endpoints")
    
    def test_should_handle_api_error_cases(self):
        """
        Test 19.5: API endpoints should handle error cases properly
        
        RED PHASE: This test will fail until we implement proper error handling
        """
        try:
            # Test: Non-existent character
            response = requests.get(f"{self.BASE_URL}/api/characters/non_existent/knowledge")
            # Should return empty list or appropriate error, not crash
            assert response.status_code in [200, 404], "Should handle non-existent character gracefully"
            
            # Test: Invalid knowledge creation
            invalid_knowledge = {"title": ""}  # Missing required fields
            response = requests.post(
                f"{self.BASE_URL}/api/characters/test/knowledge",
                json=invalid_knowledge
            )
            # Should return validation error
            assert response.status_code == 422, "Should validate knowledge data"
            
        except requests.exceptions.ConnectionError:
            # Expected to fail in RED phase - endpoints don't exist yet
            pytest.fail("API endpoints not implemented yet - error handling can't be tested")

    def test_api_endpoints_implemented(self):
        """
        Test that API endpoints are implemented and working
        GREEN phase test to confirm endpoints exist
        """
        # Test that the knowledge endpoints are working
        try:
            # Test GET endpoint
            response = requests.get(f"{self.BASE_URL}/api/characters/dr_python/knowledge", timeout=5)
            assert response.status_code == 200, "GET endpoint should work"
            
            # Test POST endpoint
            test_knowledge = {
                "title": "API Test Knowledge",
                "content": "Testing API functionality",
                "keywords": ["api", "test"],
                "category": "testing"
            }
            response = requests.post(
                f"{self.BASE_URL}/api/characters/api_test_char/knowledge",
                json=test_knowledge,
                timeout=5
            )
            assert response.status_code == 201, "POST endpoint should work"
            
            data = response.json()
            assert data["success"] is True, "Should return success"
            assert "knowledge_id" in data, "Should return knowledge_id"
            
        except requests.exceptions.ConnectionError:
            pytest.fail("API server not running - start backend server to test endpoints")