# LM Studio 完整设置指南

> 使用 LM Studio 在 Mac 上本地运行 MiniMax M2.1 模型

## 目录

- [为什么选择 LM Studio](#为什么选择-lm-studio)
- [快速开始](#快速开始)
- [详细安装步骤](#详细安装步骤)
- [模型下载与加载](#模型下载与加载)
- [启动 API 服务器](#启动-api-服务器)
- [OpenClaw 集成](#openclaw-集成)
- [性能优化](#性能优化)
- [故障排除](#故障排除)

## 为什么选择 LM Studio

✅ **优势**
- 🖥️ **图形界面**: 无需命令行，易于使用
- 🚀 **开箱即用**: 自动处理依赖和配置
- 🔌 **OpenAI 兼容**: 原生提供 OpenAI API
- 💪 **高性能**: 针对 Apple Silicon 优化
- 📊 **实时监控**: GPU/CPU/内存使用可视化
- 🔄 **模型管理**: 轻松切换不同模型

📉 **对比 MLX**
- LM Studio: GUI 操作，更友好
- MLX: 命令行操作，需要 Python 环境

## 快速开始

### 3 步运行起来 (GUI 方式)

```bash
# 1. 下载并安装 LM Studio
open https://lmstudio.ai

# 2. 在 LM Studio 中下载模型
# 搜索: mlx-community/MiniMax-M2.1-8bit
# 或使用: unsloth/MiniMax-M2.1-GGUF (Q4_K_M)

# 3. 启动本地服务器
# 在 LM Studio: Local Server -> Start Server
```

### 3 步运行起来 (CLI 方式) ⭐ 推荐

```bash
# 1. 安装 LM Studio (如果未安装)
brew install --cask lm-studio

# 2. 下载模型
lms download mlx-community/MiniMax-M2.1-4bit

# 3. 启动 API 服务器
lms server start mlx-community/MiniMax-M2.1-4bit --port 1234
```

完成！现在可以在 `http://localhost:1234` 使用 API。

## 详细安装步骤

### 1. 安装 LM Studio

**下载:**
- 官网: https://lmstudio.ai
- 或直接下载: https://lmstudio.ai/download

**安装:**
```bash
# 下载 .dmg 文件后
1. 打开 LMStudio.dmg
2. 拖拽到 Applications 文件夹
3. 打开 LM Studio
4. 允许必要的系统权限
```

**首次启动:**
- 同意许可协议
- 可选：登录账号（用于同步设置）
- 完成初始设置向导

### 2. 配置 LM Studio

**GUI 方式:**

1. **打开设置 (⚙️)**
   - `File > Preferences` 或 `Cmd+,`

2. **GPU 设置**
   ```
   GPU Offload: Auto (推荐)
   GPU Layers: Max (或根据内存调整)
   Context Length: 32768 (或更高)
   ```

3. **API 服务器设置**
   ```
   Port: 1234 (默认)
   CORS: Enabled (如果需要网页访问)
   API Key: 可选（本地使用不需要）
   ```

**CLI 方式:**

```bash
# 查看当前配置
lms config list

# 设置 GPU layers
lms config set gpu.layers -1  # -1 = 全部

# 设置默认端口
lms config set server.port 1234

# 启用 CORS
lms config set server.cors true
```

## 模型下载与加载

### 推荐模型

#### 选项 1: MLX 格式 (推荐 for Mac)

```
mlx-community/MiniMax-M2.1-4bit  (~120GB) ⭐ 推荐
mlx-community/MiniMax-M2.1-8bit  (~240GB) - 质量更好
```

#### 选项 2: GGUF 格式

```
unsloth/MiniMax-M2.1-GGUF:Q4_K_M  (~138GB)
unsloth/MiniMax-M2.1-GGUF:Q8_0    (~243GB)
```

### 在 LM Studio 中下载模型

**方法 1: CLI 下载** ⭐ 推荐

```bash
# 下载 4-bit 模型 (最快)
lms download mlx-community/MiniMax-M2.1-4bit

# 下载 8-bit 模型 (质量更好)
lms download mlx-community/MiniMax-M2.1-8bit

# 下载 GGUF 版本
lms download unsloth/MiniMax-M2.1-GGUF:Q4_K_M

# 查看下载进度
lms download list

# 列出已下载的模型
lms models list
```

**方法 2: GUI 搜索下载**

1. 点击左侧 **🔍 Search** 标签
2. 搜索栏输入: `MiniMax-M2.1`
3. 找到模型:
   - `mlx-community/MiniMax-M2.1-4bit` (Mac 推荐)
   - `unsloth/MiniMax-M2.1-GGUF` (通用)
4. 点击 **Download**
5. 等待下载完成（120-240GB，需要 30-120 分钟）

**方法 3: 使用已下载的模型**

如果你已经通过其他方式下载了模型（如 MLX 或 Hugging Face CLI），可以创建符号链接：

```bash
# MLX 模型 -> LM Studio
ln -s ~/.cache/huggingface/hub/models--mlx-community--MiniMax-M2.1-8bit/snapshots/* \
      ~/.lmstudio/models/mlx-community/MiniMax-M2.1-8bit/

# GGUF 模型 -> LM Studio
ln -s /path/to/MiniMax-M2.1-Q4_K_M.gguf \
      ~/.lmstudio/models/unsloth/MiniMax-M2.1-GGUF/
```

重启 LM Studio 后，模型会出现在列表中。

### 加载模型

1. 点击左侧 **💬 Chat** 标签
2. 点击顶部模型选择器
3. 选择 `MiniMax-M2.1-4bit` (或其他版本)
4. 等待模型加载（首次加载需要 20-30 秒）

**加载成功标志:**
- 底部显示 ✅ "Model loaded"
- GPU/CPU 使用率出现在状态栏
- 可以在聊天框输入消息

## 启动 API 服务器

### CLI 方式 ⭐ 推荐

```bash
# 启动服务器 (自动选择最近使用的模型)
lms server start

# 启动服务器并指定模型
lms server start mlx-community/MiniMax-M2.1-4bit

# 自定义端口
lms server start --port 8080

# 后台运行
lms server start --detach

# 查看服务器状态
lms server status

# 停止服务器
lms server stop

# 查看日志
lms server logs
```

**高级选项:**

```bash
# 完整命令
lms server start \
  --model mlx-community/MiniMax-M2.1-4bit \
  --port 1234 \
  --host 0.0.0.0 \
  --cors true \
  --gpu-layers -1 \
  --ctx-size 32768
```

### GUI 方式

1. 点击左侧 **⚡ Local Server** 标签
2. 选择已加载的模型
3. 配置服务器:
   ```
   Port: 1234
   CORS: ✅ Enabled
   Auto-start: ✅ (可选)
   ```
4. 点击 **Start Server** 🚀

**服务器启动后:**
```
✅ Server running on http://localhost:1234
📡 Endpoints available:
   • /v1/models
   • /v1/chat/completions
   • /v1/completions
```

### 命令行测试

```bash
# 健康检查
curl http://localhost:1234/v1/models

# 测试对话
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "minimax-m2.1",
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

### Python 测试

```python
import openai

openai.api_base = "http://localhost:1234/v1"
openai.api_key = "lm-studio"  # 任意值

response = openai.ChatCompletion.create(
    model="minimax-m2.1",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=100
)

print(response.choices[0].message.content)
```

## OpenClaw 集成

### 配置 OpenClaw

**方法 1: 环境变量**

```bash
export OPENAI_API_BASE="http://localhost:1234/v1"
export OPENAI_API_KEY="lm-studio"
```

**方法 2: 配置文件** (推荐)

编辑 `~/.openclaw/openclaw.json`:

```json
{
  "models": {
    "providers": {
      "lmstudio": {
        "baseUrl": "http://localhost:1234/v1",
        "api": "openai-completions",
        "apiKey": "lm-studio",
        "models": [
          {
            "id": "minimax-m2.1",
            "name": "MiniMax M2.1 (LM Studio)",
            "reasoning": true,
            "contextWindow": 200000,
            "maxTokens": 8192,
            "inputPricePerToken": 0,
            "outputPricePerToken": 0
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "lmstudio/minimax-m2.1"
      }
    }
  }
}
```

**方法 3: config.yaml**

如果使用 YAML 配置:

```yaml
llm:
  provider: openai
  base_url: http://localhost:1234/v1
  api_key: lm-studio
  model: minimax-m2.1
  temperature: 0.7
  max_tokens: 4000
```

### 重启 OpenClaw

```bash
# 重启 gateway
openclaw gateway restart

# 或重启整个 OpenClaw
openclaw restart
```

### 测试集成

```bash
# 使用 OpenClaw CLI
openclaw chat "请介绍一下量子计算"

# 检查模型状态
openclaw models list
```

## 性能优化

### GPU 配置

**最大化 GPU 使用:**

1. LM Studio 设置:
   ```
   GPU Offload: Max
   GPU Layers: -1 (全部)
   Metal: Enabled
   ```

2. 关闭其他应用:
   - 释放内存和 GPU
   - 提升推理速度

### 内存优化

**512GB Mac 推荐配置:**

| 模型版本 | 内存占用 | 推荐 GPU Layers | 预期 TPS |
|---------|---------|----------------|---------|
| 4-bit   | ~135GB  | Max (-1)       | 40-45   |
| 8-bit   | ~240GB  | Max (-1)       | 30-35   |
| Q4_K_M  | ~140GB  | Max (-1)       | 35-40   |
| Q8_0    | ~250GB  | Max (-1)       | 28-33   |

**调整系统 VRAM 限制:**

```bash
# 查看当前限制
sysctl iogpu.wired_limit_mb

# 增加到 448GB (如果需要)
sudo sysctl iogpu.wired_limit_mb=458752
```

### 推理参数调优

**响应速度优先:**
```json
{
  "temperature": 0.3,
  "top_p": 0.9,
  "max_tokens": 1000,
  "stream": true
}
```

**质量优先:**
```json
{
  "temperature": 0.7,
  "top_p": 0.95,
  "max_tokens": 4000,
  "stream": true
}
```

## 故障排除

### 模型未显示

**问题:** 下载的模型不在列表中

**解决:**
```bash
# 1. 检查模型路径
ls -la ~/.lmstudio/models/

# 2. 检查权限
chmod -R 755 ~/.lmstudio/models/

# 3. 重启 LM Studio
killall "LM Studio" && open -a "LM Studio"
```

### 服务器启动失败

**问题:** "Port 1234 already in use"

**解决:**
```bash
# 查找占用端口的进程
lsof -i :1234

# 杀死进程
kill -9 <PID>

# 或使用其他端口
# LM Studio -> Settings -> Server Port: 8080
```

### 内存不足 (OOM)

**问题:** "Out of memory" 或模型加载失败

**解决:**
1. 使用更小的模型 (4-bit 而非 8-bit)
2. 减少 GPU Layers
3. 关闭其他应用
4. 重启 Mac 清理内存

```bash
# 检查内存使用
vm_stat

# 清理内存 (重启)
sudo purge
```

### 响应速度慢 (<10 TPS)

**问题:** 生成速度很慢

**诊断:**
```bash
# 1. 检查 GPU 使用
# 在 LM Studio 底部查看 GPU 使用率

# 2. 检查系统资源
Activity Monitor -> GPU -> % Use
```

**解决:**
1. 确保 GPU Offload = Max
2. 关闭后台应用 (Chrome, Docker, etc.)
3. 使用更小的模型 (4-bit)
4. 减少 context length

### OpenClaw 连接失败

**问题:** OpenClaw 无法连接到 LM Studio

**检查:**
```bash
# 1. 服务器是否运行
curl http://localhost:1234/v1/models

# 2. 端口是否正确
cat ~/.openclaw/openclaw.json | grep baseUrl

# 3. 防火墙设置
# System Settings > Network > Firewall
```

**解决:**
1. 确保 LM Studio 服务器在运行
2. 检查 OpenClaw 配置中的端口
3. 重启两个服务

## LMS CLI 命令参考

### 常用命令

```bash
# 模型管理
lms models list              # 列出本地模型
lms models search minimax    # 搜索模型
lms download <model-id>      # 下载模型
lms models delete <model-id> # 删除模型

# 服务器管理
lms server start             # 启动服务器
lms server start --detach    # 后台运行
lms server stop              # 停止服务器
lms server status            # 查看状态
lms server logs              # 查看日志
lms server restart           # 重启服务器

# 配置管理
lms config list              # 列出所有配置
lms config get <key>         # 获取配置值
lms config set <key> <value> # 设置配置
lms config reset             # 重置为默认

# 工具命令
lms version                  # 查看版本
lms update                   # 更新 LM Studio
lms doctor                   # 诊断问题
```

### 完整示例工作流

```bash
# 1. 搜索并下载模型
lms models search "MiniMax"
lms download mlx-community/MiniMax-M2.1-4bit

# 2. 配置服务器
lms config set server.port 1234
lms config set server.cors true
lms config set gpu.layers -1

# 3. 启动服务器 (后台)
lms server start mlx-community/MiniMax-M2.1-4bit --detach

# 4. 测试连接
curl http://localhost:1234/v1/models

# 5. 查看日志
lms server logs --tail 50

# 6. 停止服务器
lms server stop
```

### 环境变量

```bash
# LMS CLI 配置
export LMS_HOME="$HOME/.lmstudio"
export LMS_SERVER_PORT="1234"
export LMS_GPU_LAYERS="-1"

# 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export LMS_SERVER_PORT="1234"' >> ~/.zshrc
```

### 自动化脚本

创建 `start_lmstudio.sh`:

```bash
#!/bin/bash
# LM Studio 自动启动脚本

MODEL="mlx-community/MiniMax-M2.1-4bit"
PORT=1234

echo "🚀 启动 LM Studio 服务器..."

# 检查模型是否已下载
if ! lms models list | grep -q "$MODEL"; then
    echo "📥 下载模型: $MODEL"
    lms download "$MODEL"
fi

# 启动服务器
lms server start "$MODEL" \
    --port "$PORT" \
    --host 0.0.0.0 \
    --cors true \
    --gpu-layers -1 \
    --detach

echo "✅ 服务器运行在 http://localhost:$PORT"
echo "📊 查看日志: lms server logs"
echo "🛑 停止服务器: lms server stop"
```

使用:
```bash
chmod +x start_lmstudio.sh
./start_lmstudio.sh
```

## 高级功能

### 自定义 Chat Template

MiniMax M2.1 使用特殊的思考格式 `<think>...</think>`。可以在 LM Studio 中配置：

1. 打开模型设置 (⚙️)
2. 找到 "Chat Template"
3. 添加自定义模板（可选）

### API Key 保护

如果需要在网络上暴露 API：

1. LM Studio Settings:
   ```
   API Key: your-secret-key
   Require Authentication: ✅
   ```

2. OpenClaw 配置:
   ```json
   {
     "apiKey": "your-secret-key"
   }
   ```

### 多模型切换

LM Studio 支持加载多个模型并快速切换：

1. 下载多个模型版本
2. 在 Chat 或 Server 界面切换
3. OpenClaw 会自动适应当前模型

## 性能基准

### 在 M3 Ultra 512GB 上的表现

| 模型 | 加载时间 | 内存使用 | TPS | TTFT |
|------|---------|---------|-----|------|
| MLX 4-bit | 21s | 135GB | 45.7 | 67ms |
| MLX 8-bit | 28s | 252GB | 33.0 | 95ms |
| GGUF Q4_K_M | ~25s | 140GB | ~40 | ~80ms |
| GGUF Q8_0 | ~30s | 250GB | ~30 | ~100ms |

### 推荐配置

**交互式使用 (对话/编程):**
- 模型: `mlx-community/MiniMax-M2.1-4bit`
- 理由: 最快速度 (45 TPS)，低延迟 (67ms)

**批量处理 (文档生成/分析):**
- 模型: `mlx-community/MiniMax-M2.1-8bit`
- 理由: 更高质量，内存足够

## 资源链接

- **LM Studio 官网**: https://lmstudio.ai
- **文档**: https://lmstudio.ai/docs
- **Discord 社区**: https://discord.gg/lmstudio
- **模型仓库**: https://huggingface.co/mlx-community
- **GGUF 模型**: https://huggingface.co/unsloth/MiniMax-M2.1-GGUF

## 下一步

1. ✅ 安装 LM Studio
2. ✅ 下载并加载模型
3. ✅ 启动 API 服务器
4. ✅ 配置 OpenClaw
5. 📊 运行性能测试
6. 🚀 开始使用！

---

## 备选方案

如果你想使用命令行或需要更多控制，可以查看：
- **MLX 方式**: [docs/mlx-local-setup.md](mlx-local-setup.md)
- **llama.cpp 方式**: [docs/test-plan.md](test-plan.md)

---

**准备好了吗？** 下载 LM Studio 开始: https://lmstudio.ai
