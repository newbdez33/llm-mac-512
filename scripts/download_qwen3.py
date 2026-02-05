#!/usr/bin/env python3
"""
Download Qwen3-Coder-Next GGUF Q4_K_M from HuggingFace
"""

import os
from huggingface_hub import hf_hub_download
import time

print("="*60)
print("Qwen3-Coder-Next GGUF Q4_K_M 下载")
print("="*60)

# 模型信息
repo_id = "unsloth/Qwen3-Coder-Next-GGUF"
filename = "Qwen3-Coder-Next-Q4_K_M.gguf"
local_dir = os.path.expanduser("~/.cache/lm-studio/models/unsloth/Qwen3-Coder-Next-GGUF")

print(f"\n📦 仓库: {repo_id}")
print(f"📁 文件: {filename}")
print(f"💾 目标: {local_dir}")
print(f"\n开始下载...\n")

start_time = time.time()

try:
    # 下载文件
    downloaded_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=local_dir,
        local_dir_use_symlinks=False,
        resume_download=True
    )

    elapsed = time.time() - start_time
    file_size = os.path.getsize(downloaded_path) / (1024**3)  # GB

    print("\n" + "="*60)
    print("✅ 下载完成！")
    print("="*60)
    print(f"📁 路径: {downloaded_path}")
    print(f"📊 大小: {file_size:.2f} GB")
    print(f"⏱️  用时: {elapsed/60:.1f} 分钟")
    print(f"🚀 速度: {file_size/(elapsed/60):.2f} GB/分钟")

except Exception as e:
    print(f"\n❌ 下载失败: {e}")
    exit(1)
