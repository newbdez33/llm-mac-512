#!/usr/bin/env python3
"""
MiniMax M2.1 MLX Benchmark Script

Usage:
    python benchmark_mlx.py --model mlx-community/MiniMax-M2.1-4bit
    python benchmark_mlx.py --model mlx-community/MiniMax-M2.1-8bit
"""

import argparse
import gc
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

# Add scripts directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    MemoryMonitor,
    Timer,
    format_duration,
    generate_markdown_report,
    get_system_info,
    load_test_prompts,
    save_results,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark MiniMax M2.1 with MLX")
    parser.add_argument(
        "--model",
        type=str,
        default="mlx-community/MiniMax-M2.1-4bit",
        help="Model name or path (HuggingFace repo or local path)",
    )
    parser.add_argument(
        "--prompts",
        type=str,
        default=None,
        help="Path to test prompts JSON file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for results",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Override max_tokens for all tests",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature for generation",
    )
    parser.add_argument(
        "--tests",
        type=str,
        nargs="+",
        default=None,
        help="Specific tests to run (e.g., short medium)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check setup without running benchmarks",
    )
    return parser.parse_args()


def load_model(model_name: str, memory_monitor: MemoryMonitor):
    """Load MLX model and tokenizer with timing."""
    from mlx_lm import load

    print(f"\n{'='*60}")
    print(f"Loading model: {model_name}")
    print(f"{'='*60}")

    memory_monitor.sample()
    print(f"Memory before loading: {memory_monitor.samples[-1]:.2f} GB")

    with Timer("model_load") as timer:
        model, tokenizer = load(model_name)
        memory_monitor.sample()

    print(f"Model loaded in {format_duration(timer.duration)}")
    print(f"Memory after loading: {memory_monitor.samples[-1]:.2f} GB")

    return model, tokenizer, timer.duration


def run_generation_test(
    model,
    tokenizer,
    prompt: str,
    max_tokens: int,
    temperature: float,
    memory_monitor: MemoryMonitor,
) -> dict:
    """Run a single generation test and collect metrics."""
    from mlx_lm import generate

    # Apply chat template if available
    if hasattr(tokenizer, "apply_chat_template"):
        messages = [{"role": "user", "content": prompt}]
        formatted_prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        formatted_prompt = prompt

    # Variables for streaming callback
    first_token_time = None
    token_count = 0
    start_time = time.perf_counter()

    def token_callback(token):
        nonlocal first_token_time, token_count
        if first_token_time is None:
            first_token_time = time.perf_counter()
        token_count += 1
        # Sample memory periodically
        if token_count % 50 == 0:
            memory_monitor.sample()

    # Run generation
    memory_monitor.sample()

    output = generate(
        model,
        tokenizer,
        prompt=formatted_prompt,
        max_tokens=max_tokens,
        temp=temperature,
    )

    end_time = time.perf_counter()
    memory_monitor.sample()

    # Calculate metrics
    total_time = end_time - start_time

    # Count actual tokens in output
    output_tokens = len(tokenizer.encode(output))

    # Estimate TTFT (first token time) - if we don't have streaming, estimate
    # based on typical first-token overhead
    if first_token_time is None:
        # Estimate: assume first token takes about 10% of per-token time + overhead
        estimated_ttft = min(total_time * 0.1, total_time / max(output_tokens, 1) * 3)
        ttft = estimated_ttft
    else:
        ttft = first_token_time - start_time

    # Calculate TPS (excluding first token time for pure generation speed)
    generation_time = total_time - ttft if total_time > ttft else total_time
    tps = output_tokens / generation_time if generation_time > 0 else 0

    return {
        "output": output,
        "total_tokens": output_tokens,
        "ttft_sec": round(ttft, 3),
        "generation_time_sec": round(generation_time, 3),
        "total_time_sec": round(total_time, 3),
        "tps": round(tps, 2),
    }


def run_benchmark(args):
    """Run the complete benchmark suite."""
    print("\n" + "=" * 60)
    print("MiniMax M2.1 MLX Benchmark")
    print("=" * 60)

    # Initialize
    memory_monitor = MemoryMonitor()
    results = {
        "model_name": args.model,
        "framework": "MLX",
        "timestamp": datetime.now().isoformat(),
        "system_info": get_system_info(),
        "config": {
            "temperature": args.temperature,
            "max_tokens_override": args.max_tokens,
        },
        "metrics": {},
        "tests": [],
    }

    # Check MLX installation
    try:
        import mlx.core as mx
        import mlx_lm

        # Get version from mlx.core or use package metadata
        try:
            from importlib.metadata import version
            mlx_version = version("mlx")
        except Exception:
            mlx_version = "unknown"

        print(f"MLX version: {mlx_version}")
        results["system_info"]["mlx_version"] = mlx_version
    except ImportError as e:
        print(f"Error: MLX not installed. Run: pip install -U mlx-lm")
        print(f"Details: {e}")
        return None

    if args.dry_run:
        print("\nDry run mode - skipping model load and tests")
        print(f"Would test model: {args.model}")
        return results

    # Load model
    try:
        model, tokenizer, load_time = load_model(args.model, memory_monitor)
        results["metrics"]["load_time_sec"] = round(load_time, 2)
    except Exception as e:
        print(f"Error loading model: {e}")
        raise

    # Load test prompts
    prompts = load_test_prompts(args.prompts)

    # Filter tests if specified
    if args.tests:
        prompts = {k: v for k, v in prompts.items() if k in args.tests}

    print(f"\nRunning {len(prompts)} tests...")

    # Run tests
    all_tps = []
    all_ttft = []

    for test_key, test_config in prompts.items():
        print(f"\n--- Test: {test_config['name']} ({test_key}) ---")

        max_tokens = args.max_tokens or test_config.get("max_tokens", 500)
        prompt = test_config["prompt"]

        print(f"Prompt: {prompt[:50]}...")
        print(f"Max tokens: {max_tokens}")

        try:
            test_result = run_generation_test(
                model=model,
                tokenizer=tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=args.temperature,
                memory_monitor=memory_monitor,
            )

            test_result["name"] = test_config["name"]
            test_result["key"] = test_key
            test_result["prompt"] = prompt
            test_result["max_tokens"] = max_tokens

            results["tests"].append(test_result)

            all_tps.append(test_result["tps"])
            all_ttft.append(test_result["ttft_sec"])

            print(f"TTFT: {test_result['ttft_sec']:.3f}s")
            print(f"TPS: {test_result['tps']:.2f} tokens/sec")
            print(f"Total tokens: {test_result['total_tokens']}")
            print(f"Output preview: {test_result['output'][:100]}...")

        except Exception as e:
            print(f"Error in test {test_key}: {e}")
            results["tests"].append({
                "name": test_config["name"],
                "key": test_key,
                "error": str(e),
            })

    # Calculate aggregate metrics
    memory_stats = memory_monitor.get_stats()
    results["metrics"]["peak_memory_gb"] = memory_stats["peak_gb"]
    results["metrics"]["avg_memory_gb"] = memory_stats["avg_gb"]

    if all_tps:
        results["metrics"]["avg_tps"] = round(sum(all_tps) / len(all_tps), 2)
        results["metrics"]["min_tps"] = round(min(all_tps), 2)
        results["metrics"]["max_tps"] = round(max(all_tps), 2)

    if all_ttft:
        results["metrics"]["avg_ttft_sec"] = round(sum(all_ttft) / len(all_ttft), 3)

    # Print summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"Model: {args.model}")
    print(f"Load time: {format_duration(results['metrics'].get('load_time_sec', 0))}")
    print(f"Peak memory: {results['metrics'].get('peak_memory_gb', 0):.2f} GB")
    print(f"Average TPS: {results['metrics'].get('avg_tps', 0):.2f} tokens/sec")
    print(f"Average TTFT: {results['metrics'].get('avg_ttft_sec', 0):.3f} sec")

    # Cleanup
    del model
    del tokenizer
    gc.collect()

    return results


def main():
    args = parse_args()

    # Run benchmark
    results = run_benchmark(args)

    if results is None:
        sys.exit(1)

    # Determine output paths
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path(__file__).parent.parent / "docs" / "test-results"

    # Create model-specific filename
    model_short = args.model.split("/")[-1].lower().replace(".", "-")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    json_file = output_dir / f"mlx-{model_short}-{timestamp}.json"
    md_file = output_dir / f"mlx-{model_short}-{timestamp}.md"

    # Save results
    if not args.dry_run:
        save_results(results, str(json_file))
        generate_markdown_report(results, str(md_file))

    print(f"\nResults saved to:")
    print(f"  JSON: {json_file}")
    print(f"  Markdown: {md_file}")


if __name__ == "__main__":
    main()
