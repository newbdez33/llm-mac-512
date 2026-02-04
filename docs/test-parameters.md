# 测试参数设计

> 版本: 1.0
> 更新: 2026-02-04

## 参数设计目标

1. **一致性**: MLX 和 llama.cpp 使用相同参数，确保公平对比
2. **可重现**: 固定随机种子，结果可复现
3. **全面性**: 测试不同场景下的性能表现
4. **实用性**: 模拟真实使用场景

---

## 核心参数矩阵

### 1. Context Length (上下文窗口)

#### 模型理论上限

| 模型 | 官方最大值 | 推荐值 | 说明 |
|------|-----------|--------|------|
| **MiniMax M2.1** | 196,608 | 131,072 | 超过可能影响性能 |
| **Qwen3-Coder-Next** | 256,000 | 131,072 | 超大context需要更多内存 |

#### 测试配置方案

##### 方案 A: 固定 Context (推荐 - 公平对比)

**所有测试统一使用**:
```json
{
  "context_length": 131072,
  "reason": "平衡性能和能力，符合实际使用"
}
```

**优点**:
- ✅ 所有测试参数一致
- ✅ 结果可直接对比
- ✅ 足够大（128K tokens）

**MLX 配置**:
```python
# benchmark_mlx.py
max_kv_size = 131072  # MLX 使用这个参数
```

**llama.cpp 配置**:
```bash
# LM Studio settings.json
"defaultContextLength": {
  "type": "custom",
  "value": 131072
}
```

##### 方案 B: 变化 Context (性能影响测试)

测试不同 context 对性能的影响：

| Context | 场景 | 内存影响 | 测试优先级 |
|---------|------|----------|------------|
| 4,096 | 短对话 | 最小 | 参考 |
| 32,768 | 中等文档 | 较小 | 参考 |
| **131,072** | **标准配置** | **中等** | **主要** |
| 196,608 | MiniMax 极限 | 较大 | 可选 |
| 256,000 | Qwen3 极限 | 最大 | 可选 |

**测试矩阵** (如果时间充足):
```
Model: MiniMax M2.1 4-bit
├── Context: 4K   → TPS baseline
├── Context: 32K  → TPS impact
├── Context: 131K → TPS (recommended)
└── Context: 196K → TPS (max)
```

---

### 2. Generation Parameters (生成参数)

#### 标准配置 (所有测试统一)

```json
{
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "repetition_penalty": 1.1,
  "seed": 42
}
```

#### 参数说明

| 参数 | 值 | 说明 | 影响 |
|------|-----|------|------|
| **temperature** | 0.7 | 采样温度 | 平衡创造性和确定性 |
| **top_p** | 0.9 | Nucleus sampling | 控制输出多样性 |
| **top_k** | 40 | Top-K sampling | 限制候选token数 |
| **repetition_penalty** | 1.1 | 重复惩罚 | 减少重复内容 |
| **seed** | 42 | 随机种子 | 确保可重现性 |

#### 不同场景配置 (可选测试)

**场景 1: 确定性输出** (代码生成)
```json
{
  "temperature": 0.2,
  "top_p": 0.95,
  "top_k": 50,
  "repetition_penalty": 1.0
}
```

**场景 2: 创造性输出** (头脑风暴)
```json
{
  "temperature": 1.0,
  "top_p": 0.9,
  "top_k": 100,
  "repetition_penalty": 1.2
}
```

---

### 3. Performance Parameters (性能参数)

#### MLX 特定参数

```python
# benchmark_mlx.py
mlx_config = {
    "max_kv_size": 131072,        # Context length
    "max_tokens": None,           # 由测试用例指定
    "temp": 0.7,
    "top_p": 0.9,
    "repetition_penalty": 1.1,
    "repetition_context_size": 20,
    "seed": 42
}
```

#### llama.cpp 特定参数

```python
# benchmark_lmstudio.py
gguf_config = {
    "model": "model-name",
    "messages": [...],
    "max_tokens": None,           # 由测试用例指定
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "frequency_penalty": 0.1,     # 对应 repetition_penalty
    "seed": 42,
    "stream": False
}
```

**LM Studio Server 配置**:
```json
{
  "context_length": 131072,
  "n_gpu_layers": -1,              // 全部使用 GPU
  "use_mlock": true,               // 锁定内存
  "use_mmap": true,                // 内存映射
  "rope_freq_base": 0,             // 自动
  "rope_freq_scale": 0,            // 自动
  "num_threads": 0                 // 自动
}
```

---

### 4. Test Workload Parameters (测试负载参数)

#### 标准测试用例 (5个)

```json
{
  "test_cases": {
    "short": {
      "name": "短对话",
      "prompt": "请用一句话解释量子计算",
      "max_tokens": 100,
      "context_tokens": ~20
    },
    "medium": {
      "name": "代码生成",
      "prompt": "写一个Python快速排序算法，包含详细注释和测试用例",
      "max_tokens": 500,
      "context_tokens": ~30
    },
    "long": {
      "name": "长文本",
      "prompt": "详细解释深度学习的反向传播算法，包含数学推导和代码实现",
      "max_tokens": 2000,
      "context_tokens": ~40
    },
    "reasoning": {
      "name": "逻辑推理",
      "prompt": "有三个盒子：红盒、蓝盒、绿盒。红盒里装蓝球，蓝盒里装红球，绿盒里装绿球，但所有标签都贴错了。你最少需要从几个盒子中各取一个球才能确定每个盒子的真实内容？请详细说明推理过程。",
      "max_tokens": 500,
      "context_tokens": ~80
    },
    "instruction": {
      "name": "指令跟随",
      "prompt": "作为Python代码审查专家，请审查以下代码并提出改进建议：\n\n```python\ndef calc(a,b,op):\n    if op=='+':\n        return a+b\n    elif op=='-':\n        return a-b\n    elif op=='*':\n        return a*b\n    elif op=='/':\n        return a/b\n```",
      "max_tokens": 400,
      "context_tokens": ~100
    }
  }
}
```

#### Qwen3-Coder-Next 特殊测试用例

```json
{
  "code_agent": {
    "name": "代码代理",
    "prompt": "分析以下项目结构，建议重构方案：\n\nproject/\n├── main.py (500行)\n├── utils.py (300行)\n└── config.py (100行)\n\n所有业务逻辑都在main.py中，没有模块化。",
    "max_tokens": 1000,
    "context_tokens": ~150
  },
  "multi_file": {
    "name": "多文件重构",
    "prompt": "将以下单文件Flask应用重构为模块化结构：[代码省略]",
    "max_tokens": 1500,
    "context_tokens": ~200
  }
}
```

---

## 参数影响测试 (可选)

### Test A: Context Length 影响

**目的**: 测试不同 context length 对性能的影响

**固定参数**: model=MiniMax-4bit, temperature=0.7, max_tokens=500

| Context | 预期 TPS | 预期内存增加 | 测试时间 |
|---------|----------|--------------|----------|
| 4K | 最高 | baseline | 5 min |
| 32K | 高 | +10GB | 5 min |
| 131K | 中等 | +40GB | 5 min |
| 196K | 较低 | +60GB | 5 min |

**脚本**:
```bash
python scripts/benchmark_context_impact.py \
  --model mlx-community/MiniMax-M2.1-4bit \
  --contexts 4096,32768,131072,196608
```

---

### Test B: Temperature 影响

**目的**: 测试不同 temperature 对质量和性能的影响

**固定参数**: model=MiniMax-4bit, context=131K, max_tokens=500

| Temperature | 输出特点 | 预期 TPS | 质量评估 |
|-------------|----------|----------|----------|
| 0.1 | 极度确定 | 最高 | 代码最准确 |
| 0.5 | 较确定 | 高 | 平衡 |
| 0.7 | **标准** | **中等** | **推荐** |
| 1.0 | 多样化 | 较低 | 创造性强 |
| 1.5 | 高度随机 | 低 | 可能离题 |

---

### Test C: Batch Size 影响 (并发测试)

**目的**: 测试并发请求对吞吐量的影响

**固定参数**: model=MiniMax-4bit, context=131K, max_tokens=500

| 并发数 | 预期聚合 TPS | 单请求延迟 | 内存增加 |
|--------|--------------|------------|----------|
| 1 | baseline | 最低 | baseline |
| 2 | 1.8x | +50% | +10% |
| 4 | 3.2x | +100% | +20% |
| 8 | 5.5x | +200% | +40% |

**注**: 需要 vllm-mlx 或 LM Studio 并发模式

---

## 推荐配置方案

### 方案 1: 标准对比测试 (推荐)

**目标**: MLX vs llama.cpp 公平对比

```yaml
Configuration:
  context_length: 131072
  temperature: 0.7
  top_p: 0.9
  top_k: 40
  repetition_penalty: 1.1
  seed: 42

Test Cases: 5个标准用例
Models:
  - MiniMax M2.1: mlx-4bit, mlx-6bit, mlx-8bit vs Q4_K_S, Q6_K, Q8_0
  - Qwen3-Coder: mlx-4bit (if exists), Q4_K_M, Q6_K, Q8_0

Duration: ~10-15 次测试
```

---

### 方案 2: 扩展测试 (如果时间充足)

**目标**: 深入分析参数影响

```yaml
Phase 1: 标准测试 (方案1)
Phase 2: Context 影响测试 (4K, 32K, 131K, 196K)
Phase 3: Temperature 影响测试 (0.1, 0.5, 0.7, 1.0)
Phase 4: 并发测试 (1, 2, 4, 8 并发)

Duration: ~30-40 次测试
```

---

## 配置文件模板

### MLX 配置: configs/mlx_standard.json

```json
{
  "model_config": {
    "max_kv_size": 131072,
    "temp": 0.7,
    "top_p": 0.9,
    "repetition_penalty": 1.1,
    "repetition_context_size": 20,
    "seed": 42
  },
  "test_cases": {
    "short": {"max_tokens": 100},
    "medium": {"max_tokens": 500},
    "long": {"max_tokens": 2000},
    "reasoning": {"max_tokens": 500},
    "instruction": {"max_tokens": 400}
  }
}
```

### GGUF 配置: configs/gguf_standard.json

```json
{
  "model_config": {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "frequency_penalty": 0.1,
    "seed": 42
  },
  "server_config": {
    "context_length": 131072,
    "n_gpu_layers": -1,
    "use_mlock": true,
    "use_mmap": true
  },
  "test_cases": {
    "short": {"max_tokens": 100},
    "medium": {"max_tokens": 500},
    "long": {"max_tokens": 2000},
    "reasoning": {"max_tokens": 500},
    "instruction": {"max_tokens": 400}
  }
}
```

---

## 参数验证清单

在开始测试前确认：

### MLX 侧
- [ ] `max_kv_size` = 131072
- [ ] `temperature` = 0.7
- [ ] `top_p` = 0.9
- [ ] `seed` = 42
- [ ] `repetition_penalty` = 1.1

### llama.cpp 侧
- [ ] LM Studio `context_length` = 131072
- [ ] API `temperature` = 0.7
- [ ] API `top_p` = 0.9
- [ ] API `top_k` = 40
- [ ] API `seed` = 42

### 测试用例
- [ ] 5个标准用例 prompt 一致
- [ ] `max_tokens` 设置正确
- [ ] 测试顺序固定

---

## 参数映射表

| 功能 | MLX 参数 | llama.cpp 参数 | 说明 |
|------|----------|----------------|------|
| Context 窗口 | `max_kv_size` | `context_length` (server) | 需要在服务器配置 |
| 采样温度 | `temp` | `temperature` | 相同 |
| Nucleus 采样 | `top_p` | `top_p` | 相同 |
| Top-K 采样 | - | `top_k` | MLX 无此参数 |
| 重复惩罚 | `repetition_penalty` | `frequency_penalty` | 类似但不完全相同 |
| 随机种子 | `seed` | `seed` | 相同 |
| 最大生成 | `max_tokens` | `max_tokens` | 相同 |

**注意**: `top_k` 和 `repetition_penalty` 实现可能略有不同，需注意对比结果时考虑这点。

---

## 下一步

1. **更新测试脚本**:
   ```bash
   # 将配置写入脚本
   scripts/benchmark_mlx.py → 读取 configs/mlx_standard.json
   scripts/benchmark_lmstudio.py → 读取 configs/gguf_standard.json
   ```

2. **验证配置**:
   ```bash
   # 运行测试前打印配置
   python scripts/verify_config.py
   ```

3. **开始测试**:
   ```bash
   # 使用标准配置
   python scripts/benchmark_mlx.py --config configs/mlx_standard.json
   python scripts/benchmark_lmstudio.py --config configs/gguf_standard.json
   ```

---

## 参考资料

- [MLX LM Documentation](https://github.com/ml-explore/mlx-examples/tree/main/llms)
- [llama.cpp Parameters](https://github.com/ggerganov/llama.cpp/blob/master/examples/main/README.md)
- [LM Studio API Reference](https://lmstudio.ai/docs/api)
- [OpenAI API Compatibility](https://platform.openai.com/docs/api-reference/chat/create)
