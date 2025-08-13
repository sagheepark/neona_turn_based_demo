import json
import asyncio
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class VoiceCacheService:
    """목소리 리스트 캐싱 서비스"""
    
    def __init__(self):
        self.cache: Dict[str, any] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        self.CACHE_DURATION = timedelta(hours=6)  # 6시간 캐시
        self.loading_locks: Dict[str, asyncio.Lock] = {}
        
    async def get_cached_voices(self, cache_key: str = "korean_voices") -> Optional[List[Dict]]:
        """캐시된 목소리 리스트 조회"""
        try:
            # 캐시 유효성 검사
            if cache_key in self.cache and cache_key in self.cache_expiry:
                if datetime.now() < self.cache_expiry[cache_key]:
                    logger.info(f"✅ Returning cached voices ({len(self.cache[cache_key])} voices)")
                    return self.cache[cache_key]
                else:
                    # 만료된 캐시 제거
                    self.invalidate_cache(cache_key)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached voices: {e}")
            return None
    
    async def set_cached_voices(self, voices: List[Dict], cache_key: str = "korean_voices"):
        """목소리 리스트 캐시 저장"""
        try:
            self.cache[cache_key] = voices
            self.cache_expiry[cache_key] = datetime.now() + self.CACHE_DURATION
            logger.info(f"✅ Cached {len(voices)} voices for {self.CACHE_DURATION}")
            
        except Exception as e:
            logger.error(f"Error caching voices: {e}")
    
    def invalidate_cache(self, cache_key: str = "korean_voices"):
        """캐시 무효화"""
        if cache_key in self.cache:
            del self.cache[cache_key]
        if cache_key in self.cache_expiry:
            del self.cache_expiry[cache_key]
        logger.info(f"🗑️ Cache invalidated for {cache_key}")
    
    async def get_or_load_voices(self, loader_func, cache_key: str = "korean_voices") -> List[Dict]:
        """캐시된 목소리 조회 또는 새로 로드 (중복 요청 방지)"""
        try:
            # 캐시 먼저 확인
            cached = await self.get_cached_voices(cache_key)
            if cached is not None:
                return cached
            
            # 로딩 중복 방지를 위한 락
            if cache_key not in self.loading_locks:
                self.loading_locks[cache_key] = asyncio.Lock()
            
            async with self.loading_locks[cache_key]:
                # 다시 한번 캐시 확인 (다른 요청이 이미 로드했을 수 있음)
                cached = await self.get_cached_voices(cache_key)
                if cached is not None:
                    return cached
                
                # 새로 로드
                logger.info(f"🔄 Loading voices from API...")
                start_time = time.time()
                
                voices = await loader_func()
                
                load_time = time.time() - start_time
                logger.info(f"⏱️ Voice loading took {load_time:.2f}s")
                
                if voices:
                    await self.set_cached_voices(voices, cache_key)
                    return voices
                else:
                    logger.warning("Failed to load voices from API")
                    return []
                    
        except Exception as e:
            logger.error(f"Error in get_or_load_voices: {e}")
            return []
    
    def get_cache_stats(self) -> Dict[str, any]:
        """캐시 통계 정보"""
        stats = {}
        for key in self.cache:
            stats[key] = {
                "count": len(self.cache[key]) if isinstance(self.cache[key], list) else 1,
                "expires_at": self.cache_expiry.get(key, "Never").isoformat() if key in self.cache_expiry else "Never",
                "is_expired": key in self.cache_expiry and datetime.now() > self.cache_expiry[key]
            }
        return stats

# 전역 캐시 서비스 인스턴스
voice_cache_service = VoiceCacheService()