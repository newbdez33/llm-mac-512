# LM Studio 快速开始 - 5分钟运行 MiniMax M2.1

> 最简单的方式在 Mac 上运行大型语言模型

## 🚀 3 步开始

> **选择你喜欢的方式:** [GUI 图形界面](#gui-方式) | [CLI 命令行](#cli-方式-推荐)

---

## CLI 方式 ⭐ 推荐

### 3 个命令完成

```bash
# 1. 安装 LM Studio
brew install --cask lm-studio

# 2. 下载模型 (自动下载 ~120GB)
lms download mlx-community/MiniMax-M2.1-4bit

# 3. 启动服务器
lms server start mlx-community/MiniMax-M2.1-4bit --port 1234
```

**完成！**服务器运行在 `http://localhost:1234`

### 快速测试

```bash
# 测试 API
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "你好"}], "max_tokens": 100}'

# 查看服务器状态
lms server status

# 查看日志
lms server logs
```

---

## GUI 方式

### 步骤 1: 下载 LM Studio (2 分钟)

```bash
# 打开浏览器下载
open https://lmstudio.ai/download

# 或直接下载 dmg
curl -L https://lmstudio.ai/download -o LMStudio.dmg
```

**安装:**
1. 打开下载的 `.dmg` 文件
2. 拖拽 LM Studio 到 Applications 文件夹
3. 从 Launchpad 或 Applications 打开 LM Studio

### 步骤 2: 下载模型 (30-60 分钟)

**在 LM Studio 界面中:**

1. 点击左侧 **🔍 Search** 图标
2. 搜索框输入: `MiniMax-M2.1`
3. 找到并下载 **推荐模型**:

   **推荐 - MLX 4-bit (最快):**
   ```
   mlx-community/MiniMax-M2.1-4bit
   大小: ~120GB
   速度: 45 TPS
   ```

   **备选 - GGUF Q4 (通用):**
   ```
   unsloth/MiniMax-M2.1-GGUF:Q4_K_M
   大小: ~138GB
   速度: 40 TPS
   ```

4. 点击 **Download** 按钮
5. 等待下载完成（进度条会显示）

**首次下载需要时间：**
- 120GB 模型约需 30-60 分钟
- 取决于网络速度
- 可以暂停后继续下载

### 步骤 3: 启动并测试 (2 分钟)

**方式 A: 聊天界面 (最简单)**

1. 点击左侧 **💬 Chat** 图标
2. 顶部选择刚下载的模型
3. 等待模型加载 (约 20 秒)
4. 在底部输入框输入消息，比如:
   ```
   请用一句话解释量子计算
   ```
5. 按 Enter，查看回复！

**方式 B: API 服务器 (用于 OpenClaw)**

1. 点击左侧 **⚡ Local Server** 图标
2. 选择模型 (如果未加载)
3. 点击 **Start Server** 🚀
4. 等待服务器启动，看到:
   ```
   ✅ Server running on http://localhost:1234
   ```

**测试 API:**
```bash
# 打开终端，运行测试
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100
  }'
```

完成！🎉

---

## 📱 使用示例

### 示例 1: 简单对话

```
你: 什么是深度学习？

助手: 深度学习是机器学习的一个分支，它使用多层神经网络来学习数据的层次化表示，从而实现对复杂模式的识别和预测。

⚡ 23 tokens | 0.52s | 44.2 tokens/s
```

### 示例 2: 代码生成

```
你: 写一个 Python 快速排序算法

助手: [生成完整的快速排序代码，包含注释和示例]

⚡ 156 tokens | 3.4s | 45.9 tokens/s
```

### 示例 3: 推理任务

```
你: 如果我有 5 个苹果，给了 2 个给朋友，又买了 3 个，现在有多少个？

助手: <think>
初始: 5 个苹果
给出: -2 个
购买: +3 个
计算: 5 - 2 + 3 = 6
</think>

你现在有 6 个苹果。

⚡ 45 tokens | 1.0s | 45.0 tokens/s
```

---

## 🔌 配置 OpenClaw

### 快速配置 (3 个命令)

```bash
# 1. 设置 API 端点
export OPENAI_API_BASE="http://localhost:1234/v1"
export OPENAI_API_KEY="lm-studio"

# 2. 测试连接
openclaw models list

# 3. 开始使用
openclaw chat "请介绍量子计算"
```

### 永久配置

编辑 `~/.openclaw/config.yaml`:

```yaml
llm:
  provider: openai
  base_url: http://localhost:1234/v1
  api_key: lm-studio
  model: minimax-m2.1
  temperature: 0.7
  max_tokens: 4000
```

然后重启 OpenClaw:

```bash
openclaw restart
```

---

## ⚙️ 常用设置

### 推荐配置 (LM Studio 界面)

**GPU 设置:**
```
GPU Offload: Max
GPU Layers: -1 (全部)
Metal: ✅ Enabled
```

**服务器设置:**
```
Port: 1234
CORS: ✅ Enabled
Auto-start: ✅ (可选)
Require Auth: ❌ (本地不需要)
```

**生成参数:**
```
Temperature: 0.7
Top P: 0.95
Max Tokens: 4000
Context Length: 32768
```

---

## 🎯 快捷键

| 快捷键 | 功能 |
|-------|------|
| `Cmd+K` | 新对话 |
| `Cmd+,` | 设置 |
| `Cmd+Shift+L` | 切换模型 |
| `Cmd+Enter` | 发送消息 |
| `Esc` | 停止生成 |

---

## 🔧 故障排除

### Q: 模型下载很慢？

**A:**
- 耐心等待，120GB 需要时间
- 可以暂停后继续
- 检查网络连接
- 考虑使用 VPN 或镜像

### Q: 模型不显示？

**A:**
```bash
# 1. 检查下载完成
ls ~/.lmstudio/models/

# 2. 重启 LM Studio
killall "LM Studio"
open -a "LM Studio"

# 3. 检查磁盘空间
df -h
```

### Q: 生成速度慢？

**A:**
1. 确保 GPU Offload = Max
2. 关闭其他应用 (Chrome, Docker)
3. 使用 4-bit 模型 (最快)
4. 检查内存压力:
   ```bash
   vm_stat | grep "Pages free"
   ```

### Q: API 连接失败？

**A:**
```bash
# 1. 确认服务器运行
curl http://localhost:1234/v1/models

# 2. 检查端口
lsof -i :1234

# 3. 重启服务器
# LM Studio -> Local Server -> Stop -> Start
```

### Q: 内存不足？

**A:**
- 使用 4-bit 模型 (~135GB)
- 关闭其他应用
- 重启 Mac 释放内存
- 检查: `Activity Monitor -> Memory`

---

## 📊 性能参考

### M3 Ultra 512GB 预期性能

| 模型版本 | 内存 | TPS | TTFT | 推荐用途 |
|---------|------|-----|------|---------|
| MLX 4-bit | 135GB | 45.7 | 67ms | ⭐ 日常对话/编程 |
| MLX 8-bit | 252GB | 33.0 | 95ms | 📝 文档生成 |
| GGUF Q4 | 140GB | ~40 | ~80ms | 🔄 通用 |
| GGUF Q8 | 250GB | ~30 | ~100ms | 🎯 高质量输出 |

**术语解释:**
- **TPS**: Tokens Per Second (每秒生成的 token 数)
- **TTFT**: Time To First Token (首个 token 延迟)
- **内存**: 运行时占用的系统内存

---

## 🚀 进阶使用

### Python 脚本调用

```python
import openai

# 配置 LM Studio
openai.api_base = "http://localhost:1234/v1"
openai.api_key = "lm-studio"

# 发送请求
response = openai.ChatCompletion.create(
    model="minimax-m2.1",
    messages=[
        {"role": "system", "content": "你是一个有帮助的助手"},
        {"role": "user", "content": "解释量子纠缠"}
    ],
    max_tokens=500,
    temperature=0.7
)

print(response.choices[0].message.content)
```

### 命令行快速测试

```bash
# 测试脚本
cat > test_lmstudio.sh << 'EOF'
#!/bin/bash
curl -s http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"messages\": [{\"role\": \"user\", \"content\": \"$1\"}],
    \"max_tokens\": 500
  }" | python3 -c "import sys, json; print(json.load(sys.stdin)['choices'][0]['message']['content'])"
EOF

chmod +x test_lmstudio.sh

# 使用
./test_lmstudio.sh "什么是量子计算？"
```

### 批量处理

```python
# batch_process.py
import openai
openai.api_base = "http://localhost:1234/v1"

questions = [
    "什么是机器学习？",
    "深度学习的应用有哪些？",
    "如何开始学习 AI？"
]

for q in questions:
    response = openai.ChatCompletion.create(
        model="minimax-m2.1",
        messages=[{"role": "user", "content": q}],
        max_tokens=200
    )
    print(f"Q: {q}")
    print(f"A: {response.choices[0].message.content}\n")
```

---

## 📚 更多资源

**文档:**
- 完整设置指南: [docs/lm-studio-setup.md](docs/lm-studio-setup.md)
- OpenClaw 集成: [docs/openclaw-setup.md](docs/openclaw-setup.md)
- 性能测试结果: [docs/benchmark-results.md](docs/benchmark-results.md)

**链接:**
- LM Studio 官网: https://lmstudio.ai
- 官方文档: https://lmstudio.ai/docs
- Discord 社区: https://discord.gg/lmstudio
- 模型仓库: https://huggingface.co/mlx-community

**备选方案:**
- 如果你偏好命令行: [MLX 方式](QUICKSTART.md)
- 高级测试和优化: [Test Plan](docs/test-plan.md)

---

## ✅ 检查清单

完成以下步骤确保一切正常：

- [ ] LM Studio 已安装并可以打开
- [ ] 模型已下载完成 (检查 ~/.lmstudio/models/)
- [ ] 模型可以在 Chat 界面加载
- [ ] 可以与模型对话并收到回复
- [ ] API 服务器可以启动 (http://localhost:1234)
- [ ] curl 测试成功返回响应
- [ ] OpenClaw 配置完成 (可选)
- [ ] OpenClaw 可以调用本地模型 (可选)

---

## 📋 LMS CLI 快速参考

```bash
# 模型操作
lms models list                    # 列出本地模型
lms models search minimax          # 搜索模型
lms download <model-id>            # 下载模型
lms models delete <model-id>       # 删除模型

# 服务器操作
lms server start                   # 启动 (使用最近的模型)
lms server start <model> --port 1234  # 指定模型和端口
lms server start --detach          # 后台运行
lms server stop                    # 停止服务器
lms server status                  # 查看状态
lms server logs                    # 查看日志
lms server restart                 # 重启

# 配置
lms config list                    # 列出配置
lms config set server.port 1234    # 设置端口
lms config set gpu.layers -1       # 设置 GPU layers

# 工具
lms version                        # 版本信息
lms doctor                         # 诊断问题
```

---

**准备好了吗？**

**CLI 用户:**
```bash
brew install --cask lm-studio && lms download mlx-community/MiniMax-M2.1-4bit
```

**GUI 用户:**
```bash
open https://lmstudio.ai/download
```

🎉 开始你的本地 AI 之旅！
