"""
PaddleOCR HTTP Client
通过 HTTP API 调用远程 PaddleOCR 服务
"""

import requests
from PIL import Image
from typing import List, Dict, Any
import io
from utils.logger import get_logger

logger = get_logger(__name__)


class PaddleOCRClient:
    """PaddleOCR HTTP API 客户端"""
    
    def __init__(self, service_url: str = "http://localhost:5000"):
        """
        初始化客户端
        
        Args:
            service_url: PaddleOCR 服务地址
        """
        self.service_url = service_url.rstrip('/')
        self._available = self._check_service()
    
    def _check_service(self) -> bool:
        """检查服务是否可用"""
        try:
            response = requests.get(
                f"{self.service_url}/health",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    logger.info(f"PaddleOCR service is ready at {self.service_url}")
                    return True
            
            logger.warning(f"PaddleOCR service at {self.service_url} is not healthy")
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Cannot connect to PaddleOCR service at {self.service_url}: {e}")
            return False
    
    def extract_text(self, image: Image.Image) -> str:
        """
        提取图片中的文字
        
        Args:
            image: PIL Image 对象
            
        Returns:
            提取的文字字符串
        """
        if not self._available:
            logger.error("PaddleOCR service is not available")
            return ""
        
        try:
            # 将 PIL Image 转换为字节流
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # 发送请求
            files = {'file': ('image.png', img_byte_arr, 'image/png')}
            response = requests.post(
                f"{self.service_url}/api/ocr",
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    text = data.get("text", "")
                    logger.debug(f"OCR extracted text: {text[:100]}...")
                    return text
            
            # 记录详细错误信息
            error_detail = ""
            try:
                error_response = response.json()
                error_detail = error_response.get("detail", "")
            except:
                error_detail = response.text
            
            logger.error(
                f"OCR request failed with status {response.status_code}: {error_detail}"
            )
            return ""
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def detect_keywords(
        self,
        image: Image.Image,
        keywords: List[str],
        case_sensitive: bool = False
    ) -> Dict[str, Any]:
        """
        检测图片中的关键词
        
        Args:
            image: PIL Image 对象
            keywords: 关键词列表
            case_sensitive: 是否大小写敏感（当前未使用，服务端默认不区分大小写）
            
        Returns:
            检测结果字典
        """
        if not self._available:
            logger.error("PaddleOCR service is not available")
            return {
                "detected": False,
                "matched_keywords": [],
                "extracted_text": ""
            }
        
        # 验证关键词列表
        if not keywords or len(keywords) == 0:
            logger.warning("No keywords provided for detection")
            return {
                "detected": False,
                "matched_keywords": [],
                "extracted_text": ""
            }
        
        try:
            # 将 PIL Image 转换为字节流
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # 发送请求
            keywords_str = ','.join(keywords)
            files = {'file': ('image.png', img_byte_arr, 'image/png')}
            data = {'keywords': keywords_str}
            
            logger.debug(f"Detecting keywords: {keywords}")
            logger.debug(f"Sending keywords string: '{keywords_str}'")
            
            response = requests.post(
                f"{self.service_url}/api/detect_keywords",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return {
                        "detected": result.get("detected", False),
                        "matched_keywords": result.get("matched_keywords", []),
                        "contexts": result.get("contexts", {}),
                        "extracted_text": result.get("text", "")
                    }
            
            # 记录详细错误信息
            error_detail = ""
            try:
                error_response = response.json()
                error_detail = error_response.get("detail", "")
            except:
                error_detail = response.text
            
            logger.error(
                f"Keyword detection failed with status {response.status_code}: {error_detail}"
            )
            return {
                "detected": False,
                "matched_keywords": [],
                "extracted_text": ""
            }
            
        except Exception as e:
            logger.error(f"Keyword detection failed: {e}")
            return {
                "detected": False,
                "matched_keywords": [],
                "extracted_text": ""
            }
    
    def _initialize_ocr(self):
        """
        兼容性方法，与 PaddleOCRDetector 接口保持一致
        对于客户端模式，不需要初始化，直接返回服务是否可用
        """
        return self._available
    
    @staticmethod
    def is_available(service_url: str = "http://localhost:5000") -> bool:
        """
        检查服务是否可用（静态方法）
        
        Args:
            service_url: 服务地址
            
        Returns:
            是否可用
        """
        try:
            response = requests.get(
                f"{service_url.rstrip('/')}/health",
                timeout=3
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "healthy"
            return False
        except:
            return False
