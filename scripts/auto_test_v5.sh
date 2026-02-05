#!/bin/bash

# 完全自动化测试 v5 - 修正语法，完成所有测试
# MLX 4-bit + 已下载模型 + 下载并测试所有 GGUF 量化版本

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
    lms ls 2>/dev/null | grep -i "$(echo $model_path | sed 's/@.*//')" | grep -q "."
}

# 下载模型（统一接口）
download_model() {
    local model_path="$1"
    local label="$2"

    log "下载模型: $model_path"

    # 检查是否已下载
    if is_model_downloaded "$model_path"; then
        log "✓ 模型已存在，跳过下载"
        return 0
    fi

    # 开始下载
    notify "下载中" "$label"
    log "开始下载..."

    if lms get "$model_path" --yes 2>&1 | tee -a "$LOG_FILE"; then
        log "✓ 下载完成"
        sleep 5  # 等待文件系统同步
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
            if [[ "$current" != "none" && "$current" != "" ]]; then
                log "✓ 模型已就绪: $current"
                sleep 10
                return 0
            fi
            wait=$((wait + 5))
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
    local label="$2"

    # 保护 Q4_K_S
    if [[ "$label" == *"Q4_K_S"* ]]; then
        log "✓ 保留: $label"
        return 0
    fi

    log "删除: $label"

    local lms_dir="$HOME/.lmstudio/models"

    # MLX 模型
    if [[ "$model_path" == mlx-community/* ]]; then
        local model_name=$(echo "$model_path" | cut -d'/' -f2)
        local mlx_path="$lms_dir/mlx-community/$model_name"
        if [[ -d "$mlx_path" ]]; then
            local size=$(du -sh "$mlx_path" 2>/dev/null | cut -f1)
            log "找到: $mlx_path ($size)"
            rm -rf "$mlx_path"
            log "✓ 已删除: $size"
            return 0
        fi
    fi

    # GGUF 模型
    if [[ "$model_path" == unsloth/* ]]; then
        # 查找所有 unsloth 目录，删除非 Q4_K_S 的
        find "$lms_dir/unsloth" -maxdepth 1 -type d 2>/dev/null | while read dir; do
            if [[ "$dir" != "$lms_dir/unsloth" && "$dir" != *"Q4_K_S"* ]]; then
                local size=$(du -sh "$dir" 2>/dev/null | cut -f1)
                log "找到: $dir ($size)"
                rm -rf "$dir"
                log "✓ 已删除: $size"
            fi
        done
    fi

    log "删除完成"
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

# 所有测试（按优先级排序）
declare -a ALL_TESTS=(
    "unsloth/MiniMax-M2.1-GGUF@Q4_K_S|MiniMax M2.1 GGUF Q4_K_S|skip_download"
    "mlx-community/minimax-m2.1|MiniMax M2.1 MLX 8-bit|skip_download"
    "mlx-community/MiniMax-M2.1-4bit|MiniMax M2.1 MLX 4-bit|download"
    "unsloth/MiniMax-M2.1-GGUF@Q4_K_M|MiniMax M2.1 GGUF Q4_K_M|download"
    "unsloth/MiniMax-M2.1-GGUF@Q6_K|MiniMax M2.1 GGUF Q6_K|download"
    "unsloth/MiniMax-M2.1-GGUF@Q8_0|MiniMax M2.1 GGUF Q8_0|download"
)

# ==================== 主函数 ====================

main() {
    log_section "自动化测试 v5 开始"

    local total=${#ALL_TESTS[@]}
    notify "测试开始" "共 $total 个模型"

    # 确保服务器运行
    if ! ensure_server; then
        log "✗ 无法启动服务器，退出"
        exit 1
    fi

    local count=0
    local success=0
    local fail=0

    for item in "${ALL_TESTS[@]}"; do
        count=$((count + 1))

        IFS='|' read -r model_path label action <<< "$item"

        log_section "测试 ${count}/${total}: $label"

        # 下载模型（如果需要）
        if [[ "$action" == "download" ]]; then
            notify "准备中" "($count/$total) $label"

            if ! download_model "$model_path" "$label"; then
                log "✗ 下载失败，跳过"
                fail=$((fail + 1))
                continue
            fi
        fi

        # 加载模型
        notify "加载中" "($count/$total) $label"
        if ! load_model "$model_path"; then
            log "✗ 加载失败，跳过"
            fail=$((fail + 1))
            # 尝试删除失败的模型
            if [[ "$action" == "download" ]]; then
                delete_model "$model_path" "$label"
            fi
            continue
        fi

        # 运行测试
        if run_test "$label"; then
            success=$((success + 1))

            # 删除模型（除了 Q4_K_S）
            if [[ "$action" == "download" ]]; then
                sleep 5
                delete_model "$model_path" "$label"
            fi
        else
            fail=$((fail + 1))
        fi

        # 间隔
        if [[ $count -lt $total ]]; then
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
