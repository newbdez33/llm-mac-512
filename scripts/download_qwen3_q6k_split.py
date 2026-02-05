#!/usr/bin/env python3
"""
Download Qwen3-Coder-Next GGUF Q6_K split files (3 parts, 65.5GB total)
"""

import os
import requests
from tqdm import tqdm

print("="*60)
print("Qwen3-Coder-Next Q6_K 分片下载 (3 parts, 65.5GB)")
print("="*60)

base_url = "https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF/resolve/main/Q6_K"
output_dir = os.path.expanduser("~/.lmstudio/models/unsloth/Qwen3-Coder-Next-GGUF")
os.makedirs(output_dir, exist_ok=True)

files = [
    ("Qwen3-Coder-Next-Q6_K-00001-of-00003.gguf", 5.94 * 1024 * 1024),  # 5.94 MB
    ("Qwen3-Coder-Next-Q6_K-00002-of-00003.gguf", 49.7 * 1024 * 1024 * 1024),  # 49.7 GB
    ("Qwen3-Coder-Next-Q6_K-00003-of-00003.gguf", 15.8 * 1024 * 1024 * 1024),  # 15.8 GB
]

for filename, expected_size in files:
    url = f"{base_url}/{filename}"
    output_file = os.path.join(output_dir, filename)

    print(f"\n{'='*60}")
    print(f"下载: {filename}")
    print(f"预期大小: {expected_size / (1024**3):.2f} GB")
    print(f"{'='*60}")

    # 检查已下载大小
    start_byte = 0
    if os.path.exists(output_file):
        start_byte = os.path.getsize(output_file)
        if start_byte >= expected_size * 0.99:  # Allow 1% margin
            print(f"✅ 文件已完整下载，跳过")
            continue
        print(f"✅ 已下载 {start_byte / (1024**3):.2f} GB，继续下载...")

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
            desc=filename
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

    print(f"✅ {filename} 下载完成！")

print("\n" + "="*60)
print("✅ 所有分片下载完成！")
print("="*60)
print(f"📁 位置: {output_dir}")
print(f"📊 总大小: ~65.5 GB (3 files)")
print("\n💡 llama.cpp 会自动合并这些分片文件")
