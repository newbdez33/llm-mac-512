#!/usr/bin/env python3
"""
MLX MiniMax M2.1 交互式对话

使用方法:
    python scripts/chat_mlx.py
    python scripts/chat_mlx.py --model mlx-community/MiniMax-M2.1-8bit
"""

import argparse
import time
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler


def parse_args():
    parser = argparse.ArgumentParser(description="MLX MiniMax M2.1 交互式对话")
    parser.add_argument(
        "--model",
        type=str,
        default="mlx-community/MiniMax-M2.1-4bit",
        help="模型名称 (default: MiniMax-M2.1-4bit)",
    )
    parser.add_argument(
        "--temp",
        type=float,
        default=0.7,
        help="Temperature (default: 0.7)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=500,
        help="最大生成tokens (default: 500)",
    )
    return parser.parse_args()


def chat(model_name, temperature=0.7, max_tokens=500):
    """交互式对话"""

    # 加载模型
    print("\n" + "=" * 60)
    print(f"正在加载模型: {model_name}")
    print("=" * 60)
    start_time = time.time()
    model, tokenizer = load(model_name)
    load_time = time.time() - start_time
    print(f"✓ 模型加载完成！用时 {load_time:.2f} 秒\n")

    print("=" * 60)
    print("MiniMax M2.1 本地对话")
    print("=" * 60)
    print("输入 'quit', 'exit' 或 'q' 退出")
    print("输入 '/help' 查看帮助\n")

    # 创建采样器
    sampler = make_sampler(temp=temperature)

    while True:
        # 获取用户输入
        try:
            user_input = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n再见！")
            break

        # 处理命令
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n再见！")
            break

        if user_input == '/help':
            print("\n可用命令:")
            print("  quit, exit, q  - 退出程序")
            print("  /help          - 显示此帮助")
            print("  /stats         - 显示统计信息")
            continue

        if user_input == '/stats':
            print(f"\n当前配置:")
            print(f"  模型: {model_name}")
            print(f"  Temperature: {temperature}")
            print(f"  最大tokens: {max_tokens}")
            continue

        if not user_input:
            continue

        # 应用chat模板（如果有）
        if hasattr(tokenizer, 'apply_chat_template'):
            messages = [{"role": "user", "content": user_input}]
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            prompt = user_input

        # 生成回答
        print("\n助手: ", end="", flush=True)
        start_gen = time.time()

        try:
            response = generate(
                model,
                tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                sampler=sampler,
                verbose=False
            )

            gen_time = time.time() - start_gen
            tokens = len(tokenizer.encode(response))
            tps = tokens / gen_time if gen_time > 0 else 0

            print(response)
            print(f"\n[{tokens} tokens | {gen_time:.2f}s | {tps:.1f} tokens/s]")

        except Exception as e:
            print(f"\n错误: {e}")


def main():
    args = parse_args()

    print(f"""
╔══════════════════════════════════════════════════════════╗
║           MLX MiniMax M2.1 交互式对话                    ║
╚══════════════════════════════════════════════════════════╝

模型: {args.model}
Temperature: {args.temp}
最大tokens: {args.max_tokens}
""")

    chat(args.model, args.temp, args.max_tokens)


if __name__ == "__main__":
    main()
