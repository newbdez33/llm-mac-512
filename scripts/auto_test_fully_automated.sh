#!/bin/bash

# 完全自动化测试脚本
# 自动加载模型、测试、删除，无需人工干预

set -e

PROJECT_DIR="/Users/jacky/projects/llm-mac-512"
cd "$PROJECT_DIR"

LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/auto_test_${TIMESTAMP}.log"

API_URL="http://localhost:1234"

# ==================== 日志函数 ====================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_section() {
    echo "" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
    echo "$1" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
}

send_notification() {
    local title="$1"
    local message="$2"
    log "📢 通知: $title - $message"

    if command -v lily &> /dev/null; then
        lily notify "$title: $message" 2>/dev/null || true
    fi

    osascript -e "display notification \"$message\" with title \"$title\" sound name \"Glass\"" 2>/dev/null || true
}

# ==================== 工具函数 ====================

check_lms_server() {
    if curl -s "${API_URL}/v1/models" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

get_current_model() {
    local response=$(curl -s "${API_URL}/v1/models" 2>/dev/null)
    echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['data'][0]['id'] if d.get('data') else 'none')" 2>/dev/null || echo "none"
}

# 自动加载模型
load_model() {
    local model_name="$1"

    log "自动加载模型: $model_name"

    # 先停止当前服务器
    log "停止 LM Studio 服务器..."
    lms server stop 2>/dev/null || true
    sleep 5

    # 加载新模型并启动服务器
    log "启动服务器并加载模型..."
    lms server start "$model_name" --port 1234 > /dev/null 2>&1 &

    # 等待服务器启动
    local max_wait=180
    local waited=0

    while [ $waited -lt $max_wait ]; do
        if check_lms_server; then
            local current=$(get_current_model)
            if [[ "$current" != "none" ]]; then
                log "✓ 模型已加载: $current"
                sleep 10  # 额外等待确保完全就绪
                return 0
            fi
        fi

        sleep 5
        waited=$((waited + 5))
        log "等待模型加载... ($waited/$max_wait 秒)"
    done

    log "✗ 模型加载超时"
    return 1
}

# 删除模型
delete_model() {
    local model_name="$1"

    # 保护 Q4_K_S
    if [[ "$model_name" == *"Q4_K_S"* ]]; then
        log "✓ 保留模型: $model_name"
        return 0
    fi

    log "删除模型: $model_name"

    local lms_models_dir="$HOME/.lmstudio/models"
    local model_paths=(
        "$lms_models_dir/$(echo $model_name | sed 's|/|--|g')"
        "$lms_models_dir/$(echo $model_name | sed 's|/|--|g' | sed 's|:|@|g')"
        "$lms_models_dir/$(echo $model_name | cut -d'/' -f2 | cut -d':' -f1)"
    )

    local deleted=false
    for model_path in "${model_paths[@]}"; do
        if [[ -d "$model_path" ]]; then
            local dir_size=$(du -sh "$model_path" 2>/dev/null | cut -f1)
            log "找到: $model_path ($dir_size)"
            rm -rf "$model_path"
            log "✓ 已删除: $dir_size"
            deleted=true
        fi
    done

    if [[ "$deleted" == false ]]; then
        log "⚠ 未找到模型文件"
    fi
}

# 运行测试
run_test() {
    local model_name="$1"
    local test_label="$2"

    log_section "测试: $test_label"

    if ! check_lms_server; then
        log "✗ 服务器未运行"
        return 1
    fi

    log "开始测试..."
    local test_start=$(date +%s)

    if python3 scripts/benchmark_lmstudio.py; then
        local test_end=$(date +%s)
        local duration=$((test_end - test_start))
        log "✓ 测试完成 (耗时: ${duration}秒)"

        # 提取结果
        local latest_result=$(ls -t docs/test-results/*.md 2>/dev/null | head -1)
        if [[ -n "$latest_result" ]]; then
            log "结果: $latest_result"
            local tps=$(grep "Average TPS" "$latest_result" 2>/dev/null | head -1 | awk '{print $NF}')
            grep -E "Average TPS|Total tokens|Peak memory" "$latest_result" | tee -a "$LOG_FILE"

            # 发送通知
            send_notification "测试完成" "$test_label (TPS: $tps)"
        fi

        return 0
    else
        log "✗ 测试失败"
        return 1
    fi
}

# ==================== 测试序列 ====================

declare -a TESTS=(
    "mlx-community/MiniMax-M2.1-4bit|MiniMax M2.1 MLX 4-bit"
    "unsloth/MiniMax-M2.1-GGUF:Q4_K_S|MiniMax M2.1 GGUF Q4_K_S"
    "unsloth/MiniMax-M2.1-GGUF:Q4_K_M|MiniMax M2.1 GGUF Q4_K_M"
    "mlx-community/MiniMax-M2.1-8bit-gs32|MiniMax M2.1 MLX 8-bit"
    "unsloth/MiniMax-M2.1-GGUF:Q8_0|MiniMax M2.1 GGUF Q8_0"
    "unsloth/MiniMax-M2.1-GGUF:Q6_K|MiniMax M2.1 GGUF Q6_K"
)

# ==================== 主函数 ====================

main() {
    log_section "完全自动化测试开始"
    send_notification "测试开始" "自动测试 ${#TESTS[@]} 个模型"

    local test_count=0
    local success_count=0
    local fail_count=0

    for test_item in "${TESTS[@]}"; do
        test_count=$((test_count + 1))

        IFS='|' read -r model_name test_label <<< "$test_item"

        log_section "测试 ${test_count}/${#TESTS[@]}: $test_label"
        send_notification "加载模型" "($test_count/${#TESTS[@]}) $test_label"

        # 自动加载模型
        if ! load_model "$model_name"; then
            log "✗ 模型加载失败，跳过"
            fail_count=$((fail_count + 1))
            continue
        fi

        # 运行测试
        if run_test "$model_name" "$test_label"; then
            success_count=$((success_count + 1))

            # 删除模型（除了 Q4_K_S）
            sleep 5
            delete_model "$model_name"
        else
            fail_count=$((fail_count + 1))
        fi

        # 测试间隔
        if [[ $test_count -lt ${#TESTS[@]} ]]; then
            log "等待 30 秒..."
            sleep 30
        fi
    done

    # 总结
    log_section "测试完成"
    log "总数: $test_count"
    log "成功: $success_count"
    log "失败: $fail_count"

    send_notification "测试完成" "成功: $success_count, 失败: $fail_count" "Hero"

    log "日志: $LOG_FILE"
}

# ==================== 启动 ====================

trap 'log "测试被中断"; exit 1' INT

main "$@"
