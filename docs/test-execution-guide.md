# Test Execution Guide

> Quick reference for running all MiniMax M2.1 benchmarks

## Overview

This guide provides step-by-step instructions for running all planned tests on Mac (512GB).

---

## Prerequisites

### 1. Environment Setup

```bash
# Navigate to project
cd /Users/jacky/projects/llm-mac-512

# Activate virtual environment
source venv/bin/activate

# Verify installations
python --version  # Should be 3.12+
pip list | grep mlx  # Check mlx-lm version
llama-cli --version  # Check llama.cpp
```

### 2. Disk Space

Check available space before downloading models:

```bash
df -h ~  # Check home directory space
```

**Space requirements:**
- Q4_K_M GGUF: 138 GB
- Q8_0 GGUF: 243 GB
- Total for llama.cpp tests: ~381 GB

---

## Phase 3: llama.cpp Quantization Tests

### Test 1: Q4_K_M (138GB)

**Download model:**
```bash
# Using huggingface-cli
huggingface-cli download unsloth/MiniMax-M2.1-GGUF \
  MiniMax-M2.1-Q4_K_M.gguf \
  --local-dir ~/models/minimax-m2.1-gguf
```

**Run benchmark:**
```bash
python scripts/benchmark_llama.py \
  --model ~/models/minimax-m2.1-gguf/MiniMax-M2.1-Q4_K_M.gguf \
  --n-gpu-layers -1 \
  --ctx-size 4096
```

**Expected results:**
- Load time: ~15-25 seconds
- Memory usage: ~140-150 GB
- TPS: 30-50 tokens/sec (compare with MLX 4-bit: 45.73 TPS)

---

### Test 2: Q8_0 (243GB)

**Download model:**
```bash
huggingface-cli download unsloth/MiniMax-M2.1-GGUF \
  MiniMax-M2.1-Q8_0.gguf \
  --local-dir ~/models/minimax-m2.1-gguf
```

**Run benchmark:**
```bash
python scripts/benchmark_llama.py \
  --model ~/models/minimax-m2.1-gguf/MiniMax-M2.1-Q8_0.gguf \
  --n-gpu-layers -1 \
  --ctx-size 4096
```

**Expected results:**
- Load time: ~20-30 seconds
- Memory usage: ~250-260 GB
- TPS: 25-35 tokens/sec (compare with MLX 8-bit: 33.04 TPS)

---

### Cleanup Between Tests

To save disk space, delete models after testing:

```bash
# After Q4_K_M test
rm ~/models/minimax-m2.1-gguf/MiniMax-M2.1-Q4_K_M.gguf

# After Q8_0 test
rm ~/models/minimax-m2.1-gguf/MiniMax-M2.1-Q8_0.gguf
```

---

## Phase 4: MLX Batching Tests

### Setup vllm-mlx

```bash
# Install vllm-mlx (if not already installed)
pip install vllm-mlx

# Verify installation
python -c "import vllm_mlx; print('vllm-mlx installed')"
```

**Note:** If vllm-mlx is not available, the script will fall back to mlx-lm with simulated concurrency.

---

### Test 3: Baseline (Single Request)

**Purpose:** Establish baseline for comparison with concurrent tests

```bash
python scripts/benchmark_batching.py \
  --model mlx-community/MiniMax-M2.1-4bit \
  --concurrent 1 \
  --tokens 500
```

**Expected results:**
- TPS: ~45-50 tokens/sec (similar to MLX 4-bit baseline)

---

### Test 4: 2 Concurrent Requests

```bash
python scripts/benchmark_batching.py \
  --model mlx-community/MiniMax-M2.1-4bit \
  --concurrent 2 \
  --tokens 500
```

**Expected results:**
- Aggregate TPS: ~80-90 tokens/sec (1.8x scaling)
- Per-request TPS: ~40-45 tokens/sec

---

### Test 5: 4 Concurrent Requests

```bash
python scripts/benchmark_batching.py \
  --model mlx-community/MiniMax-M2.1-4bit \
  --concurrent 4 \
  --tokens 500
```

**Expected results:**
- Aggregate TPS: ~140-160 tokens/sec (3.0-3.5x scaling)
- Per-request TPS: ~35-40 tokens/sec

---

### Test 6: 8 Concurrent Requests

```bash
python scripts/benchmark_batching.py \
  --model mlx-community/MiniMax-M2.1-4bit \
  --concurrent 8 \
  --tokens 500
```

**Expected results:**
- Aggregate TPS: ~200-250 tokens/sec (4.0-5.0x scaling)
- Per-request TPS: ~25-30 tokens/sec
- Memory usage: ~150-180 GB

---

### Test 7: 16 Concurrent Requests

```bash
python scripts/benchmark_batching.py \
  --model mlx-community/MiniMax-M2.1-4bit \
  --concurrent 16 \
  --tokens 500
```

**Expected results:**
- Aggregate TPS: ~250-300 tokens/sec (5.0-6.5x scaling)
- Per-request TPS: ~15-20 tokens/sec
- Memory usage: ~180-220 GB

**Note:** This test will determine the practical concurrency limit on 512GB.

---

### Test 8: Mixed Workload

```bash
python scripts/benchmark_batching.py \
  --model mlx-community/MiniMax-M2.1-4bit \
  --concurrent 4 \
  --mixed
```

**Purpose:** Test with varying request lengths (100, 500, 2000 tokens)

**Expected results:**
- Tests batching fairness and scheduling
- Short requests should complete faster than long ones

---

## Monitoring During Tests

### Memory Monitoring

```bash
# In a separate terminal, monitor memory
watch -n 1 'ps aux | grep -E "(python|llama)" | grep -v grep'
```

Or use Activity Monitor:
```bash
open -a "Activity Monitor"
```

### Temperature Monitoring

```bash
# Check system temperature (requires sudo)
sudo powermetrics --samplers smc -n 1 | grep -i temp
```

---

## Results Analysis

### After Each Test

Results are automatically saved to:
- JSON: `docs/test-results/<framework>-<model>-<timestamp>.json`
- Markdown: `docs/test-results/<framework>-<model>-<timestamp>.md`

### Aggregate Results

After completing all tests, update:
```bash
# Edit benchmark-results.md with new results
vim docs/benchmark-results.md
```

---

## Troubleshooting

### Issue: Model Download Fails

```bash
# Try with --resume-download
huggingface-cli download unsloth/MiniMax-M2.1-GGUF \
  <model-file> \
  --local-dir ~/models/minimax-m2.1-gguf \
  --resume-download
```

### Issue: Out of Memory

If tests fail with OOM:
1. Close other applications
2. Restart the Mac to clear memory
3. Try with smaller batch size (for batching tests)
4. Monitor memory with Activity Monitor

### Issue: llama.cpp Runs Too Slow

If TPS < 1:
- Check if model is fully loaded (wait for "system info" message)
- Verify Metal GPU acceleration: `--n-gpu-layers -1`
- Check Activity Monitor for swapping

### Issue: vllm-mlx Not Available

The batching script will automatically fall back to mlx-lm:
```bash
python scripts/benchmark_batching.py --use-mlx-lm ...
```

---

## Test Checklist

Use this checklist to track progress:

**Phase 3: llama.cpp**
- [ ] Q4_K_M downloaded (138GB)
- [ ] Q4_K_M benchmark completed
- [ ] Q4_K_M model deleted (save space)
- [ ] Q8_0 downloaded (243GB)
- [ ] Q8_0 benchmark completed
- [ ] Q8_0 model deleted (save space)

**Phase 4: Batching**
- [ ] vllm-mlx installed (or using mlx-lm fallback)
- [ ] Baseline (1 concurrent) completed
- [ ] 2 concurrent completed
- [ ] 4 concurrent completed
- [ ] 8 concurrent completed
- [ ] 16 concurrent completed
- [ ] Mixed workload completed

**Documentation**
- [ ] Results added to benchmark-results.md
- [ ] Summary analysis written
- [ ] Comparison charts created (optional)
- [ ] Twitter summary prepared

---

## Quick Commands Summary

```bash
# llama.cpp Q4_K_M
python scripts/benchmark_llama.py --model ~/models/minimax-m2.1-gguf/MiniMax-M2.1-Q4_K_M.gguf

# llama.cpp Q8_0
python scripts/benchmark_llama.py --model ~/models/minimax-m2.1-gguf/MiniMax-M2.1-Q8_0.gguf

# Batching: baseline
python scripts/benchmark_batching.py --model mlx-community/MiniMax-M2.1-4bit --concurrent 1

# Batching: scaling tests
for c in 2 4 8 16; do
  python scripts/benchmark_batching.py --model mlx-community/MiniMax-M2.1-4bit --concurrent $c
done

# Batching: mixed workload
python scripts/benchmark_batching.py --model mlx-community/MiniMax-M2.1-4bit --concurrent 4 --mixed
```

---

## Estimated Time

| Test | Duration | Notes |
|------|----------|-------|
| Q4_K_M download | 20-40 min | Depends on network |
| Q4_K_M benchmark | 10-15 min | 5 test cases |
| Q8_0 download | 30-60 min | Larger file |
| Q8_0 benchmark | 15-20 min | Slower TPS |
| Batching baseline | 5 min | Already have model |
| Batching 2-16 concurrent | 20-30 min | 4 tests |
| Mixed workload | 5-10 min | |
| **Total** | **2-3 hours** | Excludes download time |

---

## Phase 5: VRAM/Memory Optimization Tests

### Background

macOS limits GPU memory usage to ~75% of unified memory by default:
- 512GB system → ~384GB for GPU, 128GB reserved
- Can be increased via `sysctl iogpu.wired_limit_mb`
- Settings reset on restart (safe to test)

### Test 9: Check Current VRAM Limit

```bash
# Check current setting
sysctl iogpu.wired_limit_mb

# Expected: ~393216 (384GB) or similar
```

---

### Test 10: MLX with Optimized VRAM (448GB)

**Purpose:** Test if higher VRAM limit improves MLX performance

```bash
# Check current baseline (for comparison)
# Should already have results from Phase 2

# Set VRAM to 448GB
sudo sysctl iogpu.wired_limit_mb=458752

# Verify
sysctl iogpu.wired_limit_mb

# Re-run 4-bit test
python scripts/benchmark_mlx.py --model mlx-community/MiniMax-M2.1-4bit

# Compare TPS with baseline (Phase 2: 45.73 TPS)
```

**Expected results:**
- TPS: 45.73 → 46-48? (0-5% improvement)
- Memory: Similar (~135GB)

---

### Test 11: MLX 8-bit with VRAM Optimization

**Purpose:** Test VRAM impact on larger models

```bash
# Keep VRAM at 448GB
sudo sysctl iogpu.wired_limit_mb=458752

# Re-run 8-bit test
python scripts/benchmark_mlx.py --model mlx-community/MiniMax-M2.1-8bit

# Compare with baseline (Phase 2: 33.04 TPS)
```

**Expected results:**
- TPS: 33.04 → 34-36? (5-10% improvement)
- Larger models benefit more from extra VRAM

---

### Test 12: Aggressive VRAM (480GB)

**Purpose:** Find maximum safe VRAM limit

```bash
# Set VRAM to 480GB (aggressive)
sudo sysctl iogpu.wired_limit_mb=491520

# Verify
sysctl iogpu.wired_limit_mb

# Test with 4-bit
python scripts/benchmark_mlx.py --model mlx-community/MiniMax-M2.1-4bit

# Monitor system stability
```

**Expected results:**
- May see additional improvement or no change
- Watch for system instability

**Note:** If system becomes unstable, restart to reset VRAM limit.

---

### Test 13: llama.cpp with Metal Optimization

**Purpose:** Test Metal backend environment variables

```bash
# Baseline (already done or pending)
python scripts/benchmark_llama.py --model ~/models/MiniMax-M2.1-Q4_K_M.gguf

# Test with FORCE_PRIVATE
export GGML_METAL_FORCE_PRIVATE=1
python scripts/benchmark_llama.py --model ~/models/MiniMax-M2.1-Q4_K_M.gguf
unset GGML_METAL_FORCE_PRIVATE

# Compare TPS
```

**Expected results:**
- 0-10% improvement with FORCE_PRIVATE
- May use more memory

---

### Test 14: Metal Device Selection (M3 Ultra)

**Purpose:** Test if different GPU dies perform differently

```bash
# Test die 0
export GGML_METAL_DEVICE_INDEX=0
python scripts/benchmark_llama.py --model ~/models/MiniMax-M2.1-Q4_K_M.gguf

# Test die 1
export GGML_METAL_DEVICE_INDEX=1
python scripts/benchmark_llama.py --model ~/models/MiniMax-M2.1-Q4_K_M.gguf

# Compare performance
unset GGML_METAL_DEVICE_INDEX
```

**Expected results:**
- Minimal difference (load balancing should be automatic)
- Interesting data point for M3 Ultra architecture

---

### Test 15: Combined Optimization

**Purpose:** Test all optimizations together

```bash
# System-level VRAM
sudo sysctl iogpu.wired_limit_mb=458752

# Metal backend optimizations
export GGML_METAL_FORCE_PRIVATE=1
export GGML_METAL_DEVICE_INDEX=0
export GGML_METAL_N_CB=2

# Run test
python scripts/benchmark_llama.py --model ~/models/MiniMax-M2.1-Q4_K_M.gguf

# Cleanup
unset GGML_METAL_FORCE_PRIVATE
unset GGML_METAL_DEVICE_INDEX
unset GGML_METAL_N_CB
```

**Expected results:**
- Best possible performance for llama.cpp
- Baseline for future tests

---

### Test 16: Automated VRAM Testing

**Purpose:** Run all VRAM configs automatically

```bash
# MLX model testing
./scripts/benchmark_vram.sh --model mlx-community/MiniMax-M2.1-4bit

# llama.cpp testing
./scripts/benchmark_vram.sh --gguf ~/models/MiniMax-M2.1-Q4_K_M.gguf

# Results saved to docs/test-results/vram-optimization/
```

**The script will test:**
- Default VRAM (~384GB)
- Optimized VRAM (448GB)
- Aggressive VRAM (480GB)

---

### Monitoring During VRAM Tests

```bash
# Monitor GPU memory usage
watch -n 1 'sysctl -a | grep iogpu'

# Monitor system memory pressure
memory_pressure

# Check GPU activity
sudo powermetrics --samplers gpu_power -i 1000
```

---

### Restore Default VRAM

```bash
# VRAM settings automatically reset on restart
# Or manually reset (if you know the default):
sudo sysctl iogpu.wired_limit_mb=393216  # Example: 384GB

# To restore without knowing default, just restart:
sudo reboot
```

---

## Test Checklist (Updated)

**Phase 3: llama.cpp**
- [ ] Q4_K_M downloaded (138GB)
- [ ] Q4_K_M benchmark completed
- [ ] Q4_K_M model deleted (save space)
- [ ] Q8_0 downloaded (243GB)
- [ ] Q8_0 benchmark completed
- [ ] Q8_0 model deleted (save space)

**Phase 4: Batching**
- [ ] vllm-mlx installed (or using mlx-lm fallback)
- [ ] Baseline (1 concurrent) completed
- [ ] 2 concurrent completed
- [ ] 4 concurrent completed
- [ ] 8 concurrent completed
- [ ] 16 concurrent completed
- [ ] Mixed workload completed

**Phase 5: VRAM Optimization** 🆕
- [ ] Current VRAM limit checked
- [ ] MLX 4-bit with 448GB VRAM
- [ ] MLX 8-bit with 448GB VRAM
- [ ] Aggressive VRAM (480GB) tested
- [ ] llama.cpp with FORCE_PRIVATE
- [ ] Metal device selection tested
- [ ] Combined optimization tested
- [ ] Automated testing script run

**Documentation**
- [ ] Results added to benchmark-results.md
- [ ] VRAM optimization analysis written
- [ ] Summary analysis written
- [ ] Comparison charts created (optional)
- [ ] Twitter summary prepared

---

## Quick Commands Summary (Updated)

```bash
# llama.cpp Q4_K_M
python scripts/benchmark_llama.py --model ~/models/minimax-m2.1-gguf/MiniMax-M2.1-Q4_K_M.gguf

# llama.cpp Q8_0
python scripts/benchmark_llama.py --model ~/models/minimax-m2.1-gguf/MiniMax-M2.1-Q8_0.gguf

# Batching: baseline
python scripts/benchmark_batching.py --model mlx-community/MiniMax-M2.1-4bit --concurrent 1

# Batching: scaling tests
for c in 2 4 8 16; do
  python scripts/benchmark_batching.py --model mlx-community/MiniMax-M2.1-4bit --concurrent $c
done

# Batching: mixed workload
python scripts/benchmark_batching.py --model mlx-community/MiniMax-M2.1-4bit --concurrent 4 --mixed

# VRAM optimization (automated)
./scripts/benchmark_vram.sh --model mlx-community/MiniMax-M2.1-4bit

# VRAM optimization (manual)
sudo sysctl iogpu.wired_limit_mb=458752
python scripts/benchmark_mlx.py --model mlx-community/MiniMax-M2.1-4bit

# llama.cpp with Metal optimization
export GGML_METAL_FORCE_PRIVATE=1
python scripts/benchmark_llama.py --model ~/models/model.gguf
```

---

## Estimated Time (Updated)

| Test | Duration | Notes |
|------|----------|-------|
| Q4_K_M download | 20-40 min | Depends on network |
| Q4_K_M benchmark | 10-15 min | 5 test cases |
| Q8_0 download | 30-60 min | Larger file |
| Q8_0 benchmark | 15-20 min | Slower TPS |
| Batching baseline | 5 min | Already have model |
| Batching 2-16 concurrent | 20-30 min | 4 tests |
| Mixed workload | 5-10 min | |
| **VRAM optimization** 🆕 | **30-45 min** | Multiple configs |
| **Total** | **3-4 hours** | Excludes download time |

---

## Next Steps

After completing all tests:

1. Update `docs/benchmark-results.md`
2. Analyze VRAM optimization impact
3. Create comparison summary
4. Write Twitter thread with findings
5. Consider additional tests:
   - 6-bit batching tests
   - 8-bit batching tests
   - Context length scaling
   - Long-running stability tests
   - bf16 with optimized VRAM (may now be runnable!)
