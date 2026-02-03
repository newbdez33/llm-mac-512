# LM Studio + OpenClaw 故障排除指南

> 解决切换到本地 LM Studio 后回答质量问题

## 问题描述

从云端 API 切换到本地 LM Studio 后，出现以下问题：

1. **回答包含大量英文思考过程**
2. **`<think>` 标签暴露给用户**
3. **实际答案被埋在解释中**
4. **响应质量明显下降**

### 问题示例

**期望输出：**
```
你好！我是 MiniMax-M2.1，很高兴为你服务。
```

**实际输出：**
```
The user greeted me in Chinese with "你好" which means "Hello".
I should respond politely and appropriately. Since the user wrote
in Chinese, I can respond in Chinese as well to match their language
choice.

Let me respond naturally in Chinese:
</think>

你好！我是 MiniMax-M2.1，很高兴为你服务。
```

---

## 根本原因

### 1. API 类型配置错误 ⭐ 主要原因

**错误配置：**
```json
{
  "models": {
    "providers": {
      "lmstudio": {
        "api": "openai-completions"  // ❌ 错误
      }
    }
  }
}
```

**正确配置：**
```json
{
  "models": {
    "providers": {
      "lmstudio": {
        "api": "openai-responses"  // ✅ 正确
      }
    }
  }
}
```

**原因说明：**

| API 类型 | 适用场景 | 行为 |
|---------|---------|------|
| `openai-completions` | 普通模型 | 返回完整输出 |
| `openai-responses` | 推理模型（如 MiniMax M2.1） | 分离 `<think>` 和答案 |

MiniMax M2.1 是一个**推理模型**（reasoning model），会生成：
- `<think>...</think>` - 内部思考过程
- 实际答案 - 用户应该看到的内容

使用 `openai-responses` 后，OpenClaw 会自动：
1. 解析 `<think>` 标签
2. 提取实际答案
3. 只向用户显示答案部分

### 2. Context Length 限制

**LM Studio 默认：** 4,096 tokens
**MiniMax M2.1 能力：** 200,000 tokens
**官方推荐：** 196,608 tokens

过小的 context length 会：
- 限制模型理解能力
- 影响长对话质量
- 降低推理能力

### 3. 配置未生效

更改配置后，需要重启 OpenClaw gateway 才能生效。

---

## 完整解决方案

### 步骤 1: 修改 OpenClaw 配置

#### 自动修复脚本

```bash
#!/bin/bash
# 保存为 fix_openclaw_lmstudio.sh

echo "=== OpenClaw + LM Studio 配置修复 ==="

# 备份配置
BACKUP_FILE="$HOME/.openclaw/openclaw.json.backup.$(date +%s)"
cp ~/.openclaw/openclaw.json "$BACKUP_FILE"
echo "✓ 已备份到 $BACKUP_FILE"

# 修改 API 类型
python3 << 'PYTHON'
import json

config_file = '/Users/jacky/.openclaw/openclaw.json'

with open(config_file, 'r') as f:
    config = json.load(f)

# 确保 lmstudio provider 存在
if 'lmstudio' not in config.get('models', {}).get('providers', {}):
    print("❌ 错误: 未找到 lmstudio provider")
    exit(1)

# 修改 API 类型
config['models']['providers']['lmstudio']['api'] = 'openai-responses'

# 可选: 确保其他配置正确
lms_config = config['models']['providers']['lmstudio']
if 'contextWindow' not in lms_config.get('models', [{}])[0]:
    lms_config['models'][0]['contextWindow'] = 196608

if 'maxTokens' not in lms_config.get('models', [{}])[0]:
    lms_config['models'][0]['maxTokens'] = 8192

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print("✓ API 类型已更改为 openai-responses")
print("✓ Context window: 196608")
print("✓ Max tokens: 8192")
PYTHON

echo ""
echo "✓ 配置修改完成"
echo ""
```

#### 手动修改

编辑 `~/.openclaw/openclaw.json`:

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "lmstudio": {
        "baseUrl": "http://127.0.0.1:1234/v1",
        "api": "openai-responses",
        "apiKey": "lm-studio",
        "models": [
          {
            "id": "minimax-m2.1",
            "name": "MiniMax M2.1 (LM Studio)",
            "reasoning": true,
            "input": ["text"],
            "contextWindow": 196608,
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

### 步骤 2: 增加 LM Studio Context Length

#### 方法 A: 修改配置文件

```bash
python3 << 'EOF'
import json

config_file = '/Users/jacky/.lmstudio/settings.json'

with open(config_file, 'r') as f:
    config = json.load(f)

# 增加 context length
config['defaultContextLength'] = {
    "type": "custom",
    "value": 131072  # 128K (推荐) 或 196608
}

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print("✓ LM Studio context length 已更新为 131072")
EOF
```

#### 方法 B: LM Studio GUI

1. 打开 LM Studio
2. Settings (⚙️)
3. Context Length → 输入 `131072` 或更高
4. 保存

### 步骤 3: 重启服务

```bash
# 重启 LM Studio 服务器
lms server restart

# 重启 OpenClaw Gateway
openclaw gateway stop
openclaw gateway start

# 或者杀掉旧进程
pkill openclaw-gateway
openclaw gateway start
```

### 步骤 4: 验证修复

#### 测试 1: 检查配置

```bash
# 检查 API 类型
grep '"api"' ~/.openclaw/openclaw.json
# 应显示: "api": "openai-responses",

# 检查 context length
grep -A 2 "defaultContextLength" ~/.lmstudio/settings.json
# 应显示: "value": 131072 或更高
```

#### 测试 2: 测试响应质量

```bash
# 使用 OpenClaw
openclaw chat "你好，请用一句话介绍自己"

# 预期输出（无英文思考）:
# 你好！我是 MiniMax-M2.1，很高兴为你服务。
```

#### 测试 3: 完整测试脚本

```bash
#!/bin/bash
echo "=== OpenClaw + LM Studio 测试 ==="

# 1. 配置检查
echo -e "\n1. API 类型:"
grep '"api"' ~/.openclaw/openclaw.json | grep -q "openai-responses" && \
  echo "✓ openai-responses" || echo "✗ 配置错误"

# 2. Context length 检查
echo -e "\n2. Context Length:"
CTX=$(grep -A 2 "defaultContextLength" ~/.lmstudio/settings.json | grep "value" | grep -o '[0-9]*')
if [ "$CTX" -ge 131072 ]; then
  echo "✓ $CTX (足够)"
else
  echo "⚠ $CTX (建议 ≥131072)"
fi

# 3. Gateway 状态
echo -e "\n3. Gateway 状态:"
ps aux | grep -q "openclaw-gateway" && \
  echo "✓ 运行中" || echo "✗ 未运行"

# 4. LM Studio 状态
echo -e "\n4. LM Studio 状态:"
lms server status | grep -q "running" && \
  echo "✓ 运行中" || echo "✗ 未运行"

# 5. 简单测试
echo -e "\n5. 响应测试:"
RESPONSE=$(openclaw chat "你好" --max-tokens 50 2>&1 | tail -1)
echo "响应: $RESPONSE"

if echo "$RESPONSE" | grep -qi "think"; then
  echo "⚠ 仍包含推理内容"
elif echo "$RESPONSE" | grep -qi "The user"; then
  echo "⚠ 仍包含英文解释"
else
  echo "✓ 响应正常"
fi

echo -e "\n=== 测试完成 ==="
```

---

## 配置参考

### 完整的 OpenClaw 配置模板

```json
{
  "meta": {
    "lastTouchedVersion": "2026.2.1",
    "lastTouchedAt": "2026-02-03T10:42:19.383Z"
  },
  "wizard": {
    "lastRunAt": "2026-02-03T10:42:19.378Z",
    "lastRunVersion": "2026.2.1",
    "lastRunCommand": "doctor",
    "lastRunMode": "local"
  },
  "browser": {
    "defaultProfile": "openclaw"
  },
  "auth": {
    "profiles": {
      "local:default": {
        "provider": "local",
        "mode": "api_key"
      }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "lmstudio": {
        "baseUrl": "http://127.0.0.1:1234/v1",
        "api": "openai-responses",
        "apiKey": "lm-studio",
        "models": [
          {
            "id": "minimax-m2.1",
            "name": "MiniMax M2.1 (LM Studio)",
            "reasoning": true,
            "input": ["text"],
            "contextWindow": 196608,
            "maxTokens": 8192
          }
        ]
      },
      "anthropic": {
        "apiKey": "your-key-here",
        "models": [
          {
            "id": "claude-opus-4-5",
            "name": "Claude Opus 4.5 (Fallback)"
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "lmstudio/minimax-m2.1",
        "fallback": "anthropic/claude-opus-4-5"
      }
    }
  }
}
```

### LM Studio 推荐配置

```json
{
  "defaultContextLength": {
    "type": "custom",
    "value": 131072
  },
  "developer": {
    "showExperimentalFeatures": false,
    "showDebugInfoBlocksInChat": false
  },
  "modelLoadingGuardrails": {
    "mode": "high"
  }
}
```

---

## 常见问题

### Q1: 为什么改了配置还是有问题？

**A:** 需要重启 OpenClaw gateway：

```bash
pkill openclaw-gateway
openclaw gateway start
```

### Q2: 如何确认 gateway 使用了新配置？

**A:** 检查 gateway 日志：

```bash
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log
```

### Q3: Context length 应该设置多大？

**A:** 推荐值：

| 用途 | 推荐值 | 说明 |
|------|--------|------|
| 基本使用 | 8,192 | 短对话 |
| 日常使用 | 32,768 | 普通对话 |
| **推荐** | **131,072** | 长对话、代码 |
| 专业 | 196,608 | 官方推荐 |
| 最大 | 200,000 | MiniMax M2.1 上限 |

### Q4: 性能会受影响吗？

**A:** Context length 增加会略微影响性能：

- 131,072: 几乎无影响
- 196,608: 可接受的轻微影响
- 建议根据实际需求选择

### Q5: 如何恢复到云端 API？

**A:** 修改 OpenClaw 配置：

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-5"
      }
    }
  }
}
```

---

## 性能对比

### API 类型对响应的影响

| 配置 | 响应时间 | 质量 | 用户体验 |
|------|---------|------|---------|
| `openai-completions` | 慢 | 包含推理 | ❌ 差 |
| `openai-responses` | 快 | 仅答案 | ✅ 好 |

### Context Length 对性能的影响

| Context Length | TPS | 内存 | 质量 |
|---------------|-----|------|------|
| 4,096 | 20.73 | ~238GB | ⚠️ 受限 |
| 32,768 | ~25 | ~240GB | ✓ 良好 |
| 131,072 | ~22 | ~245GB | ✓ 优秀 |
| 196,608 | ~20 | ~250GB | ✓ 最佳 |

---

## 参考资源

- **OpenClaw 官方文档**: https://docs.openclaw.ai/gateway/local-models
- **LM Studio 官网**: https://lmstudio.ai
- **MiniMax M2.1 模型**: https://huggingface.co/mlx-community/MiniMax-M2.1-8bit

---

## 总结

**关键配置（必须）：**
1. ✅ `api: "openai-responses"`
2. ✅ `contextWindow: 196608`
3. ✅ LM Studio context length ≥ 131072

**可选优化：**
- 混合模式（本地 + 云端）
- 调整 temperature 和 max_tokens
- 启用 fallback 机制

**验证步骤：**
1. 检查配置文件
2. 重启 gateway
3. 测试响应质量
4. 确认无英文推理内容

修复后，本地 LM Studio 的响应质量应该与云端 API 一致！
