# MiniMax M2.1 在 512GB 统一内存 Mac 上的性能测试

在 Mac (512GB 统一内存) 上对 MiniMax M2.1 模型的各个变体进行全面的性能基准测试，对比 MLX 和 llama.cpp 框架。

[中文版](./README.zh-CN.md) | [English](./README.md)

**🚀 [快速开始 - 5分钟运行MLX](./QUICKSTART.md)** | **📖 [完整本地运行指南](./docs/mlx-local-setup.md)** | **🔌 [OpenClaw API配置](./docs/openclaw-setup.md)**

## 模型概述

- **MiniMax M2.1**: 230B 参数的 MoE 模型（10B 激活参数）
- **发布日期**: 2025年12月23日
- **优化方向**: 代码生成、工具使用、指令跟随、长期规划

## 测试机器配置

| 规格 | 详情 |
|------|------|
| **型号** | Mac Studio (Mac15,14) |
| **芯片** | Apple M3 Ultra |
| **CPU 核心** | 32核（24性能核 + 8效率核）|
| **统一内存** | 512 GB |
| **macOS** | 26.2 (Build 25C56) |
| **Python** | 3.12.12 |
| **MLX** | 0.30.4 |
| **mlx-lm** | 0.30.5 |

## 🚀 性能测试结果

### MLX 性能总结

| 版本 | 加载时间 | 内存占用 | 平均 TPS | TTFT (Prefill) | 状态 |
|------|---------|---------|----------|----------------|------|
| **4-bit** | 21.25秒 | 135 GB | **45.73** | 67ms | ✅ 推荐 |
| **6-bit** | 29.85秒 | 192 GB | **41.83** | 75ms | ✅ 完成 |
| **8-bit** | 28.07秒 | 252 GB | **33.04** | 95ms | ✅ 完成 |
| **bf16** | - | ~460 GB | N/A | N/A | ❌ 未提供 |

### llama.cpp 性能总结

| 版本 | 加载时间 | 内存占用 | 平均 TPS | 状态 |
|------|---------|---------|---------|------|
| **BF16** | - | 426 GB | <0.3 | ❌ 失败（运行6小时后OOM）|
| **Q4_K_M** | - | ~140 GB | 待测 | ⏳ 计划中 |
| **Q8_0** | - | ~250 GB | 待测 | ⏳ 计划中 |

### 关键发现

#### ✅ MLX 4-bit（推荐配置）
- **性能最佳**: 45.73 TPS，仅占用 135GB 内存
- **超低延迟**: 67ms TTFT（prefill速度）
- **稳定生成**: 预热后稳定在 48-49 TPS
- **内存高效**: 为其他工作负载留出 377GB 空间

#### ⚡ 性能洞察
- **Prefill 速度**: 所有量化级别都在 60-95ms（接近GPU水平）
- **内存扩展**: 与量化位数线性相关（4→6→8 bit）
- **速度 vs 质量**: 4-bit 对交互式使用提供最佳平衡
- **8-bit 权衡**: 慢 28%，但质量更好

#### ❌ BF16 不实用
- **llama.cpp BF16**: 运行 6+ 小时后失败，系统 OOM 杀死进程
- **内存压力**: 83% 使用率导致严重性能下降
- **建议**: 任何实际工作负载请使用 8-bit 或更低

> 📊 详细结果: [docs/benchmark-results.md](./docs/benchmark-results.md)

## 📋 测试计划状态

### ✅ Phase 1-2: 已完成 (50%)
- [x] 环境搭建
- [x] MLX 4-bit, 6-bit, 8-bit 性能测试
- [x] llama.cpp BF16 失败分析

### ⏳ Phase 3: llama.cpp 量化测试
- [ ] Q4_K_M (138GB) - 对比 MLX 4-bit
- [ ] Q8_0 (243GB) - 对比 MLX 8-bit

### 🆕 Phase 4: MLX Batching 与并发测试
- [ ] vllm-mlx continuous batching 测试
- [ ] 并发请求扩展性测试（1/2/4/8/16 用户）
- [ ] 聚合吞吐量测量
- [ ] 混合工作负载测试

### 🆕 Phase 5: VRAM/内存优化
- [ ] 系统VRAM限制调整（默认384GB → 448GB/480GB）
- [ ] llama.cpp Metal后端优化（FORCE_PRIVATE、DEVICE_INDEX）
- [ ] 性能影响测量
- [ ] 大模型优化（8-bit、bf16）

> 📖 完整测试计划: [docs/test-plan.md](./docs/test-plan.md)
> 🔧 执行指南: [docs/test-execution-guide.md](./docs/test-execution-guide.md)

## 快速开始

### 1. 环境配置

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -U mlx-lm psutil

# 安装 llama.cpp（可选）
brew install llama.cpp
```

### 2. 运行 MLX 测试

```bash
# 测试 4-bit 版本（推荐先测试）
python scripts/benchmark_mlx.py --model mlx-community/MiniMax-M2.1-4bit

# 测试 8-bit 版本
python scripts/benchmark_mlx.py --model mlx-community/MiniMax-M2.1-8bit

# 测试全精度版本（需要 ~460GB 内存）
python scripts/benchmark_mlx.py --model mlx-community/MiniMax-M2.1-bf16
```

### 3. 运行 llama.cpp 测试

```bash
# 下载 GGUF 模型后运行
python scripts/benchmark_llama.py --model /path/to/MiniMax-M2.1-Q4_K_M.gguf
```

### 4. 运行 Batching 测试

```bash
# 基线测试（单请求）
python scripts/benchmark_batching.py --model mlx-community/MiniMax-M2.1-4bit --concurrent 1

# 并发扩展测试
python scripts/benchmark_batching.py --model mlx-community/MiniMax-M2.1-4bit --concurrent 4
python scripts/benchmark_batching.py --model mlx-community/MiniMax-M2.1-4bit --concurrent 8
python scripts/benchmark_batching.py --model mlx-community/MiniMax-M2.1-4bit --concurrent 16

# 混合工作负载
python scripts/benchmark_batching.py --model mlx-community/MiniMax-M2.1-4bit --concurrent 4 --mixed
```

## 测试矩阵

### MLX 版本（mlx-community）

| 版本 | 估计大小 | 优先级 | 状态 |
|------|---------|---------|------|
| MiniMax-M2.1-4bit | ~120GB | 1（先测试）| ✅ 完成 |
| MiniMax-M2.1-6bit | ~180GB | 2 | ✅ 完成 |
| MiniMax-M2.1-8bit | ~240GB | 3 | ✅ 完成 |
| MiniMax-M2.1-bf16 | ~460GB | 4（全精度）| ❌ 未提供 |

### GGUF 版本（unsloth/MiniMax-M2.1-GGUF）

| 版本 | 文件大小 | 优先级 | 状态 |
|------|---------|---------|------|
| Q4_K_M | 138GB | 1 | ⏳ 计划中 |
| Q6_K | 188GB | 2 | ⏳ 计划中 |
| Q8_0 | 243GB | 3 | ⏳ 计划中 |
| BF16 | 457GB | 4 | ❌ 失败 |

## 测试指标

| 指标 | 说明 |
|------|------|
| **Load Time** | 模型加载到内存的时间 |
| **TTFT** | Time to First Token（首个token时间，即prefill速度）|
| **TPS** | Tokens per Second（生成速度）|
| **Peak Memory** | 推理期间的最大内存使用量 |
| **Aggregate TPS** | 多并发场景下的总吞吐量 |

## 项目结构

```
llm-mac-512/
├── README.md               # 英文版
├── README.zh-CN.md        # 中文版
├── docs/
│   ├── test-plan.md           # 详细测试计划
│   ├── test-execution-guide.md  # 分步执行指南
│   ├── test-design-summary.md   # 测试设计概览
│   ├── benchmark-results.md     # 完整结果
│   └── test-results/          # 单独的测试输出
├── scripts/
│   ├── benchmark_mlx.py       # MLX 测试脚本
│   ├── benchmark_llama.py     # llama.cpp 测试脚本
│   ├── benchmark_batching.py  # Batching/并发测试
│   └── utils.py               # 工具函数
└── prompts/
    └── test_prompts.json      # 测试用例
```

## 命令行选项

### benchmark_mlx.py

```
--model         模型名称（HuggingFace 仓库）
--prompts       测试 prompts JSON 文件路径
--output-dir    结果输出目录
--max-tokens    覆盖所有测试的最大 token 数
--temperature   生成温度（默认: 0.7）
--tests         指定要运行的测试（例如: short medium）
--dry-run       检查设置但不运行测试
```

### benchmark_llama.py

```
--model         GGUF 模型文件路径（必需）
--n-gpu-layers  GPU 层数（-1 表示全部）
--ctx-size      上下文大小（默认: 4096）
--threads       线程数
--llama-cli     llama-cli 可执行文件路径
```

### benchmark_batching.py

```
--model         模型名称（HuggingFace 格式）
--concurrent    并发请求数（1, 2, 4, 8, 16）
--tokens        每个请求的 token 数
--mixed         使用混合工作负载（100/500/2000 tokens）
--temperature   生成温度（默认: 0.7）
--use-mlx-lm    使用 mlx-lm 而不是 vllm-mlx
```

## 使用场景推荐

| 使用场景 | 推荐配置 | 理由 |
|---------|---------|------|
| 单用户，交互式 | MLX 4-bit | 速度最快，内存占用低 |
| 单用户，质量优先 | MLX 6-bit 或 8-bit | 质量更好，速度可接受 |
| 多用户 API (2-4用户) | vllm-mlx 4-bit, batching | 高效批处理 |
| 多用户 API (8+用户) | vllm-mlx 4-bit, batching | 高吞吐量 |
| 兼容性（GGUF格式）| llama.cpp Q4_K_M | 标准格式 |
| 内存受限 | MLX 4-bit | 最低内存使用 |

## 注意事项

- bf16 版本（~460GB）接近 512GB 限制；测试前请关闭其他应用
- 在下载下一个版本前，先测试并记录当前版本结果（节省磁盘空间）
- 模型在首次运行时会自动从 HuggingFace 下载
- vllm-mlx 需要单独安装：`pip install vllm-mlx`

## 参考资料

- [MLX 部署指南](https://github.com/MiniMax-AI/MiniMax-M2.1/blob/main/docs/mlx_deploy_guide.md)
- [Unsloth GGUF 版本](https://huggingface.co/unsloth/MiniMax-M2.1-GGUF)
- [MLX Community 模型](https://huggingface.co/mlx-community)
- [MiniMax 官方新闻](https://www.minimax.io/news/minimax-m21)
- [vllm-mlx GitHub](https://github.com/waybarrios/vllm-mlx)

## 许可证

MIT
