# MiniMax M2.1 Benchmark Results

> Last updated: 2026-02-02

## Test Environment

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

---

## MLX Results

### MiniMax-M2.1-4bit

**Test Date:** 2026-02-02

| Metric | Value |
|--------|-------|
| **Model Size** | ~120 GB |
| **Load Time** | 21.25 sec |
| **Peak Memory** | 134.81 GB |
| **Average TPS** | 45.73 tokens/sec |
| **Max TPS** | 49.24 tokens/sec |
| **Min TPS** | 34.85 tokens/sec |
| **Average TTFT** | 0.067 sec |

#### Individual Test Results

| Test | Description | Tokens | TPS | TTFT | Gen Time |
|------|-------------|--------|-----|------|----------|
| short | Short text generation | 100 | 34.85 | 0.089s | 2.87s |
| medium | Code generation | 500 | 49.24 | 0.061s | 10.15s |
| long | Long text generation | 2000 | 48.16 | 0.062s | 41.53s |
| reasoning | Logical reasoning | 500 | 48.64 | 0.062s | 10.28s |
| instruction | Instruction following | 400 | 47.77 | 0.063s | 8.37s |

**Notes:**
- First test (short) shows lower TPS due to initial warm-up
- After warm-up, consistent ~48-49 TPS across all test types
- Very low TTFT (~61-89ms) indicates fast prompt processing

---

### MiniMax-M2.1-6bit

**Test Date:** 2026-02-02

| Metric | Value |
|--------|-------|
| **Model Size** | ~180 GB |
| **Load Time** | 29.85 sec (cached) |
| **Peak Memory** | 191.88 GB |
| **Average TPS** | 41.83 tokens/sec |
| **Max TPS** | 47.19 tokens/sec |
| **Min TPS** | 29.37 tokens/sec |
| **Average TTFT** | 0.075 sec |

#### Individual Test Results

| Test | Description | Tokens | TPS | TTFT | Gen Time |
|------|-------------|--------|-----|------|----------|
| short | Short text generation | 110 | 29.37 | 0.105s | 3.75s |
| medium | Code generation | 583 | 47.19 | 0.064s | 12.35s |
| long | Long text generation | 2232 | 44.58 | 0.067s | 50.07s |
| reasoning | Logical reasoning | 561 | 44.90 | 0.067s | 12.49s |
| instruction | Instruction following | 433 | 43.11 | 0.070s | 10.04s |

**Notes:**
- 6-bit provides modest quality improvement over 4-bit
- ~9% slower than 4-bit due to larger model size
- Memory usage increased by ~57GB over 4-bit

---

### MiniMax-M2.1-8bit

**Test Date:** 2026-02-02

| Metric | Value |
|--------|-------|
| **Model Size** | ~240 GB |
| **Load Time** | 28.07 sec (cached) |
| **Peak Memory** | 252.19 GB |
| **Average TPS** | 33.04 tokens/sec |
| **Max TPS** | 35.98 tokens/sec |
| **Min TPS** | 22.52 tokens/sec |
| **Average TTFT** | 0.095 sec |

#### Individual Test Results

| Test | Description | Tokens | TPS | TTFT | Gen Time |
|------|-------------|--------|-----|------|----------|
| short | Short text generation | 100 | 22.52 | 0.137s | 4.44s |
| medium | Code generation | 500 | 35.98 | 0.084s | 13.90s |
| long | Long text generation | 2000 | 35.59 | 0.084s | 56.19s |
| reasoning | Logical reasoning | 500 | 35.76 | 0.084s | 13.98s |
| instruction | Instruction following | 400 | 35.34 | 0.086s | 11.32s |

**Notes:**
- 8-bit provides better quality at cost of speed
- ~28% slower than 4-bit
- Uses about 2x memory compared to 4-bit

---

### MiniMax-M2.1-bf16

**Status:** Not yet tested (~460GB, close to 512GB limit)

---

## llama.cpp Results

### BF16 (Full Precision)

**Test Date:** 2026-02-03

| Metric | Value |
|--------|-------|
| **Model Size** | ~457 GB (10 shards) |
| **Memory Usage** | 426 GB (83% of 512GB) |
| **Status** | FAILED - Process killed after ~6 hours |
| **TPS** | <0.3 tokens/sec (estimated) |

**Notes:**
- BF16 is NOT practical on 512GB Mac with llama.cpp
- Process ran for 6+ hours without completing first test (100 tokens)
- Killed by system (exit code 137 - likely OOM)
- Memory usage at limit, causing severe performance degradation

**Failure Analysis:**

Exit code 137 = SIGKILL (killed by system)

| Factor | Value |
|--------|-------|
| Model size | 457 GB |
| Memory used | 426 GB |
| System total | 512 GB |
| Usage ratio | **83%** |

Root causes:
1. **Memory near limit** - Only ~86GB left for system and other processes
2. **Swap pressure** - macOS swaps heavily under memory pressure, causing severe slowdown
3. **Extreme slowdown** - 6 hours for <100 tokens = TPS < 0.3 (normal: 30-50)
4. **OOM kill** - System killed process when additional memory was needed

**Recommendation:** BF16 requires at least **640GB+ RAM** for practical use. On 512GB Mac, use 8-bit or lower quantization.

---

### Q4_K_M

**Status:** Not yet tested

---

### Q8_0

**Status:** Not yet tested

---

## Summary

| Version | Framework | Load Time | Memory | Avg TPS | TTFT |
|---------|-----------|-----------|--------|---------|------|
| 4-bit | MLX | 21.25s | 135 GB | 45.73 | 67ms |
| 6-bit | MLX | 29.85s | 192 GB | 41.83 | 75ms |
| 8-bit | MLX | 28.07s | 252 GB | 33.04 | 95ms |
| bf16 | MLX | - | ~460 GB | N/A | N/A |
| BF16 | llama.cpp | - | 426 GB | <0.3 | FAILED |
| Q4_K_M | llama.cpp | - | - | - | - |
| Q8_0 | llama.cpp | - | - | - | - |

## Observations

### MiniMax M2.1 on M3 Ultra (512GB)

1. **Memory Scaling**: Memory usage scales roughly linearly with quantization:
   - 4-bit: ~135 GB
   - 6-bit: ~192 GB (+42%)
   - 8-bit: ~252 GB (+87%)

2. **Speed vs Quality Trade-off**:
   - 4-bit: 45.73 TPS - Best speed, acceptable quality
   - 6-bit: 41.83 TPS - 9% slower, modest quality improvement
   - 8-bit: 33.04 TPS - 28% slower, better quality

3. **Low Latency**: All versions maintain excellent TTFT:
   - 4-bit: 67ms
   - 6-bit: 75ms
   - 8-bit: 95ms

4. **Recommendation**: For interactive use, 4-bit offers the best balance of speed and quality. For tasks requiring higher accuracy, 6-bit is a good middle ground.

5. **512GB Headroom**: Even 8-bit (252GB) leaves room for concurrent workloads.

6. **BF16 Not Practical**: BF16 (457GB) consumes 83% of memory and is extremely slow:
   - llama.cpp BF16 failed after 6 hours without completing even 100 tokens
   - Memory pressure causes severe performance degradation
   - Estimated TPS <0.3 (vs 45+ for 4-bit MLX)
   - **Recommendation**: Use 8-bit or lower for any interactive use
