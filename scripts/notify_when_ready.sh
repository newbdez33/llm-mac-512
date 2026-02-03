#!/bin/bash
#
# 监控并汇报下载进度
# 每5分钟汇报一次，完成时发送通知
#

LOG_FILE="/tmp/api_server_8bit.log"
CACHE_DIR="$HOME/.cache/huggingface/hub/models--mlx-community--MiniMax-M2.1-8bit"
NOTIFY_DIR="$HOME/.openclaw/notifications"
REPORT_INTERVAL=300  # 5分钟 = 300秒
TARGET_SIZE=240  # 目标240GB

echo "开始监控模型下载..."
echo "日志: $LOG_FILE"
echo "每5分钟汇报一次进度"
echo ""

# 创建通知目录
mkdir -p "$NOTIFY_DIR"

start_time=$(date +%s)
last_report=0
check_count=0

while true; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))

    # 检查是否完成
    if [ -f "$LOG_FILE" ]; then
        if grep -q "模型加载完成\|Running on" "$LOG_FILE"; then
            elapsed_min=$((elapsed / 60))

            echo ""
            echo "════════════════════════════════════════"
            echo "✓ 模型加载完成！"
            echo "总用时: ${elapsed_min} 分钟"
            echo "════════════════════════════════════════"

            # 发送OpenClaw通知
            cat > "$NOTIFY_DIR/$(date +%Y-%m-%d).md" << EOF
# 通知
## 消息
🚀 MLX 8-bit模型下载完成！

✅ API服务器已就绪
📍 http://127.0.0.1:8000
⏱️ 用时: ${elapsed_min} 分钟

下一步:
1. python scripts/test_api.py
2. export OPENAI_API_BASE="http://127.0.0.1:8000/v1"
3. openclaw

性能: 33 TPS, 95ms TTFT
## 优先级
normal
EOF

            osascript -e 'display notification "API服务器已就绪" with title "MLX 8-bit完成" sound name "Glass"' 2>/dev/null

            echo "✓ 通知已发送！"
            exit 0
        fi
    fi

    # 每5分钟汇报一次
    if [ $((elapsed - last_report)) -ge $REPORT_INTERVAL ]; then
        if [ -d "$CACHE_DIR" ]; then
            # 获取当前大小（GB）
            size_kb=$(du -sk "$CACHE_DIR" | awk '{print $1}')
            size_gb=$(echo "scale=1; $size_kb / 1024 / 1024" | bc)
            progress=$(echo "scale=1; $size_gb * 100 / $TARGET_SIZE" | bc)

            elapsed_min=$((elapsed / 60))

            echo ""
            echo "┌────────────────────────────────────────┐"
            echo "│ [$(date '+%H:%M')] 进度汇报 #$((elapsed_min / 5))"
            echo "├────────────────────────────────────────┤"
            echo "│ 已下载: ${size_gb} GB / ${TARGET_SIZE} GB"
            echo "│ 进度: ${progress}%"
            echo "│ 用时: ${elapsed_min} 分钟"
            echo "└────────────────────────────────────────┘"
            echo ""

            # 发送进度通知到OpenClaw
            cat > "$NOTIFY_DIR/$(date +%Y-%m-%d-%H%M).md" << EOF
# 通知
## 消息
📊 下载进度汇报

已下载: ${size_gb}GB / ${TARGET_SIZE}GB
进度: ${progress}%
用时: ${elapsed_min}分钟

请继续等待...
## 优先级
normal
EOF
        fi

        last_report=$elapsed
    fi

    # 每30秒检查一次
    check_count=$((check_count + 1))
    if [ $((check_count % 10)) -eq 0 ]; then
        echo -n "[$(date '+%H:%M:%S')] 检查中..."
    fi
    echo -n "."

    sleep 30
done
