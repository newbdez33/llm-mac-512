#!/bin/bash
#
# MLX模型下载监控脚本
# 下载完成后通过OpenClaw通知
#
# 使用方法:
#   ./scripts/monitor_download.sh

set -e

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# 配置
LOG_FILE="/tmp/api_server_8bit.log"
CACHE_DIR="$HOME/.cache/huggingface/hub/models--mlx-community--MiniMax-M2.1-8bit"
OPENCLAW_NOTIFY_DIR="$HOME/.openclaw/notifications"
CHECK_INTERVAL=60  # 检查间隔（秒）
TARGET_SIZE_GB=240  # 目标大小（GB）

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         MLX 模型下载监控                                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# 检查OpenClaw通知目录
if [ ! -d "$OPENCLAW_NOTIFY_DIR" ]; then
    echo -e "${YELLOW}⚠ OpenClaw通知目录不存在，创建中...${NC}"
    mkdir -p "$OPENCLAW_NOTIFY_DIR"
fi

# 获取当前下载大小（GB）
get_download_size() {
    if [ -d "$CACHE_DIR" ]; then
        # 使用du获取大小（字节），转换为GB
        local size_bytes=$(du -s "$CACHE_DIR" | awk '{print $1}')
        local size_gb=$(echo "scale=2; $size_bytes / 1024 / 1024" | bc)
        echo "$size_gb"
    else
        echo "0"
    fi
}

# 检查是否下载完成
is_download_complete() {
    if [ -f "$LOG_FILE" ]; then
        # 检查日志中是否有"模型加载完成"
        if grep -q "模型加载完成" "$LOG_FILE"; then
            return 0
        fi
    fi
    return 1
}

# 发送OpenClaw通知
send_notification() {
    local message="$1"
    local priority="${2:-normal}"  # normal 或 urgent
    local timestamp=$(date +%Y-%m-%d)
    local notify_file="$OPENCLAW_NOTIFY_DIR/${timestamp}.md"

    cat > "$notify_file" << EOF
# 通知
## 消息
$message
## 优先级
$priority
EOF

    echo -e "${GREEN}✓ 通知已发送到OpenClaw${NC}"
}

# 发送系统通知（可选，作为备份）
send_system_notification() {
    local title="$1"
    local message="$2"

    osascript -e "display notification \"$message\" with title \"$title\" sound name \"Glass\"" 2>/dev/null || true
}

# 主监控循环
echo -e "${GREEN}开始监控模型下载...${NC}"
echo -e "日志文件: ${BLUE}$LOG_FILE${NC}"
echo -e "缓存目录: ${BLUE}$CACHE_DIR${NC}"
echo -e "检查间隔: ${YELLOW}${CHECK_INTERVAL}秒${NC}"
echo -e "目标大小: ${YELLOW}${TARGET_SIZE_GB}GB${NC}"
echo ""

start_time=$(date +%s)
last_size=0

while true; do
    # 检查是否完成
    if is_download_complete; then
        current_time=$(date +%s)
        elapsed=$((current_time - start_time))
        elapsed_min=$((elapsed / 60))

        echo ""
        echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║         模型下载完成！                                  ║${NC}"
        echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${GREEN}✓ 总用时: ${elapsed_min} 分钟${NC}"

        # 发送OpenClaw通知
        send_notification "🚀 MLX 8-bit模型下载完成！

服务器地址: http://127.0.0.1:8000
用时: ${elapsed_min} 分钟

下一步:
1. 运行测试: python scripts/test_api.py
2. 配置OpenClaw:
   export OPENAI_API_BASE=\"http://127.0.0.1:8000/v1\"
   export OPENAI_API_KEY=\"sk-dummy\"
3. 启动: openclaw

模型性能:
- TPS: 33.04 tokens/秒
- TTFT: 95ms
- 内存: 252GB" "normal"

        # 发送系统通知（备份）
        send_system_notification "MLX模型下载完成" "8-bit模型已就绪，用时 ${elapsed_min} 分钟"

        echo ""
        echo -e "${BLUE}下一步:${NC}"
        echo -e "  1. 测试API: ${GREEN}python scripts/test_api.py${NC}"
        echo -e "  2. 配置OpenClaw: ${GREEN}export OPENAI_API_BASE=\"http://127.0.0.1:8000/v1\"${NC}"
        echo -e "  3. 启动OpenClaw: ${GREEN}openclaw${NC}"
        echo ""

        exit 0
    fi

    # 获取当前下载大小
    current_size=$(get_download_size)
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))
    elapsed_min=$((elapsed / 60))

    # 计算下载速度
    if [ "$last_size" != "0" ]; then
        size_diff=$(echo "$current_size - $last_size" | bc)
        speed_mbps=$(echo "scale=2; $size_diff * 1024 / $CHECK_INTERVAL" | bc)
    else
        speed_mbps="0"
    fi

    # 计算进度
    if [ "$current_size" != "0" ]; then
        progress=$(echo "scale=2; $current_size * 100 / $TARGET_SIZE_GB" | bc)
    else
        progress="0"
    fi

    # 预计剩余时间
    if [ "$speed_mbps" != "0" ] && [ "$(echo "$speed_mbps > 0" | bc)" -eq 1 ]; then
        remaining_gb=$(echo "$TARGET_SIZE_GB - $current_size" | bc)
        remaining_mb=$(echo "$remaining_gb * 1024" | bc)
        eta_seconds=$(echo "scale=0; $remaining_mb / $speed_mbps" | bc)
        eta_min=$((eta_seconds / 60))
    else
        eta_min="未知"
    fi

    # 显示进度
    echo -e "[$(date '+%H:%M:%S')] 进度: ${YELLOW}${current_size}GB / ${TARGET_SIZE_GB}GB${NC} (${GREEN}${progress}%${NC}) | 速度: ${BLUE}${speed_mbps}MB/s${NC} | 已用: ${elapsed_min}分钟 | 预计剩余: ${eta_min}分钟"

    last_size=$current_size

    # 等待下一次检查
    sleep $CHECK_INTERVAL
done
