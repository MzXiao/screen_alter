"""
Image similarity detection.
Compares screenshots with reference images using perceptual hashing.
"""

from PIL import Image
import imagehash
import cv2
import numpy as np
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

    def detect_template(self, screenshot: Image.Image, template_path: str, threshold: float = 0.8) -> Tuple[bool, float, Tuple[int, int]]:
        """
        Detect template in screenshot using OpenCV template matching.
        
        Args:
            screenshot: PIL Image of the screen
            template_path: Path to the template image
            threshold: Matching threshold (0.8-0.9 recommended)
            
        Returns:
            Tuple of (detected, max_val, max_loc)
        """
        try:
            # Convert PIL image to OpenCV format (BGR)
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Load template
            template = cv2.imread(template_path)
            if template is None:
                logger.error(f"Failed to load template: {template_path}")
                return False, 0.0, (0, 0)
                
            # Perform template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            
            # Get the best match position
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                return True, float(max_val), max_loc
            
            return False, float(max_val), max_loc
            
        except Exception as e:
            logger.error(f"Template matching failed for {template_path}: {e}")
            return False, 0.0, (0, 0)

    def detect_features_sift(self, screenshot: Image.Image, template_path: str, min_match_count: int = 15) -> Tuple[bool, float]:
        """
        Detect template using SIFT feature matching (robust to scale/rotation).
        
        Args:
            screenshot: PIL Image of the screen
            template_path: Path to the template image
            min_match_count: Minimum good matches required
            
        Returns:
            Tuple of (detected, score) where score is match_count/keypoints_count
        """
        try:
            # Convert PIL image to grayscale for feature matching
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
            
            # Load template in grayscale
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                logger.error(f"Failed to load template: {template_path}")
                return False, 0.0
                
            # Initialize SIFT detector
            sift = cv2.SIFT_create()
            
            # Find keypoints and descriptors
            kp1, des1 = sift.detectAndCompute(template, None)
            kp2, des2 = sift.detectAndCompute(screenshot_cv, None)
            
            if des1 is None or des2 is None or len(kp1) < min_match_count:
                # Not enough keypoints in template to be significant
                return False, 0.0
                
            # FLANN parameters or BFMatcher
            # BFMatcher with default params
            bf = cv2.BFMatcher()
            matches = bf.knnMatch(des1, des2, k=2)
            
            # Apply ratio test
            good = []
            for m, n in matches:
                if m.distance < 0.75 * n.distance:
                    good.append(m)
            
            match_count = len(good)
            
            if match_count >= min_match_count:
                # Calculate a rough "confidence" score
                score = min(1.0, match_count / len(kp1)) 
                logger.debug(f"SIFT match: {match_count} good matches (score: {score:.2f})")
                return True, score
            
            return False, 0.0
            
        except Exception as e:
            logger.error(f"SIFT feature matching failed for {template_path}: {e}")
            return False, 0.0
    
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
                # Check extension to decide method?
                # Use SIFT Feature Matching as primary method (robust to scale/content changes)
                
                # 1. Try SIFT Feature Matching
                sift_detected, sift_score = self.detect_features_sift(screenshot, ref_path)
                
                if sift_detected:
                     matches.append({
                        'path': ref_path,
                        'similarity': sift_score,
                        'method': 'sift_feature_matching'
                    })
                     logger.info(f"Match found (SIFT): {ref_path} (score: {sift_score:.2f})")
                     continue

                # 2. Fallback to Template Matching (OpenCV) - Good for exact icon matches
                tm_detected, tm_score, _ = self.detect_template(screenshot, ref_path, self.threshold)
                
                if tm_detected:
                     matches.append({
                        'path': ref_path,
                        'similarity': tm_score,
                        'method': 'template_matching'
                    })
                     logger.info(f"Match found (Template): {ref_path} (score: {tm_score:.2f})")
                     continue

                # 3. Fallback to Hash Comparison (Optional/Last resort)
                # Only if the user requested hash matching explicitly or as fallback?
                # For this task, we prioritize Template Matching for speed and "finding buttons"
                
                # Existing Hash Logic (optional keep or replace)
                ref_image = Image.open(ref_path)
                similarity = self.calculate_similarity(screenshot, ref_image)
                
                if similarity >= self.threshold:
                    matches.append({
                        'path': ref_path,
                        'similarity': similarity,
                        'method': 'perceptual_hash'
                    })
                    logger.info(f"Match found (Hash): {ref_path} (similarity: {similarity:.2f})")
                
                
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
