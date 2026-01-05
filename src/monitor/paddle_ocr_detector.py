"""
PaddleOCR-based keyword detection.
Provides high-accuracy text recognition for screen monitoring.
"""

import os
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Optional
import re

from utils.logger import get_logger

logger = get_logger(__name__)

# Try to import PaddleOCR
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    logger.warning("paddleocr not available")


class PaddleOCRDetector:
    """PaddleOCR-based keyword detection."""
    
    def __init__(self, lang: str = "ch", use_gpu: bool = False):
        """
        Initialize PaddleOCR detector.
        
        Args:
            lang: Language for OCR ('ch', 'en', etc.)
            use_gpu: Whether to use GPU for acceleration
        """
        self.lang = lang
        self.use_gpu = use_gpu
        self.ocr = None
        self._initialized = False
        
        # Don't initialize here to avoid thread issues
        # and to speed up main window startup
        logger.debug(f"PaddleOCRDetector created (lang={lang}, gpu={use_gpu})")

    def _initialize_ocr(self):
        """Initialize PaddleOCR instance lazily."""
        if self._initialized:
            return True
            
        if not PADDLE_AVAILABLE:
            logger.error("PaddleOCR package not available")
            return False
            
        try:
            logger.info(f"Initializing PaddleOCR (lang={self.lang}, gpu={self.use_gpu})...")
            # show_log=False to reduce console noise
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(
                use_angle_cls=False, # Changed from True to False for macOS stability
                lang=self.lang, 
                use_gpu=self.use_gpu, 
                show_log=False,
                enable_mkldnn=False,
                use_mp=False
            )
            self._initialized = True
            logger.info("PaddleOCR initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            self._initialized = False
            return False

    def extract_text(self, image: Image.Image) -> str:
        """
        Extract text from image using PaddleOCR.
        
        Args:
            image: Input PIL Image
            
        Returns:
            Extracted text string
        """
        if not self._initialize_ocr():
            return ""
            
        try:
            # Convert PIL Image to numpy array (RGB)
            logger.debug("Converting image to numpy array...")
            img_array = np.array(image.convert('RGB'))
            logger.debug(f"Image array shape: {img_array.shape}")
            
            # Perform OCR
            logger.debug("Starting PaddleOCR inference (ocr.ocr)...")
            # Set cls=False to see if angle classification is the cause
            result = self.ocr.ocr(img_array, cls=False)
            logger.debug("PaddleOCR inference complete")
            
            # Parse result
            # PaddleOCR returns a list of lists: [[[[box], [text, confidence]], ...]]
            # We need to handle potential None results if nothing is detected
            if not result or result[0] is None:
                return ""
                
            text_lines = []
            for line in result[0]:
                text_lines.append(line[1][0])
            
            combined_text = " ".join(text_lines)
            logger.debug(f"PaddleOCR extracted: {combined_text[:100]}...")
            return combined_text
            
        except Exception as e:
            logger.error(f"PaddleOCR extraction failed: {e}")
            return ""

    def detect_keywords(
        self,
        image: Image.Image,
        keywords: List[str],
        case_sensitive: bool = False
    ) -> Dict[str, Any]:
        """
        Detect keywords in image.
        
        Args:
            image: Input image
            keywords: List of keywords to detect
            case_sensitive: Whether to match case-sensitively
        
        Returns:
            Detection result dictionary
        """
        text = self.extract_text(image)
        
        if not text:
            return {
                "detected": False,
                "matched_keywords": [],
                "extracted_text": ""
            }
            
        matched_keywords = []
        contexts = {}
        clean_text = ' '.join(text.split())
        search_text = clean_text if case_sensitive else clean_text.lower()
        
        for keyword in keywords:
            search_keyword = keyword if case_sensitive else keyword.lower()
            match = re.search(re.escape(search_keyword), search_text)
            if match:
                matched_keywords.append(keyword)
                # Extract context
                start = max(0, match.start() - 20)
                end = min(len(clean_text), match.end() + 20)
                contexts[keyword] = f"...{clean_text[start:end]}..."
        
        return {
            "detected": len(matched_keywords) > 0,
            "matched_keywords": matched_keywords,
            "contexts": contexts,
            "extracted_text": text
        }

    @staticmethod
    def is_available() -> bool:
        """Check if PaddleOCR is available."""
        return PADDLE_AVAILABLE
