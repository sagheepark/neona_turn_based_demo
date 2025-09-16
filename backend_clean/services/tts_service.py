import os
import requests
import base64
import logging
import time
from typing import Optional, Dict, Any
from io import BytesIO

logger = logging.getLogger(__name__)

class TypecastTTSService:
    """Typecast TTS API 서비스"""
    
    def __init__(self):
        self.api_key = os.getenv("TYPECAST_API_KEY") or "__pltGFCASijaw6JxcHMDpKRDcc7PcKRU58AyvHsVnSPW"
        # Typecast API endpoint - can be overridden with TYPECAST_API_URL env var
        self.base_url = os.getenv("TYPECAST_API_URL", "https://api.icepeak.ai/v1")
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        if not self.api_key:
            logger.warning("TYPECAST_API_KEY not found in environment variables")
        else:
            logger.info("✅ Typecast TTS service initialized successfully")
    
    async def get_voices(self, model: str = "ssfm-v21") -> Optional[list]:
        """사용 가능한 음성 목록 조회"""
        try:
            url = f"{self.base_url}/voices"
            params = {"model": model} if model else {}
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                voices = response.json()
                logger.info(f"Retrieved {len(voices)} voices from Typecast")
                return voices
            else:
                logger.error(f"Failed to get voices: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
            return None
    
    async def generate_speech(
        self, 
        text: str, 
        voice_id: str = "tc_61c97b56f1b7877a74df625b",  # Default Emma voice (icepeak.ai)
        emotion: str = "normal",
        speed: float = 1.0,
        model: str = "ssfm-v21",
        character_id: str = None,  # Added for compatibility - ignored in this service
        timeout_seconds: float = 3.0,  # PHASE 1: Aggressive timeout
        **kwargs  # Accept any other parameters for compatibility
    ) -> Optional[str]:
        """텍스트를 음성으로 변환하고 base64로 반환"""
        try:
            # Try real Typecast API first
            url = f"{self.base_url}/text-to-speech"
            
            # 감정을 Typecast 형식으로 매핑
            emotion_mapping = {
                "happy": "happy",
                "sad": "sad",
                "angry": "angry",
                "excited": "toneup",
                "neutral": "normal",
                "normal": "normal",
                "surprised": "toneup",
                "fearful": "tonemid",
                "disgusted": "tonemid",
                "whisper": "whisper"
            }
            
            preset = emotion_mapping.get(emotion, "normal")
            intensity = 2.0 if emotion in ["happy", "excited"] else 1.0
            
            payload = {
                "text": text,
                "model": model,
                "voice_id": voice_id,
                "prompt": {
                    "preset": preset,
                    "preset_intensity": intensity
                }
            }
            
            # Add speed only if it's not the default value  
            if speed != 1.0:
                payload["speed"] = speed
            
            logger.info(f"🎵 Generating TTS for text: '{text[:50]}...' with voice: {voice_id}, emotion: {preset}")
            logger.info(f"🎵 Voice ID being used: {voice_id}")
            print(f"🎵 [TTS SERVICE] Voice ID: {voice_id}, Text: {text[:30]}...")
            logger.info(f"TTS Request payload: {payload}")
            
            # PHASE 1: Use aggressive timeout to prevent 20+ second delays
            response = requests.post(url, headers=self.headers, json=payload, timeout=timeout_seconds)
            
            logger.info(f"TTS Response status: {response.status_code}")
            print(f"🔍 TTS RESPONSE STATUS: {response.status_code}")
            logger.info(f"TTS Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                # 오디오 데이터를 base64로 인코딩
                audio_data = response.content
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                logger.info(f"✅ TTS generated successfully, audio size: {len(audio_data)} bytes")
                return audio_base64
            elif response.status_code == 403:
                # PHASE 1: Fast fallback for auth errors - don't waste time retrying
                logger.warning(f"🚨 TTS auth failed (403) - immediate fallback, no audio")
                print(f"🔇 TTS auth failed (403), immediate fallback")
                return None
            else:
                logger.error(f"TTS generation failed: {response.status_code} - {response.text}")
                print(f"🔇 TTS failed ({response.status_code}), returning None")
                return None
                
        except requests.exceptions.Timeout:
            # PHASE 1: Fast timeout fallback
            logger.warning(f"🚨 TTS timeout after {timeout_seconds}s - immediate fallback, no audio")
            print(f"🔇 TTS timeout after {timeout_seconds}s, immediate fallback")
            return None
        except Exception as e:
            logger.warning(f"🚨 TTS error: {str(e)} - immediate fallback, no audio")
            print(f"🔇 TTS error: {str(e)}, immediate fallback")
            return None
    
    async def get_korean_voices(self) -> list:
        """한국어 음성 목록 조회 - 캐싱 및 최적화 적용"""
        from .voice_cache_service import voice_cache_service
        
        async def load_voices():
            start_time = time.time()
            try:
                # 실제 API에서 전체 목소리 가져오기
                all_voices = await self.get_voices()
                
                if not all_voices:
                    logger.warning("Failed to fetch voices from API, using fallback")
                    return self._get_fallback_voices()
                
                # 성별과 연령대별로 분류하여 다양한 목소리 선택
                processed_voices = []
                
                for voice in all_voices:
                    voice_name = voice.get('voice_name', 'Unknown')
                    voice_id = voice.get('voice_id', '')
                    
                    # 기본 정보 추가
                    processed_voice = {
                        "voice_id": voice_id,
                        "voice_name": voice_name,
                        "model": voice.get('model', 'ssfm-v21'),
                        "emotions": voice.get('emotions', ['normal'])
                    }
                    
                    # 이름 기반으로 성별과 특성 추정
                    if any(name in voice_name.lower() for name in ['emma', 'sophia', 'jennifer', 'margaret', 'kristen', 'glenda', 'nana']):
                        processed_voice.update({
                            "gender": "여성",
                            "age": "20-30대",
                            "description": f"{voice_name} - 여성 목소리"
                        })
                    elif any(name in voice_name.lower() for name in ['duke', 'tyson', 'liam', 'mark', 'jimmy', 'john', 'james']):
                        processed_voice.update({
                            "gender": "남성", 
                            "age": "20-40대",
                            "description": f"{voice_name} - 남성 목소리"
                        })
                    else:
                        processed_voice.update({
                            "gender": "기타",
                            "age": "다양",
                            "description": f"{voice_name} - 다양한 목소리"
                        })
                    
                    processed_voices.append(processed_voice)
                
                processing_time = time.time() - start_time
                logger.info(f"✅ Processed {len(processed_voices)} voices in {processing_time:.2f}s")
                return processed_voices
                
            except Exception as e:
                logger.error(f"Error getting voices: {str(e)}")
                return self._get_fallback_voices()
        
        # 캐시 서비스를 통해 조회
        return await voice_cache_service.get_or_load_voices(load_voices, "korean_voices")
    
    def _get_fallback_voices(self) -> list:
        """API 실패시 폴백 목소리들"""
        return [
            {
                "voice_id": "tc_61c97b56f1b7877a74df625b",
                "voice_name": "Emma",
                "gender": "여성",
                "age": "20대",
                "description": "부드럽고 친근한 여성 목소리"
            },
            {
                "voice_id": "tc_6073b2f6817dccf658bb159f", 
                "voice_name": "Duke",
                "gender": "남성",
                "age": "30대", 
                "description": "차분하고 신뢰감 있는 남성 목소리"
            },
            {
                "voice_id": "tc_624152dced4a43e78f703148",
                "voice_name": "Tyson", 
                "gender": "남성",
                "age": "40대",
                "description": "강인하고 카리스마 있는 남성 목소리"
            }
        ]

# 전역 TTS 서비스 인스턴스 - FIXED: Use working SeolMinSeok TTS instead of broken TypeCast
from .seolminseok_tts_service import seolminseok_tts_service
tts_service = seolminseok_tts_service