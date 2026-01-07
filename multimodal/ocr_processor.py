import pytesseract
from PIL import Image
import numpy as np

class OCRProcessor:
    def __init__(self, confidence_threshold=0.7):
        self.confidence_threshold = confidence_threshold

    def process_image(self, image_file):
        """
        Safe OCR with graceful fallback when Tesseract is unavailable
        """
        try:
            image = Image.open(image_file)

            ocr_data = pytesseract.image_to_data(
                image,
                output_type=pytesseract.Output.DICT
            )

            confidences = [
                int(conf) for conf in ocr_data['conf']
                if conf != '-1'
            ]

            avg_confidence = (
                np.mean(confidences) / 100 if confidences else 0
            )

            text = pytesseract.image_to_string(image)

            return {
                "text": text.strip(),
                "confidence": avg_confidence,
                "needs_review": avg_confidence < self.confidence_threshold,
                "ocr_available": True
            }

        except Exception as e:
            # 🔑 CRITICAL: graceful fallback
            return {
                "text": "",
                "confidence": 0.0,
                "needs_review": True,
                "ocr_available": False,
                "error": "OCR engine not available in this environment"
            }
