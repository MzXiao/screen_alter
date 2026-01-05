# PaddleOCR Deployment Guide

This guide describes how to deploy and configure PaddleOCR for the Screen Alter application.

## 1. Prerequisites

- Python 3.8 - 3.12 (Python 3.13 support is experimental)
- C++ Build Tools (Windows: Visual Studio with C++ development)
- CUDA / cuDNN (Optional, for GPU acceleration)

## 2. Installation

### General Installation

Install the required packages via pip:

```bash
pip install paddlepaddle paddleocr
```

### Windows (CPU)

If you encounter issues with `paddlepaddle` on Windows, try:

```bash
pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### macOS (Silcon/M1/M2/M3)

PaddlePaddle works well on Apple Silicon. Install with:

```bash
pip install paddlepaddle
```

### GPU Acceleration (Optional)

If you have an NVIDIA GPU, install the GPU version for significantly faster OCR:

```bash
# CUDA 11.8 example
pip install paddlepaddle-gpu==2.6.2 -f https://www.paddlepaddle.org.cn/whl/stable/gpu.html
```

## 3. Configuration in Screen Alter

1. Start the application and log in.
2. In the "Config" panel, select **paddleocr** from the "OCR Engine" dropdown.
3. The application will automatically download the lightweight mobile models on first run (stored in `~/.paddleocr/`).

## 4. Performance Tips

- **Inference Speed**: On a standard CPU, PaddleOCR takes ~300-800ms per screenshot. Since we run a 1-second capture interval, this might consume 50-80% of one CPU core.
- **GPU Usage**: Setting `use_gpu=True` in `src/monitor/paddle_ocr_detector.py` (if supported by your hardware) will reduce OCR time to <100ms and significantly lower CPU usage.
- **Capture Region**: Selecting a smaller capture region (instead of full screen) will improve both capture and OCR speed.

## 5. Troubleshooting

- **ImportError: libGL.so.1**: On Linux, install `mesa-utils` or `libgl1-mesa-glx`:
  ```bash
  sudo apt-get install libgl1-mesa-glx
  ```
- **OMP: Error #15**: If you see an OpenMP error, set the following environment variable:
  ```python
  import os
  os.environ['KMP_DUPLICATE_LIB_OK']='True'
  ```
