import google.generativeai as genai
from PIL import Image
import io

class GeminiOCR:
    def __init__(self, model):
        self.model = model

    def extract_text(self, uploaded_file):
        """
        Uses Gemini Vision to extract text from image.
        """
        image_bytes = uploaded_file.read()
        image = Image.open(io.BytesIO(image_bytes))

        prompt = """
        Extract the complete math problem text from this image.
        Preserve mathematical symbols and expressions.
        Do NOT solve the problem.
        Return only the extracted text.
        """

        response = self.model.generate_content(
            [prompt, image]
        )

        return {
            "text": response.text.strip(),
            "confidence": 0.9,   # Gemini vision is highly reliable
            "needs_review": True  # Always allow HITL editing
        }
