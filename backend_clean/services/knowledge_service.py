import json
import os
import uuid
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime


class KnowledgeService:
    def __init__(self):
        self.knowledge_base_path = Path("knowledge/characters")
        self.knowledge_cache = {}
        self._load_all_knowledge()
    
    def _load_all_knowledge(self):
        """Load character knowledge - minimal implementation"""
        if not self.knowledge_base_path.exists():
            self.knowledge_base_path.mkdir(parents=True, exist_ok=True)
        
        for character_dir in self.knowledge_base_path.iterdir():
            if character_dir.is_dir():
                knowledge_file = character_dir / "knowledge.json"
                if knowledge_file.exists():
                    with open(knowledge_file, 'r', encoding='utf-8') as f:
                        self.knowledge_cache[character_dir.name] = json.load(f)
    
    def search_relevant_knowledge(self, query: str, character_id: str, max_results: int = 3) -> List[Dict]:
        """
        Search for relevant knowledge using weighted keyword matching.
        
        Args:
            query: Search query string
            character_id: ID of the character to search knowledge for
            max_results: Maximum number of results to return
            
        Returns:
            List of knowledge items sorted by relevance score
        """
        # Return empty list if no query or character doesn't exist
        if not query or not query.strip() or character_id not in self.knowledge_cache:
            return []
        
        knowledge_items = self.knowledge_cache[character_id].get("knowledge_items", [])
        scored_results = []
        
        for item in knowledge_items:
            score = self._calculate_relevance_score(query, item)
            if score > 0:
                scored_results.append((score, item))
        
        # Sort by score (highest first) and return top results
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored_results[:max_results]]
    
    def _calculate_relevance_score(self, query: str, knowledge_item: Dict) -> int:
        """
        Calculate relevance score for a knowledge item based on query.
        
        Scoring weights:
        - Trigger keywords: 10 points
        - Title match: 5 points  
        - Tag match: 3 points
        - Content match: 1 point
        """
        score = 0
        query_lower = query.lower()
        
        # Check trigger keywords (highest weight)
        for keyword in knowledge_item.get("trigger_keywords", []):
            if keyword.lower() in query_lower:
                score += 10
        
        # Check title (medium weight)
        if query_lower in knowledge_item.get("title", "").lower():
            score += 5
        
        # Check tags (low weight)
        for tag in knowledge_item.get("tags", []):
            if tag.lower() in query_lower:
                score += 3
        
        # Check content (lowest weight)
        if query_lower in knowledge_item.get("content", "").lower():
            score += 1
            
        return score
    
    def process_simplified_keywords(self, knowledge_item: Dict) -> Dict:
        """
        Process knowledge item with simplified single keywords field
        Minimal implementation for TDD Green phase
        """
        # Keep the simplified keywords field as-is
        if "keywords" in knowledge_item:
            # Ensure keywords is a list
            if isinstance(knowledge_item["keywords"], str):
                knowledge_item["keywords"] = [k.strip() for k in knowledge_item["keywords"].split(",")]
            elif not isinstance(knowledge_item["keywords"], list):
                knowledge_item["keywords"] = []
        return knowledge_item
    
    def search_with_simplified_keywords(self, query: str, character_id: str, knowledge_items: List[Dict]) -> List[Dict]:
        """
        Search using simplified keywords field
        Minimal implementation for TDD Green phase
        """
        results = []
        query_lower = query.lower()
        
        for item in knowledge_items:
            # Check simplified keywords field
            if "keywords" in item:
                for keyword in item["keywords"]:
                    if keyword.lower() in query_lower or query_lower in keyword.lower():
                        results.append(item)
                        break
        
        return results
    
    def add_knowledge_item(self, character_id: str, knowledge_item: Dict) -> Dict:
        """
        Add a knowledge item to a character's knowledge base
        Minimal implementation for TDD Green phase
        """
        # Ensure character directory exists
        char_path = self.knowledge_base_path / character_id
        char_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing knowledge or create new
        knowledge_file = char_path / "knowledge.json"
        if knowledge_file.exists():
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                knowledge_data = json.load(f)
        else:
            knowledge_data = {
                "character_id": character_id,
                "knowledge_items": []
            }
        
        # Add new item with generated ID
        knowledge_item["id"] = f"kb_{uuid.uuid4().hex[:8]}"
        knowledge_item["created_at"] = datetime.now().isoformat()
        knowledge_data["knowledge_items"].append(knowledge_item)
        
        # Save back to file
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
        
        # Update cache
        self.knowledge_cache[character_id] = knowledge_data
        
        return {
            "success": True,
            "knowledge_id": knowledge_item["id"]
        }
    
    def get_character_knowledge(self, character_id: str) -> List[Dict]:
        """
        Get all knowledge items for a character
        Minimal implementation for TDD Green phase
        """
        if character_id in self.knowledge_cache:
            return self.knowledge_cache[character_id].get("knowledge_items", [])
        
        # Try to load from file if not in cache
        knowledge_file = self.knowledge_base_path / character_id / "knowledge.json"
        if knowledge_file.exists():
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                knowledge_data = json.load(f)
                self.knowledge_cache[character_id] = knowledge_data
                return knowledge_data.get("knowledge_items", [])
        
        return []
    
    def create_knowledge_item(self, character_id: str, knowledge_item: Dict) -> Dict:
        """
        Create a new knowledge item (CRUD operation)
        Minimal implementation for TDD Green phase
        """
        return self.add_knowledge_item(character_id, knowledge_item)
    
    def get_knowledge_item(self, character_id: str, knowledge_id: str) -> Optional[Dict]:
        """
        Get a specific knowledge item (CRUD operation)
        Minimal implementation for TDD Green phase
        """
        items = self.get_character_knowledge(character_id)
        for item in items:
            if item.get("id") == knowledge_id:
                return item
        return None
    
    def update_knowledge_item(self, character_id: str, knowledge_id: str, updated_data: Dict) -> Dict:
        """
        Update a knowledge item (CRUD operation)
        Minimal implementation for TDD Green phase
        """
        knowledge_file = self.knowledge_base_path / character_id / "knowledge.json"
        if not knowledge_file.exists():
            return {"success": False, "error": "Knowledge file not found"}
        
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            knowledge_data = json.load(f)
        
        # Find and update the item
        for i, item in enumerate(knowledge_data["knowledge_items"]):
            if item.get("id") == knowledge_id:
                # Merge updated data
                knowledge_data["knowledge_items"][i].update(updated_data)
                knowledge_data["knowledge_items"][i]["updated_at"] = datetime.now().isoformat()
                
                # Save back to file
                with open(knowledge_file, 'w', encoding='utf-8') as f:
                    json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
                
                # Update cache
                self.knowledge_cache[character_id] = knowledge_data
                
                return {"success": True}
        
        return {"success": False, "error": "Knowledge item not found"}
    
    def delete_knowledge_item(self, character_id: str, knowledge_id: str) -> Dict:
        """
        Delete a knowledge item (CRUD operation)
        Minimal implementation for TDD Green phase
        """
        knowledge_file = self.knowledge_base_path / character_id / "knowledge.json"
        if not knowledge_file.exists():
            return {"success": False, "error": "Knowledge file not found"}
        
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            knowledge_data = json.load(f)
        
        # Remove the item
        original_length = len(knowledge_data["knowledge_items"])
        knowledge_data["knowledge_items"] = [
            item for item in knowledge_data["knowledge_items"]
            if item.get("id") != knowledge_id
        ]
        
        if len(knowledge_data["knowledge_items"]) < original_length:
            # Save back to file
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
            
            # Update cache
            self.knowledge_cache[character_id] = knowledge_data
            
            return {"success": True}
        
        return {"success": False, "error": "Knowledge item not found"}