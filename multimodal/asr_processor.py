# multimodal/asr_processor.py

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️ Whisper not installed. Audio input will use fallback.")

class ASRProcessor:
    def __init__(self, model_size="base"):
        if WHISPER_AVAILABLE:
            self.model = whisper.load_model(model_size)
        else:
            self.model = None
    
    def process_audio(self, audio_path):
        """Convert audio to text"""
        if not WHISPER_AVAILABLE:
            return {
                "text": "Audio transcription not available. Please install openai-whisper.",
                "confidence": 0.0,
                "needs_review": True,
                "error": "Whisper not installed"
            }
        
        result = self.model.transcribe(
            audio_path,
            language="en",
            task="transcribe"
        )
        
        return {
            "text": result["text"].strip(),
            "confidence": self._estimate_confidence(result),
            "needs_review": False
        }
    
    def _estimate_confidence(self, result):
        """Estimate confidence from Whisper output"""
        text_length = len(result["text"].split())
        return min(0.9, 0.5 + (text_length / 100))
    
    def is_available(self):
        """Check if Whisper is available"""
        return WHISPER_AVAILABLE