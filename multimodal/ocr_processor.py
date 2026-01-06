import pytesseract
from PIL import Image
import numpy as np

class OCRProcessor:
    def __init__(self, confidence_threshold=0.7):
        self.confidence_threshold = confidence_threshold
    
    def process_image(self, image_path):
        """Extract text from image with confidence scores"""
        image = Image.open(image_path)
        
        # Get detailed OCR data
        ocr_data = pytesseract.image_to_data(
            image, 
            output_type=pytesseract.Output.DICT
        )
        
        # Calculate average confidence
        confidences = [
            int(conf) for conf in ocr_data['conf'] 
            if conf != '-1'
        ]
        avg_confidence = np.mean(confidences) / 100 if confidences else 0
        
        # Extract text
        text = pytesseract.image_to_string(image)
        
        return {
            "text": text.strip(),
            "confidence": avg_confidence,
            "needs_review": avg_confidence < self.confidence_threshold,
            "raw_data": ocr_data
        }