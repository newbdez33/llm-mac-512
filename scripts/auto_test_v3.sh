#!/bin/bash

# 完全自动化测试 v3 - 下载→测试→删除流程
# 逐个下载模型，测试后删除

set -e

PROJECT_DIR="/Users/jacky/projects/llm-mac-512"
cd "$PROJECT_DIR"

LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/auto_test_${TIMESTAMP}.log"

API_URL="http://localhost:1234"

# ==================== 日志 ====================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_section() {
    echo "" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
    echo "$1" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
}

notify() {
    local title="$1"
    local message="$2"
    log "📢 $title: $message"

    if command -v lily &> /dev/null; then
        lily notify "$title: $message" 2>/dev/null || true
    fi

    osascript -e "display notification \"$message\" with title \"$title\" sound name \"Glass\"" 2>/dev/null || true
}

# ==================== 工具 ====================

check_server() {
    curl -s "${API_URL}/v1/models" > /dev/null 2>&1
}

get_model() {
    curl -s "${API_URL}/v1/models" 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['data'][0]['id'] if d.get('data') else 'none')" 2>/dev/null || echo "none"
}

# 启动服务器（如果未运行）
ensure_server() {
    if check_server; then
        log "✓ 服务器已运行"
        return 0
    fi

    log "启动 LM Studio 服务器..."
    lms server start -p 1234 > /dev/null 2>&1 &

    local wait=0
    while [ $wait -lt 30 ]; do
        sleep 2
        if check_server; then
            log "✓ 服务器已启动"
            return 0
        fi
        wait=$((wait + 2))
    done

    log "✗ 服务器启动失败"
    return 1
}

# 检查模型是否已下载
is_model_downloaded() {
    local model_path="$1"
    lms ls 2>/dev/null | grep -q "$model_path"
}

# 下载模型
download_model() {
    local model_path="$1"

    log "下载模型: $model_path"

    # 检查是否已下载
    if is_model_downloaded "$model_path"; then
        log "✓ 模型已存在，跳过下载"
        return 0
    fi

    # 开始下载 (使用 lms get 命令)
    log "开始下载..."
    if lms get "$model_path" --yes 2>&1 | tee -a "$LOG_FILE"; then
        log "✓ 下载完成"
        return 0
    else
        log "✗ 下载失败"
        return 1
    fi
}

# 加载模型
load_model() {
    local model_path="$1"

    log "加载模型: $model_path"

    # 先卸载当前模型
    lms unload 2>/dev/null || true
    sleep 3

    # 加载新模型
    if lms load -y "$model_path" --context-length 131072 2>&1 | tee -a "$LOG_FILE"; then
        log "✓ 模型加载命令已执行"

        # 等待模型真正加载完成
        local wait=0
        while [ $wait -lt 180 ]; do
            sleep 5
            local current=$(get_model)
            if [[ "$current" != "none" ]]; then
                log "✓ 模型已就绪: $current"
                sleep 10  # 额外等待10秒确保稳定
                return 0
            fi
            wait=$((wait + 5))
            log "等待模型加载... ($wait/180)"
        done

        log "✗ 模型加载超时"
        return 1
    else
        log "✗ 模型加载命令失败"
        return 1
    fi
}

# 删除模型
delete_model() {
    local model_path="$1"

    # 保护 Q4_K_S
    if [[ "$model_path" == *"Q4_K_S"* ]]; then
        log "✓ 保留: $model_path"
        return 0
    fi

    log "删除: $model_path"

    local lms_dir="$HOME/.lmstudio/models"

    # 尝试多种路径格式
    local paths=(
        "$lms_dir/$model_path"
        "$lms_dir/$(echo $model_path | sed 's|/|--|g')"
        "$lms_dir/$(echo $model_path | sed 's|@|:|g')"
        "$lms_dir/$(echo $model_path | sed 's|/|--|g' | sed 's|@|:|g')"
    )

    for path in "${paths[@]}"; do
        if [[ -d "$path" ]]; then
            local size=$(du -sh "$path" 2>/dev/null | cut -f1)
            log "找到: $path ($size)"
            rm -rf "$path"
            log "✓ 已删除: $size"
            return 0
        fi
    done

    log "⚠ 未找到模型文件"
}

# 运行测试
run_test() {
    local label="$1"

    log_section "测试: $label"

    if ! check_server; then
        log "✗ 服务器未运行"
        return 1
    fi

    log "开始测试..."
    local start=$(date +%s)

    if python3 scripts/benchmark_lmstudio.py 2>&1 | tee -a "$LOG_FILE"; then
        local end=$(date +%s)
        local duration=$((end - start))
        log "✓ 测试完成 (${duration}秒)"

        # 提取结果
        local result=$(ls -t docs/test-results/*.md 2>/dev/null | head -1)
        if [[ -n "$result" ]]; then
            local tps=$(grep "Average TPS" "$result" 2>/dev/null | head -1 | awk '{print $NF}')
            log "结果: $result"
            log "TPS: $tps"
            grep -E "Average TPS|Total tokens|Peak memory" "$result" | tee -a "$LOG_FILE"

            notify "测试完成" "$label (TPS: $tps)"
            return 0
        fi
    fi

    log "✗ 测试失败"
    return 1
}

# ==================== 测试序列 ====================

declare -a TESTS=(
    "mlx-community/MiniMax-M2.1-4bit|MiniMax M2.1 MLX 4-bit"
    "unsloth/MiniMax-M2.1-GGUF@Q4_K_S|MiniMax M2.1 GGUF Q4_K_S"
    "unsloth/MiniMax-M2.1-GGUF@Q4_K_M|MiniMax M2.1 GGUF Q4_K_M"
    "mlx-community/MiniMax-M2.1-8bit-gs32|MiniMax M2.1 MLX 8-bit"
    "unsloth/MiniMax-M2.1-GGUF@Q8_0|MiniMax M2.1 GGUF Q8_0"
    "unsloth/MiniMax-M2.1-GGUF@Q6_K|MiniMax M2.1 GGUF Q6_K"
)

# ==================== 主函数 ====================

main() {
    log_section "自动化测试 v3 开始"
    notify "测试开始" "自动测试 ${#TESTS[@]} 个模型 (下载→测试→删除)"

    # 确保服务器运行
    if ! ensure_server; then
        log "✗ 无法启动服务器，退出"
        exit 1
    fi

    local count=0
    local success=0
    local fail=0

    for item in "${TESTS[@]}"; do
        count=$((count + 1))

        IFS='|' read -r model_path label <<< "$item"

        log_section "测试 ${count}/${#TESTS[@]}: $label"
        notify "处理模型" "($count/${#TESTS[@]}) $label"

        # 下载模型（如果需要）
        if ! is_model_downloaded "$model_path"; then
            notify "下载中" "$label"
            if ! download_model "$model_path"; then
                log "✗ 下载失败，跳过"
                fail=$((fail + 1))
                continue
            fi
        fi

        # 加载模型
        if ! load_model "$model_path"; then
            log "✗ 加载失败，跳过"
            fail=$((fail + 1))
            # 尝试删除失败的模型
            delete_model "$model_path"
            continue
        fi

        # 运行测试
        if run_test "$label"; then
            success=$((success + 1))

            # 删除模型
            sleep 5
            delete_model "$model_path"
        else
            fail=$((fail + 1))
        fi

        # 间隔
        if [[ $count -lt ${#TESTS[@]} ]]; then
            log "等待 30 秒..."
            sleep 30
        fi
    done

    # 总结
    log_section "测试完成"
    log "总数: $count, 成功: $success, 失败: $fail"
    notify "全部完成" "成功: $success, 失败: $fail"

    log "日志: $LOG_FILE"
}

# ==================== 启动 ====================

trap 'log "测试中断"; exit 1' INT

main "$@"
