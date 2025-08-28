"""
Fallback TTS Service
Generates silent audio with appropriate duration when TTS APIs are unavailable
"""

import base64
import struct
import wave
import io
import logging

logger = logging.getLogger(__name__)

class FallbackTTSService:
    """
    Fallback TTS service that generates silent audio with realistic duration
    """
    
    def __init__(self):
        self.sample_rate = 44100  # Standard CD quality
        self.channels = 1  # Mono
        self.sample_width = 2  # 16-bit audio
        logger.info("✅ Fallback TTS service initialized")
    
    def generate_silent_audio(self, text: str, words_per_minute: int = 180) -> str:
        """
        Generate silent audio with duration based on text length
        
        Args:
            text: Text to calculate duration for
            words_per_minute: Average speaking rate (default 180 WPM for Korean)
            
        Returns:
            Base64 encoded WAV audio data
        """
        if not text:
            # Very short silence for empty text
            duration_seconds = 0.5
        else:
            # Calculate realistic duration based on text length
            word_count = len(text.split())
            character_count = len(text)
            
            # For Korean text, use character count for more accuracy
            # Average Korean speaking rate: ~300-400 characters per minute
            if any(ord(char) > 127 for char in text):  # Contains non-ASCII (likely Korean)
                duration_seconds = (character_count / 350) * 60  # 350 chars per minute
            else:
                duration_seconds = (word_count / words_per_minute) * 60
            
            # Minimum 1 second, maximum 30 seconds
            duration_seconds = max(1.0, min(30.0, duration_seconds))
        
        # Generate silent audio samples
        num_samples = int(duration_seconds * self.sample_rate)
        
        # Create WAV file in memory
        buffer = io.BytesIO()
        
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(self.sample_width)
            wav_file.setframerate(self.sample_rate)
            
            # Write silent samples (all zeros)
            silent_samples = b'\x00\x00' * num_samples
            wav_file.writeframes(silent_samples)
        
        # Get WAV data and encode to base64
        buffer.seek(0)
        wav_data = buffer.read()
        audio_base64 = base64.b64encode(wav_data).decode('utf-8')
        
        logger.info(f"🔇 Generated {duration_seconds:.1f}s silent audio for text: '{text[:30]}...'")
        
        return audio_base64
    
    async def generate_tts(
        self, 
        text: str,
        voice_id: str = None,
        emotion: str = "normal",
        **kwargs
    ) -> str:
        """
        Generate fallback TTS (silent audio with appropriate duration)
        
        Args:
            text: Text to synthesize
            voice_id: Voice ID (ignored in fallback)
            emotion: Emotion (ignored in fallback)
            **kwargs: Additional parameters (ignored)
            
        Returns:
            Base64 encoded silent audio
        """
        return self.generate_silent_audio(text)