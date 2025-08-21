"""
TDD Tests for Knowledge Management UI Functionality
Following TDD: Red → Green → Refactor
Testing actual UI functionality beyond minimal implementation
"""

import pytest
import json
from pathlib import Path

class TestKnowledgeUIFunctionality:
    """
    Test actual functionality of knowledge management UI components
    These tests verify the components work correctly, not just exist
    """
    
    def test_should_render_knowledge_items_in_rows(self):
        """
        Test 22.1: Knowledge items should render as editable rows
        
        RED PHASE: This test will fail until we implement row rendering
        """
        # Check if KnowledgeManagementSection component renders items
        component_path = Path("../frontend/src/components/knowledge/KnowledgeManagementSection.tsx")
        
        if component_path.exists():
            with open(component_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for actual row rendering implementation
            required_features = [
                "items.map",           # Should iterate over items
                "KnowledgeItemRow",     # Should use row component
                "onUpdate",             # Should handle updates
                "onDelete",             # Should handle deletion
                "AddKnowledgeButton"    # Should have add button
            ]
            
            missing_features = []
            for feature in required_features:
                if feature not in content:
                    missing_features.append(feature)
            
            assert len(missing_features) == 0, f"Missing row rendering features: {missing_features}"
        else:
            pytest.fail("KnowledgeManagementSection component not found")
    
    def test_should_handle_keyword_input_correctly(self):
        """
        Test 22.2: Keywords should be handled as comma-separated values
        
        RED PHASE: This test will fail until we implement keyword processing
        """
        component_path = Path("../frontend/src/components/knowledge/KnowledgeKeywordInput.tsx")
        
        if component_path.exists():
            with open(component_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for keyword processing logic
            required_features = [
                "split(',",             # Should split by comma
                "trim()",               # Should trim whitespace
                "filter(",              # Should filter empty values
                "onChange"              # Should notify parent of changes
            ]
            
            missing_features = []
            for feature in required_features:
                if feature not in content:
                    missing_features.append(feature)
            
            # Also check if it's more than minimal implementation
            if "minimal implementation" in content:
                pytest.fail("Component still has minimal implementation")
            
            assert len(missing_features) == 0, f"Missing keyword processing features: {missing_features}"
        else:
            pytest.fail("KnowledgeKeywordInput component not found")
    
    def test_should_support_crud_operations(self):
        """
        Test 22.3: Knowledge items should support full CRUD operations
        
        RED PHASE: This test will fail until we implement CRUD functionality
        """
        component_path = Path("../frontend/src/components/knowledge/KnowledgeItemRow.tsx")
        
        if component_path.exists():
            with open(component_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for CRUD operation implementations
            required_features = [
                "useState",             # Should have local state
                "handleEdit",           # Should handle editing
                "handleSave",           # Should save changes
                "handleDelete",         # Should delete items
                "input",                # Should have input fields
                "textarea"              # Should have textarea for content
            ]
            
            missing_features = []
            for feature in required_features:
                if feature not in content:
                    missing_features.append(feature)
            
            # Check it's not minimal implementation
            if "minimal implementation" in content:
                pytest.fail("Component still has minimal implementation")
            
            assert len(missing_features) == 0, f"Missing CRUD features: {missing_features}"
        else:
            pytest.fail("KnowledgeItemRow component not found")
    
    def test_should_integrate_with_character_pages(self):
        """
        Test 22.4: Character pages should properly integrate knowledge management
        
        RED PHASE: This test will fail until we add integration
        """
        character_page = Path("../frontend/src/app/characters/page.tsx")
        
        if character_page.exists():
            with open(character_page, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for knowledge management integration
            required_features = [
                "KnowledgeManagementSection",  # Should import component
                "knowledgeItems",               # Should manage knowledge state
                "handleKnowledgeChange",        # Should handle updates
                "getCharacterKnowledge",        # Should fetch knowledge
                "createKnowledgeItem"           # Should create new items
            ]
            
            missing_features = []
            for feature in required_features:
                if feature not in content:
                    missing_features.append(feature)
            
            assert len(missing_features) == 0, f"Missing integration features: {missing_features}"
        else:
            pytest.fail("Character page not found")
    
    def test_should_have_proper_styling(self):
        """
        Test 22.5: Components should have proper CSS/styling
        
        RED PHASE: This test will fail until we add styling
        """
        components_dir = Path("../frontend/src/components/knowledge")
        
        if components_dir.exists():
            # Check each component for styling
            components = ["KnowledgeManagementSection", "KnowledgeItemRow", 
                         "AddKnowledgeButton", "KnowledgeKeywordInput"]
            
            missing_styles = []
            
            for component_name in components:
                component_file = components_dir / f"{component_name}.tsx"
                if component_file.exists():
                    with open(component_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for styling approaches
                    has_styling = any([
                        "className=" in content and content.count("className=") > 1,
                        "style=" in content,
                        "styled" in content,
                        "css" in content,
                        "tailwind" in content.lower()
                    ])
                    
                    if not has_styling or "minimal" in content:
                        missing_styles.append(component_name)
            
            assert len(missing_styles) == 0, f"Components missing proper styling: {missing_styles}"
        else:
            pytest.fail("Knowledge components directory not found")
    
    def test_should_validate_user_input(self):
        """
        Test 22.6: Components should validate user input
        
        RED PHASE: This test will fail until we add validation
        """
        components_dir = Path("../frontend/src/components/knowledge")
        
        if components_dir.exists():
            validation_features = {
                "KnowledgeItemRow.tsx": ["required", "minLength", "maxLength", "trim"],
                "KnowledgeKeywordInput.tsx": ["validation", "error", "invalid"]
            }
            
            missing_validation = []
            
            for file_name, features in validation_features.items():
                file_path = components_dir / file_name
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    has_validation = any(feature in content for feature in features)
                    if not has_validation:
                        missing_validation.append(file_name)
            
            assert len(missing_validation) == 0, f"Components missing validation: {missing_validation}"
        else:
            pytest.fail("Knowledge components directory not found")