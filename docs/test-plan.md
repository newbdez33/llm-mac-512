# MiniMax M2.1 Mac 512GB Performance Test Plan

> Created: 2026-02-02

## Objective

Comprehensive performance testing of MiniMax M2.1 variants on Mac (512GB unified memory), comparing MLX and llama.cpp frameworks.

## Model Overview

- **MiniMax M2.1**: 230B parameter MoE model (10B active parameters)
- **Release Date**: December 23, 2025
- **Optimized for**: Code generation, tool use, instruction following, and long-horizon planning

## Test Configuration

### Testing Framework

**🎯 统一测试平台: LM Studio**

所有后续测试（MLX 和 llama.cpp）统一通过 LM Studio 加载模型并提供 API 服务器。

| 组件 | 作用 | 说明 |
|------|------|------|
| **LM Studio** | 统一模型加载器 + API 服务器 | GUI + CLI，支持 MLX 和 GGUF |
| **MLX Backend** | Apple Silicon 优化 | LM Studio 自动使用 MLX |
| **llama.cpp Backend** | GGUF 格式支持 | LM Studio 内置 llama.cpp |

**优势：**
- ✅ 统一的测试接口（OpenAI-compatible API）
- ✅ 易于切换不同模型
- ✅ 内置性能监控
- ✅ 配置一致性
- ✅ 适配 OpenClaw

**安装：**
```bash
# LM Studio
brew install --cask lm-studio

# 或下载
open https://lmstudio.ai/download
```

### Test Matrix

#### MLX Versions (mlx-community)

| Version | Est. Size | Priority | Status |
|---------|-----------|----------|--------|
| MiniMax-M2.1-4bit | ~120GB | 1 | ✅ Complete |
| MiniMax-M2.1-6bit | ~180GB | 2 | ✅ Complete |
| MiniMax-M2.1-8bit | ~240GB | 3 | ✅ Complete |
| MiniMax-M2.1-bf16 | ~460GB | 4 | ❌ Not available |

#### GGUF Versions (unsloth/MiniMax-M2.1-GGUF)

| Version | File Size | Priority | Status |
|---------|-----------|----------|--------|
| Q4_K_M | 138GB | 1 | ⏳ Pending |
| Q6_K | 188GB | 2 | ⏳ Pending |
| Q8_0 | 243GB | 3 | ⏳ Pending |
| BF16 | 457GB | 4 | ⏳ Pending |

### Metrics

| Metric | Description | Measurement Method |
|--------|-------------|-------------------|
| **Load Time** | Time to load model into memory | Timer on model initialization |
| **TTFT** | Time to First Token | Time from request to first token |
| **TPS** | Tokens per Second | Total tokens / generation time |
| **Peak Memory** | Maximum memory usage | System memory monitoring |
| **Quality** | Output quality comparison | Same prompt output comparison |

## Implementation Phases

### Phase 1: Environment Setup ✅

1. **Project Structure**
   ```
   /Users/jacky/projects/llm-mac-512/
   ├── README.md
   ├── docs/
   │   ├── test-plan.md
   │   ├── benchmark-results.md
   │   └── test-results/
   ├── scripts/
   │   ├── benchmark_mlx.py
   │   ├── benchmark_llama.py
   │   └── utils.py
   └── prompts/
       └── test_prompts.json
   ```

2. **Dependencies**
   - Python 3.12 virtual environment
   - mlx-lm 0.30.5
   - psutil for memory monitoring
   - llama.cpp via Homebrew

### Phase 2: Benchmark Scripts ✅

**benchmark_lmstudio.py features:**
- Unified testing interface for both MLX and GGUF models via LM Studio API
- Model loading with timing
- Memory monitoring (using psutil)
- Token generation timing
- Results output as JSON/Markdown

**Test cases:**
```json
{
  "short": {"prompt": "请用一句话解释量子计算", "max_tokens": 100},
  "medium": {"prompt": "写一个Python快速排序算法", "max_tokens": 500},
  "long": {"prompt": "详细解释深度学习的反向传播算法", "max_tokens": 2000},
  "reasoning": {"prompt": "逻辑推理题", "max_tokens": 500},
  "instruction": {"prompt": "指令跟随任务", "max_tokens": 400}
}
```

### Phase 3: llama.cpp (GGUF) Testing via LM Studio

**Objective:** Compare llama.cpp quantized versions with MLX baseline

**🎯 测试方法: 通过 LM Studio 统一测试**

所有 GGUF 模型通过 LM Studio 加载和测试，使用相同的 API 接口。

**Test Order:**
1. ⏳ Q4_K_S (130GB) → 当前已加载，待完整测试
2. ⏳ Q4_K_M (138GB) → Compare with MLX 4-bit
3. ⏳ Q8_0 (243GB) → Compare with MLX 8-bit
4. ❌ BF16 (457GB) → Already tested, FAILED (see benchmark-results.md)

**Test Configuration via LM Studio:**

```bash
# 1. 通过 LM Studio 下载模型
lms download unsloth/MiniMax-M2.1-GGUF:Q4_K_M

# 2. 启动 API 服务器
lms server start unsloth/MiniMax-M2.1-GGUF --port 1234

# 3. 运行统一测试脚本
python scripts/benchmark_lmstudio.py

# 或直接测试 API
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "minimax-m2.1",
    "messages": [{"role": "user", "content": "测试提示"}],
    "max_tokens": 100
  }'
```

**统一测试脚本:**
```bash
# 所有模型使用相同的测试脚本
python scripts/benchmark_lmstudio.py
```

**Metrics to Track:**
- Load time (model loading into memory)
- TPS (tokens per second)
- TTFT (time to first token)
- Peak memory usage
- Memory efficiency (TPS per GB)

**Comparison Points:**
| Quantization | MLX Version | llama.cpp Version | Expected Comparison |
|--------------|-------------|-------------------|---------------------|
| 4-bit | MiniMax-M2.1-4bit (135GB) | Q4_K_M (138GB) | Similar size, speed comparison |
| 8-bit | MiniMax-M2.1-8bit (252GB) | Q8_0 (243GB) | Similar size, speed comparison |

**Success Criteria:**
- llama.cpp models complete all 5 test cases
- Results comparable or better than MLX in some metrics
- Memory usage stays within 512GB limit
- No OOM kills (unlike BF16)

**Expected Outcomes:**
- Determine if llama.cpp quantization is competitive with MLX
- Identify which framework is better for different use cases
- Document trade-offs: performance vs compatibility

---

### Phase 4: MLX Batching & Concurrency Testing 🆕

**Objective:** Test MLX batching performance for multi-user scenarios

#### 4.1 vllm-mlx Setup

**Installation:**
```bash
pip install vllm-mlx
```

**Framework Comparison:**
| Feature | mlx-lm (current) | vllm-mlx (new) |
|---------|------------------|----------------|
| Mode | Single request | Continuous batching |
| Best for | One user | Multiple concurrent users |
| Throughput | Optimized per-request | Optimized aggregate |
| Scheduling | None | PagedAttention |

#### 4.2 Test Scenarios

**Scenario 1: Single Request Baseline**
- Purpose: Compare vllm-mlx single mode with mlx-lm baseline
- Config: 1 concurrent request
- Expected: Similar or slightly lower TPS (overhead from batching framework)

**Scenario 2: Concurrent Load**
- Purpose: Measure throughput scaling with concurrent requests
- Config: 2, 4, 8, 16 concurrent requests
- Expected: Aggregate throughput increases, per-request latency increases

**Scenario 3: Mixed Workload**
- Purpose: Simulate real-world usage with varying request lengths
- Config: Mix of short (100), medium (500), long (2000) token requests
- Expected: Batching handles mixed lengths efficiently

#### 4.3 Test Matrix

| Test | Concurrent Requests | Tokens per Request | Quantization | Metric |
|------|---------------------|-------------------|--------------|--------|
| baseline | 1 | 100, 500, 2000 | 4-bit | TPS, latency |
| scale-2 | 2 | 500 | 4-bit | Aggregate TPS |
| scale-4 | 4 | 500 | 4-bit | Aggregate TPS |
| scale-8 | 8 | 500 | 4-bit | Aggregate TPS |
| scale-16 | 16 | 500 | 4-bit | Aggregate TPS |
| mixed | 4 | 100, 500, 2000 (mixed) | 4-bit | Fairness |

#### 4.4 Metrics

**Primary Metrics:**
- **Aggregate TPS**: Total tokens/sec across all requests
- **Per-request TPS**: Average TPS per request
- **Throughput Scaling**: Aggregate TPS at N requests / Baseline TPS
- **P50/P95/P99 Latency**: Response time percentiles

**Secondary Metrics:**
- **Memory usage**: Peak memory at different concurrency levels
- **Queue time**: Time waiting for batch scheduling
- **Batch efficiency**: Actual batch size vs theoretical max

#### 4.5 Implementation

**Script: `scripts/benchmark_batching.py`**
```python
# Test vllm-mlx batching performance
# Usage:
#   python benchmark_batching.py --model MiniMax-M2.1-4bit --concurrent 4
#   python benchmark_batching.py --model MiniMax-M2.1-4bit --concurrent 16
```

**Key Features:**
- Async request handling (concurrent requests)
- Latency tracking per request
- Aggregate throughput calculation
- Memory monitoring during concurrent load
- Results comparison with baseline

#### 4.6 Expected Results

Based on vllm-mlx benchmarks (M4 Max):
- **Single request**: ~450 TPS (baseline)
- **16 concurrent**: ~1900 TPS aggregate (4.3x scaling)

On M3 Ultra (512GB):
- MLX 4-bit baseline: 45.73 TPS
- Expected 16-concurrent: ~200 TPS aggregate (4.4x scaling)
- Memory headroom: 512GB - 135GB = 377GB available for batching

**Questions to Answer:**
1. Does M3 Ultra scale better than M4 Max due to more memory/cores?
2. What's the optimal concurrent request count for 512GB?
3. Is batching worth it for single-user scenarios?
4. Memory per concurrent request overhead?

---

### Phase 5: Memory/VRAM Optimization Testing 🆕

**Objective:** Test impact of macOS VRAM limits and Metal backend configurations on performance

#### 5.1 Background

**macOS Unified Memory Constraints:**
- By default, macOS only allows GPU to use ~75% of unified memory
- On 512GB system: ~384GB available for GPU, 128GB reserved
- Can be adjusted via `sysctl iogpu.wired_limit_mb`

**llama.cpp Metal Backend Options:**
- `GGML_METAL_FORCE_PRIVATE=1` - Force private VRAM mode
- `GGML_METAL_DEVICE_INDEX` - Select specific GPU die (M3 Ultra has 2)
- `GGML_METAL_N_CB` - Tune command buffer count

#### 5.2 Test Matrix

**Test 1: System VRAM Limit Impact (MLX)**

| Config | VRAM Limit | Expected GPU Memory | Test Model |
|--------|------------|---------------------|------------|
| Default | ~384GB | 384GB | MLX 4-bit |
| Optimized | 448GB | 448GB | MLX 4-bit |
| Aggressive | 480GB | 480GB | MLX 4-bit |

**Commands:**
```bash
# Baseline (default)
sysctl iogpu.wired_limit_mb  # Check current
# Load MLX 4-bit model via LM Studio
python scripts/benchmark_lmstudio.py

# Optimized (448GB for GPU)
sudo sysctl iogpu.wired_limit_mb=458752
# Load MLX 4-bit model via LM Studio
python scripts/benchmark_lmstudio.py

# Aggressive (480GB for GPU)
sudo sysctl iogpu.wired_limit_mb=491520
# Load MLX 4-bit model via LM Studio
python scripts/benchmark_lmstudio.py
```

**Test 2: VRAM Impact on Large Models**

Test same VRAM configs with 8-bit model (252GB baseline):
```bash
# Default vs Optimized VRAM limit
# Load MLX 8-bit model via LM Studio, then test
python scripts/benchmark_lmstudio.py
```

**Test 3: llama.cpp Metal Backend Optimization**

| Config | FORCE_PRIVATE | DEVICE_INDEX | N_CB | Purpose |
|--------|---------------|--------------|------|---------|
| Baseline | 0 (default) | - | - | Reference |
| Private VRAM | 1 | - | 2 | Force private memory |
| Die 0 | - | 0 | 2 | Test first die |
| Die 1 | - | 1 | 2 | Test second die |
| CB tuning | 1 | - | 1 | Reduce buffers |
| CB tuning | 1 | - | 3 | Increase buffers |
| Combined | 1 | 0 | 2 | All optimizations |

**Commands:**
```bash
# Note: All tests run via LM Studio API
# LM Studio internally uses llama.cpp for GGUF models
# Set environment variables before starting LM Studio server

# Baseline
# Start LM Studio normally, load GGUF model
python scripts/benchmark_lmstudio.py

# Force private VRAM
export GGML_METAL_FORCE_PRIVATE=1
# Restart LM Studio server with this env var
python scripts/benchmark_lmstudio.py
unset GGML_METAL_FORCE_PRIVATE

# Test different dies
export GGML_METAL_DEVICE_INDEX=0
# Restart LM Studio server
python scripts/benchmark_lmstudio.py

export GGML_METAL_DEVICE_INDEX=1
# Restart LM Studio server
python scripts/benchmark_lmstudio.py
unset GGML_METAL_DEVICE_INDEX

# Test command buffer count
export GGML_METAL_FORCE_PRIVATE=1
export GGML_METAL_N_CB=1
# Restart LM Studio server
python scripts/benchmark_lmstudio.py

export GGML_METAL_N_CB=3
# Restart LM Studio server
python scripts/benchmark_lmstudio.py
```

**Test 4: Combined Optimization**

```bash
# System-level + Metal optimizations
sudo sysctl iogpu.wired_limit_mb=458752
export GGML_METAL_FORCE_PRIVATE=1
export GGML_METAL_DEVICE_INDEX=0
export GGML_METAL_N_CB=2

# Restart LM Studio server with these env vars
# Load Q4_K_M via LM Studio
python scripts/benchmark_lmstudio.py

# Load Q8_0 via LM Studio
python scripts/benchmark_lmstudio.py
```

#### 5.3 Metrics to Track

**Primary:**
- TPS change (baseline vs optimized)
- Memory usage (actual GPU memory allocated)
- TTFT impact

**Secondary:**
- Stability (any crashes or OOM)
- Temperature/power consumption
- Sustained performance over multiple runs

#### 5.4 Expected Results

**System VRAM Limit:**
- Small models (4-bit, 135GB): 0-5% TPS improvement
- Large models (8-bit, 252GB): 5-10% TPS improvement
- May enable bf16 to run without OOM

**Metal Backend:**
- FORCE_PRIVATE: 0-10% improvement, but higher memory pressure
- DEVICE_INDEX: Minimal difference (load balancing)
- N_CB: Varies, 2 is generally optimal

#### 5.5 Script: benchmark_vram.sh

Automated testing script (to be created):
```bash
#!/bin/bash
# Test different VRAM configurations automatically
# Loads models via LM Studio and runs benchmark_lmstudio.py
./scripts/benchmark_vram.sh
```

#### 5.6 Safety Notes

- ⚠️ VRAM settings revert on restart (safe to test)
- ⚠️ Setting VRAM too high (>480GB) may cause system instability
- ⚠️ Monitor memory pressure during tests
- ✅ Test with smaller models first before bf16

---

### Phase 6: Analysis & Documentation

1. Aggregate all test results
2. Generate comparison charts
3. Write analysis report
4. Update benchmark-results.md with:
   - llama.cpp quantization results
   - MLX batching results
   - Memory optimization results
   - Framework recommendations

## Key Files

| File | Purpose |
|------|---------|
| `scripts/benchmark_lmstudio.py` | Unified performance test script (via LM Studio API) |
| `docs/benchmark-results.md` | Aggregated results |
| `docs/test-plan.md` | This plan document |
| `docs/lmstudio-openclaw-troubleshooting.md` | LM Studio + OpenClaw setup guide |

## Validation Methods

1. **Functional**: Confirm model loads and generates correctly
2. **Performance**: Run complete benchmark, verify data recording
3. **Quality**: Compare outputs across versions
4. **Documentation**: Confirm all results are recorded

## Expected Outcomes

1. Performance comparison data across quantization versions
2. MLX vs llama.cpp framework comparison
3. Best practices for running MiniMax M2.1 on 512GB Mac
4. Complete test documentation and reproducible scripts

## References

- [MLX Deployment Guide](https://github.com/MiniMax-AI/MiniMax-M2.1/blob/main/docs/mlx_deploy_guide.md)
- [Unsloth GGUF Versions](https://huggingface.co/unsloth/MiniMax-M2.1-GGUF)
- [MLX Community Models](https://huggingface.co/mlx-community)
- [MiniMax Official News](https://www.minimax.io/news/minimax-m21)
