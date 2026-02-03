# Test Design Summary

## Overview

This document summarizes the complete test design for MiniMax M2.1 on Mac (512GB unified memory).

---

## Test Phases

### ✅ Phase 1-2: Completed

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 1** | Environment setup | ✅ Complete |
| **Phase 2** | MLX baseline testing (4/6/8-bit) | ✅ Complete |

**Results:**
- MLX 4-bit: 45.73 TPS, 135GB memory
- MLX 6-bit: 41.83 TPS, 192GB memory
- MLX 8-bit: 33.04 TPS, 252GB memory

---

### ⏳ Phase 3: llama.cpp Quantization Testing

**Objective:** Compare llama.cpp GGUF quantizations with MLX baseline

| Test | Model | Size | Expected TPS | Status |
|------|-------|------|--------------|--------|
| llama.cpp Q4_K_M | MiniMax-M2.1-Q4_K_M.gguf | 138GB | ~30-50 | ⏳ Pending |
| llama.cpp Q8_0 | MiniMax-M2.1-Q8_0.gguf | 243GB | ~25-35 | ⏳ Pending |
| llama.cpp BF16 | MiniMax-M2.1-BF16.gguf | 457GB | N/A | ❌ Failed (OOM) |

**Key Questions:**
1. Is llama.cpp competitive with MLX on Apple Silicon?
2. Which framework offers better TPS per GB of memory?
3. Are there quality differences between frameworks?

**Expected Outcome:**
- Determine framework recommendation for different use cases
- Identify performance vs compatibility trade-offs

---

### 🆕 Phase 4: MLX Batching & Concurrency

**Objective:** Test MLX performance with concurrent requests using vllm-mlx

#### 4.1 Framework Comparison

| Feature | mlx-lm (current) | vllm-mlx (new) |
|---------|------------------|----------------|
| **Architecture** | Single request | Continuous batching |
| **Best for** | One user | Multiple users |
| **Optimization** | Per-request latency | Aggregate throughput |
| **Memory** | Fixed allocation | Dynamic batching |

#### 4.2 Test Matrix

| Test ID | Concurrent Requests | Tokens | Purpose |
|---------|---------------------|--------|---------|
| B1 | 1 | 500 | Baseline comparison |
| B2 | 2 | 500 | Initial scaling |
| B4 | 4 | 500 | Light load scaling |
| B8 | 8 | 500 | Medium load scaling |
| B16 | 16 | 500 | Heavy load scaling |
| BM | 4 | 100/500/2000 | Mixed workload fairness |

#### 4.3 Key Metrics

**Primary:**
- **Aggregate TPS**: Total tokens/sec across all requests
- **Throughput Scaling**: Aggregate TPS @ N / Baseline TPS
- **Latency Percentiles**: P50, P95, P99 response times

**Secondary:**
- Memory efficiency (MB per concurrent request)
- Queue time and scheduling overhead
- Batch utilization

#### 4.4 Expected Scaling

Based on vllm-mlx M4 Max benchmarks:
- 1 request: 450 TPS baseline
- 16 requests: 1900 TPS (4.3x scaling)

Projected for M3 Ultra (512GB):
- 1 request: 45 TPS baseline
- 16 requests: ~200 TPS (4.4x scaling)

**Key Questions:**
1. Does M3 Ultra scale better than M4 Max?
2. What's the optimal concurrency for 512GB?
3. Memory overhead per concurrent request?
4. Is batching worth it for < 4 concurrent users?

---

## Test Scripts

### benchmark_mlx.py ✅
```bash
python scripts/benchmark_mlx.py --model mlx-community/MiniMax-M2.1-4bit
```

**Features:**
- Single-request testing
- Memory monitoring
- 5 standard test cases
- JSON + Markdown output

### benchmark_llama.py ✅
```bash
python scripts/benchmark_llama.py --model ~/models/model.gguf
```

**Features:**
- llama.cpp integration
- Timing parsing from stderr
- GPU layer configuration
- Same 5 test cases as MLX

### benchmark_batching.py 🆕
```bash
python scripts/benchmark_batching.py --model MiniMax-M2.1-4bit --concurrent 4
```

**Features:**
- vllm-mlx integration
- Concurrent request handling
- Latency percentile tracking
- Automatic mlx-lm fallback

---

## Standard Test Cases

All benchmarks use these 5 test cases:

| Test | Description | Tokens | Prompt (CN) |
|------|-------------|--------|-------------|
| short | Quick response | 100 | 请用一句话解释量子计算 |
| medium | Code generation | 500 | 写一个Python快速排序算法 |
| long | Detailed explanation | 2000 | 详细解释深度学习的反向传播算法 |
| reasoning | Logic problem | 500 | [Logic puzzle] |
| instruction | Task following | 400 | [Instruction task] |

---

## Metrics Definitions

### Load Time
- Time to load model into memory (seconds)
- Measured from script start to model ready

### TTFT (Time to First Token)
- Time from request to first generated token (seconds)
- Indicates prompt processing speed

### TPS (Tokens Per Second)
- Generation speed: tokens / generation_time
- Excludes TTFT for pure generation speed

### Peak Memory
- Maximum unified memory usage during generation (GB)
- Measured using psutil

### Aggregate TPS
- Total tokens across all requests / total time
- For batching tests only

### Throughput Scaling
- Aggregate TPS @ N concurrent / Baseline TPS
- Ideal: linear (2x, 4x, 8x, 16x)
- Reality: sublinear due to overhead

---

## Success Criteria

### Phase 3: llama.cpp
- ✅ Models load without OOM
- ✅ All 5 test cases complete successfully
- ✅ TPS > 10 tokens/sec (usable)
- ✅ Results documented in benchmark-results.md

### Phase 4: Batching
- ✅ Baseline matches MLX 4-bit (~45 TPS)
- ✅ Scaling factor > 3x at 8 concurrent
- ✅ Memory usage < 400GB at 16 concurrent
- ✅ P95 latency < 30s at 16 concurrent

---

## Comparison Dimensions

After completing all tests, we will compare:

### 1. Framework Performance
| Dimension | MLX 4-bit | llama.cpp Q4_K_M | Winner |
|-----------|-----------|------------------|--------|
| TPS (single) | 45.73 | TBD | TBD |
| Memory | 135GB | ~140GB | TBD |
| Load time | 21.25s | TBD | TBD |
| TTFT | 67ms | TBD | TBD |

### 2. Quantization Trade-offs
| Level | Framework | TPS | Memory | Quality |
|-------|-----------|-----|--------|---------|
| 4-bit | MLX | 45.73 | 135GB | Good |
| 4-bit | llama.cpp | TBD | ~140GB | TBD |
| 8-bit | MLX | 33.04 | 252GB | Better |
| 8-bit | llama.cpp | TBD | ~250GB | TBD |

### 3. Batching Efficiency
| Concurrent | TPS (single) | TPS (aggregate) | Scaling | Memory |
|------------|--------------|-----------------|---------|--------|
| 1 | ~45 | ~45 | 1.0x | 135GB |
| 2 | ~40 | ~80 | 1.8x | TBD |
| 4 | ~35 | ~140 | 3.1x | TBD |
| 8 | ~30 | ~240 | 5.3x | TBD |
| 16 | ~20 | ~320 | 7.1x | TBD |

---

## Deliverables

### Documentation
- [x] test-plan.md - Detailed test plan
- [x] test-execution-guide.md - Step-by-step instructions
- [x] test-design-summary.md - This document
- [ ] benchmark-results.md - Updated with Phase 3-4 results

### Scripts
- [x] benchmark_mlx.py
- [x] benchmark_llama.py
- [x] benchmark_batching.py
- [x] utils.py

### Results
- [x] MLX 4/6/8-bit results
- [x] llama.cpp BF16 failure analysis
- [ ] llama.cpp Q4_K_M results
- [ ] llama.cpp Q8_0 results
- [ ] Batching 1/2/4/8/16 concurrent results
- [ ] Mixed workload results

### Analysis
- [ ] Framework comparison chart
- [ ] Quantization recommendation
- [ ] Batching scaling analysis
- [ ] Use case recommendations
- [ ] Twitter summary thread

---

## Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1-2 | 2 days | ✅ Complete |
| Phase 3 (llama.cpp) | 1 day | ⏳ Pending |
| Phase 4 (batching) | 0.5 day | ⏳ Pending |
| Analysis & docs | 0.5 day | ⏳ Pending |
| **Total** | **4 days** | 50% complete |

---

## Key Insights (So Far)

### From Phase 2 (MLX Testing)

1. **Memory scales linearly** with quantization bits
2. **4-bit offers best speed** (45.73 TPS) with acceptable quality
3. **8-bit is 28% slower** but uses 87% more memory
4. **Low latency** across all versions (67-95ms TTFT)
5. **BF16 is impractical** on 512GB (83% memory usage, extreme slowdown)

### Questions for Phase 3-4

1. Can llama.cpp match MLX performance on Apple Silicon?
2. Is there a quality difference between frameworks?
3. How well does batching scale on M3 Ultra?
4. What's the optimal configuration for different use cases?
5. Is 512GB enough for practical multi-user scenarios?

---

## Use Case Recommendations (Draft)

Will be finalized after Phase 3-4 completion:

| Use Case | Recommended Config | Rationale |
|----------|-------------------|-----------|
| Single user, interactive | MLX 4-bit | Best speed, low memory |
| Single user, quality | MLX 6-bit or 8-bit | Better quality, acceptable speed |
| Multi-user API (2-4 users) | vllm-mlx 4-bit, batching | Efficient batching |
| Multi-user API (8+ users) | vllm-mlx 4-bit, batching | High throughput |
| Compatibility (GGUF) | llama.cpp Q4_K_M | Standard format |
| Memory constrained | MLX 4-bit | Lowest memory usage |

---

## References

- [test-plan.md](./test-plan.md) - Detailed test plan
- [test-execution-guide.md](./test-execution-guide.md) - Execution instructions  
- [benchmark-results.md](./benchmark-results.md) - Current results
- [vllm-mlx GitHub](https://github.com/waybarrios/vllm-mlx) - Batching framework
- [MiniMax M2.1 MLX Guide](https://github.com/MiniMax-AI/MiniMax-M2.1/blob/main/docs/mlx_deploy_guide.md)
