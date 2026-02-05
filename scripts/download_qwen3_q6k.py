#!/usr/bin/env python3
"""
Download Qwen3-Coder-Next GGUF Q6_K from HuggingFace
"""

import os
import requests
from tqdm import tqdm

print("="*60)
print("Qwen3-Coder-Next GGUF Q6_K 下载 (带进度条)")
print("="*60)

url = "https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF/resolve/main/Q6_K/Qwen3-Coder-Next-Q6_K.gguf"
output_file = os.path.expanduser("~/.lmstudio/models/unsloth/Qwen3-Coder-Next-GGUF/Qwen3-Coder-Next-Q6_K.gguf")

os.makedirs(os.path.dirname(output_file), exist_ok=True)

print(f"\n📁 下载到: {output_file}")
print(f"🌐 URL: {url}\n")

# 检查已下载大小
start_byte = 0
if os.path.exists(output_file):
    start_byte = os.path.getsize(output_file)
    print(f"✅ 发现已下载 {start_byte / (1024**3):.2f} GB，继续下载...")

# 设置请求头支持断点续传
headers = {}
if start_byte > 0:
    headers['Range'] = f'bytes={start_byte}-'

# 开始下载
response = requests.get(url, headers=headers, stream=True)
total_size = int(response.headers.get('content-length', 0)) + start_byte

mode = 'ab' if start_byte > 0 else 'wb'

with open(output_file, mode) as f:
    with tqdm(
        total=total_size,
        initial=start_byte,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
        desc="下载进度"
    ) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                pbar.update(len(chunk))

print("\n" + "="*60)
print("✅ 下载完成！")
print("="*60)
print(f"📁 文件: {output_file}")
print(f"📊 大小: {os.path.getsize(output_file) / (1024**3):.2f} GB")
