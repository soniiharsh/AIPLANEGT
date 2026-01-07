import google.generativeai as genai

class GeminiASR:
    def __init__(self, model):
        self.model = model

    def transcribe_audio(self, uploaded_file):
        """
        Uses Gemini to transcribe audio.
        """
        audio_bytes = uploaded_file.read()

        prompt = """
        Transcribe this audio accurately.
        Preserve mathematical expressions.
        Do not summarize.
        """

        response = self.model.generate_content(
            [
                prompt,
                {
                    "mime_type": uploaded_file.type,
                    "data": audio_bytes
                }
            ]
        )

        return {
            "text": response.text.strip(),
            "confidence": 0.85,
            "needs_review": True
        }
