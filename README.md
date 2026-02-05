# Large MoE Model Performance Testing on Mac 512GB

> Comprehensive performance benchmarking of MiniMax M2.1 and Qwen3-Coder-Next on Mac (512GB unified memory)
> Testing framework: **MLX** (native) vs **llama.cpp** (GGUF)

[中文版](./README.zh-CN.md) | [English](./README.md)

**🚀 [Quick Start](./QUICKSTART-LMSTUDIO.md)** | **📖 [LM Studio Guide](./docs/lm-studio-setup.md)** | **🔌 [OpenClaw API](./docs/openclaw-setup.md)**

---

## 🏆 Key Finding (Feb 2026)

**MiniMax M2.1 on Mac 512GB: GGUF Q4_K_S is the winner**

| Model | TPS | Size | Recommendation |
|-------|-----|------|----------------|
| **GGUF Q4_K_S** | **37.37** | 138GB | ✅ **Use this for production** |
| MLX 8-bit | 25.98 | ~240GB | Good quality alternative |
| MLX 4-bit | 7.96 | ~120GB | ⚠️ Avoid (unexpectedly slow) |

📊 [Full comparison report](./docs/test-results/reports/final-comparison-20260205.md)

---

## 🎯 Test Overview

### Models Under Test

| Model | Parameters | Active | Context | Released | Specialty |
|-------|-----------|--------|---------|----------|-----------|
| **MiniMax M2.1** | 230B | 10B | 196K | Dec 2025 | Code, Tool Use, Planning |
| **Qwen3-Coder-Next** | 80B | 3B | 256K | Feb 2026 | Code Agents, Local Dev |

### Testing Strategy

**🔬 Fair Comparison via Unified Platform: LM Studio**

| Backend | Format | Loading | Testing | Advantage |
|---------|--------|---------|---------|-----------|
| **MLX Backend** | MLX Native | LM Studio | `benchmark_lmstudio.py` | Apple Silicon Optimized |
| **llama.cpp Backend** | GGUF | LM Studio | `benchmark_lmstudio.py` | Universal, Mature |

**Key**: Both tested through **LM Studio API** for fair comparison

**Why Fair**:
- ✅ Same API overhead
- ✅ Same request/response handling
- ✅ Eliminates external factors
- ✅ Real production scenario (API-based)

**Testing**:
- ✅ MLX backend (in LM Studio) vs llama.cpp backend (in LM Studio)
- ❌ NOT: native mlx-lm vs LM Studio (unfair API overhead)

---

## 📊 Test Results Summary

### MiniMax M2.1 Performance - COMPLETED ✅

**🏆 Winner: GGUF Q4_K_S (llama.cpp) - 37.37 TPS**

#### Completed Tests (February 2026)

| Rank | Model | Framework | Quantization | Avg TPS | Load Time | Size |
|------|-------|-----------|--------------|---------|-----------|------|
| 🥇 | **GGUF Q4_K_S** | llama.cpp | 4-bit | **37.37** | 0.7s | 138GB |
| 🥈 | **MLX 8-bit** | MLX | 8-bit | **25.98** | 1.8s | ~240GB |
| 🥉 | **MLX 4-bit** | MLX | 4-bit | **7.96** | 6.3s | ~120GB |

#### Key Findings

**Performance:**
- ✅ GGUF Q4_K_S is **4.7x faster** than MLX 4-bit
- ✅ GGUF Q4_K_S is **1.4x faster** than MLX 8-bit
- ⚠️ MLX 4-bit paradox: Lower quantization but worst performance (algorithm optimization issue)

**Recommendations:**
- **Production Use**: GGUF Q4_K_S (best speed, smallest size, excellent quality)
- **High Quality**: MLX 8-bit (good balance if you need higher precision)
- **Avoid**: MLX 4-bit (unexpectedly slow, needs investigation)

**Detailed Reports:**
- 📊 [Final Comparison Report](./docs/test-results/reports/final-comparison-20260205.md)
- 📈 [Automated Test Summary](./docs/test-results/reports/automated-test-summary-20260205.md)
- 📁 [Raw JSON Data](./docs/test-results/json/)

#### Archived Baseline Tests (Native mlx-lm)

| Version | Memory | Avg TPS | TTFT | Status |
|---------|--------|---------|------|--------|
| mlx-4bit | 135 GB | 45.73 | 67ms | 📦 Archived |
| mlx-6bit | 198 GB | 39.01 | 75ms | 📦 Archived |
| mlx-8bit | 252 GB | 33.04 | 95ms | 📦 Archived |

*Note: These are older baseline tests using native mlx-lm directly (not via LM Studio). Results not directly comparable due to different testing methods.*

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

### Unified Testing via LM Studio (Recommended for Fair Comparison)

**3 commands to start:**

```bash
# 1. Install LM Studio
brew install --cask lm-studio

# 2. Download models (both MLX and GGUF)
# MLX model
lms download mlx-community/MiniMax-M2.1-4bit

# OR GGUF model
lms download unsloth/MiniMax-M2.1-GGUF:Q4_K_S

# 3. Load model in LM Studio GUI, then start API server
lms server start --port 1234
```

**Run unified benchmark:**
```bash
# Same script for both MLX and GGUF!
python scripts/benchmark_lmstudio.py

# LM Studio automatically uses:
# - MLX backend for .mlx models
# - llama.cpp backend for .gguf models
```

**Why this way?**
- ✅ Fair comparison (same API overhead)
- ✅ Real-world scenario (API-based deployment)
- ✅ Easy to switch between backends

📖 Complete guide: [QUICKSTART-LMSTUDIO.md](./QUICKSTART-LMSTUDIO.md)

---

## 📋 Test Plan Progress

### Phase 1: MiniMax M2.1 ✅ COMPLETED (Feb 2026)

**MLX Testing:**
- [x] mlx-4bit (7.96 TPS - via native mlx-lm)
- [x] mlx-8bit (25.98 TPS - via LM Studio)
- [x] mlx-6bit (39.01 TPS baseline - archived)

**llama.cpp Testing:**
- [x] Q4_K_S (37.37 TPS - via LM Studio) 🏆 **Winner**

**Comparison Analysis:**
- [x] MLX vs llama.cpp performance comparison
- [x] Framework recommendations (GGUF Q4_K_S recommended)
- [x] Final comparison report published

**Key Insights:**
- ✅ GGUF Q4_K_S is the optimal choice for Mac 512GB
- ✅ MLX 4-bit has unexpected performance issues
- ✅ Complete documentation in `docs/test-results/reports/`

### Phase 2: Qwen3-Coder-Next ⏳ PENDING

**MLX Testing:**
- [ ] Find/convert MLX versions
- [ ] Test 4-bit, 6-bit, 8-bit (if available)

**llama.cpp Testing:**
- [ ] Q4_K_M (48.5GB)
- [ ] Q6_K (65.5GB)
- [ ] Q8_0 (84.8GB)

### Phase 3: Cross-Model Analysis 📝 PENDING

- [ ] Model comparison (MiniMax vs Qwen3)
- [ ] Best practices for different use cases
- [ ] Production deployment recommendations

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
├── README.md                           # This file (you are here)
├── docs/
│   ├── test-plan-v2.md                 # Complete test plan
│   ├── test-parameters.md              # Parameter configuration
│   ├── benchmark-results.md            # Historical results
│   ├── lmstudio-openclaw-troubleshooting.md
│   └── test-results/
│       ├── reports/                    # 📊 Markdown analysis reports
│       │   ├── final-comparison-20260205.md       # Final results
│       │   └── automated-test-summary-20260205.md # Test summary
│       ├── json/                       # 📁 Raw benchmark data (13 files)
│       │   └── lmstudio-benchmark-*.json
│       └── archive/                    # 📦 Old baseline tests
├── configs/
│   ├── mlx_standard.json               # MLX test config
│   └── gguf_standard.json              # GGUF test config
├── scripts/
│   ├── benchmark_mlx.py                # MLX native testing
│   ├── benchmark_lmstudio.py           # LM Studio API testing
│   ├── auto_test_v5.sh                 # Automated testing script
│   └── utils.py
└── prompts/
    └── test_prompts.json               # Standard test prompts
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
- [Model Inventory](./docs/model-inventory.md) - All models to test (with HuggingFace links)
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

### ✅ Phase 1 Complete: MiniMax M2.1 Testing (Feb 5, 2026)

**Achievements:**
- ✅ Tested 3 model variants (GGUF Q4_K_S, MLX 8-bit, MLX 4-bit)
- ✅ Comprehensive 5-test benchmark suite on all models
- ✅ Published detailed comparison analysis
- ✅ Clear production recommendation: GGUF Q4_K_S

**Key Results:**
- 🏆 **GGUF Q4_K_S**: 37.37 TPS (recommended for production)
- 🥈 MLX 8-bit: 25.98 TPS (good quality alternative)
- 🥉 MLX 4-bit: 7.96 TPS (surprisingly slow, needs investigation)

**Documentation:**
- Complete results in `docs/test-results/reports/`
- 13 JSON benchmark files in `docs/test-results/json/`
- Automated testing scripts in `scripts/`

### 🔜 Next Phase: Qwen3-Coder-Next

**Planning:**
1. Identify available MLX versions of Qwen3-Coder-Next
2. Download GGUF versions from unsloth
3. Run same 5-test benchmark suite
4. Compare with MiniMax M2.1 results

**Timeline:**
- Target start: After documentation review
- Expected duration: 3-4 days
- Focus: Code generation and agent capabilities

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
