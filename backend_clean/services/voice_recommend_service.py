import requests
import os
from typing import List, Dict, Optional
import json
import asyncio

class VoiceRecommendService:
    def __init__(self):
        self.base_url = "https://neona-voice-recommend-dev.z2.neosapience.xyz"
        self.timeout = 30
        
        # TTS API 설정
        self.tts_api_key = os.getenv("TYPECAST_API_KEY") or "__pltGFCASijaw6JxcHMDpKRDcc7PcKRU58AyvHsVnSPW"
        self.tts_base_url = os.getenv("TYPECAST_API_URL", "https://api.icepeak.ai/v1")
        self.tts_headers = {
            "X-API-KEY": self.tts_api_key,
            "Content-Type": "application/json"
        }
        
        # 매핑 테이블 제거 - 나중에 올바른 매핑 방법 찾은 후 다시 구현
        
        # 이름 기반 매칭을 위한 캐시
        self._tts_voices_cache = None
        self._cache_timestamp = 0
        self._cache_duration = 3600  # 1시간
    
    async def _get_tts_voices(self) -> List[Dict]:
        """TTS API에서 사용 가능한 목소리 목록을 가져옵니다 (캐시 사용)"""
        import time
        current_time = time.time()
        
        # 캐시가 유효한지 확인
        if (self._tts_voices_cache is not None and 
            current_time - self._cache_timestamp < self._cache_duration):
            return self._tts_voices_cache
        
        try:
            response = requests.get(
                f"{self.tts_base_url}/voices",
                headers=self.tts_headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                voices = response.json()
                self._tts_voices_cache = voices
                self._cache_timestamp = current_time
                print(f"✅ TTS API에서 {len(voices)}개 목소리 정보를 가져왔습니다")
                return voices
            else:
                print(f"❌ TTS API 목소리 조회 실패: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ TTS API 목소리 조회 오류: {e}")
            return []
    
    async def _find_voice_by_name(self, voice_name: str) -> Optional[str]:
        """이름으로 TTS API voice_id를 찾습니다"""
        tts_voices = await self._get_tts_voices()
        
        if not tts_voices:
            return None
        
        # 정확한 이름 매칭 시도
        for voice in tts_voices:
            if voice.get("voice_name") == voice_name:
                print(f"✅ 정확한 이름 매칭: {voice_name} → {voice.get('voice_id')}")
                return voice.get("voice_id")
        
        # 부분 매칭 시도 (케이스 무관)
        voice_name_lower = voice_name.lower()
        for voice in tts_voices:
            tts_name_lower = voice.get("voice_name", "").lower()
            if voice_name_lower in tts_name_lower or tts_name_lower in voice_name_lower:
                print(f"✅ 부분 이름 매칭: {voice_name} → {voice.get('voice_name')} ({voice.get('voice_id')})")
                return voice.get("voice_id")
        
        print(f"⚠️ 이름으로 매칭된 목소리를 찾을 수 없음: {voice_name}")
        return None
        
    async def recommend_voices(self, character_prompt: str, top_k: int = 5) -> List[Dict]:
        """
        Recommend suitable voices based on character description
        
        Args:
            character_prompt: Character personality description
            top_k: Number of recommendations to return
            
        Returns:
            List of recommended voices with scores
        """
        try:
            response = requests.post(
                f"{self.base_url}/recommend",
                json={
                    "persona_raw": character_prompt,
                    "top_k": top_k
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                recommendations = response.json()
                
                # 매핑 없이 추천 결과를 그대로 반환 (한글 이름 표시용)
                formatted = []
                
                for rec in recommendations:
                    original_voice_id = rec.get("voice_id")
                    voice_name = rec.get("name", "Unknown")
                    
                    formatted.append({
                        "voice_id": None,  # 매핑 해결 전까지 None
                        "voice_name": voice_name,  # 한글 이름 표시
                        "score": rec.get("match_percent", 0) / 100.0,
                        "gender": rec.get("gender", "Unknown"),
                        "age": rec.get("age", "Unknown"),
                        "description": f"AI 추천 목소리 - {voice_name} (매칭률: {rec.get('match_percent', 0)}%)",
                        "original_voice_id": original_voice_id,  # 나중에 매핑에 사용
                        "mapping_needed": True  # 매핑이 필요함을 표시
                    })
                
                print(f"✅ 추천 결과 {len(formatted)}개 (매핑 없이 한글 이름만 표시)")
                return formatted
                
            else:
                print(f"Voice recommendation API error: {response.status_code}")
                return self._get_default_recommendations()
                
        except requests.exceptions.Timeout:
            print("Voice recommendation API timeout")
            return self._get_default_recommendations()
        except Exception as e:
            print(f"Error calling voice recommendation API: {e}")
            return self._get_default_recommendations()
    
    def _get_default_recommendations(self) -> List[Dict]:
        """기본 목소리 추천 반환 (항상 결과가 있도록)"""
        return [
            {
                "voice_id": "tc_61c97b56f1b7877a74df625b",  # Emma
                "voice_name": "희연",
                "score": 0.75,
                "gender": "Female",
                "age": "Adult",
                "description": "밝고 친근한 목소리 (기본 추천)",
                "original_voice_id": "neo_ko_2022_a3"
            },
            {
                "voice_id": "tc_6621c95cd872405d1a6de98e",  # Kristen
                "voice_name": "수지",
                "score": 0.70,
                "gender": "Female", 
                "age": "Young Adult",
                "description": "부드럽고 따뜻한 목소리 (기본 추천)",
                "original_voice_id": "yuna_general_clean_mix_cats3"
            },
            {
                "voice_id": "tc_6073b2f6817dccf658bb159f",  # Duke
                "voice_name": "하린",
                "score": 0.65,
                "gender": "Male",
                "age": "Adult", 
                "description": "안정적이고 신뢰감 있는 목소리 (기본 추천)",
                "original_voice_id": "seungyun_slowwoman_plugin"
            }
        ]
    
    async def get_voice_preview_text(self, language: str = "en") -> str:
        """
        Get appropriate preview text for voice testing
        
        Args:
            language: Language code (en, ko, etc.)
            
        Returns:
            Preview text string
        """
        preview_texts = {
            "en": "This is my voice. I hope you like how I sound.",
            "ko": "안녕하세요. 제 목소리입니다. 어떠신가요?"
        }
        
        return preview_texts.get(language, preview_texts["en"])

# Initialize service
voice_recommend_service = VoiceRecommendService()