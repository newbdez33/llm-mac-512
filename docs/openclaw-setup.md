# OpenClaw 本地 API 配置指南

> 使用本地 LLM 为 OpenClaw 提供 AI 能力

## 📋 目录

- [概述](#概述)
- [方式选择](#方式选择)
- [方式 1: LM Studio (推荐)](#方式-1-lm-studio-推荐)
- [方式 2: MLX (命令行)](#方式-2-mlx-命令行)
- [测试验证](#测试验证)
- [故障排除](#故障排除)

---

## 概述

本指南提供两种方式为 OpenClaw 配置本地 LLM API：

1. **LM Studio** (推荐): GUI + CLI，开箱即用
2. **MLX**: 命令行方式，更多控制

**架构：**
```
OpenClaw → 本地 API 服务器 → LLM (MiniMax M2.1)
```

---

## 方式选择

| 特性 | LM Studio | MLX |
|------|----------|-----|
| **安装难度** | ⭐ 简单 (GUI) | ⭐⭐ 中等 (命令行) |
| **使用方式** | GUI + CLI | 仅命令行 |
| **性能** | 🚀 优秀 | 🚀 优秀 |
| **灵活性** | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **推荐用户** | 所有用户 | 开发者/高级用户 |

**推荐:** 除非你需要高度自定义，否则选择 LM Studio。

---

## 方式 1: LM Studio (推荐)

### 前置要求

- LM Studio 已安装（如未安装，参考下方）

### 快速开始 (3 步)

```bash
# 1. 安装 LM Studio (如果未安装)
brew install --cask lm-studio

# 2. 下载模型
lms download mlx-community/MiniMax-M2.1-4bit

# 3. 启动 API 服务器
lms server start mlx-community/MiniMax-M2.1-4bit --port 1234
```

**完成！** API 运行在 `http://localhost:1234`

### 配置 OpenClaw

**方法 A: 环境变量 (最简单)**

```bash
export OPENAI_API_BASE="http://localhost:1234/v1"
export OPENAI_API_KEY="lm-studio"

# 添加到 ~/.bashrc 或 ~/.zshrc 永久生效
echo 'export OPENAI_API_BASE="http://localhost:1234/v1"' >> ~/.zshrc
echo 'export OPENAI_API_KEY="lm-studio"' >> ~/.zshrc
```

**方法 B: OpenClaw 配置文件 (推荐)**

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
            "name": "MiniMax M2.1 (Local)",
            "reasoning": true,
            "contextWindow": 200000,
            "maxTokens": 8192
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

**方法 C: config.yaml**

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

### 重启 OpenClaw

```bash
# 重启 gateway
openclaw gateway restart

# 或重启整个服务
openclaw restart
```

### 管理服务器

```bash
# 查看状态
lms server status

# 查看日志
lms server logs

# 停止服务器
lms server stop

# 后台运行
lms server start mlx-community/MiniMax-M2.1-4bit --detach
```

---

## 方式 2: MLX (命令行)

### 前置要求

```bash
# 1. 检查 Python 环境
python3 --version  # 需要 3.12+

# 2. 创建虚拟环境
cd ~/projects/llm-mac-512
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -U mlx-lm flask flask-cors psutil
```

完整安装指南: [docs/mlx-local-setup.md](./mlx-local-setup.md)

### 快速开始

#### 第1步：启动API服务器

```bash
# 进入项目目录
cd ~/projects/llm-mac-512
source venv/bin/activate

# 启动API服务器（使用4-bit模型，最快）
python scripts/api_server.py --model mlx-community/MiniMax-M2.1-4bit --port 8000
```

**首次运行会下载模型（~120GB），请耐心等待！**

服务器启动后会显示：
```
╔══════════════════════════════════════════════════════════╗
║         MLX MiniMax M2.1 API Server                      ║
║         OpenAI-Compatible API                            ║
╚══════════════════════════════════════════════════════════╝

✓ 模型加载完成！用时 21.25 秒

════════════════════════════════════════════════════════════
API 服务器配置
════════════════════════════════════════════════════════════
模型: mlx-community/MiniMax-M2.1-4bit
地址: http://127.0.0.1:8000
端点:
  • Chat: http://127.0.0.1:8000/v1/chat/completions
  • Completions: http://127.0.0.1:8000/v1/completions
  • Models: http://127.0.0.1:8000/v1/models
  • Health: http://127.0.0.1:8000/health

按 Ctrl+C 停止服务器
════════════════════════════════════════════════════════════
```

**首次运行会下载模型（~120GB），请耐心等待！**

服务器启动后会显示：
```
╔══════════════════════════════════════════════════════════╗
║         MLX MiniMax M2.1 API Server                      ║
╚══════════════════════════════════════════════════════════╝

✓ 模型加载完成！用时 21.25 秒

API 服务器配置
模型: mlx-community/MiniMax-M2.1-4bit
地址: http://127.0.0.1:8000
```

#### 第2步：配置 OpenClaw

**环境变量方式:**
```bash
export OPENAI_API_BASE="http://127.0.0.1:8000/v1"
export OPENAI_API_KEY="sk-dummy"
```

**配置文件方式 (config.yaml):**
```yaml
llm:
  provider: openai
  base_url: http://127.0.0.1:8000/v1
  api_key: sk-dummy
  model: mlx-community/MiniMax-M2.1-4bit
  temperature: 0.7
  max_tokens: 4000
```

#### 第3步：重启 OpenClaw

```bash
openclaw restart
```

---

## 测试验证

### 方法 1: curl 测试

**LM Studio (端口 1234):**
```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100
  }'
```

**MLX (端口 8000):**
```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100
  }'
```

### 方法 2: Python 测试

```python
import openai

# LM Studio
openai.api_base = "http://localhost:1234/v1"
openai.api_key = "lm-studio"

# 或 MLX
# openai.api_base = "http://127.0.0.1:8000/v1"
# openai.api_key = "sk-dummy"

response = openai.ChatCompletion.create(
    model="minimax-m2.1",
    messages=[{"role": "user", "content": "你好"}],
    max_tokens=100
)

print(response.choices[0].message.content)
```

### 方法 3: OpenClaw CLI

```bash
# 测试连接
openclaw models list

# 发送测试消息
openclaw chat "请介绍一下量子计算"

# 检查响应时间和质量
openclaw chat "写一个Python快速排序算法"
```

---

## 故障排除

### LM Studio 相关

**问题: 端口被占用**
```bash
# 查找占用进程
lsof -i :1234

# 使用其他端口
lms server start --port 8080
```

**问题: 模型未加载**
```bash
# 检查模型列表
lms models list

# 重启服务器
lms server restart
```

**问题: 连接超时**
```bash
# 检查服务器状态
lms server status

# 查看日志
lms server logs --tail 50
```

### MLX 相关

**问题: Flask 未安装**
```bash
source venv/bin/activate
pip install flask flask-cors
```

**问题: 模型下载失败**
```bash
# 手动下载
huggingface-cli download mlx-community/MiniMax-M2.1-4bit

# 或使用 LM Studio 下载，然后创建符号链接
ln -s ~/.lmstudio/models/mlx-community/MiniMax-M2.1-4bit \
      ~/.cache/huggingface/hub/
```

**问题: 端口被占用**
```bash
# 使用其他端口
python scripts/api_server.py --port 8080

# 更新 OpenClaw 配置中的端口
```

### OpenClaw 相关

**问题: OpenClaw 无法连接**

检查清单:
```bash
# 1. API 服务器是否运行
curl http://localhost:1234/health  # LM Studio
curl http://127.0.0.1:8000/health  # MLX

# 2. OpenClaw 配置是否正确
cat ~/.openclaw/config.yaml | grep base_url

# 3. 防火墙设置
# System Settings -> Network -> Firewall

# 4. 重启服务
openclaw restart
```

**问题: 响应速度慢**

优化建议:
1. 使用 4-bit 模型 (最快)
2. 关闭其他应用释放内存
3. 确保 GPU layers = -1 (全部)
4. 检查系统资源: `Activity Monitor`

**问题: 输出质量差**

调整参数:
```yaml
llm:
  temperature: 0.7    # 降低获得更确定的输出
  top_p: 0.95         # 调整采样策略
  max_tokens: 4000    # 增加允许更长输出
```

---

## 性能对比

### M3 Ultra 512GB 实测

| 方式 | 模型 | TPS | TTFT | 内存 |
|------|------|-----|------|------|
| LM Studio | MLX 4-bit | 45.7 | 67ms | 135GB |
| LM Studio | GGUF Q4 | ~40 | ~80ms | 140GB |
| MLX | 4-bit | 45.7 | 67ms | 135GB |
| MLX | 8-bit | 33.0 | 95ms | 252GB |

**结论:** LM Studio 和 MLX 性能相当，选择取决于偏好。

---

## 推荐配置

### 日常使用 (对话/编程)

**LM Studio:**
```bash
lms server start mlx-community/MiniMax-M2.1-4bit \
  --port 1234 \
  --gpu-layers -1
```

**OpenClaw config.yaml:**
```yaml
llm:
  provider: openai
  base_url: http://localhost:1234/v1
  model: minimax-m2.1
  temperature: 0.7
  max_tokens: 2000
```

### 高质量输出 (文档生成/分析)

**LM Studio:**
```bash
lms server start mlx-community/MiniMax-M2.1-8bit \
  --port 1234 \
  --gpu-layers -1
```

**OpenClaw config.yaml:**
```yaml
llm:
  provider: openai
  base_url: http://localhost:1234/v1
  model: minimax-m2.1
  temperature: 0.5
  max_tokens: 4000
```

---

## 相关资源

- **LM Studio 完整设置**: [docs/lm-studio-setup.md](./lm-studio-setup.md)
- **MLX 完整设置**: [docs/mlx-local-setup.md](./mlx-local-setup.md)
- **快速开始指南**: [QUICKSTART-LMSTUDIO.md](../QUICKSTART-LMSTUDIO.md)
- **性能测试结果**: [docs/benchmark-results.md](./benchmark-results.md)

---

**准备好了吗？** 选择你喜欢的方式开始配置！

### 第2步：验证API工作

打开**新终端**，测试API：

```bash
# 测试健康检查
curl http://127.0.0.1:8000/health

# 测试chat API
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mlx-community/MiniMax-M2.1-4bit",
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100
  }'
```

### 第3步：配置OpenClaw

#### 方式A：环境变量（推荐）

```bash
# 设置环境变量
export OPENAI_API_BASE="http://127.0.0.1:8000/v1"
export OPENAI_API_KEY="sk-dummy"  # 本地API不需要真实key

# 启动OpenClaw
openclaw
```

#### 方式B：配置文件

编辑OpenClaw配置文件（通常在 `~/.openclaw/config.yaml` 或类似位置）：

```yaml
llm:
  provider: openai
  base_url: http://127.0.0.1:8000/v1
  api_key: sk-dummy  # 本地API不需要真实key
  model: mlx-community/MiniMax-M2.1-4bit
```

#### 方式C：命令行参数

```bash
openclaw \
  --llm-provider openai \
  --llm-base-url http://127.0.0.1:8000/v1 \
  --llm-api-key sk-dummy \
  --llm-model mlx-community/MiniMax-M2.1-4bit
```

### 第4步：测试OpenClaw

在OpenClaw中测试：

```
> 你好，请介绍一下你自己
> 写一个Python快速排序算法
> 帮我分析一下当前目录的文件
```

---

## 详细配置

### API服务器选项

```bash
# 使用不同的模型
python scripts/api_server.py --model mlx-community/MiniMax-M2.1-8bit

# 更改端口
python scripts/api_server.py --port 8080

# 允许外部访问（谨慎使用！）
python scripts/api_server.py --host 0.0.0.0 --port 8000

# 完整示例
python scripts/api_server.py \
  --model mlx-community/MiniMax-M2.1-4bit \
  --host 127.0.0.1 \
  --port 8000
```

### OpenClaw配置示例

**完整的config.yaml示例：**

```yaml
# ~/.openclaw/config.yaml

# LLM配置
llm:
  provider: openai
  base_url: http://127.0.0.1:8000/v1
  api_key: sk-dummy
  model: mlx-community/MiniMax-M2.1-4bit
  temperature: 0.7
  max_tokens: 2000

# OpenClaw其他配置
agent:
  name: "MiniMax助手"
  personality: "helpful and concise"

# 工具配置
tools:
  enabled:
    - shell
    - file_system
    - web_search
```

---

## 测试验证

### 1. API健康检查

```bash
curl http://127.0.0.1:8000/health
```

期望输出：
```json
{
  "status": "ok",
  "model": "mlx-community/MiniMax-M2.1-4bit",
  "model_loaded": true
}
```

### 2. 测试Chat API

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mlx-community/MiniMax-M2.1-4bit",
    "messages": [
      {"role": "user", "content": "请用一句话解释量子计算"}
    ],
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

### 3. 测试Completions API

```bash
curl http://127.0.0.1:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mlx-community/MiniMax-M2.1-4bit",
    "prompt": "写一个Python冒泡排序：",
    "max_tokens": 300
  }'
```

### 4. 列出模型

```bash
curl http://127.0.0.1:8000/v1/models
```

### 5. Python测试脚本

创建 `test_api.py`：

```python
import requests

BASE_URL = "http://127.0.0.1:8000/v1"

# 测试chat
response = requests.post(
    f"{BASE_URL}/chat/completions",
    json={
        "model": "mlx-community/MiniMax-M2.1-4bit",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "max_tokens": 100
    }
)

print("Status:", response.status_code)
print("Response:", response.json())
```

运行：
```bash
python test_api.py
```

---

## 性能优化

### 1. 选择合适的模型

```bash
# 速度优先（推荐OpenClaw使用）
python scripts/api_server.py --model mlx-community/MiniMax-M2.1-4bit

# 质量优先
python scripts/api_server.py --model mlx-community/MiniMax-M2.1-8bit

# 平衡
python scripts/api_server.py --model mlx-community/MiniMax-M2.1-6bit
```

**推荐：** 对于OpenClaw，使用4-bit模型（45 TPS），响应快速。

### 2. 优化VRAM（可选）

```bash
# 增加GPU可用内存
sudo sysctl iogpu.wired_limit_mb=458752

# 启动API服务器
python scripts/api_server.py
```

### 3. 调整OpenClaw参数

```yaml
llm:
  temperature: 0.7      # 默认，平衡
  # temperature: 0.5   # 更确定性
  # temperature: 0.9   # 更有创意

  max_tokens: 1000      # 适中
  # max_tokens: 2000   # 长回复
  # max_tokens: 500    # 快速回复
```

---

## 故障排除

### 问题1：API服务器无法启动

**症状：** `ModuleNotFoundError: No module named 'flask'`

**解决：**
```bash
source venv/bin/activate
pip install flask flask-cors
```

### 问题2：OpenClaw连接失败

**症状：** `Connection refused` 或 `Connection timeout`

**检查清单：**
```bash
# 1. 确认API服务器正在运行
curl http://127.0.0.1:8000/health

# 2. 检查端口是否被占用
lsof -i :8000

# 3. 查看服务器日志
# 在运行api_server.py的终端查看错误信息

# 4. 验证OpenClaw配置
cat ~/.openclaw/config.yaml
```

### 问题3：响应很慢

**症状：** 响应时间 > 10秒

**解决：**
```bash
# 1. 使用4-bit模型
python scripts/api_server.py --model mlx-community/MiniMax-M2.1-4bit

# 2. 减少max_tokens
# 在OpenClaw配置中设置 max_tokens: 500

# 3. 检查系统资源
# 关闭其他占用内存的应用

# 4. 优化VRAM
sudo sysctl iogpu.wired_limit_mb=458752
```

### 问题4：模型输出质量差

**症状：** 回复不连贯或无意义

**解决：**

1. 调整temperature：
```yaml
llm:
  temperature: 0.7  # 尝试0.5-0.9之间
```

2. 使用更高bit的模型：
```bash
python scripts/api_server.py --model mlx-community/MiniMax-M2.1-8bit
```

### 问题5：API返回401错误

**症状：** `Unauthorized` 或 `Invalid API key`

**解决：**
本地API不需要真实key，使用任意值即可：
```bash
export OPENAI_API_KEY="sk-dummy"
```

或在OpenClaw配置中：
```yaml
llm:
  api_key: sk-anything-works
```

---

## 高级使用

### 1. 后台运行API服务器

```bash
# 使用nohup后台运行
nohup python scripts/api_server.py > api_server.log 2>&1 &

# 查看日志
tail -f api_server.log

# 停止服务器
pkill -f api_server.py
```

### 2. 使用systemd服务（macOS使用launchd）

创建 `~/Library/LaunchAgents/com.mlx.api.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mlx.api</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/jacky/projects/llm-mac-512/venv/bin/python</string>
        <string>/Users/jacky/projects/llm-mac-512/scripts/api_server.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/mlx-api.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/mlx-api.error.log</string>
</dict>
</plist>
```

加载服务：
```bash
launchctl load ~/Library/LaunchAgents/com.mlx.api.plist
```

### 3. 监控API性能

```bash
# 查看请求日志
# API服务器会在终端显示每个请求

# 监控系统资源
watch -n 1 'ps aux | grep api_server'

# 查看内存使用
memory_pressure
```

---

## 性能参考

**你的系统（M3 Ultra 512GB）+ MLX 4-bit：**

| 指标 | 性能 |
|------|------|
| 模型加载时间 | ~21秒 |
| TTFT (首token) | 67ms |
| 生成速度 | 45.73 tokens/sec |
| 内存占用 | 135 GB |
| 并发能力 | 1-4个请求 |

**OpenClaw使用体验：**
- 响应迅速，接近云API体验
- 无网络延迟
- 完全私密，数据不出本地
- 无API费用

---

## 常见问题 FAQ

### Q1: 可以同时连接多个OpenClaw实例吗？

**A:** 可以，API服务器支持并发请求。但性能会随并发数下降。

### Q2: 能否使用其他端口？

**A:** 可以：
```bash
python scripts/api_server.py --port 8080
```
然后在OpenClaw中配置 `base_url: http://127.0.0.1:8080/v1`

### Q3: 是否支持流式响应？

**A:** API包含基础的流式支持，但可能需要根据OpenClaw的具体需求调整。

### Q4: 如何查看API日志？

**A:** API服务器会在终端实时显示请求日志。

### Q5: 可以远程访问吗？

**A:** 可以，但**不推荐**（安全风险）。如需要：
```bash
python scripts/api_server.py --host 0.0.0.0
```
然后配置防火墙和认证。

---

## 下一步

1. ✅ 启动API服务器
2. ✅ 配置OpenClaw
3. ✅ 测试基本功能
4. 📊 监控性能和优化
5. 🚀 享受本地AI助手！

---

## 相关资源

- **API服务器脚本：** `scripts/api_server.py`
- **MLX设置指南：** `docs/mlx-local-setup.md`
- **性能测试结果：** `docs/benchmark-results.md`
- **OpenClaw官网：** https://openclaw.ai
- **OpenClaw文档：** https://docs.openclaw.ai

---

**祝使用愉快！如有问题，查看故障排除部分或检查日志。**
