# MLX 本地运行指南

> 在Mac上本地运行MiniMax M2.1模型的完整指南

## 📋 目录

- [系统要求](#系统要求)
- [环境配置](#环境配置)
- [安装MLX](#安装mlx)
- [运行模型](#运行模型)
- [使用示例](#使用示例)
- [性能优化](#性能优化)
- [故障排除](#故障排除)

---

## 系统要求

### 最低要求

| 项目 | 要求 |
|------|------|
| **硬件** | Apple Silicon Mac (M1/M2/M3系列) |
| **macOS** | 13.3+ (推荐 14.0+) |
| **内存** | 16GB+ (推荐64GB+) |
| **磁盘空间** | 150GB+ 可用空间 |
| **Python** | 3.9+ (推荐 3.12) |

### 推荐配置（MiniMax M2.1）

| 模型版本 | 推荐内存 | 磁盘空间 | 性能预期 |
|---------|---------|---------|---------|
| 4-bit | 32GB+ | 120GB | 最快 (~45 TPS) |
| 6-bit | 64GB+ | 180GB | 平衡 (~40 TPS) |
| 8-bit | 128GB+ | 240GB | 高质量 (~33 TPS) |
| bf16 | 512GB | 460GB | 全精度 (不推荐) |

> **注意：** 你的Mac Studio (512GB) 可以运行所有版本！

---

## 环境配置

### 1. 检查系统信息

```bash
# 查看系统信息
system_profiler SPHardwareDataType | grep -E "Model Name|Model Identifier|Chip|Memory"

# 查看macOS版本
sw_vers

# 查看可用磁盘空间
df -h
```

**你的配置：**
- Mac Studio (Mac15,14)
- Apple M3 Ultra
- 512 GB 统一内存
- macOS 26.2

✅ 满足所有要求！

### 2. 安装Homebrew（如果未安装）

```bash
# 检查是否已安装
which brew

# 如果未安装，运行：
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 3. 安装Python 3.12

```bash
# 安装Python 3.12
brew install python@3.12

# 验证安装
python3.12 --version
```

---

## 安装MLX

### 方式一：使用现有项目（推荐）

你已经有这个项目了，直接激活环境：

```bash
# 进入项目目录
cd ~/projects/llm-mac-512  # 或你的项目实际路径

# 激活虚拟环境
source venv/bin/activate

# 验证MLX安装
python -c "import mlx.core as mx; print(f'MLX version: {mx.__version__}')"
python -c "import mlx_lm; print('mlx-lm installed')"
```

如果出现错误，重新安装：

```bash
# 确保虚拟环境激活
source venv/bin/activate

# 更新MLX
pip install --upgrade mlx mlx-lm

# 验证
python -c "import mlx_lm; print('Success!')"
```

### 方式二：从零开始（新项目）

```bash
# 创建项目目录
mkdir -p ~/mlx-minimax
cd ~/mlx-minimax

# 创建虚拟环境
python3.12 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装MLX和mlx-lm
pip install mlx mlx-lm

# 安装其他工具
pip install huggingface-hub psutil

# 验证安装
python -c "import mlx.core as mx; print('MLX installed successfully!')"
```

---

## 运行模型

### 快速开始：命令行运行

#### 1. 最简单的方式（4-bit，推荐首次测试）

```bash
# 进入项目目录并激活环境
cd ~/projects/llm-mac-512  # 或你的项目实际路径
source venv/bin/activate

# 运行模型（会自动下载）
mlx_lm.generate --model mlx-community/MiniMax-M2.1-4bit \
  --prompt "请用一句话解释量子计算" \
  --max-tokens 100
```

**首次运行会下载模型（~120GB），请耐心等待！**

#### 2. 交互式对话

```bash
# 启动交互模式
mlx_lm.generate --model mlx-community/MiniMax-M2.1-4bit \
  --prompt "你好，请介绍一下你自己" \
  --max-tokens 500
```

#### 3. 使用不同的模型版本

```bash
# 6-bit（更好的质量）
mlx_lm.generate --model mlx-community/MiniMax-M2.1-6bit \
  --prompt "写一个Python快速排序算法" \
  --max-tokens 500

# 8-bit（最佳质量）
mlx_lm.generate --model mlx-community/MiniMax-M2.1-8bit \
  --prompt "详细解释深度学习的反向传播算法" \
  --max-tokens 2000
```

---

### Python脚本运行

#### 基础示例

创建文件 `test_mlx.py`：

```python
#!/usr/bin/env python3
"""
MLX MiniMax M2.1 基础测试
"""

from mlx_lm import load, generate

# 加载模型（首次会下载）
print("Loading model...")
model, tokenizer = load("mlx-community/MiniMax-M2.1-4bit")
print("Model loaded!")

# 准备prompt
prompt = "请用一句话解释量子计算"

# 生成回答
print(f"\nPrompt: {prompt}\n")
print("Generating...")

response = generate(
    model,
    tokenizer,
    prompt=prompt,
    max_tokens=100,
    verbose=True  # 显示生成过程
)

print(f"\nResponse:\n{response}")
```

运行：

```bash
python test_mlx.py
```

#### 高级示例：带参数控制

创建文件 `chat_mlx.py`：

```python
#!/usr/bin/env python3
"""
MLX MiniMax M2.1 对话示例
"""

from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
import time

def chat(model_name="mlx-community/MiniMax-M2.1-4bit"):
    """交互式对话"""

    # 加载模型
    print("Loading model...")
    start_time = time.time()
    model, tokenizer = load(model_name)
    load_time = time.time() - start_time
    print(f"Model loaded in {load_time:.2f} seconds\n")

    print("=" * 60)
    print("MiniMax M2.1 本地对话")
    print("=" * 60)
    print("输入 'quit' 或 'exit' 退出\n")

    while True:
        # 获取用户输入
        user_input = input("You: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("再见！")
            break

        if not user_input:
            continue

        # 应用chat模板（如果有）
        if hasattr(tokenizer, 'apply_chat_template'):
            messages = [{"role": "user", "content": user_input}]
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            prompt = user_input

        # 生成回答
        print("\nAssistant: ", end="", flush=True)
        start_gen = time.time()

        # 创建采样器
        sampler = make_sampler(temp=0.7)

        response = generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=500,
            sampler=sampler,
            verbose=False
        )

        gen_time = time.time() - start_gen
        tokens = len(tokenizer.encode(response))
        tps = tokens / gen_time if gen_time > 0 else 0

        print(response)
        print(f"\n[生成 {tokens} tokens，用时 {gen_time:.2f}s，速度 {tps:.1f} tokens/s]\n")

if __name__ == "__main__":
    # 可以修改模型版本
    # chat("mlx-community/MiniMax-M2.1-4bit")  # 最快
    # chat("mlx-community/MiniMax-M2.1-6bit")  # 平衡
    # chat("mlx-community/MiniMax-M2.1-8bit")  # 最佳质量

    chat()  # 默认4-bit
```

运行：

```bash
python chat_mlx.py
```

#### 批量测试示例

创建文件 `batch_test.py`：

```python
#!/usr/bin/env python3
"""
批量测试多个prompts
"""

from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
import time

# 测试prompts
test_prompts = [
    "请用一句话解释量子计算",
    "写一个Python快速排序算法",
    "什么是人工智能？",
    "解释一下区块链技术",
    "给我讲个笑话"
]

def batch_test(model_name="mlx-community/MiniMax-M2.1-4bit"):
    """批量测试"""

    print("Loading model...")
    model, tokenizer = load(model_name)
    print("Model loaded!\n")

    sampler = make_sampler(temp=0.7)

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}/{len(test_prompts)}")
        print(f"{'='*60}")
        print(f"Prompt: {prompt}\n")

        start_time = time.time()
        response = generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=200,
            sampler=sampler,
            verbose=False
        )
        gen_time = time.time() - start_time

        tokens = len(tokenizer.encode(response))
        tps = tokens / gen_time if gen_time > 0 else 0

        print(f"Response:\n{response}\n")
        print(f"Stats: {tokens} tokens in {gen_time:.2f}s ({tps:.1f} TPS)")

if __name__ == "__main__":
    batch_test()
```

运行：

```bash
python batch_test.py
```

---

## 使用示例

### 示例1：代码生成

```bash
mlx_lm.generate \
  --model mlx-community/MiniMax-M2.1-4bit \
  --prompt "写一个Python函数，计算斐波那契数列的第n项" \
  --max-tokens 300
```

### 示例2：文本翻译

```bash
mlx_lm.generate \
  --model mlx-community/MiniMax-M2.1-4bit \
  --prompt "将以下英文翻译成中文：Machine learning is a subset of artificial intelligence" \
  --max-tokens 100
```

### 示例3：问答

```bash
mlx_lm.generate \
  --model mlx-community/MiniMax-M2.1-4bit \
  --prompt "什么是梯度下降？请用简单的语言解释" \
  --max-tokens 300
```

### 示例4：长文本生成

```bash
mlx_lm.generate \
  --model mlx-community/MiniMax-M2.1-4bit \
  --prompt "写一篇关于人工智能未来发展的文章" \
  --max-tokens 2000 \
  --temp 0.8
```

---

## 性能优化

### 1. 选择合适的模型版本

根据你的需求选择：

```bash
# 速度优先（推荐日常使用）
mlx_lm.generate --model mlx-community/MiniMax-M2.1-4bit ...

# 质量优先（重要任务）
mlx_lm.generate --model mlx-community/MiniMax-M2.1-8bit ...

# 平衡（折中方案）
mlx_lm.generate --model mlx-community/MiniMax-M2.1-6bit ...
```

### 2. 调整生成参数

```python
from mlx_lm.sample_utils import make_sampler

# 更快但可能质量略低
sampler = make_sampler(temp=0.5, top_p=0.9)

# 更有创意但可能不够精确
sampler = make_sampler(temp=0.9, top_p=0.95)

# 平衡（推荐）
sampler = make_sampler(temp=0.7, top_p=0.9)
```

### 3. 优化VRAM（可选，高级）

```bash
# 检查当前VRAM限制
sysctl iogpu.wired_limit_mb

# 增加VRAM限制到448GB（推荐）
sudo sysctl iogpu.wired_limit_mb=458752

# 运行模型
mlx_lm.generate --model mlx-community/MiniMax-M2.1-4bit ...
```

### 4. 预加载模型（避免重复加载）

对于频繁使用，使用Python脚本保持模型在内存中：

```python
# 一次加载，多次使用
model, tokenizer = load("mlx-community/MiniMax-M2.1-4bit")

# 多次生成不需要重新加载
for prompt in prompts:
    response = generate(model, tokenizer, prompt=prompt)
```

---

## 故障排除

### 问题1：模型下载失败

**症状：** `Connection timeout` 或下载中断

**解决方案：**

```bash
# 方法1：使用镜像（如果在中国）
export HF_ENDPOINT=https://hf-mirror.com
mlx_lm.generate --model mlx-community/MiniMax-M2.1-4bit ...

# 方法2：手动下载
pip install huggingface-hub
huggingface-cli download mlx-community/MiniMax-M2.1-4bit \
  --local-dir ~/models/MiniMax-M2.1-4bit \
  --resume-download

# 然后使用本地路径
mlx_lm.generate --model ~/models/MiniMax-M2.1-4bit ...
```

### 问题2：内存不足

**症状：** `Out of memory` 或系统卡死

**解决方案：**

```bash
# 1. 使用更小的模型
mlx_lm.generate --model mlx-community/MiniMax-M2.1-4bit ...  # 而不是8-bit

# 2. 减少max_tokens
mlx_lm.generate --model ... --max-tokens 100  # 而不是2000

# 3. 关闭其他应用程序
# 在Activity Monitor中关闭不需要的应用

# 4. 重启Mac清理内存
sudo reboot
```

### 问题3：生成速度慢

**症状：** TPS < 10

**诊断：**

```bash
# 检查是否使用了Metal GPU
python -c "import mlx.core as mx; print(mx.metal.is_available())"

# 检查内存压力
memory_pressure

# 监控GPU使用
sudo powermetrics --samplers gpu_power -i 1000
```

**解决方案：**

1. 确保MLX使用Metal：应该是自动的
2. 优化VRAM限制（见上文）
3. 使用4-bit模型
4. 重启Mac

### 问题4：生成结果质量差

**症状：** 输出不连贯或重复

**解决方案：**

```bash
# 调整temperature
mlx_lm.generate --model ... --temp 0.7  # 默认

# 更确定性（质量更稳定）
mlx_lm.generate --model ... --temp 0.5

# 更有创意（但可能不稳定）
mlx_lm.generate --model ... --temp 0.9
```

或在Python中：

```python
from mlx_lm.sample_utils import make_sampler

# 更稳定的输出
sampler = make_sampler(temp=0.5, top_p=0.9)

# 或者使用不同的采样策略
sampler = make_sampler(temp=0.7, top_p=0.95, top_k=50)
```

### 问题5：ImportError

**症状：** `ModuleNotFoundError: No module named 'mlx'`

**解决方案：**

```bash
# 确保虚拟环境激活
source venv/bin/activate

# 重新安装MLX
pip install --upgrade mlx mlx-lm

# 验证
python -c "import mlx; import mlx_lm; print('OK')"
```

### 问题6：模型文件损坏

**症状：** `Error loading model` 或 `Invalid file`

**解决方案：**

```bash
# 清理缓存
rm -rf ~/.cache/huggingface/hub/models--mlx-community--MiniMax-M2.1-4bit

# 重新下载
mlx_lm.generate --model mlx-community/MiniMax-M2.1-4bit ...
```

---

## 常见问题 FAQ

### Q1: 首次下载需要多长时间？

**A:** 取决于网速和模型大小：
- 4-bit (~120GB): 1-3小时（100Mbps网络）
- 8-bit (~240GB): 2-6小时

### Q2: 模型存储在哪里？

**A:** 默认位置：
```bash
~/.cache/huggingface/hub/
```

查看占用空间：
```bash
du -sh ~/.cache/huggingface/hub/
```

清理缓存：
```bash
rm -rf ~/.cache/huggingface/hub/*
```

### Q3: 可以同时运行多个模型吗？

**A:** 可以，但取决于内存：
- 512GB系统：可以同时加载4-bit (135GB) + 8-bit (252GB)
- 建议：一次运行一个模型，避免内存压力

### Q4: 如何离线使用？

**A:** 下载后即可离线使用：

```bash
# 在线时下载
mlx_lm.generate --model mlx-community/MiniMax-M2.1-4bit --prompt "test"

# 之后可以断网使用
# 模型已缓存在 ~/.cache/huggingface/hub/
```

### Q5: 如何更新MLX？

**A:**
```bash
source venv/bin/activate
pip install --upgrade mlx mlx-lm
```

### Q6: 支持哪些语言？

**A:** MiniMax M2.1主要优化中文和英文，但也支持其他语言。

---

## 性能参考

**你的系统（M3 Ultra 512GB）预期性能：**

| 模型 | 加载时间 | 内存占用 | TPS | TTFT |
|------|---------|---------|-----|------|
| 4-bit | ~21秒 | 135 GB | 45.73 | 67ms |
| 6-bit | ~30秒 | 192 GB | 41.83 | 75ms |
| 8-bit | ~28秒 | 252 GB | 33.04 | 95ms |

---

## 下一步

1. ✅ **开始使用**：运行4-bit模型测试
2. 📊 **性能测试**：使用benchmark脚本
3. 🔧 **优化配置**：调整VRAM和参数
4. 🚀 **生产部署**：构建应用或API

---

## 相关资源

- **项目根目录：** 本项目所在目录
- **测试脚本：** `scripts/benchmark_mlx.py`
- **性能结果：** `docs/benchmark-results.md`
- **测试计划：** `docs/test-plan.md`

---

## 获取帮助

如果遇到问题：

1. 查看本文档的"故障排除"部分
2. 查看 `docs/benchmark-results.md` 的已知问题
3. 检查 MLX GitHub Issues: https://github.com/ml-explore/mlx
4. 检查 mlx-lm GitHub: https://github.com/ml-explore/mlx-lm

---

**祝使用愉快！🚀**
