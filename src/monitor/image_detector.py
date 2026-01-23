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

    def detect_template(self, screenshot: Image.Image, template_path: str, threshold: float = 0.85, 
                       multi_scale: bool = True, scale_range: Tuple[float, float] = (0.5, 2.0), 
                       scale_step: float = 0.1) -> Tuple[bool, float, Tuple[int, int], float, Tuple[int, int]]:
        """
        Detect template in screenshot using OpenCV template matching with multi-scale support.
        High precision method that returns exact location, supports scaled templates.
        
        Args:
            screenshot: PIL Image of the screen
            template_path: Path to the template image
            threshold: Matching threshold (0.85+ recommended for precision)
            multi_scale: Whether to try multiple scales (default: True)
            scale_range: (min_scale, max_scale) to try (default: 0.5 to 2.0)
            scale_step: Step size for scale search (default: 0.1)
            
        Returns:
            Tuple of (detected, max_val, max_loc, best_scale, scaled_template_size)
            - detected: bool
            - max_val: best match score
            - max_loc: (x, y) position of best match
            - best_scale: scale factor used (1.0 if no scaling)
            - scaled_template_size: (width, height) of template at best scale
        """
        try:
            # Convert PIL image to OpenCV format (BGR)
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Load template
            template = cv2.imread(template_path)
            if template is None:
                logger.error(f"Failed to load template: {template_path}")
                return False, 0.0, (0, 0), 1.0, (0, 0)
            
            template_h, template_w = template.shape[:2]
            screenshot_h, screenshot_w = screenshot_cv.shape[:2]
            
            best_match = {
                'score': 0.0,
                'location': (0, 0),
                'scale': 1.0,
                'scaled_size': (template_w, template_h)
            }
            
            if multi_scale:
                # Try multiple scales
                scales = []
                current_scale = scale_range[0]
                while current_scale <= scale_range[1]:
                    scales.append(current_scale)
                    current_scale += scale_step
                
                # Also try original scale (1.0) if not already included
                if 1.0 not in scales:
                    scales.append(1.0)
                scales.sort()
                
                logger.debug(f"Trying {len(scales)} scales: {scales[:5]}...{scales[-2:]}")
                
                for scale in scales:
                    # Calculate scaled template size
                    scaled_w = int(template_w * scale)
                    scaled_h = int(template_h * scale)
                    
                    # Skip if scaled template is larger than screenshot
                    if scaled_w >= screenshot_w or scaled_h >= screenshot_h:
                        continue
                    
                    # Skip if scaled template is too small (less than 10 pixels)
                    if scaled_w < 10 or scaled_h < 10:
                        continue
                    
                    # Resize template
                    scaled_template = cv2.resize(template, (scaled_w, scaled_h), interpolation=cv2.INTER_AREA)
                    
                    # Perform template matching
                    result = cv2.matchTemplate(screenshot_cv, scaled_template, cv2.TM_CCOEFF_NORMED)
                    
                    # Get the best match position
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    # Update best match if this is better
                    if max_val > best_match['score']:
                        best_match['score'] = float(max_val)
                        best_match['location'] = max_loc
                        best_match['scale'] = scale
                        best_match['scaled_size'] = (scaled_w, scaled_h)
                        
                        logger.debug(f"  Scale {scale:.2f}: score={max_val:.4f}, loc={max_loc}, size={scaled_w}x{scaled_h}")
            else:
                # Single scale matching (original size)
                if template_w >= screenshot_w or template_h >= screenshot_h:
                    logger.warning(f"Template {template_path} ({template_w}x{template_h}) is not smaller than screenshot ({screenshot_w}x{screenshot_h})")
                    return False, 0.0, (0, 0), 1.0, (template_w, template_h)
                
                # Perform template matching
                result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
                
                # Get the best match position
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                best_match['score'] = float(max_val)
                best_match['location'] = max_loc
                best_match['scale'] = 1.0
                best_match['scaled_size'] = (template_w, template_h)
            
            logger.debug(f"Template matching: {template_path}, best_score: {best_match['score']:.4f}, "
                        f"threshold: {threshold:.2f}, location: {best_match['location']}, "
                        f"scale: {best_match['scale']:.2f}, scaled_size: {best_match['scaled_size']}")
            
            if best_match['score'] >= threshold:
                return (True, best_match['score'], best_match['location'], 
                       best_match['scale'], best_match['scaled_size'])
            
            return (False, best_match['score'], best_match['location'], 
                   best_match['scale'], best_match['scaled_size'])
            
        except Exception as e:
            logger.error(f"Template matching failed for {template_path}: {e}", exc_info=True)
            return False, 0.0, (0, 0), 1.0, (0, 0)

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
        Priority: Template Matching (precise location) > SIFT > Hash
        Since reference images are small parts of screenshot, precision is critical.
        
        Args:
            screenshot: Screenshot to check
            reference_images: List of reference image paths
        
        Returns:
            Detection result dictionary with:
                - detected: bool
                - matches: List[Dict] with 'path', 'similarity', 'method', 'location', 'template_size'
                - best_match: Dict or None
        """
        matches = []
        screenshot_size = screenshot.size  # (width, height)
        
        for ref_path in reference_images:
            try:
                # Load reference image to get dimensions
                ref_image = Image.open(ref_path)
                ref_size = ref_image.size  # (width, height)
                
                # Validate: reference image should be much smaller than screenshot
                if ref_size[0] >= screenshot_size[0] * 0.5 or ref_size[1] >= screenshot_size[1] * 0.5:
                    logger.warning(f"Reference image {ref_path} is too large ({ref_size}), skipping")
                    continue
                
                logger.debug(f"Checking {ref_path} (ref size: {ref_size}, screenshot size: {screenshot_size})")
                
                # 1. PRIORITY: Template Matching - Most precise, gives exact location, supports scaling
                # Use higher threshold (0.85) for precision, enable multi-scale
                tm_detected, tm_score, tm_location, tm_scale, tm_scaled_size = self.detect_template(
                    screenshot, ref_path, threshold=0.85, multi_scale=True, 
                    scale_range=(0.5, 2.0), scale_step=0.1
                )
                
                if tm_detected:
                    scaled_w, scaled_h = tm_scaled_size
                    
                    # Verify location is within screenshot bounds
                    if (tm_location[0] + scaled_w <= screenshot_size[0] and 
                        tm_location[1] + scaled_h <= screenshot_size[1]):
                        
                        matches.append({
                            'path': ref_path,
                            'similarity': tm_score,
                            'method': 'template_matching',
                            'location': tm_location,  # (x, y) top-left corner
                            'template_size': tm_scaled_size,  # (width, height) at matched scale
                            'scale': tm_scale,  # Scale factor used
                            'original_template_size': ref_size,  # Original template size
                            'ref_size': ref_size,
                            'screenshot_size': screenshot_size
                        })
                        scale_info = f" (scale: {tm_scale:.2f}x)" if tm_scale != 1.0 else ""
                        logger.info(f"✅ Match found (Template Matching): {ref_path}{scale_info}")
                        logger.info(f"   Score: {tm_score:.4f}, Location: {tm_location}, "
                                  f"Template size: {scaled_w}x{scaled_h} (original: {ref_size[0]}x{ref_size[1]})")
                        continue
                    else:
                        logger.warning(f"Template match location out of bounds: {tm_location}, "
                                     f"scaled template: {scaled_w}x{scaled_h}, screenshot: {screenshot_size}")
                else:
                    logger.debug(f"Template matching failed: {ref_path} (max score: {tm_score:.4f}, "
                               f"best scale: {tm_scale:.2f}, threshold: 0.85)")

                # 2. Fallback: SIFT Feature Matching (if template matching fails)
                # Only use if template matching didn't find anything
                sift_detected, sift_score = self.detect_features_sift(screenshot, ref_path, min_match_count=20)
                
                if sift_detected and sift_score >= 0.7:
                    # Try to get location using template matching with lower threshold and multi-scale
                    tm_detected_loc, tm_score_loc, tm_location_loc, tm_scale_loc, tm_scaled_size_loc = self.detect_template(
                        screenshot, ref_path, threshold=0.7, multi_scale=True
                    )
                    if tm_detected_loc:
                        scaled_w, scaled_h = tm_scaled_size_loc
                        
                        matches.append({
                            'path': ref_path,
                            'similarity': sift_score,
                            'method': 'sift_feature_matching',
                            'location': tm_location_loc,
                            'template_size': tm_scaled_size_loc,
                            'scale': tm_scale_loc,
                            'original_template_size': ref_size,
                            'ref_size': ref_size,
                            'screenshot_size': screenshot_size,
                            'template_match_score': tm_score_loc  # Additional verification score
                        })
                        scale_info = f" (scale: {tm_scale_loc:.2f}x)" if tm_scale_loc != 1.0 else ""
                        logger.info(f"✅ Match found (SIFT + Template location): {ref_path}{scale_info}")
                        logger.info(f"   SIFT score: {sift_score:.4f}, Template location score: {tm_score_loc:.4f}, "
                                  f"Location: {tm_location_loc}, Size: {scaled_w}x{scaled_h}")
                        continue
                    else:
                        logger.debug(f"SIFT found match but couldn't locate with template matching: {ref_path}")

                # 3. Last resort: Hash Comparison (requires very high similarity)
                # Only accept if similarity is very high (0.95+) and verify with template matching
                similarity = self.calculate_similarity(screenshot, ref_image)
                
                if similarity >= 0.95:  # Very strict threshold
                    # Must verify with template matching to get location (with multi-scale)
                    tm_detected_verify, tm_score_verify, tm_location_verify, tm_scale_verify, tm_scaled_size_verify = self.detect_template(
                        screenshot, ref_path, threshold=0.7, multi_scale=True
                    )
                    if tm_detected_verify:
                        scaled_w, scaled_h = tm_scaled_size_verify
                        
                        matches.append({
                            'path': ref_path,
                            'similarity': similarity,
                            'method': 'perceptual_hash_verified',
                            'location': tm_location_verify,
                            'template_size': tm_scaled_size_verify,
                            'scale': tm_scale_verify,
                            'original_template_size': ref_size,
                            'ref_size': ref_size,
                            'screenshot_size': screenshot_size,
                            'template_match_score': tm_score_verify
                        })
                        scale_info = f" (scale: {tm_scale_verify:.2f}x)" if tm_scale_verify != 1.0 else ""
                        logger.info(f"✅ Match found (Hash + Template verification): {ref_path}{scale_info}")
                        logger.info(f"   Hash similarity: {similarity:.4f}, Template location score: {tm_score_verify:.4f}, "
                                  f"Location: {tm_location_verify}, Size: {scaled_w}x{scaled_h}")
                    else:
                        logger.debug(f"Hash similarity high ({similarity:.4f}) but template matching verification failed: {ref_path}")
                
            except Exception as e:
                logger.error(f"Failed to process reference image {ref_path}: {e}", exc_info=True)
                continue
        
        # Sort matches by similarity (highest first)
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        result = {
            "detected": len(matches) > 0,
            "matches": matches,
            "best_match": matches[0] if matches else None
        }
        
        if result["detected"]:
            best = result["best_match"]
            logger.info(f"🎯 Best match: {best['path']} using {best['method']} (score: {best['similarity']:.4f})")
            if 'location' in best:
                logger.info(f"   Location: {best['location']}, Size: {best.get('template_size', 'unknown')}")
        else:
            logger.debug("No matches found for any reference images")
        
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
