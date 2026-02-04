# Mac 512GB 大模型性能测试计划 v2

> 创建日期: 2026-02-04
> 测试平台: LM Studio (统一测试框架)

## 测试目标

在 Mac (512GB 统一内存) 上全面测试两款大型 MoE 模型的性能表现。

## 测试模型

### 1. MiniMax M2.1
- **参数**: 230B 总参数 / 10B 激活参数 (MoE)
- **发布**: 2025年12月23日
- **特点**: 代码生成、工具使用、指令跟随、长期规划
- **Context**: 196,608 tokens

### 2. Qwen3-Coder-Next
- **参数**: 80B 总参数 / 3B 激活参数 (MoE)
- **发布**: 2026年2月3日
- **特点**: 专为编程代理和本地开发设计
- **Context**: 256,000 tokens
- **架构**: 512 experts, 10+1 active per token

## 测试框架

**🎯 统一测试平台: LM Studio (公平对比)**

| 后端框架 | 模型格式 | 加载方式 | 测试脚本 | 说明 |
|---------|----------|----------|----------|------|
| **MLX Backend** | MLX 格式 | LM Studio | benchmark_lmstudio.py | Apple Silicon 原生 |
| **llama.cpp Backend** | GGUF 格式 | LM Studio | benchmark_lmstudio.py | 通用量化格式 |

**关键**: 都通过 LM Studio API 测试，确保公平对比

**测试差异**:
- ✅ 测试的是：MLX backend vs llama.cpp backend (都在 LM Studio 内)
- ❌ 不是：native mlx-lm vs LM Studio (这样不公平，API 有开销)

**为什么这样公平**:
- 相同的 API 接口开销
- 相同的请求/响应处理
- 排除框架外部因素
- 真实生产场景 (都是通过 API 调用)

## 测试矩阵

### MiniMax M2.1

#### Phase 1A: MLX 版本测试 (原生框架)

| 版本 | 大小 | 内存占用 | 优先级 | 状态 | 基准性能 | 测试方法 |
|------|------|----------|--------|------|----------|----------|
| **mlx-4bit** | ~120GB | ~135GB | 🔥 1 | ✅ 已测 | 45.73 TPS | mlx-lm |
| **mlx-6bit** | ~180GB | ~198GB | 🔥 2 | ✅ 已测 | 39.01 TPS | mlx-lm |
| **mlx-8bit** | ~240GB | ~252GB | 🔥 3 | ✅ 已测 | 33.04 TPS | mlx-lm |
| **mlx-bf16** | ~460GB | ~478GB | 4 | ❌ 不可用 | - | 无官方版本 |

**注**: 已有归档数据，可直接使用或重新测试验证

#### Phase 1B: llama.cpp 版本测试 (GGUF via LM Studio)

| 版本 | 大小 | 内存占用 | 优先级 | 状态 | 对比MLX | 测试方法 |
|------|------|----------|--------|------|---------|----------|
| **Q4_K_S** | 130GB | ~135GB | 🔥 1 | 🔄 进行中 | vs mlx-4bit | LM Studio |
| **Q4_K_M** | 138GB | ~143GB | 🔥 2 | ⏳ 待测 | vs mlx-4bit | LM Studio |
| **Q6_K** | 188GB | ~193GB | 🔥 3 | ⏳ 待测 | vs mlx-6bit | LM Studio |
| **Q8_0** | 243GB | ~248GB | 🔥 4 | ⏳ 待测 | vs mlx-8bit | LM Studio |
| **BF16** | 457GB | ~462GB | 5 | ❌ 失败 | vs mlx-bf16 | OOM (已测) |

**对比重点**: 相同量化级别下 MLX vs llama.cpp 的性能差异

### Qwen3-Coder-Next

#### Phase 2A: MLX 版本测试 (待确认)

| 版本 | 大小 | 内存占用 | 优先级 | 状态 | 说明 |
|------|------|----------|--------|------|------|
| **mlx-4bit** | ~45GB | ~50GB | 🔥 1 | 🔍 待查找 | 查找 mlx-community 版本 |
| **mlx-6bit** | ~68GB | ~73GB | 2 | 🔍 待查找 | 如果存在 |
| **mlx-8bit** | ~90GB | ~95GB | 3 | 🔍 待查找 | 如果存在 |

**注**: 需要确认是否有 mlx-community 转换的 Qwen3-Coder-Next，或使用 mlx-lm 手动转换

#### Phase 2B: llama.cpp 版本测试 (GGUF via LM Studio)

| 版本 | 大小 | 内存占用 | 优先级 | 状态 | 对比MLX | 测试方法 |
|------|------|----------|--------|------|---------|----------|
| **Q4_K_M** | 48.5GB | ~53GB | 🔥 1 | ⏳ 待测 | vs mlx-4bit | LM Studio |
| **Q6_K** | 65.5GB | ~70GB | 🔥 2 | ⏳ 待测 | vs mlx-6bit | LM Studio |
| **Q8_0** | 84.8GB | ~90GB | 🔥 3 | ⏳ 待测 | vs mlx-8bit | LM Studio |
| **Q4_0** | 45.3GB | ~50GB | 4 | ⏳ 待测 | 快速版本 | LM Studio |
| **Q2_K** | 29.2GB | ~34GB | 5 | ⏳ 待测 | 最小版本 | LM Studio |
| **BF16** | 159GB | ~164GB | 6 | ⏳ 待测 | 完整精度 | LM Studio |

**对比重点**: 如果有 MLX 版本，对比两个框架性能；否则仅测试 GGUF 版本

## 测试顺序规划

### Week 1: MiniMax M2.1 - 双后端对比 (通过 LM Studio)

**策略**: 交替测试 MLX 和 GGUF 相同量化级别

```
Day 1:
├── MLX 4-bit (via LM Studio) → benchmark_lmstudio.py
└── GGUF Q4_K_S (via LM Studio) → benchmark_lmstudio.py
    → 生成对比表: 4-bit MLX vs Q4_K_S

Day 2:
├── GGUF Q4_K_M (via LM Studio) → benchmark_lmstudio.py
└── 对比分析: Q4_K_S vs Q4_K_M

Day 3:
├── MLX 6-bit (via LM Studio) → benchmark_lmstudio.py
└── GGUF Q6_K (via LM Studio) → benchmark_lmstudio.py
    → 生成对比表: 6-bit MLX vs Q6_K

Day 4:
├── MLX 8-bit (via LM Studio) → benchmark_lmstudio.py
└── GGUF Q8_0 (via LM Studio) → benchmark_lmstudio.py
    → 生成对比表: 8-bit MLX vs Q8_0

Day 5:
└── 综合分析: MiniMax M2.1 完整对比报告
```

**输出**:
- MiniMax M2.1 MLX vs llama.cpp 性能对比表 (3个量化级别)
- 框架推荐建议

---

### Week 2: Qwen3-Coder-Next - 双后端测试

```
Day 1:
└── 查找/下载 MLX 和 GGUF 模型

Day 2-3:
├── MLX 4-bit (via LM Studio) → benchmark_lmstudio.py
├── GGUF Q4_K_M (via LM Studio) → benchmark_lmstudio.py
├── MLX 6-bit (via LM Studio) → benchmark_lmstudio.py
└── GGUF Q6_K (via LM Studio) → benchmark_lmstudio.py

Day 4:
├── MLX 8-bit (via LM Studio) → benchmark_lmstudio.py
├── GGUF Q8_0 (via LM Studio) → benchmark_lmstudio.py
└── (可选) Q4_0, Q2_K 快速测试

Day 5:
└── 综合分析: Qwen3-Coder-Next 完整对比报告
```

**输出**:
- Qwen3-Coder-Next MLX vs llama.cpp 性能对比表
- 与 MiniMax M2.1 的横向对比

---

### Week 3: 综合分析与报告

```
Day 1: 框架对比
└── MLX backend vs llama.cpp backend (在 LM Studio 内)
    - 性能差异分析
    - 内存效率对比
    - 稳定性评估

Day 2: 模型对比
└── MiniMax M2.1 (230B/10B) vs Qwen3-Coder-Next (80B/3B)
    - 代码生成质量
    - TPS per GB 效率
    - Context 利用率

Day 3: 量化级别对比
└── 4-bit vs 6-bit vs 8-bit
    - 质量/性能权衡
    - 内存/速度权衡
    - 最佳选择建议

Day 4-5: 文档整理
├── framework-comparison.md
├── model-comparison.md
├── best-practices.md
└── benchmark-results.md (更新)
```

**最终输出**:
- 完整性能对比报告
- 512GB Mac 部署建议
- 选型决策树

## 测试指标

### 核心指标

| 指标 | 说明 | 测量方法 | 重要性 |
|------|------|----------|--------|
| **TPS** | Tokens per Second | 总tokens/生成时间 | ⭐⭐⭐⭐⭐ |
| **TTFT** | Time to First Token | 首token延迟 | ⭐⭐⭐⭐ |
| **Peak Memory** | 峰值内存占用 | 系统监控 | ⭐⭐⭐⭐⭐ |
| **Load Time** | 模型加载时间 | 初始化计时 | ⭐⭐⭐ |
| **Quality** | 输出质量 | 相同prompt对比 | ⭐⭐⭐⭐ |

### 额外指标

- **Memory Efficiency**: TPS per GB (吞吐/内存比)
- **Context Utilization**: 实际可用context vs 理论值
- **Stability**: 多次运行一致性

## 测试用例

### 标准测试集 (5个场景)

```json
{
  "short": {
    "prompt": "请用一句话解释量子计算",
    "max_tokens": 100,
    "category": "简短问答"
  },
  "medium": {
    "prompt": "写一个Python快速排序算法，包含注释",
    "max_tokens": 500,
    "category": "代码生成"
  },
  "long": {
    "prompt": "详细解释深度学习的反向传播算法，包含数学推导",
    "max_tokens": 2000,
    "category": "长文本生成"
  },
  "reasoning": {
    "prompt": "三个盒子，红盒装蓝球，蓝盒装红球，标签全错。最少取几次确定内容？",
    "max_tokens": 500,
    "category": "逻辑推理"
  },
  "instruction": {
    "prompt": "作为Python专家，审查以下代码并提出改进建议：[示例代码]",
    "max_tokens": 400,
    "category": "指令跟随"
  }
}
```

### Qwen3-Coder-Next 特殊测试

```json
{
  "code_agent": {
    "prompt": "分析这个repo结构，建议重构方案",
    "max_tokens": 1000,
    "category": "代码代理"
  },
  "multi_file": {
    "prompt": "重构项目：将单文件拆分为模块化结构",
    "max_tokens": 1500,
    "category": "多文件操作"
  }
}
```

## 测试流程

### 统一测试流程 (MLX 和 GGUF 都通过 LM Studio)

#### Step 1: 在 LM Studio 中加载模型

**MLX 模型加载**:
```bash
# 方法1: LM Studio GUI
# 搜索: mlx-community/MiniMax-M2.1-4bit
# 点击下载并加载

# 方法2: CLI (如果支持)
lms download mlx-community/MiniMax-M2.1-4bit
lms load mlx-community/MiniMax-M2.1-4bit
```

**GGUF 模型加载**:
```bash
# 方法1: LM Studio GUI
# 搜索: unsloth/MiniMax-M2.1-GGUF
# 选择 Q4_K_S 量化版本下载并加载

# 方法2: CLI
lms download unsloth/MiniMax-M2.1-GGUF:Q4_K_S
lms load unsloth/MiniMax-M2.1-GGUF:Q4_K_S
```

**启动 API Server**:
```bash
# 确保服务器运行在 port 1234
lms server start --port 1234
```

#### Step 2: 确认服务器和后端
```bash
# 检查 API
curl http://localhost:1234/v1/models

# 测试响应
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"model-name","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'

# 在 LM Studio GUI 中确认当前使用的后端
# MLX 模型 → 显示 "MLX" 标签
# GGUF 模型 → 显示 "llama.cpp" 标签
```

#### Step 3: 运行统一测试脚本
```bash
cd /Users/jacky/projects/llm-mac-512

# 无论 MLX 还是 GGUF，都用同一个脚本测试
python scripts/benchmark_lmstudio.py

# 结果自动保存并标注后端类型
# docs/test-results/mlx-minimax-m2-1-4bit-{timestamp}.json
# docs/test-results/gguf-minimax-m2-1-q4ks-{timestamp}.json
```

#### Step 4: 切换模型继续测试
```bash
# 在 LM Studio GUI 中：
# 1. Unload 当前模型
# 2. Load 下一个模型 (MLX 或 GGUF)
# 3. 重复 Step 3
```

**测试顺序建议**:
```
Week 1: MiniMax M2.1
├── MLX 4-bit → benchmark_lmstudio.py
├── GGUF Q4_K_S → benchmark_lmstudio.py (对比)
├── MLX 6-bit → benchmark_lmstudio.py
├── GGUF Q6_K → benchmark_lmstudio.py (对比)
├── MLX 8-bit → benchmark_lmstudio.py
└── GGUF Q8_0 → benchmark_lmstudio.py (对比)
```

### 3. 结果记录

每次测试生成：
- `{model}-{version}-{timestamp}.json` - 原始数据
- `{model}-{version}-{timestamp}.md` - Markdown报告

### 4. 测试后清理

```bash
# 卸载模型 (释放内存)
# 在 LM Studio GUI 中 unload model

# 删除模型 (释放磁盘)
# 仅在确认测试完成后删除
```

## 对比分析维度

### 1. 🔥 框架对比 (MLX vs llama.cpp) - 核心重点

**MiniMax M2.1:**
```
4-bit: mlx-4bit (45.73 TPS) vs Q4_K_S/Q4_K_M (待测)
6-bit: mlx-6bit (39.01 TPS) vs Q6_K (待测)
8-bit: mlx-8bit (33.04 TPS) vs Q8_0 (待测)
```

**Qwen3-Coder-Next:**
```
4-bit: mlx-4bit (待测) vs Q4_K_M (待测)
6-bit: mlx-6bit (待测) vs Q6_K (待测)
8-bit: mlx-8bit (待测) vs Q8_0 (待测)
```

**对比指标:**
- TPS (生成速度)
- TTFT (首token延迟)
- 内存使用效率
- 加载时间
- 稳定性

**预期问题:**
- MLX 在 Apple Silicon 上是否更快？
- llama.cpp 量化是否更节省内存？
- 哪个框架更适合生产环境？

### 2. 模型间对比

```
MiniMax M2.1 (230B/10B) vs Qwen3-Coder-Next (80B/3B):
- 代码生成质量
- 推理能力
- 性能/内存效率 (TPS per GB)
- Context 利用率 (196K vs 256K)
- 启动速度
```

### 3. 量化级别对比

```
4-bit vs 6-bit vs 8-bit:
- 质量下降程度
- 性能提升幅度 (TPS 增加)
- 内存节省比例
- 最佳性价比选择
```

### 4. 框架特性对比

| 特性 | MLX | llama.cpp (GGUF) |
|------|-----|------------------|
| Apple 优化 | ✅ 原生 | ⚠️ Metal 后端 |
| 通用性 | ❌ Mac only | ✅ 跨平台 |
| 生态系统 | mlx-lm | LM Studio, Ollama |
| 易用性 | Python API | CLI + API |
| 社区支持 | 🔥 Apple | 🔥🔥 最广泛 |

## 测试对比总览

### 完整测试矩阵

| 模型 | MLX 4bit | MLX 6bit | MLX 8bit | GGUF Q4 | GGUF Q6 | GGUF Q8 |
|------|----------|----------|----------|---------|---------|---------|
| **MiniMax M2.1** | ✅ 45.73 TPS | ✅ 39.01 TPS | ✅ 33.04 TPS | 🔄 测试中 | ⏳ 待测 | ⏳ 待测 |
| **Qwen3-Coder** | 🔍 待查找 | 🔍 待查找 | 🔍 待查找 | ⏳ 待测 | ⏳ 待测 | ⏳ 待测 |

### 核心对比问题

**框架对比:**
1. 相同量化下，MLX vs llama.cpp 谁更快？
2. 内存使用效率差异多大？
3. 哪个框架更适合生产环境？

**模型对比:**
1. MiniMax M2.1 vs Qwen3-Coder-Next 代码能力？
2. 230B/10B vs 80B/3B 的性能/质量权衡？
3. 256K context 是否比 196K 更实用？

**量化对比:**
1. 4bit vs 6bit vs 8bit 质量下降多少？
2. 性能提升是否值得额外内存？
3. 最佳性价比选择是什么？

## 预期成果

### 测试报告

1. **benchmark-results.md** - 汇总所有测试数据
   - MLX 测试结果汇总
   - GGUF 测试结果汇总
   - 框架对比表格

2. **framework-comparison.md** - MLX vs llama.cpp 深度对比
   - 性能对比 (TPS, TTFT)
   - 内存效率对比
   - 稳定性和易用性

3. **model-comparison.md** - MiniMax vs Qwen3 对比
   - 代码生成质量
   - 推理能力
   - 适用场景

4. **best-practices.md** - 512GB Mac 使用建议
   - 模型选型建议
   - 量化级别推荐
   - 部署最佳实践

## 参考资源

### MiniMax M2.1
- [官方新闻](https://www.minimax.io/news/minimax-m21)
- [MLX部署指南](https://github.com/MiniMax-AI/MiniMax-M2.1/blob/main/docs/mlx_deploy_guide.md)
- [Unsloth GGUF版本](https://huggingface.co/unsloth/MiniMax-M2.1-GGUF)

### Qwen3-Coder-Next
- [官方博客](https://qwen.ai/blog?id=qwen3-coder-next)
- [Hugging Face主页](https://huggingface.co/Qwen/Qwen3-Coder-Next)
- [Unsloth GGUF版本](https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF)
- [Unsloth文档](https://unsloth.ai/docs/models/qwen3-coder-next)

### 工具
- [LM Studio](https://lmstudio.ai/download)
- [OpenClaw文档](https://docs.openclaw.ai/)

## 项目文件结构

```
/Users/jacky/projects/llm-mac-512/
├── README.md
├── docs/
│   ├── test-plan-v2.md (本文档)
│   ├── test-plan.md (v1 - 已归档)
│   ├── benchmark-results.md (汇总结果)
│   ├── model-comparison.md (待创建)
│   ├── best-practices.md (待创建)
│   ├── lmstudio-openclaw-troubleshooting.md
│   └── test-results/
│       ├── archive/ (MLX原始测试)
│       ├── minimax-*.json/md (MiniMax测试)
│       └── qwen3-*.json/md (Qwen3测试)
├── scripts/
│   ├── benchmark_lmstudio.py (统一测试脚本)
│   └── utils.py
└── prompts/
    └── test_prompts.json
```

## 时间估算

| 阶段 | 预计时间 | 说明 |
|------|----------|------|
| MiniMax GGUF测试 | 5天 | 4个版本 + 分析 |
| Qwen3-Coder测试 | 5天 | 5-6个版本 + 分析 |
| 对比分析 | 3天 | 报告编写 |
| **总计** | **2-3周** | 包含文档整理 |

## 注意事项

### 测试前检查

- [ ] LM Studio 已安装并更新到最新版
- [ ] Context Length 设置为 131,072+
- [ ] 关闭其他大型应用释放内存
- [ ] 准备足够磁盘空间 (每个模型下载后测试)

### 测试中监控

- [ ] 内存使用 (Activity Monitor)
- [ ] 温度/风扇 (避免过热)
- [ ] 磁盘空间 (及时清理)

### 测试后清理

- [ ] 保存测试结果
- [ ] 卸载模型释放内存
- [ ] 归档到 Git
- [ ] (可选) 删除模型文件释放磁盘

## 下一步行动

**当前状态**: MiniMax M2.1 Q4_K_S (GGUF) 已加载在 LM Studio

### 🚨 重要更新：公平测试方法

**所有测试都通过 LM Studio**:
- ✅ MLX 模型 → LM Studio (MLX backend) → API → benchmark_lmstudio.py
- ✅ GGUF 模型 → LM Studio (llama.cpp backend) → API → benchmark_lmstudio.py

**为什么**: 确保公平对比，排除 API 开销差异

---

### 立即执行 (Day 1: 4-bit 对比)

#### Test 1: MLX 4-bit (通过 LM Studio)

```bash
# Step 1: 在 LM Studio GUI 中
# - Unload 当前的 GGUF 模型
# - 搜索并下载: mlx-community/MiniMax-M2.1-4bit
# - Load 该模型
# - 确认显示 "MLX" 后端标签

# Step 2: 启动 API server (如果未运行)
lms server start --port 1234

# Step 3: 运行测试
cd /Users/jacky/projects/llm-mac-512
python scripts/benchmark_lmstudio.py

# 结果保存为: docs/test-results/mlx-minimax-m2-1-4bit-{timestamp}.json
```

#### Test 2: GGUF Q4_K_S (通过 LM Studio)

```bash
# Step 1: 在 LM Studio GUI 中
# - Unload MLX 模型
# - Load: unsloth/MiniMax-M2.1-GGUF Q4_K_S (当前已有)
# - 确认显示 "llama.cpp" 后端标签

# Step 2: 运行测试
python scripts/benchmark_lmstudio.py

# 结果保存为: docs/test-results/gguf-minimax-m2-1-q4ks-{timestamp}.json
```

#### Test 3: 生成对比报告

```bash
# 对比两个结果
python scripts/compare_results.py \
  docs/test-results/mlx-minimax-m2-1-4bit-{timestamp}.json \
  docs/test-results/gguf-minimax-m2-1-q4ks-{timestamp}.json

# 输出: MLX 4-bit vs GGUF Q4_K_S 对比表
```

---

### 本周目标 (Week 1)

**Day 1**: 4-bit 对比 ✅
- [ ] MLX 4-bit (via LM Studio)
- [ ] GGUF Q4_K_S (via LM Studio)
- [ ] 对比分析

**Day 2**: Q4_K_M 测试
- [ ] GGUF Q4_K_M (via LM Studio)
- [ ] vs Q4_K_S 对比

**Day 3**: 6-bit 对比
- [ ] MLX 6-bit (via LM Studio)
- [ ] GGUF Q6_K (via LM Studio)
- [ ] 对比分析

**Day 4**: 8-bit 对比
- [ ] MLX 8-bit (via LM Studio)
- [ ] GGUF Q8_0 (via LM Studio)
- [ ] 对比分析

**Day 5**: Week 1 总结
- [ ] 生成 MiniMax M2.1 完整对比报告
- [ ] MLX vs llama.cpp 框架分析

---

### 测试前检查清单

#### LM Studio 配置
- [ ] LM Studio 已安装并更新
- [ ] Server 运行在 port 1234
- [ ] Context Length = 131,072 (在 Settings 中确认)
- [ ] 可以通过 GUI 看到当前后端类型 (MLX/llama.cpp)

#### 测试脚本
- [ ] `scripts/benchmark_lmstudio.py` 存在
- [ ] 脚本使用 configs/gguf_standard.json 配置
- [ ] 脚本记录后端类型到结果文件

#### 系统资源
- [ ] 关闭其他大型应用
- [ ] 至少 150GB+ 可用内存
- [ ] 足够磁盘空间保存结果

---

### 注意事项

1. **后端确认**: 每次加载模型后，在 LM Studio GUI 确认后端类型
   - MLX 模型 → 应显示 "MLX" 标签
   - GGUF 模型 → 应显示 "llama.cpp" 标签

2. **结果命名**: 确保结果文件名区分后端
   - MLX: `mlx-minimax-m2-1-4bit-{timestamp}.json`
   - GGUF: `gguf-minimax-m2-1-q4ks-{timestamp}.json`

3. **API 一致性**: 所有测试通过相同的 API endpoint
   - `http://localhost:1234/v1/chat/completions`

4. **参数一致性**: 确认两个后端使用相同参数
   - Context: 131,072
   - Temperature: 0.7
   - Top-p: 0.9
   - Seed: 42
