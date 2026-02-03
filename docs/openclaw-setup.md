# OpenClaw + MLX 本地配置指南

> 在本地使用MLX MiniMax M2.1为OpenClaw提供AI能力

## 📋 目录

- [概述](#概述)
- [前置要求](#前置要求)
- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [测试验证](#测试验证)
- [故障排除](#故障排除)

---

## 概述

这个指南将帮你：
1. 启动本地MLX API服务器
2. 配置OpenClaw使用本地API
3. 验证配置是否正常工作

**架构：**
```
OpenClaw → 本地API服务器 (127.0.0.1:8000) → MLX MiniMax M2.1
```

---

## 前置要求

### 1. MLX环境已配置

```bash
# 检查MLX是否已安装
source venv/bin/activate
python -c "import mlx_lm; print('MLX OK')"
```

如果未安装，参考：[docs/mlx-local-setup.md](./mlx-local-setup.md)

### 2. 安装API服务器依赖

```bash
# 激活环境
source venv/bin/activate

# 安装Flask（API服务器）
pip install flask flask-cors

# 验证安装
python -c "import flask; print('Flask installed')"
```

### 3. OpenClaw已安装

参考：https://openclaw.ai 或 https://github.com/openclaw/openclaw

---

## 快速开始

### 第1步：启动API服务器

```bash
# 进入项目目录
cd ~/projects/llm-mac-512
source venv/bin/activate

# 启动API服务器（使用4-bit模型，最快）
python scripts/api_server.py
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
