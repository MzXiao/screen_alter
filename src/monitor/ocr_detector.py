"""
OCR-based keyword detection.
Extracts text from images and matches keywords.
"""

from PIL import Image
from typing import List, Dict, Any, Optional
import re

from utils.logger import get_logger

logger = get_logger(__name__)

# Try to import OCR engines
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logger.warning("easyocr not available")


class OCRDetector:
    """OCR-based keyword detection."""
    
    def __init__(self, engine: str = "pytesseract", language: str = "chi_sim+eng"):
        """
        Initialize OCR detector.
        
        Args:
            engine: OCR engine to use ('pytesseract' or 'easyocr')
            language: Language(s) for OCR
        """
        self.engine = engine
        self.language = language
        self.easyocr_reader = None
        
        # Validate engine availability
        if engine == "pytesseract" and not PYTESSERACT_AVAILABLE:
            raise RuntimeError("pytesseract is not installed")
        elif engine == "easyocr" and not EASYOCR_AVAILABLE:
            raise RuntimeError("easyocr is not installed")
        
        # Initialize EasyOCR reader if needed
        if engine == "easyocr" and EASYOCR_AVAILABLE:
            try:
                # Convert language format (chi_sim -> ch_sim, eng -> en)
                lang_codes = []
                if "chi_sim" in language or "chi" in language:
                    lang_codes.append("ch_sim")
                if "eng" in language or "en" in language:
                    lang_codes.append("en")
                
                self.easyocr_reader = easyocr.Reader(lang_codes or ['ch_sim', 'en'])
                logger.info(f"EasyOCR initialized with languages: {lang_codes}")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")
                raise
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: Input image
        
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        image = image.convert('L')
        
        # Enhance contrast (optional, can improve accuracy)
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        return image
    
    def extract_text_pytesseract(self, image: Image.Image) -> str:
        """
        Extract text using pytesseract.
        
        Args:
            image: Input image
        
        Returns:
            Extracted text
        """
        try:
            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Extract text
            text = pytesseract.image_to_string(processed_image, lang=self.language)
            
            logger.debug(f"Extracted text (pytesseract): {text[:100]}...")
            return text
            
        except Exception as e:
            logger.error(f"pytesseract extraction failed: {e}")
            return ""
    
    def extract_text_easyocr(self, image: Image.Image) -> str:
        """
        Extract text using EasyOCR.
        
        Args:
            image: Input image
        
        Returns:
            Extracted text
        """
        try:
            if not self.easyocr_reader:
                logger.error("EasyOCR reader not initialized")
                return ""
            
            # EasyOCR works with numpy arrays or file paths
            import numpy as np
            img_array = np.array(image)
            
            # Extract text
            results = self.easyocr_reader.readtext(img_array)
            
            # Combine all detected text
            text = " ".join([result[1] for result in results])
            
            logger.debug(f"Extracted text (easyocr): {text[:100]}...")
            return text
            
        except Exception as e:
            logger.error(f"EasyOCR extraction failed: {e}")
            return ""
    
    def extract_text(self, image: Image.Image) -> str:
        """
        Extract text from image using configured engine.
        
        Args:
            image: Input image
        
        Returns:
            Extracted text
        """
        if self.engine == "pytesseract":
            return self.extract_text_pytesseract(image)
        elif self.engine == "easyocr":
            return self.extract_text_easyocr(image)
        else:
            logger.error(f"Unknown OCR engine: {self.engine}")
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
            Detection result dictionary with:
                - detected: bool
                - matched_keywords: List[str]
                - extracted_text: str
        """
        # Extract text from image
        text = self.extract_text(image)
        
        if not text:
            return {
                "detected": False,
                "matched_keywords": [],
                "extracted_text": ""
            }
        
        # Match keywords
        matched_keywords = []
        contexts = {}
        search_text = text if case_sensitive else text.lower()
        
        # Clean text for better context (replace multiple newlines/spaces)
        clean_text = ' '.join(text.split())
        clean_search_text = clean_text if case_sensitive else clean_text.lower()
        
        for keyword in keywords:
            search_keyword = keyword if case_sensitive else keyword.lower()
            
            match = re.search(re.escape(search_keyword), clean_search_text)
            if match:
                matched_keywords.append(keyword)
                
                # Extract context (20 chars before and after)
                start = max(0, match.start() - 20)
                end = min(len(clean_text), match.end() + 20)
                context = f"...{clean_text[start:end]}..."
                contexts[keyword] = context
        
        result = {
            "detected": len(matched_keywords) > 0,
            "matched_keywords": matched_keywords,
            "contexts": contexts,
            "extracted_text": text
        }
        
        if result["detected"]:
            for kw, ctx in contexts.items():
                logger.info(f"Matched '{kw}' in context: {ctx}")
        
        return result

    
    @staticmethod
    def is_available(engine: str = "pytesseract") -> bool:
        """
        Check if OCR engine is available.
        
        Args:
            engine: Engine to check
        
        Returns:
            True if available
        """
        if engine == "pytesseract":
            return PYTESSERACT_AVAILABLE
        elif engine == "easyocr":
            return EASYOCR_AVAILABLE
        return False
