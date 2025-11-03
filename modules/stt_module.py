"""
Speech-to-Text Module
Converts audio to text using Whisper
"""

import whisper
import os
import tempfile
import numpy as np
import io
from pydub import AudioSegment


class WhisperSTT:
    """
    Singleton class for Whisper model
    """
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WhisperSTT, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Load Whisper model - only once"""
        print("⏳ Loading Whisper model...")
        self._model = whisper.load_model("base")
        print("✅ Whisper model loaded!")
    
    def transcribe_audio(self, audio_bytes):
        """
        Convert audio bytes to text
        
        Args:
            audio_bytes: Audio data in bytes
        
        Returns:
            transcript text or None
        """
        try:
            print(f"📝 Processing audio ({len(audio_bytes)} bytes)...")
            
            # Convert bytes to AudioSegment using pydub
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
            
            # Export as wav to get proper format
            buffer = io.BytesIO()
            audio = audio.set_frame_rate(16000).set_channels(1)  # Whisper expects 16kHz mono
            audio.export(buffer, format="wav")
            buffer.seek(0)
            
            # Convert to numpy array
            samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
            
            # Normalize based on sample width
            if audio.sample_width == 2:  # 16-bit
                samples = samples / 32768.0
            elif audio.sample_width == 4:  # 32-bit
                samples = samples / 2147483648.0
            
            # Transcribe directly from numpy array
            print("🎤 Transcribing...")
            result = self._model.transcribe(samples, fp16=False, language='en')
            transcript = result["text"].strip()
            
            print(f"✅ Transcription: {transcript[:100]}...")
            return transcript
        
        except Exception as e:
            print(f"❌ Error transcribing: {e}")
            import traceback
            traceback.print_exc()
            return None


# Test function
if __name__ == "__main__":
    whisper_stt = WhisperSTT()
    print("Whisper ready!")