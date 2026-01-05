"""
测试 PaddleOCR 服务
验证 API 接口是否正常工作
"""

import requests
from PIL import Image, ImageDraw, ImageFont
import io
import sys

def create_test_image():
    """创建一个包含中文文字的测试图片"""
    # 创建白色背景图片
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # 尝试使用中文字体，如果没有则使用默认字体
    try:
        font = ImageFont.truetype("simhei.ttf", 40)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
    
    # 绘制文字
    text = "违规通知测试"
    draw.text((50, 80), text, fill='black', font=font)
    
    return img

def test_health():
    """测试健康检查接口"""
    print("\n=== 测试 1: 健康检查 ===")
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_ocr():
    """测试 OCR 识别接口"""
    print("\n=== 测试 2: OCR 识别 ===")
    try:
        # 创建测试图片
        img = create_test_image()
        
        # 转换为字节流
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # 发送请求
        files = {'file': ('test.png', img_byte_arr, 'image/png')}
        response = requests.post(
            "http://localhost:5000/api/ocr",
            files=files,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"识别成功: {result.get('success')}")
            print(f"识别文字: {result.get('text')}")
            print(f"行数: {result.get('total_lines')}")
            return True
        else:
            print(f"❌ 错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_keyword_detection():
    """测试关键词检测接口"""
    print("\n=== 测试 3: 关键词检测 ===")
    try:
        # 创建测试图片
        img = create_test_image()
        
        # 转换为字节流
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # 测试数据
        keywords = "违规通知,测试"
        print(f"关键词: {keywords}")
        
        # 发送请求
        files = {'file': ('test.png', img_byte_arr, 'image/png')}
        data = {'keywords': keywords}
        
        print(f"发送数据: files={list(files.keys())}, data={data}")
        
        response = requests.post(
            "http://localhost:5000/api/detect_keywords",
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"检测成功: {result.get('success')}")
            print(f"是否检测到: {result.get('detected')}")
            print(f"匹配的关键词: {result.get('matched_keywords')}")
            print(f"识别文字: {result.get('text')}")
            return True
        else:
            print(f"❌ 错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_empty_keywords():
    """测试空关键词（应该返回 400）"""
    print("\n=== 测试 4: 空关键词（预期失败）===")
    try:
        # 创建测试图片
        img = create_test_image()
        
        # 转换为字节流
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # 发送请求（空关键词）
        files = {'file': ('test.png', img_byte_arr, 'image/png')}
        data = {'keywords': ''}
        
        response = requests.post(
            "http://localhost:5000/api/detect_keywords",
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 400:
            print(f"✅ 正确返回 400: {response.json()}")
            return True
        else:
            print(f"❌ 应该返回 400，但返回了 {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("PaddleOCR 服务测试")
    print("=" * 60)
    print("\n请确保服务已启动：cd paddleocr_service && python server.py")
    print()
    
    results = []
    
    # 运行测试
    results.append(("健康检查", test_health()))
    results.append(("OCR 识别", test_ocr()))
    results.append(("关键词检测", test_keyword_detection()))
    results.append(("空关键词验证", test_empty_keywords()))
    
    # 显示结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查日志")
        return 1

if __name__ == "__main__":
    sys.exit(main())
