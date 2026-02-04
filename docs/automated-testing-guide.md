# 自动化测试指南

> 在晚上9点后自动逐个测试所有模型

## 快速开始

### 方法 1: 使用自动化脚本（推荐）

```bash
# 晚上9点开始测试 MiniMax M2.1
./scripts/auto_test_scheduler.sh 21:00 minimax

# 晚上10点开始测试 Qwen3-Coder-Next
./scripts/auto_test_scheduler.sh 22:00 qwen

# 立即开始测试所有模型
./scripts/auto_test_scheduler.sh now all
```

---

## 工作流程

### 准备阶段（现在完成）

1. **确认 LM Studio 配置**
```bash
# 检查 Context Length
# LM Studio → Settings → Context Length = 131,072

# 确认 API server 端口
# 应为 localhost:1234
```

2. **下载所有模型**（可选，或边测边下）
```bash
# MiniMax M2.1 模型
lms download mlx-community/MiniMax-M2.1-4bit
lms download mlx-community/MiniMax-M2.1-8bit-gs32
lms download unsloth/MiniMax-M2.1-GGUF:Q4_K_M
lms download unsloth/MiniMax-M2.1-GGUF:Q6_K
lms download unsloth/MiniMax-M2.1-GGUF:Q8_0

# Qwen3-Coder-Next 模型
lms download unsloth/Qwen3-Coder-Next-GGUF:Q4_K_M
lms download unsloth/Qwen3-Coder-Next-GGUF:Q6_K
lms download unsloth/Qwen3-Coder-Next-GGUF:Q8_0
```

3. **启动脚本**（在晚上9点前）
```bash
cd /Users/jacky/projects/llm-mac-512

# 启动调度器
./scripts/auto_test_scheduler.sh 21:00 minimax
```

---

### 测试阶段（晚上9点后自动）

#### 脚本会自动：

1. **等待到晚上9点**
2. **发送通知**：提示你切换第一个模型
3. **等待你加载模型**
4. **检测到模型加载后**：自动运行测试
5. **测试完成后**：提示切换下一个模型
6. **重复步骤 2-5**：直到所有模型测试完成

#### 你需要做的：

**当收到通知时**：
```
1. 打开 LM Studio GUI
2. Unload 当前模型（如果有）
3. Load 通知中指定的模型
4. 等待模型加载完成（显示 "Loaded"）
5. 关闭 GUI（脚本会自动检测并继续）
```

**就这样！** 其他都是自动的。

---

## 测试序列

### MiniMax M2.1 测试序列（约 6-8 小时）

| # | 模型 | 后端 | 预计时间 | 说明 |
|---|------|------|----------|------|
| 1 | mlx-community/MiniMax-M2.1-4bit | MLX | ~60 min | 4-bit 基准 |
| 2 | unsloth/MiniMax-M2.1-GGUF:Q4_K_S | llama.cpp | ~60 min | 对比 MLX 4-bit |
| 3 | unsloth/MiniMax-M2.1-GGUF:Q4_K_M | llama.cpp | ~60 min | Q4 变体 |
| 4 | mlx-community/MiniMax-M2.1-8bit-gs32 | MLX | ~90 min | 8-bit 基准 |
| 5 | unsloth/MiniMax-M2.1-GGUF:Q8_0 | llama.cpp | ~90 min | 对比 MLX 8-bit |
| 6 | unsloth/MiniMax-M2.1-GGUF:Q6_K | llama.cpp | ~75 min | 6-bit 单独测试 |

**总时间**: ~7 小时

---

### Qwen3-Coder-Next 测试序列（约 3-4 小时）

| # | 模型 | 后端 | 预计时间 | 说明 |
|---|------|------|----------|------|
| 1 | unsloth/Qwen3-Coder-Next-GGUF:Q4_K_M | llama.cpp | ~45 min | 4-bit |
| 2 | unsloth/Qwen3-Coder-Next-GGUF:Q6_K | llama.cpp | ~60 min | 6-bit |
| 3 | unsloth/Qwen3-Coder-Next-GGUF:Q8_0 | llama.cpp | ~75 min | 8-bit |

**总时间**: ~3 小时

---

## 时间规划

### 方案 A: 分两晚完成（推荐）

**第一晚（今晚）: MiniMax M2.1**
```bash
# 21:00 开始
./scripts/auto_test_scheduler.sh 21:00 minimax

# 预计完成时间: 凌晨 4:00
```

**第二晚（明晚）: Qwen3-Coder-Next**
```bash
# 21:00 开始
./scripts/auto_test_scheduler.sh 21:00 qwen

# 预计完成时间: 凌晨 12:00
```

---

### 方案 B: 一晚完成所有测试

```bash
# 21:00 开始
./scripts/auto_test_scheduler.sh 21:00 all

# 预计完成时间: 次日早上 7:00
```

**注意**: 需要约每小时切换一次模型（会有通知提醒）

---

## 通知系统

脚本会在以下情况发送 macOS 通知：

1. ✅ **准备切换模型时**
   - 通知: "请切换到: [模型名称]"
   - 声音: Glass

2. ✅ **模型加载完成时**
   - 通知: "模型已加载，即将开始测试"
   - 声音: Glass

3. ✅ **所有测试完成时**
   - 通知: "全部测试完成！成功: X, 失败: Y"
   - 声音: Glass

---

## 测试输出

### 实时日志

```bash
# 查看实时日志
tail -f logs/auto_test_*.log
```

### 测试结果

自动保存到：
```
docs/test-results/
├── mlx-minimax-m2-1-4bit-{timestamp}.json
├── mlx-minimax-m2-1-4bit-{timestamp}.md
├── gguf-minimax-m2-1-q4ks-{timestamp}.json
├── gguf-minimax-m2-1-q4ks-{timestamp}.md
└── ...
```

### 测试摘要

自动生成：
```
docs/test-results/auto_test_summary_{timestamp}.md
```

---

## 中断和恢复

### 如果需要中断测试

```bash
# 按 Ctrl+C
# 或直接关闭终端窗口
```

### 恢复测试

```bash
# 从中断的地方继续（需要手动指定起始模型）
# 编辑 auto_test_scheduler.sh，注释掉已完成的测试
```

---

## 监控建议

### 第一次测试时

建议在第一个测试时保持关注：

1. ✅ 确认模型正确加载
2. ✅ 确认测试正常开始
3. ✅ 确认结果正常保存
4. ✅ 之后就可以放心让它自动运行

### 系统资源监控

```bash
# 打开 Activity Monitor
# 关注:
# - Python 进程 (测试运行中)
# - LM Studio 进程
# - 内存使用 (应该稳定)
```

---

## 故障排除

### 问题 1: 脚本无法检测模型切换

**症状**: 切换模型后脚本一直等待

**解决**:
```bash
# 1. 确认 LM Studio API server 运行
curl http://localhost:1234/v1/models

# 2. 确认模型已完全加载
# LM Studio GUI 应显示 "Loaded"

# 3. 如果还是不行，重启脚本
```

---

### 问题 2: 测试失败

**症状**: 测试运行但报错

**检查**:
```bash
# 1. 查看详细日志
cat logs/auto_test_*.log

# 2. 检查 Python 脚本
python3 scripts/benchmark_lmstudio.py

# 3. 检查配置
cat configs/gguf_standard.json
```

---

### 问题 3: 内存不足

**症状**: 系统卡顿或测试失败

**解决**:
```bash
# 1. 关闭其他大型应用
# 2. 释放内存
sudo purge

# 3. 检查可用内存
vm_stat | head -5
```

---

## 测试完成后

### 查看结果

```bash
# 查看所有测试结果
ls -lh docs/test-results/

# 查看测试摘要
cat docs/test-results/auto_test_summary_*.md

# 生成对比表
python3 scripts/compare_results.py
```

### 提交结果

```bash
git add docs/test-results/
git commit -m "Add automated test results

- MiniMax M2.1: MLX vs GGUF comparison
- Qwen3-Coder-Next: GGUF performance test
- Tested on: $(date)"

git push
```

---

## 高级选项

### 自定义测试序列

编辑 `auto_test_scheduler.sh`，修改 `MINIMAX_TESTS` 或 `QWEN_TESTS` 数组：

```bash
declare -a CUSTOM_TESTS=(
    "model-repo/model-name|Test Label"
    "another-model|Another Test"
)
```

### 调整测试间隔

修改脚本中的 `sleep 30`：

```bash
# 默认: 30秒
sleep 30

# 更长间隔: 60秒
sleep 60
```

### 跳过某些测试

注释掉不想测试的模型：

```bash
declare -a MINIMAX_TESTS=(
    # "mlx-community/MiniMax-M2.1-3bit|MiniMax M2.1 MLX 3-bit"  # 跳过
    "mlx-community/MiniMax-M2.1-4bit|MiniMax M2.1 MLX 4-bit"
)
```

---

## 今晚行动计划

### 现在（准备阶段）

1. ✅ 确认 LM Studio 配置
```bash
# Context Length = 131,072
# API Server = localhost:1234
```

2. ✅ 启动自动化脚本
```bash
cd /Users/jacky/projects/llm-mac-512
./scripts/auto_test_scheduler.sh 21:00 minimax
```

3. ✅ 脚本会等待到晚上9点

### 晚上9点（自动开始）

1. 收到通知：请切换到第一个模型
2. 打开 LM Studio，加载指定模型
3. 之后每小时左右收到通知，切换下一个模型

### 明天早上（查看结果）

1. 查看测试摘要
2. 查看详细结果
3. 如果一切正常，晚上继续测试 Qwen3-Coder-Next

---

## 预期完成时间

### MiniMax M2.1（今晚）
- **开始**: 21:00
- **结束**: ~04:00 (次日凌晨)
- **6个模型** × ~60-90分钟

### Qwen3-Coder-Next（明晚）
- **开始**: 21:00
- **结束**: ~00:00 (午夜)
- **3个模型** × ~45-75分钟

---

准备好了吗？现在就可以启动脚本，它会等到晚上9点自动开始！
