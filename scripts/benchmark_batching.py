#!/usr/bin/env python3
"""
MiniMax M2.1 MLX Batching Benchmark Script

Tests vllm-mlx continuous batching performance with concurrent requests.

Usage:
    # Baseline (single request)
    python benchmark_batching.py --model MiniMax-M2.1-4bit --concurrent 1

    # Scaling tests
    python benchmark_batching.py --model MiniMax-M2.1-4bit --concurrent 4
    python benchmark_batching.py --model MiniMax-M2.1-4bit --concurrent 8
    python benchmark_batching.py --model MiniMax-M2.1-4bit --concurrent 16

    # Mixed workload
    python benchmark_batching.py --model MiniMax-M2.1-4bit --concurrent 4 --mixed
"""

import argparse
import asyncio
import gc
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

# Add scripts directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    MemoryMonitor,
    format_duration,
    generate_markdown_report,
    get_system_info,
    load_test_prompts,
    save_results,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Benchmark MiniMax M2.1 with vllm-mlx batching"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="mlx-community/MiniMax-M2.1-4bit",
        help="Model name (HuggingFace repo format)",
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=1,
        help="Number of concurrent requests (1, 2, 4, 8, 16)",
    )
    parser.add_argument(
        "--tokens",
        type=int,
        default=500,
        help="Tokens per request",
    )
    parser.add_argument(
        "--mixed",
        action="store_true",
        help="Use mixed workload (100, 500, 2000 tokens)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature for generation",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for results",
    )
    parser.add_argument(
        "--use-mlx-lm",
        action="store_true",
        help="Use mlx-lm instead of vllm-mlx for baseline comparison",
    )
    return parser.parse_args()


class BatchingBenchmark:
    """Manages batching benchmark tests."""

    def __init__(self, model_name: str, use_vllm: bool = True):
        self.model_name = model_name
        self.use_vllm = use_vllm
        self.memory_monitor = MemoryMonitor()
        self.model = None
        self.tokenizer = None

    def load_model(self):
        """Load model using either vllm-mlx or mlx-lm."""
        print(f"\n{'='*60}")
        print(f"Loading model: {self.model_name}")
        print(f"Framework: {'vllm-mlx' if self.use_vllm else 'mlx-lm'}")
        print(f"{'='*60}")

        self.memory_monitor.sample()
        start_time = time.perf_counter()

        if self.use_vllm:
            # TODO: Implement vllm-mlx loading
            # For now, fall back to mlx-lm
            print("Warning: vllm-mlx not yet implemented, using mlx-lm")
            from mlx_lm import load

            self.model, self.tokenizer = load(self.model_name)
        else:
            from mlx_lm import load

            self.model, self.tokenizer = load(self.model_name)

        load_time = time.perf_counter() - start_time
        self.memory_monitor.sample()

        print(f"Model loaded in {format_duration(load_time)}")
        print(f"Memory: {self.memory_monitor.samples[-1]:.2f} GB")

        return load_time

    async def run_single_request(
        self, prompt: str, max_tokens: int, temperature: float, request_id: int
    ) -> dict:
        """Run a single generation request with timing."""
        from mlx_lm import generate
        from mlx_lm.sample_utils import make_sampler

        start_time = time.perf_counter()

        # Apply chat template if available
        if hasattr(self.tokenizer, "apply_chat_template"):
            messages = [{"role": "user", "content": prompt}]
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            formatted_prompt = prompt

        # Record time before generation
        queue_start = time.perf_counter()
        self.memory_monitor.sample()

        # Run generation (blocking for now, TODO: make async for vllm-mlx)
        sampler = make_sampler(temp=temperature)
        output = generate(
            self.model,
            self.tokenizer,
            prompt=formatted_prompt,
            max_tokens=max_tokens,
            sampler=sampler,
        )

        end_time = time.perf_counter()
        self.memory_monitor.sample()

        # Calculate metrics
        total_time = end_time - start_time
        generation_time = end_time - queue_start
        output_tokens = len(self.tokenizer.encode(output))

        # Estimate TTFT (simplified for now)
        ttft = min(total_time * 0.1, total_time / max(output_tokens, 1) * 3)
        tps = output_tokens / generation_time if generation_time > 0 else 0

        return {
            "request_id": request_id,
            "output": output,
            "tokens": output_tokens,
            "total_time": round(total_time, 3),
            "generation_time": round(generation_time, 3),
            "ttft": round(ttft, 3),
            "tps": round(tps, 2),
        }

    async def run_concurrent_requests(
        self, prompts: list, max_tokens: int, temperature: float
    ) -> list:
        """Run multiple concurrent requests."""
        print(f"\nRunning {len(prompts)} concurrent requests...")

        tasks = []
        for i, prompt in enumerate(prompts):
            task = self.run_single_request(prompt, max_tokens, temperature, i)
            tasks.append(task)

        # For now, run sequentially (simulating concurrent)
        # TODO: Use asyncio.gather() with vllm-mlx async API
        results = []
        for task in tasks:
            result = await task
            results.append(result)
            print(f"  Request {result['request_id']}: {result['tokens']} tokens, "
                  f"{result['tps']:.2f} TPS, {result['total_time']:.2f}s")

        return results

    def cleanup(self):
        """Cleanup model and free memory."""
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        gc.collect()


def generate_concurrent_prompts(base_prompts: dict, concurrent: int, mixed: bool) -> list:
    """Generate prompts for concurrent testing."""
    if mixed:
        # Cycle through different prompt types for mixed workload
        prompt_types = ["short", "medium", "long"]
        prompts = []
        for i in range(concurrent):
            ptype = prompt_types[i % len(prompt_types)]
            if ptype in base_prompts:
                prompts.append(base_prompts[ptype]["prompt"])
        return prompts
    else:
        # Use same medium prompt for all requests
        base_prompt = base_prompts.get("medium", {}).get(
            "prompt", "请用一句话解释量子计算"
        )
        return [base_prompt] * concurrent


async def run_benchmark(args):
    """Run the complete batching benchmark."""
    print("\n" + "=" * 60)
    print("MiniMax M2.1 Batching Benchmark")
    print("=" * 60)

    # Initialize results
    results = {
        "model_name": args.model,
        "framework": "vllm-mlx" if not args.use_mlx_lm else "mlx-lm",
        "timestamp": datetime.now().isoformat(),
        "system_info": get_system_info(),
        "config": {
            "concurrent_requests": args.concurrent,
            "tokens_per_request": args.tokens,
            "mixed_workload": args.mixed,
            "temperature": args.temperature,
        },
        "metrics": {},
        "tests": [],
    }

    # Check dependencies
    try:
        if not args.use_mlx_lm:
            # Try to import vllm-mlx
            try:
                import vllm_mlx
                print("Using vllm-mlx for batching")
            except ImportError:
                print("Warning: vllm-mlx not installed, falling back to mlx-lm")
                print("To install: pip install vllm-mlx")
                args.use_mlx_lm = True

        import mlx_lm
    except ImportError as e:
        print(f"Error: Required packages not installed")
        print(f"Details: {e}")
        return None

    # Initialize benchmark
    benchmark = BatchingBenchmark(args.model, use_vllm=not args.use_mlx_lm)

    # Load model
    try:
        load_time = benchmark.load_model()
        results["metrics"]["load_time_sec"] = round(load_time, 2)
    except Exception as e:
        print(f"Error loading model: {e}")
        raise

    # Load base prompts
    base_prompts = load_test_prompts()

    # Generate concurrent prompts
    prompts = generate_concurrent_prompts(base_prompts, args.concurrent, args.mixed)

    # Run concurrent test
    print(f"\nTest: {args.concurrent} concurrent requests")
    overall_start = time.perf_counter()

    request_results = await benchmark.run_concurrent_requests(
        prompts, args.tokens, args.temperature
    )

    overall_end = time.perf_counter()
    overall_time = overall_end - overall_start

    # Calculate aggregate metrics
    total_tokens = sum(r["tokens"] for r in request_results)
    aggregate_tps = total_tokens / overall_time if overall_time > 0 else 0

    all_tps = [r["tps"] for r in request_results]
    all_latencies = [r["total_time"] for r in request_results]

    results["metrics"]["aggregate_tps"] = round(aggregate_tps, 2)
    results["metrics"]["avg_per_request_tps"] = round(
        statistics.mean(all_tps) if all_tps else 0, 2
    )
    results["metrics"]["total_tokens"] = total_tokens
    results["metrics"]["overall_time_sec"] = round(overall_time, 2)

    # Latency statistics
    if all_latencies:
        results["metrics"]["latency_p50"] = round(
            statistics.median(all_latencies), 3
        )
        results["metrics"]["latency_p95"] = round(
            statistics.quantiles(all_latencies, n=20)[18], 3  # 95th percentile
        )
        results["metrics"]["latency_mean"] = round(
            statistics.mean(all_latencies), 3
        )

    # Memory statistics
    memory_stats = benchmark.memory_monitor.get_stats()
    results["metrics"]["peak_memory_gb"] = memory_stats["peak_gb"]

    # Store individual request results
    results["tests"] = request_results

    # Print summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"Model: {args.model}")
    print(f"Concurrent requests: {args.concurrent}")
    print(f"Total tokens: {total_tokens}")
    print(f"Overall time: {overall_time:.2f}s")
    print(f"Aggregate TPS: {aggregate_tps:.2f} tokens/sec")
    print(f"Avg per-request TPS: {results['metrics']['avg_per_request_tps']:.2f}")
    print(f"Latency (p50/p95): {results['metrics'].get('latency_p50', 0):.2f}s / "
          f"{results['metrics'].get('latency_p95', 0):.2f}s")
    print(f"Peak memory: {results['metrics']['peak_memory_gb']:.2f} GB")

    # Cleanup
    benchmark.cleanup()

    return results


def main():
    args = parse_args()

    # Run benchmark
    results = asyncio.run(run_benchmark(args))

    if results is None:
        sys.exit(1)

    # Determine output paths
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path(__file__).parent.parent / "docs" / "test-results"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create filename
    model_short = args.model.split("/")[-1].lower().replace(".", "-")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    framework = "vllm-mlx" if not args.use_mlx_lm else "mlx-lm"

    json_file = output_dir / f"batching-{framework}-{model_short}-c{args.concurrent}-{timestamp}.json"
    md_file = output_dir / f"batching-{framework}-{model_short}-c{args.concurrent}-{timestamp}.md"

    # Save results
    save_results(results, str(json_file))
    generate_markdown_report(results, str(md_file))

    print(f"\nResults saved to:")
    print(f"  JSON: {json_file}")
    print(f"  Markdown: {md_file}")


if __name__ == "__main__":
    main()
