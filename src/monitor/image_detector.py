"""
Image similarity detection.
Compares screenshots with reference images using perceptual hashing.
"""

from PIL import Image
import imagehash
from typing import List, Dict, Any, Tuple
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)


class ImageDetector:
    """Image similarity detection using perceptual hashing."""
    
    def __init__(self, threshold: float = 0.85):
        """
        Initialize image detector.
        
        Args:
            threshold: Similarity threshold (0-1, higher means more similar)
        """
        self.threshold = threshold
    
    def _compute_hash(self, image: Image.Image, hash_size: int = 8) -> imagehash.ImageHash:
        """
        Compute perceptual hash of an image.
        
        Args:
            image: Input image
            hash_size: Hash size (larger = more precise but slower)
        
        Returns:
            Image hash
        """
        # Use average hash (fast and effective)
        return imagehash.average_hash(image, hash_size=hash_size)
    
    def calculate_similarity(self, image1: Image.Image, image2: Image.Image) -> float:
        """
        Calculate similarity between two images.
        
        Args:
            image1: First image
            image2: Second image
        
        Returns:
            Similarity score (0-1, 1 means identical)
        """
        try:
            hash1 = self._compute_hash(image1)
            hash2 = self._compute_hash(image2)
            
            # Calculate Hamming distance
            distance = hash1 - hash2
            
            # Convert to similarity score (0-1)
            # Max distance for 8x8 hash is 64
            max_distance = 64
            similarity = 1.0 - (distance / max_distance)
            
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def compare_with_references(
        self,
        screenshot: Image.Image,
        reference_images: List[str]
    ) -> Dict[str, Any]:
        """
        Compare screenshot with reference images.
        
        Args:
            screenshot: Screenshot to check
            reference_images: List of reference image paths
        
        Returns:
            Detection result dictionary with:
                - detected: bool
                - matches: List[Dict] with 'path' and 'similarity'
                - best_match: Dict or None
        """
        matches = []
        
        for ref_path in reference_images:
            try:
                # Load reference image
                ref_image = Image.open(ref_path)
                
                # Calculate similarity
                similarity = self.calculate_similarity(screenshot, ref_image)
                
                if similarity >= self.threshold:
                    matches.append({
                        'path': ref_path,
                        'similarity': similarity
                    })
                    logger.info(f"Match found: {ref_path} (similarity: {similarity:.2f})")
                
            except Exception as e:
                logger.error(f"Failed to process reference image {ref_path}: {e}")
                continue
        
        # Sort matches by similarity (highest first)
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        result = {
            "detected": len(matches) > 0,
            "matches": matches,
            "best_match": matches[0] if matches else None
        }
        
        return result
    
    def validate_reference_image(self, image_path: str) -> Tuple[bool, str]:
        """
        Validate a reference image.
        
        Args:
            image_path: Path to image
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path = Path(image_path)
            
            if not path.exists():
                return False, "文件不存在"
            
            if not path.is_file():
                return False, "不是有效的文件"
            
            # Try to open as image
            with Image.open(path) as img:
                # Check if it's a valid image
                img.verify()
            
            return True, ""
            
        except Exception as e:
            return False, f"无效的图片文件: {str(e)}"
    
    def add_reference_image(self, image_path: str, reference_list: List[str]) -> Tuple[bool, str]:
        """
        Add a reference image to the list.
        
        Args:
            image_path: Path to image
            reference_list: Current reference list
        
        Returns:
            Tuple of (success, message)
        """
        # Validate image
        is_valid, error_msg = self.validate_reference_image(image_path)
        if not is_valid:
            return False, error_msg
        
        # Check if already in list
        if image_path in reference_list:
            return False, "图片已在列表中"
        
        reference_list.append(image_path)
        return True, "添加成功"
    
    def remove_reference_image(self, image_path: str, reference_list: List[str]) -> bool:
        """
        Remove a reference image from the list.
        
        Args:
            image_path: Path to image
            reference_list: Current reference list
        
        Returns:
            True if removed
        """
        if image_path in reference_list:
            reference_list.remove(image_path)
            return True
        return False
