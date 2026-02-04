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

**🎯 统一测试平台: LM Studio**

| 组件 | 作用 | 说明 |
|------|------|------|
| **LM Studio** | 统一模型加载器 + API 服务器 | 支持 MLX 和 GGUF |
| **MLX Backend** | Apple Silicon 优化 | LM Studio 自动使用 |
| **llama.cpp Backend** | GGUF 格式支持 | LM Studio 内置 |
| **测试脚本** | benchmark_lmstudio.py | OpenAI-compatible API |

## 测试矩阵

### MiniMax M2.1

#### Phase 1: GGUF 版本测试 (优先)

| 版本 | 文件大小 | 内存占用 | 优先级 | 状态 | 说明 |
|------|----------|----------|--------|------|------|
| **Q4_K_S** | 130GB | ~135GB | 🔥 1 | 🔄 进行中 | 当前已加载 |
| **Q4_K_M** | 138GB | ~143GB | 🔥 2 | ⏳ 待测 | 标准4-bit |
| **Q6_K** | 188GB | ~193GB | 3 | ⏳ 待测 | 6-bit精度 |
| **Q8_0** | 243GB | ~248GB | 4 | ⏳ 待测 | 8-bit精度 |
| **BF16** | 457GB | ~462GB | 5 | ❌ 失败 | OOM (已测) |

#### Phase 2: MLX 版本对比 (可选)

| 版本 | 预估大小 | 优先级 | 状态 | 说明 |
|------|----------|--------|------|------|
| MiniMax-M2.1-4bit | ~120GB | 备选 | ✅ 已归档 | 45.73 TPS |
| MiniMax-M2.1-6bit | ~180GB | 备选 | ✅ 已归档 | 39.01 TPS |
| MiniMax-M2.1-8bit | ~240GB | 备选 | ✅ 已归档 | 33.04 TPS |

### Qwen3-Coder-Next

#### Phase 3: GGUF 版本测试

| 版本 | 文件大小 | 内存占用 | 优先级 | 状态 | 说明 |
|------|----------|----------|--------|------|------|
| **Q4_K_M** | 48.5GB | ~53GB | 🔥 1 | ⏳ 待测 | 推荐起点 |
| **Q6_K** | 65.5GB | ~70GB | 🔥 2 | ⏳ 待测 | 平衡选择 |
| **Q8_0** | 84.8GB | ~90GB | 🔥 3 | ⏳ 待测 | 高精度 |
| **Q4_0** | 45.3GB | ~50GB | 4 | ⏳ 待测 | 快速测试 |
| **Q2_K** | 29.2GB | ~34GB | 5 | ⏳ 待测 | 最小版本 |
| **BF16** | 159GB | ~164GB | 6 | ⏳ 待测 | 完整精度 |

**注**: Qwen3-Coder-Next 暂无官方 MLX 量化版本，使用 GGUF 版本测试。

## 测试顺序规划

### Week 1: MiniMax M2.1 完整测试

```
Day 1: Q4_K_S (当前) → 完整benchmark
Day 2: Q4_K_M → 对比Q4_K_S
Day 3: Q6_K → 中等精度测试
Day 4: Q8_0 → 高精度测试
Day 5: 数据分析 + 文档整理
```

### Week 2: Qwen3-Coder-Next 测试

```
Day 1: Q4_K_M → 基准测试
Day 2: Q6_K → 精度对比
Day 3: Q8_0 → 最高可用精度
Day 4: Q4_0, Q2_K → 快速/最小版本
Day 5: BF16 (可选) → 完整精度
```

### Week 3: 对比分析

```
Day 1-2: 模型间性能对比
Day 3-4: 编写综合报告
Day 5: 最佳实践建议
```

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

### 1. 模型加载 (via LM Studio)

```bash
# 方法1: LM Studio GUI
# - 搜索模型
# - 点击下载
# - Load to Chat

# 方法2: LM Studio CLI
lms download unsloth/MiniMax-M2.1-GGUF:Q4_K_M
lms server start --port 1234

# 方法3: 已有模型
# 直接在 GUI 中加载
```

### 2. 运行测试

```bash
# 确认服务器运行
curl http://localhost:1234/v1/models

# 运行完整benchmark
cd /Users/jacky/projects/llm-mac-512
python scripts/benchmark_lmstudio.py

# 结果自动保存到 docs/test-results/
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

### 1. 模型间对比

```
MiniMax M2.1 vs Qwen3-Coder-Next:
- 代码生成质量
- 推理能力
- 性能/内存效率
- Context利用率
```

### 2. 量化版本对比

```
Q4 vs Q6 vs Q8:
- 质量下降程度
- 性能提升幅度
- 内存节省比例
- 最佳性价比选择
```

### 3. 框架对比 (MLX vs llama.cpp)

```
仅针对 MiniMax M2.1:
- 相同量化级别性能差异
- 内存使用差异
- 稳定性对比
```

## 预期成果

### 测试报告

1. **benchmark-results.md** - 汇总所有测试数据
2. **model-comparison.md** - 模型对比分析
3. **best-practices.md** - 512GB Mac 使用建议

### 关键问题答案

1. **哪个模型更适合代码任务？**
   - 代码生成质量
   - 性能表现
   - 内存效率

2. **最佳量化级别是？**
   - 质量/性能平衡点
   - 推荐配置

3. **512GB 内存可以运行什么？**
   - 可运行模型列表
   - 并发能力
   - 资源余量

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

**当前状态**: MiniMax M2.1 Q4_K_S 已加载

**立即执行**:
```bash
# 1. 运行完整测试
python scripts/benchmark_lmstudio.py

# 2. 查看结果
cat docs/test-results/minimax-*.md

# 3. 继续下一个版本 (Q4_K_M)
```

**本周目标**: 完成 MiniMax M2.1 全部 GGUF 测试
