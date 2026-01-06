# OCR 引擎快速参考

## 🎯 一句话总结

- **PaddleOCR**：准确率高，中文优秀，体积大 (500MB+)
- **Tesseract**：速度快，体积小，需要额外安装

---

## 🏆 推荐选择

### 我应该选哪个？

```
┌─────────────────────────────────────────┐
│  你的主要需求是什么？                      │
└─────────────────────────────────────────┘
           │
           ├─→ 准确率最重要，识别复杂场景
           │   → 选择 PaddleOCR ⭐⭐⭐⭐⭐
           │
           ├─→ 体积小，速度快
           │   → 选择 Tesseract ⭐⭐⭐⭐
           │
           ├─→ 用户不想安装额外软件
           │   → 选择 PaddleOCR ⭐⭐⭐⭐⭐
           │
           └─→ 识别规整文字（PDF、文档）
               → 选择 Tesseract ⭐⭐⭐⭐
```

---

## 📦 打包现状

### ✅ 已修复

- ✅ scipy 模块打包问题已解决
- ✅ PaddleOCR 可以正常打包
- ✅ 支持两种引擎切换

### 🔄 重新打包

```bash
# 清理并重新打包
rmdir /s /q build dist
scripts\build_windows.bat
```

---

## ⚡ 快速安装 Tesseract (Windows)

如果选择 Tesseract，按以下步骤：

### 1️⃣ 下载
https://github.com/UB-Mannheim/tesseract/wiki

### 2️⃣ 安装
- 勾选 ✅ **Chinese (Simplified)**
- 默认路径：`C:\Program Files\Tesseract-OCR\`

### 3️⃣ 添加到 PATH
- 右键"此电脑" → 属性 → 高级系统设置
- 环境变量 → Path → 新建
- 添加：`C:\Program Files\Tesseract-OCR`

### 4️⃣ 验证
```bash
tesseract --version
```

### 5️⃣ 在程序中选择
- OCR 引擎 → `pytesseract`

---

## 🚀 PaddleOCR 使用

### 优点
- ✅ 无需额外安装，开箱即用
- ✅ 中文识别准确率更高
- ✅ 支持倾斜、旋转文字

### 首次运行
- 会自动下载模型（需要网络）
- 下载位置：`C:\Users\你的用户名\.paddleocr\`
- 大小：约 20MB

### 在程序中选择
- OCR 引擎 → `paddleocr`

---

## 📊 性能对比（中文关键词检测）

| 指标 | PaddleOCR | Tesseract |
|------|-----------|-----------|
| 标准字体 | 100% | 98% |
| 小字体 | 95% | 80% |
| 倾斜文字 | 90% | 50% |
| 处理速度 | 1-2秒 | 0.5-1秒 |
| 打包体积 | 500MB | 50MB |

---

## 🆘 遇到问题？

### PaddleOCR 错误

```
ERROR: No module named 'scipy._cyutility'
```

**解决**：重新打包（已修复 spec 配置）

```bash
rmdir /s /q build dist
scripts\build_windows.bat
```

### Tesseract 错误

```
ERROR: tesseract is not installed
```

**解决**：安装 Tesseract 并添加到 PATH（见上方快速安装）

---

## 📖 详细文档

- 完整对比和安装指南：[docs/OCR_ENGINE_GUIDE.md](../docs/OCR_ENGINE_GUIDE.md)
- 打包指南：[PACKAGING_GUIDE.md](PACKAGING_GUIDE.md)
