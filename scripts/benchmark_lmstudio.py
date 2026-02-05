#!/usr/bin/env python3
"""
LM Studio API Benchmark Script
测试 LM Studio 服务器性能
"""

import json
import time
import requests
from datetime import datetime

# 配置
API_BASE = "http://localhost:1234/v1"
MODEL_NAME = "qwen3-coder-next"

# 测试用例
TESTS = {
    "short": {
        "name": "短文本生成",
        "prompt": "请用一句话解释量子计算",
        "max_tokens": 100
    },
    "medium": {
        "name": "代码生成",
        "prompt": "写一个Python快速排序算法，包含完整注释",
        "max_tokens": 500
    },
    "long": {
        "name": "长文本生成",
        "prompt": "详细解释深度学习的反向传播算法，包括数学推导过程",
        "max_tokens": 2000
    },
    "reasoning": {
        "name": "推理能力",
        "prompt": "有5个人排队，已知：A不在第一位，B在C前面，D紧挨着E，A在D后面。请推理出他们的排列顺序。",
        "max_tokens": 500
    },
    "instruction": {
        "name": "指令跟随",
        "prompt": "请完成以下任务：\n1. 列出3种常见的排序算法\n2. 为每种算法写出时间复杂度\n3. 用一句话总结它们的适用场景",
        "max_tokens": 400
    }
}


def run_test(test_name, test_config):
    """运行单个测试"""
    print(f"\n{'='*60}")
    print(f"测试: {test_config['name']}")
    print(f"{'='*60}")

    # 准备请求
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": test_config["prompt"]}
        ],
        "max_tokens": test_config["max_tokens"],
        "temperature": 0.7
    }

    # 发送请求并计时
    start_time = time.time()

    try:
        response = requests.post(
            f"{API_BASE}/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        response.raise_for_status()

        end_time = time.time()
        total_time = end_time - start_time

        # 解析响应
        result = response.json()

        # 提取数据
        content = result["choices"][0]["message"]["content"]
        usage = result.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        # 计算指标
        # 注意：LM Studio 不提供 TTFT，我们估算总时间
        tps = completion_tokens / total_time if total_time > 0 else 0

        # 显示结果
        print(f"✓ 完成")
        print(f"  Prompt tokens: {prompt_tokens}")
        print(f"  Completion tokens: {completion_tokens}")
        print(f"  总时间: {total_time:.2f}s")
        print(f"  TPS: {tps:.2f}")
        print(f"  响应预览: {content[:100]}...")

        return {
            "test_name": test_name,
            "name": test_config["name"],
            "prompt": test_config["prompt"],
            "max_tokens": test_config["max_tokens"],
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_time": total_time,
            "tps": tps,
            "content": content,
            "success": True
        }

    except Exception as e:
        print(f"✗ 错误: {e}")
        return {
            "test_name": test_name,
            "name": test_config["name"],
            "error": str(e),
            "success": False
        }


def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         LM Studio Performance Benchmark                 ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"\nAPI: {API_BASE}")
    print(f"模型: {MODEL_NAME}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 检查服务器
    print("\n检查服务器状态...")
    try:
        response = requests.get(f"{API_BASE}/models", timeout=5)
        response.raise_for_status()
        print("✓ 服务器运行正常")
    except Exception as e:
        print(f"✗ 无法连接到服务器: {e}")
        return

    # 运行所有测试
    results = []
    for test_name, test_config in TESTS.items():
        result = run_test(test_name, test_config)
        results.append(result)
        time.sleep(2)  # 间隔2秒

    # 统计结果
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")

    successful_tests = [r for r in results if r.get("success")]

    if not successful_tests:
        print("所有测试失败")
        return

    # 计算平均值
    avg_tps = sum(r["tps"] for r in successful_tests) / len(successful_tests)
    max_tps = max(r["tps"] for r in successful_tests)
    min_tps = min(r["tps"] for r in successful_tests)
    total_tokens = sum(r["completion_tokens"] for r in successful_tests)
    total_time = sum(r["total_time"] for r in successful_tests)

    print(f"\n通过测试: {len(successful_tests)}/{len(results)}")
    print(f"总tokens: {total_tokens}")
    print(f"总时间: {total_time:.2f}s")
    print(f"平均TPS: {avg_tps:.2f}")
    print(f"最大TPS: {max_tps:.2f}")
    print(f"最小TPS: {min_tps:.2f}")

    # 详细结果表格
    print(f"\n{'='*60}")
    print("详细结果")
    print(f"{'='*60}")
    print(f"{'测试':<15} {'Tokens':<8} {'时间(s)':<10} {'TPS':<8}")
    print("-" * 60)

    for r in successful_tests:
        print(f"{r['name']:<15} {r['completion_tokens']:<8} "
              f"{r['total_time']:<10.2f} {r['tps']:<8.2f}")

    # 保存结果
    output_file = f"lmstudio-benchmark-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "api_base": API_BASE,
            "model": MODEL_NAME,
            "summary": {
                "avg_tps": avg_tps,
                "max_tps": max_tps,
                "min_tps": min_tps,
                "total_tokens": total_tokens,
                "total_time": total_time
            },
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n✓ 结果已保存到: {output_file}")
    print("\n🎉 测试完成!")


if __name__ == "__main__":
    main()
