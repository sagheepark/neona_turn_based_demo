"""
Enhanced Knowledge Service with smart RAG processing
Minimal implementation for TDD Green phase
"""

from typing import List, Dict
from services.knowledge_service import KnowledgeService


class EnhancedKnowledgeService(KnowledgeService):
    def __init__(self):
        super().__init__()
        self.semantic_mappings = {
            "vars": ["variables", "variable", "var"],
            "func": ["function", "functions", "method", "methods"],
            "def": ["define", "definition", "declare", "declaration"],
            "param": ["parameter", "parameters", "argument", "arguments"],
            "dict": ["dictionary", "dictionaries", "hashmap", "map"],
            "list": ["array", "arrays", "collection"],
            "str": ["string", "strings", "text"],
            "int": ["integer", "integers", "number", "numbers"]
        }
    
    def smart_search(self, query: str, character_id: str) -> List[Dict]:
        """
        Enhanced search with semantic understanding
        Minimal implementation for TDD Green phase
        """
        # Get character's knowledge
        knowledge_items = self.get_character_knowledge(character_id)
        if not knowledge_items:
            return []
        
        # Expand query with semantic understanding
        expanded_terms = self._expand_query_semantically(query)
        
        # Score and rank results
        scored_results = []
        for item in knowledge_items:
            score = self._calculate_smart_score(query, expanded_terms, item)
            if score > 0:
                item_with_score = item.copy()
                item_with_score["relevance_score"] = score
                scored_results.append((score, item_with_score))
        
        # Sort by score
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        return [item for score, item in scored_results]
    
    def _expand_query_semantically(self, query: str) -> List[str]:
        """
        Expand query terms with semantic understanding
        """
        query_lower = query.lower()
        expanded = [query_lower]
        
        # Check for semantic mappings
        for short_form, expansions in self.semantic_mappings.items():
            if short_form in query_lower:
                expanded.extend(expansions)
        
        # Split query into words and check each
        words = query_lower.split()
        for word in words:
            if word in self.semantic_mappings:
                expanded.extend(self.semantic_mappings[word])
        
        return list(set(expanded))  # Remove duplicates
    
    def _calculate_smart_score(self, original_query: str, expanded_terms: List[str], item: Dict) -> float:
        """
        Calculate relevance score with semantic understanding
        Supports both simplified 'keywords' and legacy 'trigger_keywords'/'context_keywords'
        """
        score = 0.0
        
        # Check keywords (both new simplified and legacy formats)
        keywords_to_check = []
        
        # New simplified format
        if "keywords" in item:
            keywords_to_check.extend(item.get("keywords", []))
        
        # Legacy format
        if "trigger_keywords" in item:
            keywords_to_check.extend(item.get("trigger_keywords", []))
        if "context_keywords" in item:
            keywords_to_check.extend(item.get("context_keywords", []))
        
        # Score keywords
        for keyword in keywords_to_check:
            keyword_lower = keyword.lower()
            # Direct match
            if original_query.lower() in keyword_lower or keyword_lower in original_query.lower():
                score += 10
            # Semantic match
            for term in expanded_terms:
                if term in keyword_lower or keyword_lower in term:
                    score += 5
        
        # Check title
        title_lower = item.get("title", "").lower()
        if original_query.lower() in title_lower:
            score += 7
        for term in expanded_terms:
            if term in title_lower:
                score += 3
        
        # Check content
        content_lower = item.get("content", "").lower()
        if original_query.lower() in content_lower:
            score += 2
        for term in expanded_terms:
            if term in content_lower:
                score += 1
        
        return score