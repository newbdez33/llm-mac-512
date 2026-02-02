#!/usr/bin/env python3
"""
MiniMax M2.1 llama.cpp Benchmark Script

Usage:
    python benchmark_llama.py --model /path/to/MiniMax-M2.1-Q4_K_M.gguf
    python benchmark_llama.py --model /path/to/model.gguf --n-gpu-layers -1
"""

import argparse
import gc
import json
import os
import re
import subprocess
import sys
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
    parser = argparse.ArgumentParser(description="Benchmark MiniMax M2.1 with llama.cpp")
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Path to GGUF model file",
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
        "--n-gpu-layers",
        type=int,
        default=-1,
        help="Number of layers to offload to GPU (-1 for all)",
    )
    parser.add_argument(
        "--ctx-size",
        type=int,
        default=4096,
        help="Context size",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=None,
        help="Number of threads (default: auto)",
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
    parser.add_argument(
        "--llama-cli",
        type=str,
        default="llama-cli",
        help="Path to llama-cli executable",
    )
    return parser.parse_args()


def check_llama_cpp(llama_cli: str) -> dict:
    """Check llama.cpp installation and version."""
    try:
        result = subprocess.run(
            [llama_cli, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        version_output = result.stdout + result.stderr
        return {
            "installed": True,
            "version": version_output.strip(),
            "path": llama_cli,
        }
    except FileNotFoundError:
        return {
            "installed": False,
            "error": f"llama-cli not found at: {llama_cli}",
        }
    except Exception as e:
        return {
            "installed": False,
            "error": str(e),
        }


def run_llama_generation(
    llama_cli: str,
    model_path: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    n_gpu_layers: int,
    ctx_size: int,
    threads: int = None,
    memory_monitor: MemoryMonitor = None,
) -> dict:
    """Run generation using llama-cli and parse output."""

    # Build command
    cmd = [
        llama_cli,
        "-m", model_path,
        "-p", prompt,
        "-n", str(max_tokens),
        "--temp", str(temperature),
        "-ngl", str(n_gpu_layers),
        "-c", str(ctx_size),
        "--no-display-prompt",
    ]

    if threads:
        cmd.extend(["-t", str(threads)])

    # Record start time
    start_time = time.perf_counter()

    if memory_monitor:
        memory_monitor.sample()

    # Run generation
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate()
        end_time = time.perf_counter()

        if memory_monitor:
            memory_monitor.sample()

    except Exception as e:
        return {
            "error": str(e),
            "output": "",
            "total_tokens": 0,
        }

    total_time = end_time - start_time

    # Parse llama.cpp output for timing info
    # llama.cpp prints timing stats to stderr
    timing_info = parse_llama_timing(stderr)

    # Get output text
    output = stdout.strip()

    # Estimate token count from output
    # llama.cpp should report this in timing info
    total_tokens = timing_info.get("tokens_generated", len(output.split()) * 1.3)

    # Calculate metrics
    ttft = timing_info.get("prompt_eval_time_sec", total_time * 0.1)
    generation_time = timing_info.get("eval_time_sec", total_time - ttft)

    tps = timing_info.get("tokens_per_second", 0)
    if tps == 0 and generation_time > 0:
        tps = total_tokens / generation_time

    return {
        "output": output,
        "total_tokens": int(total_tokens),
        "ttft_sec": round(ttft, 3),
        "generation_time_sec": round(generation_time, 3),
        "total_time_sec": round(total_time, 3),
        "tps": round(tps, 2),
        "timing_raw": timing_info,
        "stderr": stderr if "error" in stderr.lower() else "",
    }


def parse_llama_timing(stderr: str) -> dict:
    """Parse llama.cpp timing information from stderr."""
    timing = {}

    # Common patterns in llama.cpp output:
    # llama_print_timings:        load time =    1234.56 ms
    # llama_print_timings:      sample time =     123.45 ms /   100 runs
    # llama_print_timings: prompt eval time =    5678.90 ms /   50 tokens
    # llama_print_timings:        eval time =   12345.67 ms /   100 runs
    # llama_print_timings:       total time =   18000.00 ms /   150 tokens

    patterns = {
        "load_time_ms": r"load time\s*=\s*([\d.]+)\s*ms",
        "sample_time_ms": r"sample time\s*=\s*([\d.]+)\s*ms",
        "prompt_eval_time_ms": r"prompt eval time\s*=\s*([\d.]+)\s*ms",
        "eval_time_ms": r"eval time\s*=\s*([\d.]+)\s*ms",
        "total_time_ms": r"total time\s*=\s*([\d.]+)\s*ms",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, stderr)
        if match:
            timing[key] = float(match.group(1))

    # Convert to seconds
    if "prompt_eval_time_ms" in timing:
        timing["prompt_eval_time_sec"] = timing["prompt_eval_time_ms"] / 1000

    if "eval_time_ms" in timing:
        timing["eval_time_sec"] = timing["eval_time_ms"] / 1000

    if "load_time_ms" in timing:
        timing["load_time_sec"] = timing["load_time_ms"] / 1000

    # Parse tokens per second
    # Pattern: "eval time = ... (X.XX tokens per second)"
    tps_match = re.search(r"\(\s*([\d.]+)\s*tokens? per second\)", stderr)
    if tps_match:
        timing["tokens_per_second"] = float(tps_match.group(1))

    # Parse token counts
    tokens_match = re.search(r"eval time\s*=.*?/\s*(\d+)\s*runs", stderr)
    if tokens_match:
        timing["tokens_generated"] = int(tokens_match.group(1))

    return timing


def get_model_info(model_path: str) -> dict:
    """Get information about the GGUF model file."""
    path = Path(model_path)
    if not path.exists():
        return {"error": f"Model file not found: {model_path}"}

    size_bytes = path.stat().st_size
    size_gb = size_bytes / (1024**3)

    # Try to determine quantization from filename
    quant = "unknown"
    filename = path.name.upper()
    for q in ["Q4_K_M", "Q4_K_S", "Q5_K_M", "Q5_K_S", "Q6_K", "Q8_0", "BF16", "F16", "F32"]:
        if q in filename:
            quant = q
            break

    return {
        "path": str(path.absolute()),
        "filename": path.name,
        "size_gb": round(size_gb, 2),
        "quantization": quant,
    }


def run_benchmark(args):
    """Run the complete benchmark suite."""
    print("\n" + "=" * 60)
    print("MiniMax M2.1 llama.cpp Benchmark")
    print("=" * 60)

    # Initialize
    memory_monitor = MemoryMonitor()

    # Get model info
    model_info = get_model_info(args.model)
    if "error" in model_info:
        print(f"Error: {model_info['error']}")
        return None

    print(f"Model: {model_info['filename']}")
    print(f"Size: {model_info['size_gb']:.2f} GB")
    print(f"Quantization: {model_info['quantization']}")

    results = {
        "model_name": model_info["filename"],
        "model_path": model_info["path"],
        "quantization": model_info["quantization"],
        "model_size_gb": model_info["size_gb"],
        "framework": "llama.cpp",
        "timestamp": datetime.now().isoformat(),
        "system_info": get_system_info(),
        "config": {
            "temperature": args.temperature,
            "n_gpu_layers": args.n_gpu_layers,
            "ctx_size": args.ctx_size,
            "threads": args.threads,
            "max_tokens_override": args.max_tokens,
        },
        "metrics": {},
        "tests": [],
    }

    # Check llama.cpp installation
    llama_info = check_llama_cpp(args.llama_cli)
    if not llama_info["installed"]:
        print(f"Error: {llama_info['error']}")
        print("Install with: brew install llama.cpp")
        return None

    print(f"llama.cpp: {llama_info['version'][:50]}...")
    results["system_info"]["llama_cpp_version"] = llama_info["version"]

    if args.dry_run:
        print("\nDry run mode - skipping tests")
        return results

    # Load test prompts
    prompts = load_test_prompts(args.prompts)

    # Filter tests if specified
    if args.tests:
        prompts = {k: v for k, v in prompts.items() if k in args.tests}

    print(f"\nRunning {len(prompts)} tests...")

    # Run tests
    all_tps = []
    all_ttft = []
    first_load_time = None

    for test_key, test_config in prompts.items():
        print(f"\n--- Test: {test_config['name']} ({test_key}) ---")

        max_tokens = args.max_tokens or test_config.get("max_tokens", 500)
        prompt = test_config["prompt"]

        print(f"Prompt: {prompt[:50]}...")
        print(f"Max tokens: {max_tokens}")

        try:
            test_result = run_llama_generation(
                llama_cli=args.llama_cli,
                model_path=args.model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=args.temperature,
                n_gpu_layers=args.n_gpu_layers,
                ctx_size=args.ctx_size,
                threads=args.threads,
                memory_monitor=memory_monitor,
            )

            # Capture load time from first run
            if first_load_time is None and "load_time_sec" in test_result.get("timing_raw", {}):
                first_load_time = test_result["timing_raw"]["load_time_sec"]

            test_result["name"] = test_config["name"]
            test_result["key"] = test_key
            test_result["prompt"] = prompt
            test_result["max_tokens"] = max_tokens

            results["tests"].append(test_result)

            if "error" not in test_result:
                all_tps.append(test_result["tps"])
                all_ttft.append(test_result["ttft_sec"])

                print(f"TTFT: {test_result['ttft_sec']:.3f}s")
                print(f"TPS: {test_result['tps']:.2f} tokens/sec")
                print(f"Total tokens: {test_result['total_tokens']}")
                print(f"Output preview: {test_result['output'][:100]}...")
            else:
                print(f"Error: {test_result['error']}")

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

    if first_load_time:
        results["metrics"]["load_time_sec"] = round(first_load_time, 2)

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
    print(f"Model: {model_info['filename']}")
    print(f"Quantization: {model_info['quantization']}")
    if first_load_time:
        print(f"Load time: {format_duration(first_load_time)}")
    print(f"Peak memory: {results['metrics'].get('peak_memory_gb', 0):.2f} GB")
    print(f"Average TPS: {results['metrics'].get('avg_tps', 0):.2f} tokens/sec")
    print(f"Average TTFT: {results['metrics'].get('avg_ttft_sec', 0):.3f} sec")

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
    model_short = Path(args.model).stem.lower().replace(".", "-")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    json_file = output_dir / f"llama-{model_short}-{timestamp}.json"
    md_file = output_dir / f"llama-{model_short}-{timestamp}.md"

    # Save results
    if not args.dry_run:
        save_results(results, str(json_file))
        generate_markdown_report(results, str(md_file))

    print(f"\nResults saved to:")
    print(f"  JSON: {json_file}")
    print(f"  Markdown: {md_file}")


if __name__ == "__main__":
    main()
