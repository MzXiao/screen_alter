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
    import platform
    if platform.system() == "Darwin":
        # 针对 Mac Homebrew 路径进行显式指定
        pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
    elif platform.system() == "Windows":
         # Windows下通常需要用户自行安装Tesseract并配置环境变量，或者在此指定默认路径
         # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
         pass
    
    # 测试一下
    try:
        logger.info(f"Tesseract version check: {pytesseract.get_tesseract_version()}")
    except Exception as e:
        logger.warning(f"Tesseract check failed (might be not installed or path issue): {e}")


except ImportError:
    PYTESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available")




class OCRDetector:
    """OCR-based keyword detection."""
    
    def __init__(self, engine: str = "pytesseract", language: str = "chi_sim+eng"):
        """
        Initialize OCR detector.
        
        Args:
            engine: OCR engine to use ('pytesseract')
            language: Language(s) for OCR
        """
        self.engine = engine
        self.language = language
        
        # Validate engine availability
        if engine == "pytesseract" and not PYTESSERACT_AVAILABLE:
            raise RuntimeError("pytesseract is not installed")
        
        # We only support pytesseract here (plus paddleocr which is separate)
        if engine != "pytesseract":
             raise ValueError(f"Unknown or unsupported engine: {engine}")
    
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
        return False
