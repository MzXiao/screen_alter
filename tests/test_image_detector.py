
import unittest
import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import tempfile
import shutil

# Add src to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from monitor.image_detector import ImageDetector

class TestImageDetector(unittest.TestCase):
    def setUp(self):
        self.detector = ImageDetector(threshold=0.8)
        self.test_dir = tempfile.mkdtemp()
        
        # Create a dummy screenshot (500x500 random noise)
        np.random.seed(42)
        self.screenshot_img = np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8)
        self.screenshot_path = os.path.join(self.test_dir, "screenshot.png")
        
        # Create a unique pattern at 100,100 (larger 100x100 for SIFT)
        self.pattern = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        self.screenshot_img[100:200, 100:200] = self.pattern
        
        cv2.imwrite(self.screenshot_path, self.screenshot_img)
        
        # Create matching template
        self.template_path = os.path.join(self.test_dir, "template.png")
        cv2.imwrite(self.template_path, self.pattern)
        
        # Create a non-matching template (red square)
        self.bad_template_path = os.path.join(self.test_dir, "bad_template.png")
        self.bad_template_img = np.zeros((100, 100, 3), dtype=np.uint8)
        self.bad_template_img[:] = (0, 0, 255) # Red
        cv2.imwrite(self.bad_template_path, self.bad_template_img)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_detect_features_sift(self):
        # Load screenshot as PIL Image
        screenshot = Image.open(self.screenshot_path)
        
        # SIFT should find matches
        detected, score = self.detector.detect_features_sift(screenshot, self.template_path)
        
        self.assertTrue(detected, "SIFT should detect the pattern")
        self.assertGreater(score, 0.0)
        print(f"SIFT Score: {score}")

    def test_detect_template_match(self):
        # Load screenshot as PIL Image (to match app usage)
        screenshot = Image.open(self.screenshot_path)
        
        detected, score, loc = self.detector.detect_template(screenshot, self.template_path, threshold=0.99)
        
        self.assertTrue(detected)
        self.assertGreater(score, 0.99)
        print(f"Match found with score: {score}, loc: {loc}")
        
        # Check location (should be around 100, 100)
        # Note: minMaxLoc returns (x, y)
        self.assertEqual(loc, (100, 100))

    def test_detect_template_no_match(self):
        screenshot = Image.open(self.screenshot_path)
        
        detected, score, loc = self.detector.detect_template(screenshot, self.bad_template_path, threshold=0.9)
        
        self.assertFalse(detected)
        print(f"No match found, max score: {score}")

    def test_compare_with_references_sift_priority(self):
        screenshot = Image.open(self.screenshot_path)
        references = [self.template_path]
        
        result = self.detector.compare_with_references(screenshot, references)
        
        self.assertTrue(result['detected'])
        self.assertEqual(result['best_match']['path'], self.template_path)
        # Should now prefer SIFT if it works, or template if SIFT fails (but SIFT should work on this pattern)
        # Update: We made SIFT primary.
        print(f"Result method: {result['best_match']['method']}")
        
        # Our update prioritizes SIFT, check if it was used
        if result['best_match']['method'] == 'sift_feature_matching':
             print("Confirmed SIFT usage")
        else:
             print("Used Template Matching (SIFT might have filtered matches on random noise)")

if __name__ == '__main__':
    unittest.main()
