#!/bin/bash
#
# MLX API 服务器快速启动脚本
#
# 使用方法:
#   ./start_api.sh                    # 使用默认配置（4-bit, 端口8000）
#   ./start_api.sh 8-bit              # 使用8-bit模型
#   ./start_api.sh 4-bit 8080         # 使用4-bit模型，端口8080

set -e

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认值
MODEL_VARIANT="${1:-4-bit}"
PORT="${2:-8000}"
HOST="127.0.0.1"

# 获取项目目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 打印banner
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         MLX MiniMax M2.1 API Server 启动                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠ 虚拟环境不存在${NC}"
    echo "请先运行: python3 -m venv venv && source venv/bin/activate && pip install mlx-lm flask flask-cors"
    exit 1
fi

# 激活虚拟环境
echo -e "${GREEN}→ 激活虚拟环境...${NC}"
source venv/bin/activate

# 检查依赖
echo -e "${GREEN}→ 检查依赖...${NC}"
python -c "import mlx_lm" 2>/dev/null || {
    echo -e "${YELLOW}⚠ mlx-lm未安装${NC}"
    echo "正在安装..."
    pip install -q mlx-lm
}

python -c "import flask" 2>/dev/null || {
    echo -e "${YELLOW}⚠ flask未安装${NC}"
    echo "正在安装..."
    pip install -q flask flask-cors
}

# 确定模型名称
case "$MODEL_VARIANT" in
    4-bit|4bit)
        MODEL="mlx-community/MiniMax-M2.1-4bit"
        ;;
    6-bit|6bit)
        MODEL="mlx-community/MiniMax-M2.1-6bit"
        ;;
    8-bit|8bit)
        MODEL="mlx-community/MiniMax-M2.1-8bit"
        ;;
    *)
        # 允许直接指定完整模型名
        MODEL="$MODEL_VARIANT"
        ;;
esac

# 检查端口是否被占用
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠ 端口 $PORT 已被占用${NC}"
    echo "请选择其他端口，或停止占用该端口的进程:"
    lsof -Pi :$PORT -sTCP:LISTEN
    exit 1
fi

# 打印配置
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}配置信息${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "  模型: ${GREEN}$MODEL${NC}"
echo -e "  地址: ${GREEN}http://$HOST:$PORT${NC}"
echo -e "  Chat API: ${GREEN}http://$HOST:$PORT/v1/chat/completions${NC}"
echo ""
echo -e "${YELLOW}提示:${NC}"
echo -e "  • 首次运行会下载模型（~120-240GB）"
echo -e "  • 按 Ctrl+C 停止服务器"
echo -e "  • 在新终端运行测试: ${GREEN}python scripts/test_api.py${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# 启动API服务器
echo -e "${GREEN}→ 启动API服务器...${NC}"
echo ""

python scripts/api_server.py \
    --model "$MODEL" \
    --host "$HOST" \
    --port "$PORT"
