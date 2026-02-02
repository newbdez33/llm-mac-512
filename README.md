# MiniMax M2.1 Benchmark on Mac with 512GB Unified Memory

Comprehensive performance benchmarking of MiniMax M2.1 model variants on Mac (512GB unified memory), comparing MLX and llama.cpp frameworks.

## Model Overview

- **MiniMax M2.1**: 230B parameter MoE model (10B active parameters)
- **Optimized for**: Code generation, tool use, instruction following, and long-horizon planning

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

## Project Structure

```
llm-mac-512/
├── README.md
├── docs/
│   └── test-results/      # Benchmark results
├── scripts/
│   ├── benchmark_mlx.py   # MLX benchmark script
│   ├── benchmark_llama.py # llama.cpp benchmark script
│   └── utils.py           # Utility functions
└── prompts/
    └── test_prompts.json  # Test cases
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
