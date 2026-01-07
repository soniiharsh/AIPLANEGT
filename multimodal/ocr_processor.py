from PIL import Image
import numpy as np

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except Exception:
    TESSERACT_AVAILABLE = False


class OCRProcessor:
    def __init__(self, confidence_threshold=0.7):
        self.confidence_threshold = confidence_threshold
        self.available = TESSERACT_AVAILABLE

    def process_image(self, image_file):
        """
        OCR with hard guard against missing Tesseract.
        """

        # 🚨 HARD STOP — never call pytesseract if unavailable
        if not self.available:
            return {
                "text": "",
                "confidence": 0.0,
                "needs_review": True,
                "ocr_available": False,
                "error": "Tesseract not available in this environment"
            }

        try:
            image = Image.open(image_file)

            ocr_data = pytesseract.image_to_data(
                image,
                output_type=pytesseract.Output.DICT
            )

            confidences = [
                int(conf) for conf in ocr_data["conf"]
                if conf != "-1"
            ]

            avg_confidence = (
                np.mean(confidences) / 100 if confidences else 0.0
            )

            text = pytesseract.image_to_string(image)

            return {
                "text": text.strip(),
                "confidence": avg_confidence,
                "needs_review": avg_confidence < self.confidence_threshold,
                "ocr_available": True
            }

        except Exception:
            # Safety fallback
            return {
                "text": "",
                "confidence": 0.0,
                "needs_review": True,
                "ocr_available": False,
                "error": "OCR failed during processing"
            }
