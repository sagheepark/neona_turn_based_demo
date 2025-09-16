"""
LLM Cache Manager - Optimize LLM performance with connection pooling and response caching

This system eliminates the overhead of repeatedly initializing OpenAI clients and 
caches similar responses to achieve sub-second response times for repeated interactions.
"""

import asyncio
import hashlib
import json
import logging
import re
import time
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class LLMConnectionPool:
    """Persistent OpenAI client pool to eliminate initialization overhead"""
    
    def __init__(self):
        self.clients = {}  # character_id -> AsyncOpenAI client
        self.client_lock = asyncio.Lock()
        logger.info("✅ LLMConnectionPool initialized")
    
    async def get_client(self, character_id: str = "default") -> AsyncOpenAI:
        """Get or create persistent OpenAI client for character"""
        async with self.client_lock:
            if character_id not in self.clients:
                try:
                    self.clients[character_id] = AsyncOpenAI(
                        base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                        timeout=10.0,  # Optimize timeout
                        max_retries=2   # Reduce retries for speed
                    )
                    logger.info(f"✅ Created persistent LLM client: {character_id}")
                except Exception as e:
                    logger.error(f"❌ Failed to create LLM client for {character_id}: {e}")
                    raise
            
            return self.clients[character_id]
    
    async def warm_up_clients(self, character_ids: List[str]):
        """Pre-warm clients on server startup"""
        for char_id in character_ids:
            try:
                await self.get_client(char_id)
            except Exception as e:
                logger.error(f"❌ Failed to warm up client {char_id}: {e}")
        
        logger.info(f"🔥 Warmed up {len(self.clients)} LLM clients")
    
    def get_stats(self) -> Dict:
        """Get connection pool statistics"""
        return {
            "active_clients": len(self.clients),
            "client_ids": list(self.clients.keys())
        }

class LLMResponseCache:
    """Cache LLM responses for similar interactions"""
    
    def __init__(self):
        self.cache = {}  # context_hash -> cached_response
        self.ttl = 3600  # 1 hour cache
        self.max_size = 1000
        self.stats = {"hits": 0, "misses": 0}
        logger.info("✅ LLMResponseCache initialized")
    
    def generate_cache_key(self, user_input: str, character_id: str, question_context: Dict) -> str:
        """Generate cache key for similar interactions"""
        # Cache based on: answer correctness, question type, character
        key_data = {
            "user_input_normalized": self._normalize_answer(user_input),
            "correct_answer_normalized": self._normalize_answer(question_context.get('correct_answer', '')),
            "character_id": character_id,
            "is_correct": self._is_answer_correct(user_input, question_context.get('correct_answer', '')),
            "question_category": self._categorize_question(question_context.get('question', ''))
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    def _normalize_answer(self, answer: str) -> str:
        """Normalize answers for better cache hits"""
        if not answer:
            return ""
        return re.sub(r'[^가-힣a-zA-Z0-9]', '', answer.lower().strip())
    
    def _is_answer_correct(self, user_answer: str, correct_answer: str) -> bool:
        """Quick correctness check for cache categorization"""
        if not user_answer or not correct_answer:
            return False
        return self._normalize_answer(user_answer) == self._normalize_answer(correct_answer)
    
    def _categorize_question(self, question: str) -> str:
        """Categorize questions for cache grouping"""
        if not question:
            return "general"
        
        question = question.lower()
        if "세종" in question: return "sejong"
        elif "조선" in question: return "joseon"  
        elif "고려" in question: return "goryeo"
        elif "삼국" in question: return "samguk"
        elif "물" in question and ("화학" in question or "H2O" in question): return "chemistry"
        elif "힘" in question or "뉴턴" in question: return "physics"
        elif "상태" in question and "변화" in question: return "matter_states"
        return "general"

    async def get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached LLM response if available"""
        if cache_key in self.cache:
            response, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.ttl:
                self.stats["hits"] += 1
                logger.info(f"🎯 LLM Cache HIT: {cache_key[:8]}... (hit rate: {self.get_hit_rate():.1f}%)")
                return response
            else:
                del self.cache[cache_key]  # Expired
        
        self.stats["misses"] += 1
        logger.info(f"❌ LLM Cache MISS: {cache_key[:8]}... (hit rate: {self.get_hit_rate():.1f}%)")
        return None
    
    async def cache_response(self, cache_key: str, response: Dict):
        """Cache LLM response for future use"""
        # Implement LRU eviction
        if len(self.cache) >= self.max_size:
            # Remove oldest entries
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
            logger.info(f"🧹 Cache evicted oldest entry: {oldest_key[:8]}...")
        
        self.cache[cache_key] = (response, time.time())
        logger.info(f"💾 LLM Cached: {cache_key[:8]}... (size: {len(self.cache)}/{self.max_size})")
    
    def get_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        total = self.stats["hits"] + self.stats["misses"]
        if total == 0:
            return 0.0
        return (self.stats["hits"] / total) * 100
    
    def get_stats(self) -> Dict:
        """Get cache performance statistics"""
        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": self.get_hit_rate(),
            "ttl_hours": self.ttl / 3600
        }
    
    def clear_cache(self):
        """Clear all cached responses"""
        self.cache.clear()
        logger.info("🧹 LLM cache cleared")

class SessionContextCache:
    """Cache session context to avoid database lookups"""
    
    def __init__(self):
        self.context_cache = {}  # session_id -> context
        self.ttl = 1800  # 30 minutes
        self.stats = {"hits": 0, "misses": 0}
        logger.info("✅ SessionContextCache initialized")
    
    async def get_session_context(self, session_id: str) -> Optional[Dict]:
        """Get cached session context"""
        if session_id in self.context_cache:
            context, timestamp = self.context_cache[session_id]
            if time.time() - timestamp < self.ttl:
                self.stats["hits"] += 1
                logger.info(f"🎯 Session Cache HIT: {session_id}")
                return context
            else:
                del self.context_cache[session_id]
                logger.info(f"⏰ Session Cache EXPIRED: {session_id}")
        
        self.stats["misses"] += 1
        logger.info(f"❌ Session Cache MISS: {session_id}")
        return None
    
    async def cache_session_context(self, session_id: str, context: Dict):
        """Cache session context"""
        self.context_cache[session_id] = (context, time.time())
        logger.info(f"💾 Session Cached: {session_id} (size: {len(self.context_cache)})")
    
    def get_stats(self) -> Dict:
        """Get session cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "cache_size": len(self.context_cache),
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "ttl_minutes": self.ttl / 60
        }

class CacheMetrics:
    """Monitor cache performance and hit rates"""
    
    def __init__(self, llm_cache: LLMResponseCache, session_cache: SessionContextCache):
        self.llm_cache = llm_cache
        self.session_cache = session_cache
        logger.info("✅ CacheMetrics initialized")
    
    async def get_performance_stats(self) -> Dict:
        """Get comprehensive cache performance statistics"""
        llm_stats = self.llm_cache.get_stats()
        session_stats = self.session_cache.get_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "llm_cache": llm_stats,
            "session_cache": session_stats,
            "overall_efficiency": self._calculate_overall_efficiency(llm_stats, session_stats)
        }
    
    def _calculate_overall_efficiency(self, llm_stats: Dict, session_stats: Dict) -> str:
        """Calculate overall cache efficiency rating"""
        llm_hit_rate = llm_stats["hit_rate"]
        session_hit_rate = session_stats["hit_rate"]
        
        avg_hit_rate = (llm_hit_rate + session_hit_rate) / 2
        
        if avg_hit_rate >= 80:
            return "Excellent"
        elif avg_hit_rate >= 60:
            return "Good"
        elif avg_hit_rate >= 40:
            return "Fair"
        else:
            return "Poor"

# Global cache instances
llm_pool = LLMConnectionPool()
llm_cache = LLMResponseCache()
session_cache = SessionContextCache()
cache_metrics = CacheMetrics(llm_cache, session_cache)

logger.info("🚀 LLM Cache Manager initialized with all systems ready")