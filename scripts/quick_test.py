#!/usr/bin/env python3
"""
MLX MiniMax M2.1 快速测试脚本

快速验证MLX环境和模型运行是否正常

使用方法:
    python scripts/quick_test.py
    python scripts/quick_test.py --model mlx-community/MiniMax-M2.1-6bit
"""

import argparse
import time
import sys
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler


def parse_args():
    parser = argparse.ArgumentParser(description="MLX 快速测试")
    parser.add_argument(
        "--model",
        type=str,
        default="mlx-community/MiniMax-M2.1-4bit",
        help="模型名称",
    )
    return parser.parse_args()


def test_import():
    """测试导入"""
    print("\n" + "=" * 60)
    print("测试 1/4: 检查依赖")
    print("=" * 60)

    try:
        import mlx.core as mx
        print(f"✓ MLX version: {mx.__version__}")
    except Exception as e:
        print(f"✗ MLX导入失败: {e}")
        return False

    try:
        import mlx_lm
        print(f"✓ mlx-lm 已安装")
    except Exception as e:
        print(f"✗ mlx-lm导入失败: {e}")
        return False

    try:
        import mlx.core as mx
        if mx.metal.is_available():
            print(f"✓ Metal GPU 可用")
        else:
            print(f"⚠ Metal GPU 不可用")
    except:
        print(f"⚠ 无法检查Metal状态")

    return True


def test_model_load(model_name):
    """测试模型加载"""
    print("\n" + "=" * 60)
    print("测试 2/4: 加载模型")
    print("=" * 60)
    print(f"模型: {model_name}")
    print("首次运行会下载模型，请耐心等待...\n")

    try:
        start_time = time.time()
        model, tokenizer = load(model_name)
        load_time = time.time() - start_time

        print(f"✓ 模型加载成功！")
        print(f"  加载时间: {load_time:.2f} 秒")

        return model, tokenizer

    except Exception as e:
        print(f"✗ 模型加载失败: {e}")
        return None, None


def test_generation(model, tokenizer):
    """测试生成"""
    print("\n" + "=" * 60)
    print("测试 3/4: 文本生成")
    print("=" * 60)

    test_prompt = "请用一句话解释人工智能"
    print(f"Prompt: {test_prompt}\n")

    try:
        start_time = time.time()
        sampler = make_sampler(temp=0.7)

        response = generate(
            model,
            tokenizer,
            prompt=test_prompt,
            max_tokens=100,
            sampler=sampler,
            verbose=False
        )

        gen_time = time.time() - start_time
        tokens = len(tokenizer.encode(response))
        tps = tokens / gen_time if gen_time > 0 else 0

        print(f"Response:\n{response}\n")
        print(f"✓ 生成成功！")
        print(f"  生成tokens: {tokens}")
        print(f"  用时: {gen_time:.2f} 秒")
        print(f"  速度: {tps:.2f} tokens/秒")

        return True, tps

    except Exception as e:
        print(f"✗ 生成失败: {e}")
        return False, 0


def test_performance(model, tokenizer):
    """测试性能"""
    print("\n" + "=" * 60)
    print("测试 4/4: 性能测试")
    print("=" * 60)

    test_cases = [
        ("短文本", "什么是量子计算？", 50),
        ("中文本", "写一个Python冒泡排序", 200),
    ]

    results = []
    sampler = make_sampler(temp=0.7)

    for name, prompt, max_tokens in test_cases:
        print(f"\n{name} ({max_tokens} tokens)...")

        try:
            start_time = time.time()
            response = generate(
                model,
                tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                sampler=sampler,
                verbose=False
            )
            gen_time = time.time() - start_time
            tokens = len(tokenizer.encode(response))
            tps = tokens / gen_time if gen_time > 0 else 0

            print(f"  ✓ {tokens} tokens | {gen_time:.2f}s | {tps:.2f} TPS")
            results.append(tps)

        except Exception as e:
            print(f"  ✗ 失败: {e}")
            results.append(0)

    if results:
        avg_tps = sum(results) / len(results)
        print(f"\n平均性能: {avg_tps:.2f} tokens/秒")
        return avg_tps
    else:
        return 0


def main():
    args = parse_args()

    print("""
╔══════════════════════════════════════════════════════════╗
║              MLX MiniMax M2.1 快速测试                   ║
╚══════════════════════════════════════════════════════════╝
""")

    # 测试1: 导入
    if not test_import():
        print("\n✗ 环境检查失败，请先安装依赖:")
        print("  pip install mlx mlx-lm")
        sys.exit(1)

    # 测试2: 加载模型
    model, tokenizer = test_model_load(args.model)
    if model is None:
        print("\n✗ 模型加载失败")
        sys.exit(1)

    # 测试3: 生成
    success, tps = test_generation(model, tokenizer)
    if not success:
        print("\n✗ 生成测试失败")
        sys.exit(1)

    # 测试4: 性能
    avg_tps = test_performance(model, tokenizer)

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"✓ 所有测试通过！")
    print(f"✓ 模型: {args.model}")
    print(f"✓ 平均性能: {avg_tps:.2f} tokens/秒")

    # 性能评估
    print("\n性能评估:")
    if avg_tps > 40:
        print("  🚀 优秀！接近或超过预期性能")
    elif avg_tps > 30:
        print("  ✓ 良好！性能在可接受范围内")
    elif avg_tps > 20:
        print("  ⚠ 一般，可能需要优化（检查VRAM设置）")
    else:
        print("  ⚠ 性能较低，建议:")
        print("     - 使用4-bit模型")
        print("     - 优化VRAM限制")
        print("     - 关闭其他应用")

    print("\n✓ MLX环境正常，可以开始使用！")
    print("\n下一步:")
    print("  • 交互式对话: python scripts/chat_mlx.py")
    print("  • 性能测试: python scripts/benchmark_mlx.py --model {args.model}")
    print("  • 查看文档: docs/mlx-local-setup.md")


if __name__ == "__main__":
    main()
