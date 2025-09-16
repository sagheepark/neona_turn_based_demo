"""
설민석 Character Specific TTS Service
Uses dev.icepeak.ai endpoint with dedicated API key and actor_id
"""

import os
import base64
import logging
import requests
import time
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

class SeolMinSeokTTSService:
    """
    Dedicated TTS service for 설민석 character using dev server
    """
    
    def __init__(self):
        # RESTORE ORIGINAL WORKING CONFIGURATION
        self.api_key = os.getenv(
            "SEOLMINSEOK_API_KEY", 
            # "__apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG"
            "__api3ZQqMgVdr396HCJDWQmDi2a9ZDgXBP7hPRhaMv3x"
        )
        self.actor_id = os.getenv(
            "SEOLMINSEOK_ACTOR_ID",
            # "68c8ee2697ab32576d3eaa05"
            # "618b1849ef7827cfea34ea1e"
            "68c8ee2697ab32576d3eaa05"
        )
        self.endpoint = os.getenv(
            "SEOLMINSEOK_ENDPOINT",
            # "https://dev.icepeak.ai/api/text-to-speech"
            "https://typecast.ai/api/text-to-speech"
        )
        
        # RESTORE ORIGINAL WORKING HEADERS
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"SeolMinSeok TTS Service initialized")
        logger.info(f"Endpoint: {self.endpoint}")
        logger.info(f"Actor ID: {self.actor_id}")
    
    async def generate_tts(
        self, 
        text: str,
        use_hd: bool = True,
        language: str = "auto",
        timeout_seconds: float = 100.0,  # WORKING: Tested with 10s timeout successfully
        request_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate TTS for 설민석 character
        
        Args:
            text: Text to synthesize
            use_hd: Whether to use HD quality (default True)
            language: Language detection mode (default "auto")
            timeout_seconds: Timeout for the request
            request_id: Optional request ID for performance tracking
            
        Returns:
            Base64 encoded audio data or None if failed
        """
        
        if not text:
            logger.warning("Empty text provided for TTS")
            return None
        
        # Generate request ID if not provided
        if not request_id:
            request_id = f"tts_seol_{int(time.time() * 1000)}"
        
        # RESTORE ORIGINAL WORKING PAYLOAD FORMAT
        payload = {
            "text": text,
            "lang": language,
            "actor_id": self.actor_id,
            "xapi_hd": use_hd,
            "model_version": "latest"
        }

        logger.info(f"🎭 Generating 설민석 TTS for text: {text[:50]}...")
        
        try:
            # PHASE 1: Use aggressive timeout to prevent 20+ second delays
            
            print(f"TTS start: {text[:20]}...")
            start_time = time.time()
            async with httpx.AsyncClient() as client:
               response =  await client.post(
                    self.endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=timeout_seconds
                )
            end_time = time.time()
            print(f"TTS time: {end_time - start_time}, {text[:20]}...")
            
            logger.info(f"TTS Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Success - encode audio to base64
                audio_data = response.content
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                logger.info(f"✅ 설민석 TTS generated successfully: {len(audio_data)} bytes")
                
                # Return with proper audio format header
                return f"data:audio/wav;base64,{audio_base64}"
                
            elif response.status_code == 403:
                # NO FALLBACK - FORCE PRIMARY TTS FIX
                logger.error(f"🚨 설민석 TTS auth failed (403) - NO FALLBACK, FIX AUTH")
                print(f"❌ 설민석 TTS auth failed (403) - PRIMARY TTS MUST WORK")
                raise RuntimeError(f"TTS AUTH FAILURE: {response.text}")
            else:
                logger.error(f"TTS generation failed: HTTP {response.status_code}")
                
                # Log error details  
                try:
                    error_data = response.json()
                    logger.error(f"Error details: {error_data}")
                    print(f"TTS generation failed: {response.status_code} - {error_data}")
                except:
                    logger.error(f"Error response: {response.text[:200]}")
                    print(f"TTS generation failed: {response.status_code} - {response.text}")
                
                print(f"❌ SeolMinSeok TTS failed - NO FALLBACK, FIX PRIMARY")
                raise RuntimeError(f"TTS FAILURE: {response.status_code} - {response.text}")
                
        except requests.Timeout:
            logger.error(f"🚨 설민석 TTS timeout after {timeout_seconds}s - SERVICE TOO SLOW")
            print(f"❌ 설민석 TTS timeout after {timeout_seconds}s - Service response too slow")
            # Return None instead of raising - let caller handle gracefully
            return None
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"🚨 ] {str(e)}")
            print(f"❌ 설민석 TTS error: {str(e)}")
            # Return None instead of raising - let caller handle gracefully
            return None
    
    def _generate_fallback_audio(self, text: str) -> str:
        """
        Generate fallback silent audio with appropriate duration
        
        Args:
            text: Text to calculate duration for
            
        Returns:
            Base64 encoded WAV audio with data URI format
        """
        import struct
        import wave
        import io
        
        # Calculate realistic duration based on Korean text
        character_count = len(text)
        # For Korean text: ~350 characters per minute
        duration_seconds = max(2.0, min(15.0, (character_count / 350) * 60))
        
        print(f"🔊 Generating {duration_seconds:.1f}s audible fallback audio for {character_count} characters")
        
        sample_rate = 44100
        channels = 1
        num_samples = int(duration_seconds * sample_rate)
        
        # Create WAV file in memory
        buffer = io.BytesIO()
        
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Generate audible tone instead of silence
            # Create a gentle tone that plays for 1 second, then silence
            tone_duration = min(1.0, duration_seconds)  # 1 second tone max
            tone_samples = int(tone_duration * sample_rate)
            
            # Generate a pleasant 440Hz tone (A note) for the first part
            import math
            frequency = 440  # A note frequency
            tone_data = []
            
            # Create tone samples
            for i in range(tone_samples):
                # Fade in/out for smoother sound
                fade_samples = int(0.1 * sample_rate)  # 0.1 second fade
                amplitude = 0.1  # Gentle volume
                
                if i < fade_samples:
                    amplitude *= (i / fade_samples)  # Fade in
                elif i > tone_samples - fade_samples:
                    amplitude *= ((tone_samples - i) / fade_samples)  # Fade out
                
                # Generate sine wave sample
                sample = int(amplitude * 32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
                tone_data.extend(struct.pack('<h', sample))  # 16-bit little-endian
            
            # Add silence for remaining duration
            remaining_samples = num_samples - tone_samples
            silence_data = b'\x00\x00' * remaining_samples
            
            # Write tone + silence
            wav_file.writeframes(bytes(tone_data) + silence_data)
        
        # Get WAV data and encode to base64
        buffer.seek(0)
        wav_data = buffer.read()
        audio_base64 = base64.b64encode(wav_data).decode('utf-8')
        
        # Return with data URI format like the successful response
        return f"data:audio/wav;base64,{audio_base64}"
    
    def test_connection(self) -> bool:
        """
        Test if the TTS service is accessible
        
        Returns:
            True if service is working, False otherwise
        """
        
        test_payload = {
            "text": "테스트",
            "lang": "auto",
            "actor_id": self.actor_id,
            "xapi_hd": False,  # Use lower quality for test
            "model_version": "latest"
        }
        
        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=test_payload,
                timeout=100
            )
            
            if response.status_code == 200:
                logger.info("✅ 설민석 TTS service connection test successful")
                return True
            else:
                logger.error(f"❌ 설민석 TTS service test failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 설민석 TTS service test error: {e}")
            return False
    
    async def generate_speech(self, text: str, character_id: str = None, **kwargs) -> Optional[str]:
        """
        Compatibility method that maps to generate_tts
        Added to fix method name mismatch errors
        Accepts character_id parameter but ignores it since this service is character-specific
        """
        # Extract timeout if provided in kwargs for Phase 1 optimization
        timeout_seconds = kwargs.get('timeout_seconds', 100.0)
        return await self.generate_tts(text, timeout_seconds=timeout_seconds)

# Singleton instance
seolminseok_tts_service = SeolMinSeokTTSService()

# Convenience function for direct use
async def generate_seolminseok_tts(text: str) -> Optional[str]:
    """
    Convenience function to generate 설민석 TTS
    
    Args:
        text: Text to synthesize
        
    Returns:
        Base64 encoded audio data or None if failed
    """
    return await seolminseok_tts_service.generate_tts(text)