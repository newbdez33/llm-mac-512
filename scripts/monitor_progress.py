#!/usr/bin/env python3
"""
模型下载进度监控
每5分钟汇报一次，完成时通知
"""

import os
import time
import subprocess
from datetime import datetime
from pathlib import Path

# 配置
LOG_FILE = "/tmp/api_server_8bit.log"
CACHE_DIR = Path.home() / ".cache/huggingface/hub/models--mlx-community--MiniMax-M2.1-8bit"
NOTIFY_DIR = Path.home() / ".openclaw/notifications"
REPORT_INTERVAL = 300  # 5分钟
TARGET_SIZE_GB = 240

def get_dir_size_gb(directory):
    """获取目录大小（GB）"""
    if not directory.exists():
        return 0

    total = 0
    for path in directory.rglob('*'):
        if path.is_file():
            total += path.stat().st_size
    return total / (1024 ** 3)

def send_notification(title, message, priority="normal"):
    """发送OpenClaw通知"""
    NOTIFY_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    notify_file = NOTIFY_DIR / f"{timestamp}.md"

    content = f"""# 通知
## 消息
{message}
## 优先级
{priority}
"""

    notify_file.write_text(content)
    print(f"✓ OpenClaw通知已发送: {notify_file}")

    # 系统通知
    try:
        subprocess.run([
            'osascript', '-e',
            f'display notification "{title}" with title "MLX 8-bit" sound name "Glass"'
        ], check=False, capture_output=True)
    except:
        pass

def is_complete():
    """检查是否完成"""
    if not os.path.exists(LOG_FILE):
        return False

    with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        return '模型加载完成' in content or 'Running on' in content

def main():
    print("="*50)
    print("MLX 8-bit 模型下载监控")
    print("="*50)
    print(f"日志: {LOG_FILE}")
    print(f"缓存: {CACHE_DIR}")
    print("每5分钟汇报一次进度")
    print("")

    start_time = time.time()
    last_report = 0
    report_count = 0

    while True:
        elapsed = time.time() - start_time
        elapsed_min = int(elapsed / 60)

        # 检查是否完成
        if is_complete():
            print("\n" + "="*50)
            print("✓ 模型加载完成！")
            print(f"总用时: {elapsed_min} 分钟")
            print("="*50)

            # 发送完成通知
            message = f"""🚀 MLX 8-bit模型下载完成！

✅ API服务器已就绪
📍 http://127.0.0.1:8000
⏱️ 用时: {elapsed_min} 分钟

下一步:
1. python scripts/test_api.py
2. export OPENAI_API_BASE="http://127.0.0.1:8000/v1"
3. openclaw

性能: 33 TPS, 95ms TTFT"""

            send_notification("下载完成！", message)
            print("\n✓ 通知已发送！可以开始测试了！")
            break

        # 每5分钟汇报一次
        if elapsed - last_report >= REPORT_INTERVAL:
            size_gb = get_dir_size_gb(CACHE_DIR)
            progress = (size_gb / TARGET_SIZE_GB * 100) if TARGET_SIZE_GB > 0 else 0

            report_count += 1
            now = datetime.now().strftime("%H:%M")

            print(f"\n┌{'─'*48}┐")
            print(f"│ [{now}] 进度汇报 #{report_count}".ljust(48) + "│")
            print(f"├{'─'*48}┤")
            print(f"│ 已下载: {size_gb:.1f} GB / {TARGET_SIZE_GB} GB".ljust(48) + "│")
            print(f"│ 进度: {progress:.1f}%".ljust(48) + "│")
            print(f"│ 用时: {elapsed_min} 分钟".ljust(48) + "│")
            print(f"└{'─'*48}┘\n")

            # 发送进度通知
            message = f"""📊 下载进度汇报 #{report_count}

已下载: {size_gb:.1f} GB / {TARGET_SIZE_GB} GB
进度: {progress:.1f}%
用时: {elapsed_min} 分钟

请继续等待..."""

            send_notification(f"进度 {progress:.0f}%", message)
            last_report = elapsed

        # 每30秒检查一次
        time.sleep(30)
        print(".", end="", flush=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n监控已停止")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
