# Large MoE Model Performance Testing on Mac 512GB

> Comprehensive performance benchmarking of MiniMax M2.1 and Qwen3-Coder-Next on Mac (512GB unified memory)
> Testing framework: **MLX** (native) vs **llama.cpp** (GGUF)

[中文版](./README.zh-CN.md) | [English](./README.md)

**🚀 [Quick Start](./QUICKSTART-LMSTUDIO.md)** | **📖 [LM Studio Guide](./docs/lm-studio-setup.md)** | **🔌 [OpenClaw API](./docs/openclaw-setup.md)**

---

## 🎯 Test Overview

### Models Under Test

| Model | Parameters | Active | Context | Released | Specialty |
|-------|-----------|--------|---------|----------|-----------|
| **MiniMax M2.1** | 230B | 10B | 196K | Dec 2025 | Code, Tool Use, Planning |
| **Qwen3-Coder-Next** | 80B | 3B | 256K | Feb 2026 | Code Agents, Local Dev |

### Testing Strategy

**🔬 Dual Framework Comparison**

| Framework | Format | Testing Method | Advantage |
|-----------|--------|----------------|-----------|
| **MLX** | MLX Native | `benchmark_mlx.py` | Apple Silicon Optimized |
| **llama.cpp** | GGUF | `benchmark_lmstudio.py` | Universal, Mature Ecosystem |

**Goal**: Compare performance between MLX and llama.cpp at **identical quantization levels**

---

## 📊 Current Results

### MiniMax M2.1 Performance

#### MLX Baseline (Native Framework)

| Version | Load Time | Memory | Avg TPS | TTFT | Status |
|---------|-----------|--------|---------|------|--------|
| **mlx-4bit** | 21.25s | 135 GB | **45.73** | 67ms | ✅ Complete |
| **mlx-6bit** | 29.85s | 198 GB | **39.01** | 75ms | ✅ Complete |
| **mlx-8bit** | 28.07s | 252 GB | **33.04** | 95ms | ✅ Complete |

#### llama.cpp GGUF (via LM Studio)

| Version | Memory | Avg TPS | vs MLX | Status |
|---------|--------|---------|--------|--------|
| **Q4_K_S** | ~135 GB | 🔄 Testing | vs mlx-4bit | 🔄 In Progress |
| **Q4_K_M** | ~143 GB | ⏳ Pending | vs mlx-4bit | ⏳ Pending |
| **Q6_K** | ~193 GB | ⏳ Pending | vs mlx-6bit | ⏳ Pending |
| **Q8_0** | ~248 GB | ⏳ Pending | vs mlx-8bit | ⏳ Pending |
| **BF16** | 462 GB | ❌ Failed | OOM after 6h | ❌ Failed |

### Qwen3-Coder-Next Performance

| Framework | 4-bit | 6-bit | 8-bit | Status |
|-----------|-------|-------|-------|--------|
| **MLX** | 🔍 TBD | 🔍 TBD | 🔍 TBD | Searching for MLX version |
| **GGUF** | ⏳ Pending | ⏳ Pending | ⏳ Pending | Week 2 testing |

---

## 🧪 Test Configuration

### Standard Parameters (All Tests)

```json
{
  "context_length": 131072,
  "temperature": 0.7,
  "top_p": 0.9,
  "repetition_penalty": 1.1,
  "seed": 42
}
```

**Why 131K context?**
- ✅ Balanced performance vs capability
- ✅ Fits both MiniMax (196K max) and Qwen3 (256K max)
- ✅ Real-world usage scenario

### Test Cases (5 Standard)

| Test | Scenario | Max Tokens | Purpose |
|------|----------|------------|---------|
| **short** | Quick Q&A | 100 | Baseline latency |
| **medium** | Code generation | 500 | Standard workload |
| **long** | Documentation | 2000 | Sustained throughput |
| **reasoning** | Logic puzzle | 500 | Reasoning capability |
| **instruction** | Code review | 400 | Instruction following |

📖 Full parameters: [docs/test-parameters.md](./docs/test-parameters.md)

---

## 🚀 Quick Start

### Option 1: LM Studio (Recommended)

**3 commands to start:**

```bash
# 1. Install LM Studio
brew install --cask lm-studio

# 2. Download model (example: MiniMax M2.1 GGUF)
lms download unsloth/MiniMax-M2.1-GGUF:Q4_K_S

# 3. Start API server
lms server start --port 1234
```

**Run benchmark:**
```bash
python scripts/benchmark_lmstudio.py
```

📖 Complete guide: [QUICKSTART-LMSTUDIO.md](./QUICKSTART-LMSTUDIO.md)

---

### Option 2: MLX (Native Framework)

**Setup:**
```bash
# Create environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -U mlx-lm psutil
```

**Run benchmark:**
```bash
# Test MiniMax M2.1 MLX 4-bit
python scripts/benchmark_mlx.py --model mlx-community/MiniMax-M2.1-4bit
```

📖 Complete guide: [QUICKSTART.md](./QUICKSTART.md)

---

## 📋 Test Plan Progress

### Week 1: MiniMax M2.1 ✅ 50% Complete

**MLX Testing:**
- [x] mlx-4bit (45.73 TPS baseline)
- [x] mlx-6bit (39.01 TPS)
- [x] mlx-8bit (33.04 TPS)

**llama.cpp Testing:**
- [🔄] Q4_K_S (in progress)
- [ ] Q4_K_M
- [ ] Q6_K
- [ ] Q8_0

**Comparison Analysis:**
- [ ] MLX vs llama.cpp performance tables
- [ ] Framework recommendations

### Week 2: Qwen3-Coder-Next ⏳ Pending

**MLX Testing:**
- [ ] Find/convert MLX versions
- [ ] Test 4-bit, 6-bit, 8-bit (if available)

**llama.cpp Testing:**
- [ ] Q4_K_M (48.5GB)
- [ ] Q6_K (65.5GB)
- [ ] Q8_0 (84.8GB)

### Week 3: Analysis & Reports 📝 Pending

- [ ] Framework comparison (MLX vs llama.cpp)
- [ ] Model comparison (MiniMax vs Qwen3)
- [ ] Quantization trade-offs (4-bit vs 6-bit vs 8-bit)
- [ ] Best practices for 512GB Mac

📖 Detailed plan: [docs/test-plan-v2.md](./docs/test-plan-v2.md)

---

## 🔬 Key Comparison Questions

### Framework Performance
1. **MLX vs llama.cpp**: Which is faster at same quantization?
2. **Memory efficiency**: TPS per GB comparison
3. **Production readiness**: Stability, ecosystem, ease of use

### Model Capability
1. **MiniMax M2.1 vs Qwen3-Coder-Next**: Code generation quality
2. **230B/10B vs 80B/3B**: Performance/quality trade-off
3. **196K vs 256K context**: Real-world usability

### Quantization Trade-offs
1. **4-bit vs 6-bit vs 8-bit**: Quality degradation
2. **Speed gains**: TPS improvement per quantization level
3. **Best bang for buck**: Optimal choice for 512GB Mac

---

## 📂 Project Structure

```
llm-mac-512/
├── README.md                           # This file
├── docs/
│   ├── test-plan-v2.md                 # Complete test plan
│   ├── test-parameters.md              # Parameter configuration
│   ├── benchmark-results.md            # All test results
│   ├── lmstudio-openclaw-troubleshooting.md
│   └── test-results/
│       ├── archive/                    # Old MLX baseline tests
│       ├── mlx-minimax-*.json/md       # MLX test outputs
│       └── gguf-minimax-*.json/md      # GGUF test outputs
├── configs/
│   ├── mlx_standard.json               # MLX test config
│   └── gguf_standard.json              # GGUF test config
├── scripts/
│   ├── benchmark_mlx.py                # MLX testing script
│   ├── benchmark_lmstudio.py           # GGUF testing script
│   └── utils.py
└── prompts/
    └── test_prompts.json
```

---

## 🖥️ Test Machine

| Spec | Details |
|------|---------|
| **Model** | Mac Studio (Mac15,14) |
| **Chip** | Apple M3 Ultra |
| **CPU Cores** | 32 (24 performance + 8 efficiency) |
| **Unified Memory** | 512 GB |
| **macOS** | Sequoia 15.2 |
| **Python** | 3.12+ |
| **MLX** | 0.30.4+ |
| **mlx-lm** | 0.30.5+ |

---

## 📖 Documentation

### Test Planning
- [Test Plan v2](./docs/test-plan-v2.md) - Complete testing strategy
- [Test Parameters](./docs/test-parameters.md) - Configuration design
- [Benchmark Results](./docs/benchmark-results.md) - All test data

### Setup Guides
- [LM Studio Quick Start](./QUICKSTART-LMSTUDIO.md) - 3-minute setup
- [LM Studio Complete Guide](./docs/lm-studio-setup.md) - Full configuration
- [OpenClaw Integration](./docs/openclaw-setup.md) - API server setup
- [MLX Setup](./QUICKSTART.md) - Native MLX testing

### Troubleshooting
- [LM Studio + OpenClaw Issues](./docs/lmstudio-openclaw-troubleshooting.md)

---

## 🎯 Current Status

**Active**: Testing MiniMax M2.1 Q4_K_S (GGUF) via LM Studio

**Next**:
```bash
# Run current test
cd /Users/jacky/projects/llm-mac-512
python scripts/benchmark_lmstudio.py

# Compare with MLX baseline
# Q4_K_S TPS vs mlx-4bit (45.73 TPS)
```

---

## 📊 Expected Deliverables

1. **benchmark-results.md** - Complete test data
2. **framework-comparison.md** - MLX vs llama.cpp analysis
3. **model-comparison.md** - MiniMax vs Qwen3 comparison
4. **best-practices.md** - 512GB Mac recommendations

---

## 📚 References

### MiniMax M2.1
- [Official Announcement](https://www.minimax.io/news/minimax-m21)
- [MLX Deployment Guide](https://github.com/MiniMax-AI/MiniMax-M2.1/blob/main/docs/mlx_deploy_guide.md)
- [Unsloth GGUF](https://huggingface.co/unsloth/MiniMax-M2.1-GGUF)
- [MLX Community](https://huggingface.co/mlx-community)

### Qwen3-Coder-Next
- [Official Blog](https://qwen.ai/blog?id=qwen3-coder-next)
- [Hugging Face](https://huggingface.co/Qwen/Qwen3-Coder-Next)
- [Unsloth GGUF](https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF)
- [Unsloth Docs](https://unsloth.ai/docs/models/qwen3-coder-next)

### Tools
- [LM Studio](https://lmstudio.ai/)
- [MLX](https://github.com/ml-explore/mlx)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)

---

## 📄 License

MIT
