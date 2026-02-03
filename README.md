# MiniMax M2.1 Benchmark on Mac with 512GB Unified Memory

Comprehensive performance benchmarking of MiniMax M2.1 model variants on Mac (512GB unified memory), comparing MLX and llama.cpp frameworks.

[中文版](./README.zh-CN.md) | [English](./README.md)

**🚀 [快速开始 - 5分钟运行MLX](./QUICKSTART.md)** | **📖 [完整本地运行指南](./docs/mlx-local-setup.md)**

## Model Overview

- **MiniMax M2.1**: 230B parameter MoE model (10B active parameters)
- **Optimized for**: Code generation, tool use, instruction following, and long-horizon planning

## Test Machine Configuration

| Spec | Details |
|------|---------|
| **Model** | Mac Studio (Mac15,14) |
| **Chip** | Apple M3 Ultra |
| **CPU Cores** | 32 (24 performance + 8 efficiency) |
| **Unified Memory** | 512 GB |
| **macOS** | 26.2 (Build 25C56) |
| **Python** | 3.12.12 |
| **MLX** | 0.30.4 |
| **mlx-lm** | 0.30.5 |

## 🚀 Benchmark Results

### MLX Performance Summary

| Version | Load Time | Memory | Avg TPS | TTFT (Prefill) | Status |
|---------|-----------|--------|---------|----------------|--------|
| **4-bit** | 21.25s | 135 GB | **45.73** | 67ms | ✅ Recommended |
| **6-bit** | 29.85s | 192 GB | **41.83** | 75ms | ✅ Complete |
| **8-bit** | 28.07s | 252 GB | **33.04** | 95ms | ✅ Complete |
| **bf16** | - | ~460 GB | N/A | N/A | ❌ Not available |

### llama.cpp Performance Summary

| Version | Load Time | Memory | Avg TPS | Status |
|---------|-----------|--------|---------|--------|
| **BF16** | - | 426 GB | <0.3 | ❌ Failed (OOM after 6h) |
| **Q4_K_M** | - | ~140 GB | TBD | ⏳ Pending |
| **Q8_0** | - | ~250 GB | TBD | ⏳ Pending |

### Key Findings

#### ✅ MLX 4-bit (Recommended)
- **Best performance**: 45.73 TPS with only 135GB memory
- **Ultra-low latency**: 67ms TTFT (prefill speed)
- **Stable generation**: Consistent 48-49 TPS after warm-up
- **Memory efficient**: Leaves 377GB headroom for other workloads

#### ⚡ Performance Insights
- **Prefill speed**: 60-95ms across all quantization levels (near-GPU level)
- **Memory scaling**: Linear with quantization bits (4→6→8 bit)
- **Speed vs Quality**: 4-bit offers best balance for interactive use
- **8-bit trade-off**: 28% slower but better quality

#### ❌ BF16 Not Practical
- **llama.cpp BF16**: Failed after 6+ hours, system OOM killed
- **Memory pressure**: 83% usage causes severe performance degradation
- **Recommendation**: Use 8-bit or lower for any practical workload

> 📊 Detailed results: [docs/benchmark-results.md](./docs/benchmark-results.md)

## Quick Start

### 1. Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -U mlx-lm psutil

# Install llama.cpp (optional)
brew install llama.cpp
```

### 2. Run MLX Benchmarks

```bash
# Test 4-bit version (recommended to start)
python scripts/benchmark_mlx.py --model mlx-community/MiniMax-M2.1-4bit

# Test 8-bit version
python scripts/benchmark_mlx.py --model mlx-community/MiniMax-M2.1-8bit

# Test full precision version (requires ~460GB memory)
python scripts/benchmark_mlx.py --model mlx-community/MiniMax-M2.1-bf16
```

### 3. Run llama.cpp Benchmarks

```bash
# Run after downloading GGUF model
python scripts/benchmark_llama.py --model /path/to/MiniMax-M2.1-Q4_K_M.gguf
```

## Test Matrix

### MLX Versions (mlx-community)

| Version | Est. Size | Priority |
|---------|-----------|----------|
| MiniMax-M2.1-4bit | ~120GB | 1 (Test first) |
| MiniMax-M2.1-6bit | ~180GB | 2 |
| MiniMax-M2.1-8bit | ~240GB | 3 |
| MiniMax-M2.1-bf16 | ~460GB | 4 (Full precision) |

### GGUF Versions (unsloth/MiniMax-M2.1-GGUF)

| Version | File Size | Priority |
|---------|-----------|----------|
| Q4_K_M | 138GB | 1 |
| Q6_K | 188GB | 2 |
| Q8_0 | 243GB | 3 |
| BF16 | 457GB | 4 |

## Metrics

| Metric | Description |
|--------|-------------|
| **Load Time** | Time to load model into memory |
| **TTFT** | Time to First Token |
| **TPS** | Tokens per Second (generation speed) |
| **Peak Memory** | Maximum memory usage during inference |

## 📋 Test Plan Status

### ✅ Phase 1-2: Completed (50%)
- [x] Environment setup
- [x] MLX 4-bit, 6-bit, 8-bit benchmarks
- [x] llama.cpp BF16 failure analysis

### ⏳ Phase 3: llama.cpp Quantization Testing
- [ ] Q4_K_M (138GB) - Compare with MLX 4-bit
- [ ] Q8_0 (243GB) - Compare with MLX 8-bit

### 🆕 Phase 4: MLX Batching & Concurrency
- [ ] vllm-mlx continuous batching tests
- [ ] Concurrent request scaling (1/2/4/8/16 users)
- [ ] Aggregate throughput measurement
- [ ] Mixed workload testing

### 🆕 Phase 5: VRAM/Memory Optimization
- [ ] System VRAM limit adjustment (default 384GB → 448GB/480GB)
- [ ] llama.cpp Metal backend optimization (FORCE_PRIVATE, DEVICE_INDEX)
- [ ] Performance impact measurement
- [ ] Large model optimization (8-bit, bf16)

> 📖 Full test plan: [docs/test-plan.md](./docs/test-plan.md)
> 🔧 Execution guide: [docs/test-execution-guide.md](./docs/test-execution-guide.md)

## Project Structure

```
llm-mac-512/
├── README.md
├── README.zh-CN.md         # Chinese version
├── docs/
│   ├── test-plan.md        # Detailed test plan
│   ├── test-execution-guide.md  # Step-by-step instructions
│   ├── test-design-summary.md   # Test design overview
│   ├── benchmark-results.md     # Complete results
│   └── test-results/       # Individual test outputs
├── scripts/
│   ├── benchmark_mlx.py    # MLX benchmark script
│   ├── benchmark_llama.py  # llama.cpp benchmark script
│   ├── benchmark_batching.py  # Batching/concurrency tests
│   └── utils.py            # Utility functions
└── prompts/
    └── test_prompts.json   # Test cases
```

## CLI Options

### benchmark_mlx.py

```
--model         Model name (HuggingFace repo)
--prompts       Path to test prompts JSON file
--output-dir    Output directory for results
--max-tokens    Override max tokens for all tests
--temperature   Generation temperature (default: 0.7)
--tests         Specific tests to run (e.g., short medium)
--dry-run       Check setup without running benchmarks
```

### benchmark_llama.py

```
--model         Path to GGUF model file (required)
--n-gpu-layers  Number of GPU layers (-1 for all)
--ctx-size      Context size (default: 4096)
--threads       Number of threads
--llama-cli     Path to llama-cli executable
```

## Notes

- The bf16 version (~460GB) is close to the 512GB limit; close other applications before testing
- Test and record results for each version before downloading the next (to save disk space)
- Models are automatically downloaded from HuggingFace on first run

## References

- [MLX Deployment Guide](https://github.com/MiniMax-AI/MiniMax-M2.1/blob/main/docs/mlx_deploy_guide.md)
- [Unsloth GGUF Versions](https://huggingface.co/unsloth/MiniMax-M2.1-GGUF)
- [MLX Community Models](https://huggingface.co/mlx-community)

## License

MIT
