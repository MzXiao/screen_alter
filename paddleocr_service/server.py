"""
PaddleOCR HTTP API Service
独立运行的 OCR 服务，支持通过 HTTP API 调用
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
import io
import logging
from typing import List, Dict, Any
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="PaddleOCR Service",
    description="独立的 PaddleOCR HTTP API 服务",
    version="1.0.0"
)

# 全局 OCR 实例（单例模式）
ocr_instance = None


def get_ocr():
    """获取或创建 OCR 实例（延迟初始化）"""
    global ocr_instance
    if ocr_instance is None:
        logger.info("Initializing PaddleOCR...")
        ocr_instance = PaddleOCR(
            use_angle_cls=False,
            lang='ch',  # 中文
            use_gpu=False,  # 改为 True 启用 GPU
            show_log=False,
            enable_mkldnn=False,
            use_mp=False
        )
        logger.info("PaddleOCR initialized successfully")
    return ocr_instance


@app.get("/")
async def root():
    """健康检查"""
    return {
        "service": "PaddleOCR API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查（包含 OCR 状态）"""
    try:
        get_ocr()  # 尝试初始化
        return {"status": "healthy", "ocr_ready": True}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "ocr_ready": False}


@app.post("/api/ocr")
async def ocr_image(file: UploadFile = File(...)):
    """
    OCR 识别接口
    
    接收图片文件，返回识别的文字
    """
    try:
        logger.debug(f"Received OCR request for file: {file.filename}")
        
        # 读取图片
        contents = await file.read()
        logger.debug(f"File size: {len(contents)} bytes")
        
        image = Image.open(io.BytesIO(contents))
        logger.debug(f"Image size: {image.size}, mode: {image.mode}")
        
        # 转换为 numpy 数组
        img_array = np.array(image.convert('RGB'))
        
        # OCR 识别
        ocr = get_ocr()
        result = ocr.ocr(img_array, cls=False)
        
        # 解析结果
        if not result or result[0] is None:
            return JSONResponse({
                "success": True,
                "text": "",
                "lines": []
            })
        
        # 提取文字和坐标
        lines = []
        text_list = []
        for line in result[0]:
            box = line[0]  # 坐标
            text_info = line[1]  # (文字, 置信度)
            text = text_info[0]
            confidence = text_info[1]
            
            text_list.append(text)
            lines.append({
                "text": text,
                "confidence": float(confidence),
                "box": [[int(p[0]), int(p[1])] for p in box]
            })
        
        # 合并所有文字
        full_text = " ".join(text_list)
        
        logger.info(
            f"OCR completed: text_length={len(full_text)}, "
            f"lines={len(lines)}"
        )
        
        return JSONResponse({
            "success": True,
            "text": full_text,
            "lines": lines,
            "total_lines": len(lines)
        })
        
    except Exception as e:
        logger.error(f"OCR failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/detect_keywords")
async def detect_keywords(
    file: UploadFile = File(...),
    keywords: str = Form("")
):
    """
    关键词检测接口
    
    接收图片和关键词列表，返回是否检测到关键词
    
    参数:
        file: 图片文件
        keywords: 逗号分隔的关键词字符串（如 "关键词1,关键词2,关键词3"）
    """
    try:
        logger.debug(f"Received keywords parameter: '{keywords}' (type: {type(keywords)})")
        
        # 解析关键词
        keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
        
        if not keyword_list:
            logger.warning(f"No keywords provided in request. keywords param: '{keywords}'")
            raise HTTPException(
                status_code=400, 
                detail="No keywords provided. Please provide keywords as comma-separated string."
            )
        
        logger.debug(f"Received keyword detection request for file: {file.filename}")
        logger.debug(f"Keywords to detect: {keyword_list}")
        
        # 读取图片
        contents = await file.read()
        logger.debug(f"File size: {len(contents)} bytes")
        
        image = Image.open(io.BytesIO(contents))
        logger.debug(f"Image size: {image.size}, mode: {image.mode}")
        
        img_array = np.array(image.convert('RGB'))
        
        # OCR 识别
        ocr = get_ocr()
        result = ocr.ocr(img_array, cls=False)
        
        # 解析结果
        if not result or result[0] is None:
            return JSONResponse({
                "success": True,
                "detected": False,
                "matched_keywords": [],
                "text": ""
            })
        
        # 提取所有文字
        text_list = []
        for line in result[0]:
            text_list.append(line[1][0])
        
        full_text = " ".join(text_list)
        
        # 检测关键词
        matched_keywords = []
        contexts = {}
        search_text = full_text.lower()
        
        for keyword in keyword_list:
            if keyword.lower() in search_text:
                matched_keywords.append(keyword)
                # 提取上下文
                idx = search_text.find(keyword.lower())
                start = max(0, idx - 20)
                end = min(len(full_text), idx + len(keyword) + 20)
                contexts[keyword] = f"...{full_text[start:end]}..."
        
        logger.info(
            f"Keyword detection completed: "
            f"detected={len(matched_keywords) > 0}, "
            f"matched={matched_keywords}, "
            f"text_length={len(full_text)}"
        )
        
        return JSONResponse({
            "success": True,
            "detected": len(matched_keywords) > 0,
            "matched_keywords": matched_keywords,
            "contexts": contexts,
            "text": full_text
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Keyword detection failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """启动服务"""
    logger.info("=" * 60)
    logger.info("Starting PaddleOCR Service...")
    logger.info("Service will be available at: http://localhost:5000")
    logger.info("API documentation: http://localhost:5000/docs")
    logger.info("=" * 60)
    
    uvicorn.run(
        app,
        host="127.0.0.1",  # 本地访问，改为 "0.0.0.0" 可远程访问
        port=5000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
