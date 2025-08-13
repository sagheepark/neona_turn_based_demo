import os
import logging
import base64
import tempfile
from typing import Optional
from io import BytesIO

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None

try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_SPEECH_AVAILABLE = True
except ImportError:
    AZURE_SPEECH_AVAILABLE = False
    speechsdk = None

logger = logging.getLogger(__name__)

class AzureSTTService:
    """Azure Speech-to-Text API 서비스"""
    
    def __init__(self):
        self.speech_key = os.getenv("AZURE_SPEECH_KEY")
        self.speech_region = os.getenv("AZURE_SPEECH_REGION", "eastus")
        
        
        if not AZURE_SPEECH_AVAILABLE:
            logger.warning("Azure Speech SDK not available. Install with: pip install azure-cognitiveservices-speech")
            self.available = False
            return
            
        if not self.speech_key:
            logger.warning("AZURE_SPEECH_KEY not found in environment variables")
            self.available = False
            return
            
        try:
            # Create speech config
            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.speech_key, 
                region=self.speech_region
            )
            
            # Set recognition language to Korean
            self.speech_config.speech_recognition_language = "ko-KR"
            
            # Configure audio format
            self.speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_RecoMode,
                "INTERACTIVE"
            )
            
            self.available = True
            logger.info("✅ Azure STT service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure STT: {e}")
            self.available = False
    
    async def transcribe_audio(self, audio_base64: str) -> Optional[str]:
        """
        Base64 인코딩된 오디오를 텍스트로 변환
        
        Args:
            audio_base64: Base64 인코딩된 오디오 데이터
            
        Returns:
            인식된 텍스트 또는 None
        """
        if not self.available:
            logger.warning("Azure STT service not available")
            return None
            
        try:
            # Base64 디코딩
            audio_data = base64.b64decode(audio_base64)
            
            # 오디오 포맷 감지 및 변환 처리
            file_suffix = '.wav'  # 기본값
            logger.info(f"Audio data first 20 bytes: {audio_data[:20]}")
            is_webm_format = False
            
            if audio_data.startswith(b'RIFF'):
                file_suffix = '.wav'
                logger.info("✅ Detected WAV format")
            elif (b'webm' in audio_data[:200].lower() or 
                  audio_data.startswith(b'\x1a\x45\xdf\xa3') or  # EBML header (WebM/Matroska)
                  b'matroska' in audio_data[:200].lower() or
                  b'opus' in audio_data[:200].lower() or
                  b'vorbis' in audio_data[:200].lower()):
                file_suffix = '.webm'
                is_webm_format = True
                logger.info("✅ Detected WebM/Opus format")
            elif audio_data.startswith(b'\x00\x00\x00'):  # MP4 signature
                file_suffix = '.mp4'
                logger.info("✅ Detected MP4 format")
            elif len(audio_data) < 100:
                logger.warning(f"⚠️ Audio data too short: {len(audio_data)} bytes")
                return None
            else:
                # Default assumption for unknown format - try as WebM first since that's what MediaRecorder usually produces
                logger.warning(f"❌ Unknown audio format, first 20 bytes: {audio_data[:20]}")
                file_suffix = '.webm'
                is_webm_format = True
                logger.info("🔄 Assuming WebM format for unknown audio data")
            
            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(suffix=file_suffix, delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Convert WebM to WAV if needed for better compatibility
            wav_file_path = temp_file_path
            if is_webm_format and PYDUB_AVAILABLE:
                try:
                    logger.info("🔄 Converting WebM to WAV for better STT compatibility...")
                    
                    # Load the audio with pydub
                    audio = AudioSegment.from_file(temp_file_path)
                    
                    # Convert to WAV with optimal settings for Azure Speech
                    wav_audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
                    
                    # Save as WAV
                    wav_file_path = temp_file_path.replace(file_suffix, '.wav')
                    wav_audio.export(wav_file_path, format="wav")
                    
                    logger.info(f"✅ Successfully converted to WAV: {wav_file_path}")
                    
                except Exception as convert_error:
                    logger.warning(f"⚠️ WebM conversion failed, trying original: {convert_error}")
                    wav_file_path = temp_file_path
            elif is_webm_format:
                logger.warning("⚠️ pydub not available, cannot convert WebM to WAV")
            
            try:
                logger.info(f"🎤 Starting speech recognition, size: {len(audio_data)} bytes, format: {file_suffix}")
                
                # Use file-based recognition with the converted/original file
                logger.info(f"🎤 Using audio file: {wav_file_path}")
                
                try:
                    audio_input = speechsdk.AudioConfig(filename=wav_file_path)
                    speech_recognizer = speechsdk.SpeechRecognizer(
                        speech_config=self.speech_config,
                        audio_config=audio_input
                    )
                    
                    result = speech_recognizer.recognize_once()
                    
                    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                        logger.info(f"✅ STT successful: '{result.text}'")
                        return result.text
                    elif result.reason == speechsdk.ResultReason.NoMatch:
                        logger.warning("⚠️ No speech could be recognized")
                        return None
                    elif result.reason == speechsdk.ResultReason.Canceled:
                        cancellation_details = result.cancellation_details
                        logger.error(f"❌ STT canceled: {cancellation_details.reason}")
                        if cancellation_details.reason == speechsdk.CancellationReason.Error:
                            logger.error(f"STT error details: {cancellation_details.error_details}")
                        return None
                    else:
                        logger.error(f"❌ STT unexpected result: {result.reason}")
                        return None
                        
                except Exception as recognition_error:
                    logger.error(f"Speech recognition failed: {recognition_error}")
                    return None
                    
            finally:
                # 임시 파일 삭제
                import os
                try:
                    os.unlink(temp_file_path)
                    # Also delete converted WAV file if it's different
                    if wav_file_path != temp_file_path:
                        os.unlink(wav_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error during speech recognition: {str(e)}")
            return None
    
    async def transcribe_audio_stream(self, audio_data: bytes, format: str = "wav") -> Optional[str]:
        """
        오디오 스트림을 텍스트로 변환 (실시간용)
        
        Args:
            audio_data: 원시 오디오 데이터
            format: 오디오 포맷 ("wav", "mp3" 등)
            
        Returns:
            인식된 텍스트 또는 None
        """
        if not self.available:
            logger.warning("Azure STT service not available")
            return None
            
        try:
            # 메모리 스트림에서 오디오 설정
            audio_stream = speechsdk.audio.PushAudioInputStream()
            audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
            
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # 오디오 데이터 스트림에 추가
            audio_stream.write(audio_data)
            audio_stream.close()
            
            # 음성 인식 실행
            result = speech_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                logger.info(f"✅ STT successful: '{result.text}'")
                return result.text
            else:
                logger.warning(f"⚠️ STT failed: {result.reason}")
                return None
                
        except Exception as e:
            logger.error(f"Error during stream recognition: {str(e)}")
            return None
    
    def get_supported_languages(self) -> list:
        """지원되는 언어 목록 반환"""
        return [
            {"code": "ko-KR", "name": "Korean (Korea)"},
            {"code": "en-US", "name": "English (United States)"},
            {"code": "ja-JP", "name": "Japanese (Japan)"},
            {"code": "zh-CN", "name": "Chinese (Mandarin, Simplified)"}
        ]

# 전역 STT 서비스 인스턴스
stt_service = AzureSTTService()