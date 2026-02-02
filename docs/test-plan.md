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
| MiniMax-M2.1-6bit | ~180GB | 2 | ⏳ Pending |
| MiniMax-M2.1-8bit | ~240GB | 3 | ⏳ Pending |
| MiniMax-M2.1-bf16 | ~460GB | 4 | ⏳ Pending |

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

### Phase 3: Model Testing (In Progress)

**Test Order:**
1. ✅ MLX 4bit → Validate workflow
2. ⏳ llama.cpp Q4_K_M → Compare frameworks
3. ⏳ Progressively test larger versions
4. ⏳ Finally test bf16 full version

**Notes:**
- bf16 version ~460GB, close to 512GB limit, need to close other apps
- Record results for each version before downloading the next (save disk space)

### Phase 4: Analysis & Documentation

1. Aggregate all test results
2. Generate comparison charts
3. Write analysis report

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
