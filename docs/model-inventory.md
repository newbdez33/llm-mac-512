# 测试模型清单

> 更新时间: 2026-02-04
> 所有模型通过 LM Studio 加载测试

---

## MiniMax M2.1 (230B/10B MoE)

### MLX 版本 (mlx-community)

| 量化 | 模型仓库 | 大小 | 内存 | 状态 | 备注 |
|------|----------|------|------|------|------|
| **4-bit** | [mlx-community/MiniMax-M2.1-4bit](https://huggingface.co/mlx-community/MiniMax-M2.1-4bit) | ~120GB | ~135GB | ✅ 可用 | 推荐 |
| **3-bit** | [mlx-community/MiniMax-M2.1-3bit](https://huggingface.co/mlx-community/MiniMax-M2.1-3bit) | ~90GB | ~105GB | 🔍 备选 | 更小但质量可能下降 |
| **8-bit** | [mlx-community/MiniMax-M2.1-8bit-gs32](https://huggingface.co/mlx-community/MiniMax-M2.1-8bit-gs32) | ~240GB | ~252GB | ✅ 可用 | 高质量 |
| **6-bit** | ❌ 不存在 | - | - | ❌ | mlx-community 无此版本 |

**下载命令**:
```bash
# LM Studio CLI
lms download mlx-community/MiniMax-M2.1-4bit
lms download mlx-community/MiniMax-M2.1-8bit-gs32

# 或 mlx-lm
mlx_lm.convert --hf-path mlx-community/MiniMax-M2.1-4bit
```

---

### GGUF 版本 (unsloth)

| 量化 | 模型仓库 | 文件 | 大小 | 内存 | 状态 | 备注 |
|------|----------|------|------|------|------|------|
| **Q4_K_S** | [unsloth/MiniMax-M2.1-GGUF](https://huggingface.co/unsloth/MiniMax-M2.1-GGUF) | Q4_K_S | 130GB | ~135GB | 🔄 已加载 | 小4-bit |
| **Q4_K_M** | [unsloth/MiniMax-M2.1-GGUF](https://huggingface.co/unsloth/MiniMax-M2.1-GGUF) | Q4_K_M | 138GB | ~143GB | ✅ 可用 | 标准4-bit |
| **Q6_K** | [unsloth/MiniMax-M2.1-GGUF](https://huggingface.co/unsloth/MiniMax-M2.1-GGUF) | Q6_K | 188GB | ~193GB | ✅ 可用 | 6-bit |
| **Q8_0** | [unsloth/MiniMax-M2.1-GGUF](https://huggingface.co/unsloth/MiniMax-M2.1-GGUF) | Q8_0 | 243GB | ~248GB | ✅ 可用 | 8-bit |
| **BF16** | [unsloth/MiniMax-M2.1-GGUF](https://huggingface.co/unsloth/MiniMax-M2.1-GGUF) | BF16 | 457GB | ~462GB | ❌ 失败 | OOM (已测) |

**下载命令**:
```bash
# LM Studio
lms download unsloth/MiniMax-M2.1-GGUF:Q4_K_S
lms download unsloth/MiniMax-M2.1-GGUF:Q4_K_M
lms download unsloth/MiniMax-M2.1-GGUF:Q6_K
lms download unsloth/MiniMax-M2.1-GGUF:Q8_0
```

---

### MiniMax M2.1 测试配对

| 量化级别 | MLX 版本 | GGUF 版本 | 对比目的 |
|----------|----------|-----------|----------|
| **4-bit** | mlx-4bit (120GB) | Q4_K_S (130GB) ✅ | 相似大小，框架对比 |
| **4-bit+** | - | Q4_K_M (138GB) | 更大的 Q4 版本 |
| **8-bit** | mlx-8bit-gs32 (240GB) | Q8_0 (243GB) | 高精度对比 |

**注意**:
- ❌ 无 6-bit MLX 版本，Q6_K 只能单独测试
- ✅ 有 3-bit MLX 版本，可作为备选

---

## Qwen3-Coder-Next (80B/3B MoE)

### MLX 版本

| 状态 | 说明 |
|------|------|
| ❌ **无预量化 MLX 版本** | mlx-community 暂无转换版本 |
| ⚠️ **可手动转换** | 官方支持 MLX-LM，可自行转换原始模型 |
| 📦 **原始模型** | [Qwen/Qwen3-Coder-Next](https://huggingface.co/Qwen/Qwen3-Coder-Next) (BF16, 159GB) |

**手动转换** (如需要):
```bash
# 下载原始模型
huggingface-cli download Qwen/Qwen3-Coder-Next

# 使用 mlx-lm 转换为 4-bit
mlx_lm.convert \
  --hf-path Qwen/Qwen3-Coder-Next \
  --quantize \
  --q-bits 4 \
  --mlx-path ./qwen3-coder-next-4bit
```

**注意**:
- 原始模型 159GB，转换为 4-bit 约 45GB
- 转换需要约 200GB+ 临时空间
- 转换时间约 1-2 小时

---

### GGUF 版本 (unsloth) ✅

| 量化 | 模型仓库 | 文件 | 大小 | 内存 | 状态 | 优先级 |
|------|----------|------|------|------|------|--------|
| **Q4_K_M** | [unsloth/Qwen3-Coder-Next-GGUF](https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF) | Q4_K_M | 48.5GB | ~53GB | ✅ 推荐 | 🔥 1 |
| **Q4_0** | [unsloth/Qwen3-Coder-Next-GGUF](https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF) | Q4_0 | 45.3GB | ~50GB | ✅ 可用 | 2 |
| **Q6_K** | [unsloth/Qwen3-Coder-Next-GGUF](https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF) | Q6_K | 65.5GB | ~70GB | ✅ 推荐 | 🔥 3 |
| **Q8_0** | [unsloth/Qwen3-Coder-Next-GGUF](https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF) | Q8_0 | 84.8GB | ~90GB | ✅ 推荐 | 🔥 4 |
| **Q2_K** | [unsloth/Qwen3-Coder-Next-GGUF](https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF) | Q2_K | 29.2GB | ~34GB | ✅ 可选 | 5 |
| **BF16** | [unsloth/Qwen3-Coder-Next-GGUF](https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF) | BF16 | 159GB | ~164GB | ✅ 可测 | 6 |

**下载命令**:
```bash
# LM Studio
lms download unsloth/Qwen3-Coder-Next-GGUF:Q4_K_M
lms download unsloth/Qwen3-Coder-Next-GGUF:Q6_K
lms download unsloth/Qwen3-Coder-Next-GGUF:Q8_0
lms download unsloth/Qwen3-Coder-Next-GGUF:BF16
```

---

### Qwen3-Coder-Next 测试计划

| 量化级别 | MLX 版本 | GGUF 版本 | 测试计划 |
|----------|----------|-----------|----------|
| **4-bit** | ❌ 不存在 | Q4_K_M (48.5GB) ✅ | 仅 GGUF |
| **6-bit** | ❌ 不存在 | Q6_K (65.5GB) ✅ | 仅 GGUF |
| **8-bit** | ❌ 不存在 | Q8_0 (84.8GB) ✅ | 仅 GGUF |
| **BF16** | ❌ 不存在 | BF16 (159GB) ✅ | 仅 GGUF，可选 |

**结论**: Qwen3-Coder-Next 只能测试 GGUF 版本，无法进行 MLX vs llama.cpp 框架对比

**备选方案**:
1. 手动转换 MLX 4-bit 版本 (需要 1-2 小时 + 200GB 空间)
2. 只测试 GGUF 版本的性能
3. 使用 Qwen3-Next (不是 Coder) 的 MLX 版本进行框架对比

---

## 推荐测试矩阵

### Phase 1: MiniMax M2.1 (完整测试)

| Day | MLX Backend (LM Studio) | llama.cpp Backend (LM Studio) | 对比 |
|-----|-------------------------|-------------------------------|------|
| 1 | mlx-4bit (120GB) | Q4_K_S (130GB) | ✅ 框架对比 |
| 2 | - | Q4_K_M (138GB) | Q4 变体对比 |
| 3 | mlx-8bit (240GB) | Q8_0 (243GB) | ✅ 框架对比 |
| 4 | - | Q6_K (188GB) | 单独测试 |
| 5 | (可选) mlx-3bit (90GB) | - | 更小版本 |

**预计磁盘占用**: 最大约 400GB (同时保留 2-3 个模型)

---

### Phase 2: Qwen3-Coder-Next (GGUF only)

| Day | llama.cpp Backend (LM Studio) | 说明 |
|-----|-------------------------------|------|
| 1 | Q4_K_M (48.5GB) | 4-bit 基准 |
| 2 | Q6_K (65.5GB) | 6-bit |
| 3 | Q8_0 (84.8GB) | 8-bit |
| 4 | Q2_K (29.2GB) + Q4_0 (45.3GB) | 轻量级版本 |
| 5 | (可选) BF16 (159GB) | 完整精度 |

**预计磁盘占用**: 最大约 250GB

---

## 磁盘空间规划

### 并行保留策略

**MiniMax M2.1 测试时**:
```
活跃模型:
- MLX 4-bit: 120GB
- GGUF Q4_K_S: 130GB
总计: ~250GB

可选保留:
+ MLX 8-bit: 240GB
+ GGUF Q8_0: 243GB
如果磁盘充足: ~730GB
```

**Qwen3-Coder-Next 测试时**:
```
活跃模型:
- Q4_K_M: 48.5GB
- Q6_K: 65.5GB
- Q8_0: 84.8GB
总计: ~200GB (可同时保留)
```

### 删除策略

**测试完毕即删除**:
```bash
# 测试完成后删除模型
rm -rf ~/.lmstudio/models/{model-name}

# 或通过 LM Studio GUI 删除
```

**保留核心版本**:
- MiniMax M2.1 4-bit (120GB) - 性价比最高
- Qwen3-Coder-Next Q4_K_M (48.5GB) - 推荐版本

总计: ~170GB (长期保留)

---

## 下载清单

### Week 1 准备 (MiniMax M2.1)

```bash
# MLX 版本
lms download mlx-community/MiniMax-M2.1-4bit
lms download mlx-community/MiniMax-M2.1-8bit-gs32

# GGUF 版本 (Q4_K_S 已有)
lms download unsloth/MiniMax-M2.1-GGUF:Q4_K_M
lms download unsloth/MiniMax-M2.1-GGUF:Q6_K
lms download unsloth/MiniMax-M2.1-GGUF:Q8_0
```

**下载大小**: ~850GB
**建议**: 边测边下，测完删除

---

### Week 2 准备 (Qwen3-Coder-Next)

```bash
# GGUF 版本 (仅此一套)
lms download unsloth/Qwen3-Coder-Next-GGUF:Q4_K_M
lms download unsloth/Qwen3-Coder-Next-GGUF:Q6_K
lms download unsloth/Qwen3-Coder-Next-GGUF:Q8_0

# 可选
lms download unsloth/Qwen3-Coder-Next-GGUF:Q2_K
lms download unsloth/Qwen3-Coder-Next-GGUF:Q4_0
lms download unsloth/Qwen3-Coder-Next-GGUF:BF16
```

**下载大小**: ~200GB (核心版本)
**建议**: 可同时下载，占用空间较小

---

## 模型验证清单

下载完成后验证：

### MiniMax M2.1
- [ ] MLX 4-bit: 可在 LM Studio 中加载，显示 "MLX" 标签
- [ ] MLX 8-bit: 可在 LM Studio 中加载，显示 "MLX" 标签
- [ ] GGUF Q4_K_S: 已加载 ✅
- [ ] GGUF Q4_K_M: 可加载，显示 "llama.cpp" 标签
- [ ] GGUF Q6_K: 可加载，显示 "llama.cpp" 标签
- [ ] GGUF Q8_0: 可加载，显示 "llama.cpp" 标签

### Qwen3-Coder-Next
- [ ] GGUF Q4_K_M: 可加载，显示 "llama.cpp" 标签
- [ ] GGUF Q6_K: 可加载，显示 "llama.cpp" 标签
- [ ] GGUF Q8_0: 可加载，显示 "llama.cpp" 标签

---

## 参考链接

### MiniMax M2.1
- [MLX 4-bit](https://huggingface.co/mlx-community/MiniMax-M2.1-4bit)
- [MLX 8-bit-gs32](https://huggingface.co/mlx-community/MiniMax-M2.1-8bit-gs32)
- [Unsloth GGUF](https://huggingface.co/unsloth/MiniMax-M2.1-GGUF)

### Qwen3-Coder-Next
- [官方模型](https://huggingface.co/Qwen/Qwen3-Coder-Next)
- [Unsloth GGUF](https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF)
- [官方博客](https://qwen.ai/blog?id=qwen3-coder-next)

---

## 更新日志

- **2026-02-04**: 初始版本，确认所有测试模型
  - MiniMax M2.1: MLX 4bit/8bit + GGUF Q4/Q6/Q8
  - Qwen3-Coder-Next: GGUF only (无 MLX 预量化版本)
  - 注意: 无 MLX 6-bit MiniMax 版本
