#!/bin/bash

# 单次测试脚本 - 测试当前加载的模型
# 使用方法: ./run_single_test.sh [model_label]

PROJECT_DIR="/Users/jacky/projects/llm-mac-512"
cd "$PROJECT_DIR"

API_URL="http://localhost:1234"

# 获取当前模型
get_current_model() {
    curl -s "${API_URL}/v1/models" 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['data'][0]['id'] if d.get('data') else 'none')" 2>/dev/null || echo "none"
}

# 检查服务器
if ! curl -s "${API_URL}/v1/models" > /dev/null 2>&1; then
    echo "❌ LM Studio 服务器未运行"
    echo ""
    echo "请先启动 LM Studio 并加载模型"
    exit 1
fi

# 获取当前模型
current_model=$(get_current_model)
model_label="${1:-$current_model}"

echo "========================================="
echo "测试当前模型"
echo "========================================="
echo "模型: $current_model"
echo "标签: $model_label"
echo ""

# 运行测试
echo "开始测试..."
python3 scripts/benchmark_lmstudio.py

# 显示结果
latest=$(ls -t docs/test-results/*.md 2>/dev/null | head -1)
if [[ -n "$latest" ]]; then
    echo ""
    echo "========================================="
    echo "测试结果"
    echo "========================================="
    grep -E "Average TPS|Total tokens|Peak memory" "$latest"
    echo ""
    echo "完整结果: $latest"
fi

# 发送通知
if command -v lily &> /dev/null; then
    lily notify "测试完成: $model_label"
fi
