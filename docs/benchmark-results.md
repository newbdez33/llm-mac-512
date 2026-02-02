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
| **Load Time** | 6.08 sec |
| **Peak Memory** | 172.35 GB |
| **Average TPS** | 44.21 tokens/sec |
| **Max TPS** | 48.93 tokens/sec |
| **Min TPS** | 27.61 tokens/sec |
| **Average TTFT** | 0.072 sec |

#### Individual Test Results

| Test | Description | Tokens | TPS | TTFT | Gen Time |
|------|-------------|--------|-----|------|----------|
| short | Short text generation | 100 | 27.61 | 0.112s | 3.62s |
| medium | Code generation | 500 | 48.93 | 0.062s | 10.22s |
| long | Long text generation | 2000 | 47.99 | 0.063s | 41.67s |
| reasoning | Logical reasoning | 500 | 48.32 | 0.062s | 10.35s |
| instruction | Instruction following | 400 | 48.19 | 0.063s | 8.30s |

**Notes:**
- First test (short) shows lower TPS due to initial warm-up
- After warm-up, consistent ~48 TPS across all test types
- Very low TTFT (~62-72ms) indicates fast prompt processing

---

### MiniMax-M2.1-8bit

**Status:** Not yet tested

---

### MiniMax-M2.1-bf16

**Status:** Not yet tested

---

## llama.cpp Results

### Q4_K_M

**Status:** Not yet tested

---

### Q8_0

**Status:** Not yet tested

---

## Summary

| Version | Framework | Load Time | Memory | Avg TPS | TTFT |
|---------|-----------|-----------|--------|---------|------|
| 4-bit | MLX | 6.08s | 172 GB | 44.21 | 72ms |
| 8-bit | MLX | - | - | - | - |
| bf16 | MLX | - | - | - | - |
| Q4_K_M | llama.cpp | - | - | - | - |
| Q8_0 | llama.cpp | - | - | - | - |

## Observations

### MiniMax M2.1 4-bit on M3 Ultra (512GB)

1. **Memory Efficiency**: The 4-bit quantized model uses only ~172GB of the 512GB available, leaving plenty of headroom for larger context sizes or concurrent workloads.

2. **Generation Speed**: At ~48 tokens/sec after warm-up, the model provides a responsive interactive experience. This is excellent for a 230B parameter model.

3. **Low Latency**: TTFT of ~62-72ms means users get near-instant feedback when starting generation.

4. **Load Time**: 6 seconds to load a 120GB model is very fast, thanks to MLX's efficient memory mapping.

5. **Quality**: The model produces coherent, well-structured responses in both Chinese and English, with good code generation capabilities.
