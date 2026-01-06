import whisper

class ASRProcessor:
    def __init__(self, model_size="base"):
        self.model = whisper.load_model(model_size)
    
    def process_audio(self, audio_path):
        """Convert audio to text"""
        result = self.model.transcribe(
            audio_path,
            language="en",
            task="transcribe"
        )
        
        return {
            "text": result["text"].strip(),
            "confidence": self._estimate_confidence(result),
            "needs_review": False  # Whisper doesn't provide confidence
        }
    
    def _estimate_confidence(self, result):
        """Estimate confidence from Whisper output"""
        # Whisper doesn't provide confidence, use heuristics
        text_length = len(result["text"].split())
        return min(0.9, 0.5 + (text_length / 100))