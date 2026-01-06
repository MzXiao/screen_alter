import os
os.environ['OMP_NUM_THREADS'] = '1'  # 限制 OpenMP 线程数为 1
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'



import cv2
from paddleocr import PaddleOCR
import numpy as np


print("--- 正在检查环境 ---")
print(f"OpenCV 路径: {cv2.__file__}")
print(f"NumPy 版本: {np.__version__}")

try:
    # 初始化 OCR，建议显式关闭 mkldnn 提高稳定性
    # ocr = PaddleOCR(use_angle_cls=False, lang="ch", use_mkldnn=False, show_log=True)
    ocr = PaddleOCR(
        use_angle_cls=False,
        lang="ch",
        use_gpu=False,  # Mac 上目前 Paddle 官方包不支持直接调用 GPU（Metal）
        use_mkldnn=False,  # 必须为 False，mkldnn 仅支持 Intel CPU
        cpu_threads=1,  # 显式限制内部线程
        show_log=True,
        use_onnx=False
    )
    # 创建一个空白黑色图片进行测试
    # fake_img = np.zeros((300, 300, 3), dtype=np.uint8)
    fake_img = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)

    print("--- 正在尝试识别 (关键步骤) ---")
    result = ocr.ocr(fake_img, cls=False)

    print("恭喜！识别逻辑运行正常，没有崩溃。")
    print(f"识别结果: {result}")

except Exception as e:
    print(f"运行出错: {e}")