#!/bin/bash

# 自动化测试调度器
# 功能：在指定时间开始自动逐个测试模型
# 使用方法：./auto_test_scheduler.sh [start_time]
# 示例：./auto_test_scheduler.sh "21:00" (晚上9点开始)

set -e

# ==================== 配置 ====================

# 项目目录
PROJECT_DIR="/Users/jacky/projects/llm-mac-512"
cd "$PROJECT_DIR"

# 日志目录
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

# 时间戳
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/auto_test_${TIMESTAMP}.log"

# LM Studio CLI 路径
LMS_CLI="lms"

# API 端点
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

# 发送通知（支持 lily notify 和 osascript）
send_notification() {
    local title="$1"
    local message="$2"
    local sound="${3:-Glass}"

    log "📢 通知: $title - $message"

    # 尝试使用 lily notify
    if command -v lily &> /dev/null; then
        lily notify "$title: $message" 2>/dev/null || true
    fi

    # 同时使用 macOS 系统通知
    osascript -e "display notification \"$message\" with title \"$title\" sound name \"$sound\"" 2>/dev/null || true
}

# ==================== 工具函数 ====================

# 等待到指定时间
wait_until() {
    local target_time="$1"
    log "计划在 $target_time 开始测试"

    while true; do
        current_time=$(date +%H:%M)
        if [[ "$current_time" == "$target_time" ]]; then
            log "时间到！开始测试..."
            break
        fi

        # 每分钟检查一次
        sleep 60
    done
}

# 检查 LM Studio 服务器状态
check_lms_server() {
    log "检查 LM Studio 服务器..."

    if curl -s "${API_URL}/v1/models" > /dev/null 2>&1; then
        log "✓ LM Studio 服务器运行正常"
        return 0
    else
        log "✗ LM Studio 服务器未响应"
        return 1
    fi
}

# 获取当前加载的模型
get_current_model() {
    local response=$(curl -s "${API_URL}/v1/models" 2>/dev/null)
    echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['data'][0]['id'] if d.get('data') else 'none')" 2>/dev/null || echo "none"
}

# 等待模型加载完成
wait_for_model_ready() {
    local max_wait=300  # 最多等待5分钟
    local waited=0

    log "等待模型加载完成..."

    while [ $waited -lt $max_wait ]; do
        if check_lms_server; then
            local model=$(get_current_model)
            if [[ "$model" != "none" ]]; then
                log "✓ 模型已加载: $model"
                return 0
            fi
        fi

        sleep 10
        waited=$((waited + 10))
        log "等待中... ($waited/$max_wait 秒)"
    done

    log "✗ 模型加载超时"
    return 1
}

# 删除模型
delete_model() {
    local model_name="$1"
    local model_label="$2"

    log "准备删除模型: $model_label"

    # 保护列表：不删除这些模型
    local keep_models=(
        "Q4_K_S"  # 保留当前的 MiniMax 4-bit
    )

    # 检查是否在保护列表中
    for keep in "${keep_models[@]}"; do
        if [[ "$model_name" == *"$keep"* ]]; then
            log "✓ 保留模型: $model_label (在保护列表中)"
            return 0
        fi
    done

    # LM Studio 模型存储路径
    local lms_models_dir="$HOME/.lmstudio/models"

    # 尝试多种路径格式
    local model_paths=(
        # mlx-community/MiniMax-M2.1-4bit → mlx-community--MiniMax-M2.1-4bit
        "$lms_models_dir/$(echo $model_name | sed 's|/|--|g')"
        # unsloth/MiniMax-M2.1-GGUF:Q4_K_M → unsloth--MiniMax-M2.1-GGUF@Q4_K_M
        "$lms_models_dir/$(echo $model_name | sed 's|/|--|g' | sed 's|:|@|g')"
        # 仅使用仓库名
        "$lms_models_dir/$(echo $model_name | cut -d'/' -f2 | cut -d':' -f1)"
    )

    local deleted=false
    for model_path in "${model_paths[@]}"; do
        if [[ -d "$model_path" ]]; then
            local dir_size=$(du -sh "$model_path" 2>/dev/null | cut -f1)
            log "找到模型目录: $model_path (大小: $dir_size)"

            # 自动删除（无需确认）
            log "删除中..."
            rm -rf "$model_path"

            if [[ ! -d "$model_path" ]]; then
                log "✓ 已删除: $model_path (释放: $dir_size)"
                deleted=true
            else
                log "✗ 删除失败: $model_path"
            fi
        fi
    done

    if [[ "$deleted" == false ]]; then
        log "⚠ 未找到模型文件，可能已被删除或路径不匹配"
        # 列出所有模型目录供参考
        log "当前模型目录列表:"
        ls -lh "$lms_models_dir" 2>/dev/null | grep "^d" | awk '{print "  - " $NF}' | tee -a "$LOG_FILE"
    fi
}

# 运行单个测试
run_test() {
    local model_name="$1"
    local test_label="$2"
    local auto_delete="${3:-false}"  # 新增：是否自动删除

    log_section "测试: $test_label"
    log "模型: $model_name"

    # 检查服务器状态
    if ! check_lms_server; then
        log "✗ LM Studio 服务器未运行，跳过此测试"
        return 1
    fi

    # 获取当前模型
    local current_model=$(get_current_model)
    log "当前加载的模型: $current_model"

    # 运行测试
    log "开始运行测试..."
    local test_start=$(date +%s)

    if python3 scripts/benchmark_lmstudio.py; then
        local test_end=$(date +%s)
        local duration=$((test_end - test_start))
        log "✓ 测试完成 (耗时: ${duration}秒)"

        # 查找最新的测试结果
        local latest_result=$(ls -t docs/test-results/*.md 2>/dev/null | head -1)
        if [[ -n "$latest_result" ]]; then
            log "结果文件: $latest_result"
            # 提取关键指标
            grep -E "Average TPS|Total tokens|Peak memory" "$latest_result" | tee -a "$LOG_FILE"
        fi

        # 测试完成后删除模型（如果启用）
        if [[ "$auto_delete" == "true" ]]; then
            log "测试完成，准备删除模型..."
            sleep 5  # 等待5秒确保文件已保存
            delete_model "$model_name" "$test_label"

            # 通知测试完成和删除
            send_notification "测试完成" "$test_label 已完成并删除 (TPS: $(grep "Average TPS" "$latest_result" 2>/dev/null | head -1 | awk '{print $NF}'))"
        fi

        return 0
    else
        log "✗ 测试失败"
        return 1
    fi
}

# 等待用户切换模型
wait_for_model_switch() {
    local next_model="$1"

    log_section "等待切换到下一个模型"
    log "下一个模型: $next_model"
    log ""
    log "请在 LM Studio GUI 中:"
    log "  1. Unload 当前模型"
    log "  2. Load $next_model"
    log "  3. 等待模型加载完成"
    log ""

    # 等待模型切换
    local old_model=$(get_current_model)
    log "当前模型: $old_model"

    # 发送通知
    send_notification "LM Studio 测试" "请切换到: $next_model"

    log "等待模型切换..."

    while true; do
        sleep 10
        local current_model=$(get_current_model)

        if [[ "$current_model" != "$old_model" ]] && [[ "$current_model" != "none" ]]; then
            log "✓ 检测到模型切换: $current_model"

            # 再等待10秒确保完全加载
            log "等待模型稳定..."
            sleep 10

            # 发送通知
            send_notification "LM Studio 测试" "模型已加载，即将开始测试"

            break
        fi
    done
}

# ==================== 测试配置 ====================

# Week 1: MiniMax M2.1 测试序列
declare -a MINIMAX_TESTS=(
    "mlx-community/MiniMax-M2.1-4bit|MiniMax M2.1 MLX 4-bit"
    "unsloth/MiniMax-M2.1-GGUF:Q4_K_S|MiniMax M2.1 GGUF Q4_K_S"
    "unsloth/MiniMax-M2.1-GGUF:Q4_K_M|MiniMax M2.1 GGUF Q4_K_M"
    "mlx-community/MiniMax-M2.1-8bit-gs32|MiniMax M2.1 MLX 8-bit"
    "unsloth/MiniMax-M2.1-GGUF:Q8_0|MiniMax M2.1 GGUF Q8_0"
    "unsloth/MiniMax-M2.1-GGUF:Q6_K|MiniMax M2.1 GGUF Q6_K"
)

# Week 2: Qwen3-Coder-Next 测试序列
declare -a QWEN_TESTS=(
    "unsloth/Qwen3-Coder-Next-GGUF:Q4_K_M|Qwen3-Coder-Next GGUF Q4_K_M"
    "unsloth/Qwen3-Coder-Next-GGUF:Q6_K|Qwen3-Coder-Next GGUF Q6_K"
    "unsloth/Qwen3-Coder-Next-GGUF:Q8_0|Qwen3-Coder-Next GGUF Q8_0"
)

# ==================== 主函数 ====================

main() {
    log_section "自动化测试调度器启动"
    log "日志文件: $LOG_FILE"

    # 解析启动时间参数
    local start_time="${1:-21:00}"

    # 选择测试套件
    local test_suite="${2:-minimax}"

    if [[ "$test_suite" == "minimax" ]]; then
        log "测试套件: MiniMax M2.1"
        tests=("${MINIMAX_TESTS[@]}")
    elif [[ "$test_suite" == "qwen" ]]; then
        log "测试套件: Qwen3-Coder-Next"
        tests=("${QWEN_TESTS[@]}")
    elif [[ "$test_suite" == "all" ]]; then
        log "测试套件: 全部模型"
        tests=("${MINIMAX_TESTS[@]}" "${QWEN_TESTS[@]}")
    else
        log "✗ 未知测试套件: $test_suite"
        exit 1
    fi

    log "计划测试数量: ${#tests[@]}"

    # 如果指定了启动时间，则等待
    if [[ "$start_time" != "now" ]]; then
        wait_until "$start_time"
    fi

    # 执行测试
    log_section "开始执行测试"
    send_notification "测试开始" "开始测试 ${#tests[@]} 个模型"

    local test_count=0
    local success_count=0
    local fail_count=0

    for test_item in "${tests[@]}"; do
        test_count=$((test_count + 1))

        # 解析测试项
        IFS='|' read -r model_name test_label <<< "$test_item"

        log_section "测试 ${test_count}/${#tests[@]}"

        # 等待用户切换模型
        wait_for_model_switch "$model_name"

        # 运行测试（启用自动删除）
        if run_test "$model_name" "$test_label" "true"; then
            success_count=$((success_count + 1))
            log "✓ 测试通过（模型已删除）"
        else
            fail_count=$((fail_count + 1))
            log "✗ 测试失败"
        fi

        # 测试间隔
        if [[ $test_count -lt ${#tests[@]} ]]; then
            log "等待 30 秒后继续..."
            sleep 30
        fi
    done

    # 测试总结
    log_section "测试完成"
    log "总测试数: $test_count"
    log "成功: $success_count"
    log "失败: $fail_count"
    log "日志文件: $LOG_FILE"

    # 发送完成通知
    send_notification "LM Studio 测试完成" "全部测试完成！成功: $success_count, 失败: $fail_count" "Hero"

    # 生成测试摘要
    generate_summary
}

# 生成测试摘要
generate_summary() {
    local summary_file="$PROJECT_DIR/docs/test-results/auto_test_summary_${TIMESTAMP}.md"

    cat > "$summary_file" << EOF
# 自动化测试摘要

> 测试时间: $(date)
> 日志文件: $LOG_FILE

## 测试结果

EOF

    # 列出所有测试结果
    ls -t "$PROJECT_DIR/docs/test-results/"*.md 2>/dev/null | head -20 | while read result_file; do
        echo "- [$(basename "$result_file")]($result_file)" >> "$summary_file"
    done

    log "测试摘要: $summary_file"
}

# ==================== 启动 ====================

# 捕获 Ctrl+C
trap 'log "测试被中断"; exit 1' INT

# 显示用法
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    cat << EOF
自动化测试调度器

使用方法:
  $0 [start_time] [test_suite]

参数:
  start_time   开始时间 (HH:MM 格式，如 21:00)，或 "now" 立即开始
               默认: 21:00

  test_suite   测试套件:
               - minimax: 只测试 MiniMax M2.1 (默认)
               - qwen: 只测试 Qwen3-Coder-Next
               - all: 测试所有模型

示例:
  $0 21:00 minimax        # 晚上9点开始测试 MiniMax M2.1
  $0 22:00 qwen           # 晚上10点开始测试 Qwen3-Coder-Next
  $0 now all              # 立即开始测试所有模型

注意:
  - 需要 LM Studio 服务器运行在 localhost:1234
  - 脚本会提示你在 GUI 中切换模型
  - 每次切换后会自动检测并继续测试

EOF
    exit 0
fi

# 执行主函数
main "$@"
