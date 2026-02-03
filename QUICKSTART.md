# 快速开始 - 5分钟运行MLX

> 最快的方式在你的Mac上运行MiniMax M2.1

## 🚀 超快开始（3步）

### 1. 激活环境

```bash
cd /Users/jacky/projects/llm-mac-512
source venv/bin/activate
```

### 2. 快速测试

```bash
# 运行快速测试（会自动下载模型）
python scripts/quick_test.py
```

**首次运行会下载~120GB模型，需要20-60分钟**

### 3. 开始对话

```bash
# 启动交互式对话
python scripts/chat_mlx.py
```

就这么简单！🎉

---

## 📝 详细步骤

### 检查环境

```bash
# 确认在项目目录
pwd
# 应该显示: /Users/jacky/projects/llm-mac-512

# 激活虚拟环境
source venv/bin/activate

# 验证Python版本
python --version
# 应该是: Python 3.12.x
```

### 运行测试

```bash
# 快速测试（推荐先做）
python scripts/quick_test.py

# 如果测试通过，开始对话
python scripts/chat_mlx.py
```

### 常用命令

```bash
# 4-bit模型（默认，最快）
python scripts/chat_mlx.py

# 8-bit模型（质量更好）
python scripts/chat_mlx.py --model mlx-community/MiniMax-M2.1-8bit

# 6-bit模型（平衡）
python scripts/chat_mlx.py --model mlx-community/MiniMax-M2.1-6bit

# 调整temperature（更有创意）
python scripts/chat_mlx.py --temp 0.9

# 增加最大tokens
python scripts/chat_mlx.py --max-tokens 1000
```

---

## 💡 使用示例

### 示例1：对话

```
你: 请用一句话解释量子计算
助手: 量子计算是利用量子力学原理，使用量子比特进行并行计算，从而在特定问题上实现指数级加速的计算方式。
[23 tokens | 0.52s | 44.2 tokens/s]
```

### 示例2：代码生成

```
你: 写一个Python快速排序算法
助手: [生成完整的快速排序代码]
```

### 示例3：问答

```
你: 什么是深度学习？
助手: [详细解释]
```

---

## 🎯 命令行一键运行

如果你只想快速生成一次文本：

```bash
# 使用mlx_lm命令行工具
mlx_lm.generate \
  --model mlx-community/MiniMax-M2.1-4bit \
  --prompt "请用一句话解释人工智能" \
  --max-tokens 100
```

---

## 🔧 常见问题

### Q: 模型下载很慢？

**A:** 首次下载需要时间（120GB），请耐心等待。如果中断，重新运行命令会继续下载。

### Q: 出现 "No module named 'mlx'"？

**A:**
```bash
# 确保激活了虚拟环境
source venv/bin/activate

# 重新安装
pip install --upgrade mlx mlx-lm
```

### Q: 生成速度很慢（<10 TPS）？

**A:**
```bash
# 使用4-bit模型
python scripts/chat_mlx.py --model mlx-community/MiniMax-M2.1-4bit

# 或者优化VRAM（高级）
sudo sysctl iogpu.wired_limit_mb=458752
```

### Q: 如何退出对话？

**A:** 输入 `quit`、`exit` 或 `q`，或按 `Ctrl+C`

---

## 📚 更多资源

- **完整文档:** [docs/mlx-local-setup.md](docs/mlx-local-setup.md)
- **性能测试:** `python scripts/benchmark_mlx.py --model mlx-community/MiniMax-M2.1-4bit`
- **测试结果:** [docs/benchmark-results.md](docs/benchmark-results.md)

---

## 🎓 进阶使用

### 使用Python脚本

创建 `my_test.py`：

```python
from mlx_lm import load, generate

# 加载模型
model, tokenizer = load("mlx-community/MiniMax-M2.1-4bit")

# 生成
response = generate(
    model,
    tokenizer,
    prompt="写一个Python冒泡排序",
    max_tokens=300
)

print(response)
```

运行：
```bash
python my_test.py
```

### 性能优化

```bash
# 1. 优化VRAM（可选）
sudo sysctl iogpu.wired_limit_mb=458752

# 2. 运行优化后的测试
python scripts/quick_test.py

# 3. 比较性能提升
```

---

## ✅ 下一步

1. ✅ 运行 `quick_test.py` 验证环境
2. ✅ 使用 `chat_mlx.py` 进行对话测试
3. 📊 运行完整benchmark：`python scripts/benchmark_mlx.py`
4. 🔧 尝试不同模型版本（4-bit/6-bit/8-bit）
5. 📖 阅读完整文档：`docs/mlx-local-setup.md`

---

**准备好了吗？运行第一条命令：**

```bash
source venv/bin/activate && python scripts/quick_test.py
```

🚀 开始你的MLX之旅！
