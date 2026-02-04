# 归档测试结果 / Archived Test Results

> 归档日期: 2026-02-04

## 说明

此目录包含早期测试结果，使用原生 MLX 框架直接测试。

**归档原因**:
- 测试方法变更：统一通过 LM Studio 加载模型并提供 API 服务器
- 保留历史数据以供参考

## 归档内容

### MLX 4-bit 测试
- `mlx-minimax-m2-1-4bit-20260202-*.json/md` (4 次测试)
- 平均性能: ~45 TPS
- 内存占用: ~135GB

### MLX 6-bit 测试
- `mlx-minimax-m2-1-6bit-20260202-145356.json/md`
- 平均性能: ~39 TPS
- 内存占用: ~198GB

### MLX 8-bit 测试
- `mlx-minimax-m2-1-8bit-20260202-184426.json/md`
- 平均性能: ~33 TPS
- 内存占用: ~252GB

## 新测试方法

从 2026-02-04 起，所有测试（MLX 和 llama.cpp）统一通过 LM Studio 进行：
- 统一的测试接口（OpenAI-compatible API）
- 一致的配置管理
- 更好的适配 OpenClaw

详见: `docs/test-plan.md`
