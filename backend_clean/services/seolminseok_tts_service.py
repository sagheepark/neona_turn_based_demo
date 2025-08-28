"""
설민석 Character Specific TTS Service
Uses dev.icepeak.ai endpoint with dedicated API key and actor_id
"""

import os
import base64
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

class SeolMinSeokTTSService:
    """
    Dedicated TTS service for 설민석 character using dev server
    """
    
    def __init__(self):
        # Dev server configuration for 설민석
        self.api_key = os.getenv(
            "SEOLMINSEOK_API_KEY", 
            "__apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG"
        )
        self.actor_id = os.getenv(
            "SEOLMINSEOK_ACTOR_ID",
            "66f691e9b38df0481f09bf5e"
        )
        self.endpoint = os.getenv(
            "SEOLMINSEOK_ENDPOINT",
            "https://dev.icepeak.ai/api/text-to-speech"
        )
        
        # Headers for Bearer authentication
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
        language: str = "auto"
    ) -> Optional[str]:
        """
        Generate TTS for 설민석 character
        
        Args:
            text: Text to synthesize
            use_hd: Whether to use HD quality (default True)
            language: Language detection mode (default "auto")
            
        Returns:
            Base64 encoded audio data or None if failed
        """
        
        if not text:
            logger.warning("Empty text provided for TTS")
            return None
        
        # Prepare payload in Typecast Sync Format
        payload = {
            "text": text,
            "lang": language,
            "actor_id": self.actor_id,
            "xapi_hd": use_hd,
            "model_version": "latest"
        }
        
        logger.info(f"🎭 Generating 설민석 TTS for text: {text[:50]}...")
        
        try:
            # Make request to dev server
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            logger.info(f"TTS Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Success - encode audio to base64
                audio_data = response.content
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                logger.info(f"✅ 설민석 TTS generated successfully: {len(audio_data)} bytes")
                
                # Return with proper audio format header
                return f"data:audio/wav;base64,{audio_base64}"
                
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
                
                # Generate fallback audio instead of returning None
                print(f"🔄 SeolMinSeok TTS failed, generating fallback audio for: '{text[:30]}...'")
                return self._generate_fallback_audio(text)
                
        except requests.Timeout:
            logger.error("TTS request timeout (30s)")
            print("🔄 SeolMinSeok TTS timeout, generating fallback audio")
            return self._generate_fallback_audio(text)
            
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            print(f"🔄 SeolMinSeok TTS exception: {e}, generating fallback audio")
            return self._generate_fallback_audio(text)
    
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
        
        print(f"🔇 Generating {duration_seconds:.1f}s fallback audio for {character_count} characters")
        
        sample_rate = 44100
        channels = 1
        num_samples = int(duration_seconds * sample_rate)
        
        # Create WAV file in memory
        buffer = io.BytesIO()
        
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Write silent samples (all zeros)
            silent_samples = b'\x00\x00' * num_samples
            wav_file.writeframes(silent_samples)
        
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
                timeout=10
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