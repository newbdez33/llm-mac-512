#!/usr/bin/env python3
"""
测试MLX API服务器

使用方法:
    python scripts/test_api.py
    python scripts/test_api.py --base-url http://127.0.0.1:8080/v1
"""

import argparse
import requests
import json
import time


def parse_args():
    parser = argparse.ArgumentParser(description="测试MLX API服务器")
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://127.0.0.1:8000/v1",
        help="API基础URL (default: http://127.0.0.1:8000/v1)",
    )
    return parser.parse_args()


def test_health(base_url):
    """测试健康检查"""
    print("\n" + "="*60)
    print("测试 1/5: 健康检查")
    print("="*60)

    try:
        # 去掉 /v1 后缀
        health_url = base_url.replace("/v1", "") + "/health"
        response = requests.get(health_url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"✓ 服务器运行正常")
            print(f"  状态: {data.get('status')}")
            print(f"  模型: {data.get('model')}")
            print(f"  模型已加载: {data.get('model_loaded')}")
            return True
        else:
            print(f"✗ 健康检查失败: HTTP {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"✗ 无法连接到服务器")
        print(f"  请确认API服务器正在运行:")
        print(f"  python scripts/api_server.py")
        return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_models(base_url):
    """测试模型列表"""
    print("\n" + "="*60)
    print("测试 2/5: 模型列表")
    print("="*60)

    try:
        response = requests.get(f"{base_url}/models", timeout=10)

        if response.status_code == 200:
            data = response.json()
            models = data.get("data", [])

            if models:
                print(f"✓ 找到 {len(models)} 个模型")
                for model in models:
                    print(f"  • {model.get('id')}")
                return True
            else:
                print(f"⚠ 没有可用模型")
                return False
        else:
            print(f"✗ 获取模型列表失败: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_chat_simple(base_url):
    """测试简单对话"""
    print("\n" + "="*60)
    print("测试 3/5: 简单对话")
    print("="*60)

    prompt = "你好"
    print(f"发送: {prompt}")

    try:
        start_time = time.time()

        response = requests.post(
            f"{base_url}/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 50,
                "temperature": 0.7
            },
            timeout=30
        )

        request_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            print(f"✓ 生成成功")
            print(f"  回复: {content[:100]}...")
            print(f"  tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"  用时: {request_time:.2f}秒")

            # 检查性能统计
            if "_mlx_stats" in data:
                stats = data["_mlx_stats"]
                print(f"  TPS: {stats.get('tokens_per_second', 'N/A'):.2f}")

            return True
        else:
            print(f"✗ 请求失败: HTTP {response.status_code}")
            print(f"  响应: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_chat_complex(base_url):
    """测试复杂对话"""
    print("\n" + "="*60)
    print("测试 4/5: 复杂对话（代码生成）")
    print("="*60)

    prompt = "写一个Python冒泡排序算法"
    print(f"发送: {prompt}")

    try:
        start_time = time.time()

        response = requests.post(
            f"{base_url}/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            },
            timeout=60
        )

        request_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            print(f"✓ 生成成功")
            print(f"  回复长度: {len(content)} 字符")
            print(f"  tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"  用时: {request_time:.2f}秒")

            if "_mlx_stats" in data:
                stats = data["_mlx_stats"]
                tps = stats.get('tokens_per_second', 0)
                print(f"  TPS: {tps:.2f}")

                # 性能评估
                if tps > 40:
                    print(f"  性能: 🚀 优秀")
                elif tps > 30:
                    print(f"  性能: ✓ 良好")
                elif tps > 20:
                    print(f"  性能: ⚠ 一般")
                else:
                    print(f"  性能: ⚠ 较慢")

            return True
        else:
            print(f"✗ 请求失败: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_completions(base_url):
    """测试completions API"""
    print("\n" + "="*60)
    print("测试 5/5: Completions API")
    print("="*60)

    prompt = "人工智能的定义是："
    print(f"发送: {prompt}")

    try:
        response = requests.post(
            f"{base_url}/completions",
            json={
                "prompt": prompt,
                "max_tokens": 100,
                "temperature": 0.7
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            text = data["choices"][0]["text"]
            usage = data.get("usage", {})

            print(f"✓ 生成成功")
            print(f"  回复: {text[:150]}...")
            print(f"  tokens: {usage.get('completion_tokens', 'N/A')}")

            return True
        else:
            print(f"✗ 请求失败: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def main():
    args = parse_args()

    print("""
╔══════════════════════════════════════════════════════════╗
║              MLX API 服务器测试                          ║
╚══════════════════════════════════════════════════════════╝
""")

    print(f"API URL: {args.base_url}")

    # 运行测试
    results = []

    results.append(("健康检查", test_health(args.base_url)))
    if not results[-1][1]:
        print("\n✗ 健康检查失败，停止测试")
        print("\n请先启动API服务器:")
        print("  python scripts/api_server.py")
        return

    results.append(("模型列表", test_models(args.base_url)))
    results.append(("简单对话", test_chat_simple(args.base_url)))
    results.append(("复杂对话", test_chat_complex(args.base_url)))
    results.append(("Completions", test_completions(args.base_url)))

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！API服务器工作正常。")
        print("\n下一步:")
        print("  • 配置OpenClaw使用此API")
        print("  • 参考文档: docs/openclaw-setup.md")
    else:
        print(f"\n⚠ {total - passed} 个测试失败")
        print("请检查API服务器日志排查问题")


if __name__ == "__main__":
    main()
