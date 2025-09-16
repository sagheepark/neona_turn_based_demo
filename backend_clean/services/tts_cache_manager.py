"""
TTS Service Pool Manager - Optimize TTS performance with service pooling only

This system eliminates the overhead of repeatedly initializing TTS services.
No response caching - only initialization optimization.
"""

import asyncio
import hashlib
import logging
import re
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class TTSServicePool:
    """Persistent TTS service pool to eliminate initialization overhead"""
    
    def __init__(self):
        self.services = {}  # service_type -> TTS service instance
        self.service_lock = asyncio.Lock()
        logger.info("✅ TTSServicePool initialized")
    
    async def get_tts_service(self, character_id: str):
        """Get or create persistent TTS service"""
        async with self.service_lock:
            service_type = self._get_service_type(character_id)
            
            if service_type not in self.services:
                try:
                    if service_type == "seolminseok":
                        from .seolminseok_tts_service import SeolMinSeokTTSService
                        self.services[service_type] = SeolMinSeokTTSService()
                    else:
                        from .tts_service import TypecastTTSService
                        self.services[service_type] = TypecastTTSService()
                    
                    logger.info(f"✅ Created persistent TTS service: {service_type} for {character_id}")
                except Exception as e:
                    logger.error(f"❌ Failed to create TTS service {service_type} for {character_id}: {e}")
                    raise
            
            return self.services[service_type]
    
    def _get_service_type(self, character_id: str) -> str:
        """Determine TTS service type for character"""
        if 'seol_min_seok' in character_id or character_id == 'dr_genie_science_quiz':
            return "seolminseok"
        return "typecast"

    async def warm_up_services(self):
        """Pre-warm TTS services on server startup"""
        service_types = [
            ("seolminseok", "seol_min_seok_quiz"),
            ("typecast", "default_character")
        ]
        
        for service_type, character_id in service_types:
            try:
                await self.get_tts_service(character_id)
            except Exception as e:
                logger.error(f"❌ Failed to warm up TTS service {service_type}: {e}")
        
        logger.info(f"🔥 Warmed up {len(self.services)} TTS services")
    
    def get_stats(self) -> Dict:
        """Get TTS service pool statistics"""
        return {
            "active_services": len(self.services),
            "service_types": list(self.services.keys())
        }

# TTSResponseCache removed - only initialization optimization now

# TTSCacheMetrics removed - only service pool stats now

# Global TTS service pool instance
tts_pool = TTSServicePool()

logger.info("🚀 TTS Service Pool initialized - initialization optimization only")