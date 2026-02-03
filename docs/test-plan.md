# MiniMax M2.1 Mac 512GB Performance Test Plan

> Created: 2026-02-02

## Objective

Comprehensive performance testing of MiniMax M2.1 variants on Mac (512GB unified memory), comparing MLX and llama.cpp frameworks.

## Model Overview

- **MiniMax M2.1**: 230B parameter MoE model (10B active parameters)
- **Release Date**: December 23, 2025
- **Optimized for**: Code generation, tool use, instruction following, and long-horizon planning

## Test Configuration

### Frameworks

| Framework | Purpose | Installation |
|-----------|---------|--------------|
| **MLX** | Apple Silicon native optimization | `pip install -U mlx-lm` |
| **llama.cpp** | Universal GGUF format support | `brew install llama.cpp` |

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

**benchmark_mlx.py features:**
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

### Phase 3: llama.cpp Testing (In Progress)

**Objective:** Compare llama.cpp quantized versions with MLX baseline

**Test Order:**
1. ⏳ Q4_K_M (138GB) → Compare with MLX 4-bit
2. ⏳ Q8_0 (243GB) → Compare with MLX 8-bit
3. ❌ BF16 (457GB) → Already tested, FAILED (see benchmark-results.md)

**Test Configuration:**
```bash
# Q4_K_M test
llama-cli \
  --model MiniMax-M2.1-Q4_K_M.gguf \
  --prompt "..." \
  --n-predict 100 \
  --temp 0.7 \
  --ctx-size 4096

# Q8_0 test
llama-cli \
  --model MiniMax-M2.1-Q8_0.gguf \
  --prompt "..." \
  --n-predict 100 \
  --temp 0.7 \
  --ctx-size 4096
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

### Phase 5: Analysis & Documentation

1. Aggregate all test results
2. Generate comparison charts
3. Write analysis report
4. Update benchmark-results.md with:
   - llama.cpp quantization results
   - MLX batching results
   - Framework recommendations

## Key Files

| File | Purpose |
|------|---------|
| `scripts/benchmark_mlx.py` | MLX performance test script |
| `scripts/benchmark_llama.py` | llama.cpp performance test script |
| `docs/benchmark-results.md` | Aggregated results |
| `docs/test-plan.md` | This plan document |

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
