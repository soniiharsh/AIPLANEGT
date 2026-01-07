from PIL import Image

class OCRProcessor:
    """
    Cloud-safe OCR processor.

    On platforms without system Tesseract (e.g. Streamlit Cloud),
    OCR is intentionally disabled and routed to HITL.
    """

    def __init__(self, confidence_threshold=0.7):
        self.confidence_threshold = confidence_threshold
        self.available = False   # 🔑 FORCE DISABLE OCR

    def process_image(self, image_file):
        # Always fallback to HITL on cloud
        try:
            Image.open(image_file)  # just to validate image
        except Exception:
            pass

        return {
            "text": "",
            "confidence": 0.0,
            "needs_review": True,
            "ocr_available": False,
            "error": "OCR disabled (system Tesseract not available)"
        }
