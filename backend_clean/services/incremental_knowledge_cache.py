"""
Incremental Knowledge Cache Service
Implements greeting-triggered caching and incremental knowledge addition for improved RAG performance
"""

import re
from datetime import datetime
from typing import Dict, List, Optional
from .knowledge_service import KnowledgeService


class SessionKnowledge:
    """Data structure for session-specific knowledge cache"""
    
    def __init__(self):
        self.knowledge_base = {}  # topic -> knowledge_items
        self.topic_history = []   # chronological topic tracking
        self.last_updated = datetime.now()
        self.total_items = 0


class IncrementalKnowledgeCache:
    """
    Core caching system that:
    - Proactively caches knowledge from greetings
    - Incrementally adds knowledge as new topics emerge
    - Smart relevance scoring for cached knowledge reuse
    """
    
    def __init__(self):
        self.session_cache = {}  # session_id -> SessionKnowledge
        self.knowledge_service = KnowledgeService()
    
    def cache_greeting_knowledge(self, session_id: str, greeting: str, character_id: str) -> List[Dict]:
        """Extract topics from greeting and cache relevant knowledge"""
        
        # Extract topics from greeting
        topics = self.extract_topics(greeting)
        print(f"🎭 Greeting topics extracted: {topics}")
        
        # Initialize session cache if not exists
        if session_id not in self.session_cache:
            self.session_cache[session_id] = SessionKnowledge()
        
        session_knowledge = self.session_cache[session_id]
        
        # Retrieve knowledge for all topics
        cached_items = []
        for topic in topics:
            if topic and topic not in session_knowledge.knowledge_base:
                knowledge_items = self.knowledge_service.search_relevant_knowledge(
                    topic, character_id, max_results=3
                )
                
                if knowledge_items:
                    session_knowledge.knowledge_base[topic] = knowledge_items
                    session_knowledge.topic_history.append({
                        'topic': topic,
                        'added_at': datetime.now(),
                        'message_context': greeting[:100]
                    })
                    session_knowledge.total_items += len(knowledge_items)
                    cached_items.extend(knowledge_items)
                    
                    print(f"📚 Cached {len(knowledge_items)} items for topic: {topic}")
        
        session_knowledge.last_updated = datetime.now()
        print(f"✅ Cached {len(cached_items)} total knowledge items from greeting")
        
        return cached_items
    
    def add_knowledge_incrementally(self, session_id: str, user_message: str, character_id: str) -> List[Dict]:
        """Add new knowledge only for uncached topics"""
        
        if session_id not in self.session_cache:
            self.session_cache[session_id] = SessionKnowledge()
        
        session_knowledge = self.session_cache[session_id]
        
        # Extract new topics from current message
        new_topics = self.extract_topics(user_message)
        
        # Check which topics are not in cache
        uncached_topics = []
        for topic in new_topics:
            if topic and topic not in session_knowledge.knowledge_base:
                uncached_topics.append(topic)
        
        if uncached_topics:
            print(f"🆕 Adding knowledge for new topics: {uncached_topics}")
            
            # Retrieve knowledge for new topics only
            for topic in uncached_topics:
                knowledge_items = self.knowledge_service.search_relevant_knowledge(
                    topic, character_id, max_results=3
                )
                
                if knowledge_items:
                    session_knowledge.knowledge_base[topic] = knowledge_items
                    session_knowledge.topic_history.append({
                        'topic': topic,
                        'added_at': datetime.now(),
                        'message_context': user_message[:100]
                    })
                    session_knowledge.total_items += len(knowledge_items)
                    
                    print(f"📚 Cached {len(knowledge_items)} items for topic: {topic}")
        
        session_knowledge.last_updated = datetime.now()
        return self.get_relevant_cached_knowledge(session_id, user_message)
    
    def get_relevant_cached_knowledge(self, session_id: str, user_message: str) -> List[Dict]:
        """Get relevant knowledge from accumulated cache"""
        
        if session_id not in self.session_cache:
            return []
        
        session_knowledge = self.session_cache[session_id]
        user_topics = self.extract_topics(user_message)
        
        # Collect relevant knowledge from multiple topics
        relevant_knowledge = []
        
        print(f"🔍 Checking relevance for user message: '{user_message}'")
        print(f"🔍 User topics extracted: {user_topics}")
        print(f"🔍 Available cached topics: {list(session_knowledge.knowledge_base.keys())}")
        
        for topic in session_knowledge.knowledge_base:
            # Calculate topic relevance to current message
            relevance = self.calculate_topic_relevance(topic, user_topics, user_message)
            print(f"📊 Topic '{topic}' relevance: {relevance:.2f}")
            
            if relevance > 0.2:  # Lower threshold for better recall
                knowledge_items = session_knowledge.knowledge_base[topic]
                for item in knowledge_items:
                    relevant_knowledge.append({
                        **item,
                        'cache_topic': topic,
                        'relevance_score': relevance
                    })
                print(f"✅ Using {len(knowledge_items)} items from topic '{topic}'")
            else:
                print(f"❌ Topic '{topic}' below threshold (0.2)")
        
        # If no relevant knowledge found, use all cached knowledge as fallback
        if not relevant_knowledge and session_knowledge.knowledge_base:
            print("🔄 No relevant knowledge found, using all cached knowledge as fallback")
            for topic, knowledge_items in session_knowledge.knowledge_base.items():
                for item in knowledge_items:
                    relevant_knowledge.append({
                        **item,
                        'cache_topic': topic,
                        'relevance_score': 0.4  # Default fallback score
                    })
        
        # Sort by relevance and limit results
        relevant_knowledge.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        result = relevant_knowledge[:5]  # Top 5 most relevant
        print(f"🎯 Using {len(result)} cached knowledge items")
        return result
    
    def extract_topics(self, text: str) -> List[str]:
        """Extract meaningful topics from text"""
        if not text or not text.strip():
            return []
        
        # Define Korean topic patterns
        topic_patterns = [
            r'3·1\s*운동',
            r'유관순',
            r'독립운동',
            r'임시정부',
            r'일제강점기',
            r'역사',
            r'조선시대',
            r'고구려',
            r'백제',
            r'신라',
        ]
        
        topics = []
        
        # Extract specific historical topics
        for pattern in topic_patterns:
            matches = re.findall(pattern, text)
            topics.extend(matches)
        
        # Extract general topics (nouns that might be relevant)
        general_patterns = [
            r'\w+운동',  # movements
            r'\w+시대',  # eras
            r'\w+왕조',  # dynasties
            r'\w+전쟁',  # wars
            r'\w+사건',  # events
        ]
        
        for pattern in general_patterns:
            matches = re.findall(pattern, text)
            topics.extend(matches)
        
        # Extract question/temporal words that are topically relevant
        temporal_patterns = [
            r'언제',
            r'시기',
            r'날짜',
            r'시간',
            r'년도',
        ]
        
        for pattern in temporal_patterns:
            matches = re.findall(pattern, text)
            topics.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_topics = []
        for topic in topics:
            if topic and topic not in seen:
                seen.add(topic)
                unique_topics.append(topic)
        
        return unique_topics
    
    def calculate_topic_relevance(self, cached_topic: str, user_topics: List[str], user_message: str) -> float:
        """Calculate relevance of cached topic to current user message"""
        relevance = 0.0
        
        # Direct topic match
        if cached_topic in user_topics:
            relevance += 0.8
        
        # Substring match in user message
        if cached_topic in user_message:
            relevance += 0.6
        
        # Related topic heuristics
        related_topics = {
            "3·1 운동": ["독립운동", "유관순", "일제강점기", "만세", "시위"],
            "유관순": ["3·1 운동", "독립운동", "학생", "천안"],
            "독립운동": ["3·1 운동", "유관순", "임시정부", "일제강점기"],
            "역사": ["3·1 운동", "유관순", "독립운동", "조선시대", "시대", "과거"]
        }
        
        if cached_topic in related_topics:
            for related in related_topics[cached_topic]:
                if related in user_message:
                    relevance += 0.3
                    break  # Only add once for related topics
        
        # Temporal keywords that might relate to historical topics
        temporal_keywords = ["언제", "시기", "날짜", "년도", "시간"]
        if any(keyword in user_message for keyword in temporal_keywords):
            if any(historical in cached_topic for historical in ["운동", "시대", "전쟁", "사건"]):
                relevance += 0.2
        
        # Cap relevance at 1.0
        return min(relevance, 1.0)