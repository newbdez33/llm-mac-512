# API服务器测试状态

## 📊 当前状态

**时间：** $(date)

### ✅ 已完成

1. **代码推送**
   - ✅ API服务器代码 (`scripts/api_server.py`)
   - ✅ 测试工具 (`scripts/test_api.py`)
   - ✅ 启动脚本 (`start_api.sh`)
   - ✅ OpenClaw配置文档 (`docs/openclaw-setup.md`)

2. **依赖安装**
   - ✅ Flask 已安装
   - ✅ Flask-CORS 已安装
   - ✅ MLX 已安装

3. **服务器启动**
   - ✅ API服务器已启动（PID: 进程运行中）
   - ⏳ 模型下载中（首次运行需要下载~120GB）

### ⏳ 进行中

**模型下载：**
- 模型：mlx-community/MiniMax-M2.1-4bit
- 大小：~120GB
- 状态：下载中（约15%完成）
- 预计时间：20-60分钟（取决于网速）

**日志位置：** `/tmp/api_server.log`

---

## 🧪 测试步骤（模型下载完成后）

### 1. 检查服务器状态

```bash
# 查看日志
tail -f /tmp/api_server.log

# 等待看到这条消息：
# ✓ 模型加载完成！用时 XX 秒
```

### 2. 测试健康检查

```bash
curl http://127.0.0.1:8000/health
```

**预期输出：**
```json
{
  "status": "ok",
  "model": "mlx-community/MiniMax-M2.1-4bit",
  "model_loaded": true
}
```

### 3. 运行自动化测试

```bash
cd ~/projects/llm-mac-512
source venv/bin/activate
python scripts/test_api.py
```

**预期输出：**
```
╔══════════════════════════════════════════════════════════╗
║              MLX API 服务器测试                          ║
╚══════════════════════════════════════════════════════════╝

测试 1/5: 健康检查
✓ 服务器运行正常

测试 2/5: 模型列表
✓ 找到 1 个模型

测试 3/5: 简单对话
✓ 生成成功
  TPS: 45.73

测试 4/5: 复杂对话
✓ 生成成功
  性能: 🚀 优秀

测试 5/5: Completions API
✓ 生成成功

总计: 5/5 测试通过
🎉 所有测试通过！
```

### 4. 手动测试Chat API

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100
  }'
```

### 5. 配置OpenClaw

```bash
# 方式A: 环境变量
export OPENAI_API_BASE="http://127.0.0.1:8000/v1"
export OPENAI_API_KEY="sk-dummy"

# 方式B: 配置文件 ~/.openclaw/config.yaml
cat > ~/.openclaw/config.yaml << 'EOF'
llm:
  provider: openai
  base_url: http://127.0.0.1:8000/v1
  api_key: sk-dummy
  model: mlx-community/MiniMax-M2.1-4bit
  temperature: 0.7
  max_tokens: 1000
EOF
```

---

## 📝 快速命令参考

```bash
# 查看API服务器日志
tail -f /tmp/api_server.log

# 检查服务器是否运行
curl http://127.0.0.1:8000/health

# 停止服务器
pkill -f api_server.py

# 重新启动服务器
./start_api.sh

# 运行测试
python scripts/test_api.py
```

---

## 🔧 如果需要快速测试（不等待下载）

可以先停止当前下载，使用已有的测试来验证代码：

```bash
# 1. 停止当前服务器
pkill -f api_server.py

# 2. 测试脚本本身（不需要模型）
python -c "
from scripts.api_server import format_prompt
messages = [{'role': 'user', 'content': 'test'}]
print('✓ API服务器代码正常')
"

# 3. 测试启动脚本
./start_api.sh --help 2>&1 | head -5
```

---

## ⏭️ 下一步

**选项A：等待下载完成（推荐）**
- 让模型继续下载（20-60分钟）
- 下载完成后运行完整测试
- 配置OpenClaw使用

**选项B：后台下载，稍后测试**
- 让服务器在后台继续运行
- 可以先做其他事情
- 稍后回来检查：`tail -f /tmp/api_server.log`

**选项C：先测试代码结构**
- 停止下载：`pkill -f api_server.py`
- 验证代码和脚本
- 稍后再启动完整服务

---

## 📊 预期性能

**你的系统（M3 Ultra 512GB）：**

| 指标 | 预期值 |
|------|--------|
| 模型加载时间 | ~21秒 |
| TTFT | 67ms |
| 生成速度 | 45.73 TPS |
| 内存占用 | 135 GB |

---

## 🎯 最终目标

- [x] 代码准备完成
- [x] 依赖安装完成
- [ ] 模型下载完成（进行中）
- [ ] API测试通过
- [ ] OpenClaw集成测试

**当前进度：60%**
