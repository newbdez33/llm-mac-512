"""
Utility functions for MiniMax M2.1 benchmarking
"""

import json
import os
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import psutil


def get_memory_usage() -> dict:
    """Get current memory usage statistics."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total_gb": round(mem.total / (1024**3), 2),
        "available_gb": round(mem.available / (1024**3), 2),
        "used_gb": round(mem.used / (1024**3), 2),
        "percent": mem.percent,
        "swap_used_gb": round(swap.used / (1024**3), 2),
    }


class MemoryMonitor:
    """Monitor memory usage during model operations."""

    def __init__(self):
        self.peak_memory_gb = 0
        self.samples = []
        self._monitoring = False

    def sample(self):
        """Take a memory sample."""
        mem = get_memory_usage()
        used = mem["used_gb"]
        self.samples.append(used)
        if used > self.peak_memory_gb:
            self.peak_memory_gb = used
        return used

    def get_stats(self) -> dict:
        """Get memory statistics."""
        if not self.samples:
            return {"peak_gb": 0, "avg_gb": 0, "samples": 0}
        return {
            "peak_gb": round(self.peak_memory_gb, 2),
            "avg_gb": round(sum(self.samples) / len(self.samples), 2),
            "samples": len(self.samples),
        }


class Timer:
    """Simple context manager for timing operations."""

    def __init__(self, name: str = ""):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.duration = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time

    @property
    def elapsed(self) -> float:
        if self.duration is not None:
            return self.duration
        if self.start_time is not None:
            return time.perf_counter() - self.start_time
        return 0


def load_test_prompts(prompts_file: Optional[str] = None) -> dict:
    """Load test prompts from JSON file."""
    if prompts_file is None:
        prompts_file = Path(__file__).parent.parent / "prompts" / "test_prompts.json"
    with open(prompts_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_results(results: dict, output_file: str):
    """Save benchmark results to JSON file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results saved to: {output_path}")


def generate_markdown_report(results: dict, output_file: str):
    """Generate a markdown report from benchmark results."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    model_name = results.get("model_name", "Unknown")
    framework = results.get("framework", "Unknown")
    timestamp = results.get("timestamp", datetime.now().isoformat())

    lines = [
        f"# {model_name} 性能测试报告",
        "",
        f"> 测试时间: {timestamp}",
        f"> 框架: {framework}",
        "",
        "## 系统信息",
        "",
        "| 项目 | 值 |",
        "|------|-----|",
    ]

    sys_info = results.get("system_info", {})
    for key, value in sys_info.items():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## 性能指标",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
    ])

    metrics = results.get("metrics", {})
    metric_labels = {
        "load_time_sec": "模型加载时间 (秒)",
        "peak_memory_gb": "内存峰值 (GB)",
        "avg_tps": "平均生成速度 (tokens/sec)",
        "avg_ttft_sec": "平均首token延迟 (秒)",
    }
    for key, label in metric_labels.items():
        if key in metrics:
            lines.append(f"| {label} | {metrics[key]:.2f} |")

    lines.extend([
        "",
        "## 测试详情",
        "",
    ])

    tests = results.get("tests", [])
    for test in tests:
        test_name = test.get("name", "Unknown")
        lines.extend([
            f"### {test_name}",
            "",
            f"**Prompt:** {test.get('prompt', '')[:100]}...",
            "",
            f"- TTFT: {test.get('ttft_sec', 0):.3f} 秒",
            f"- 生成速度: {test.get('tps', 0):.2f} tokens/sec",
            f"- 总tokens: {test.get('total_tokens', 0)}",
            f"- 生成时间: {test.get('generation_time_sec', 0):.2f} 秒",
            "",
            "**输出预览:**",
            "```",
            test.get("output", "")[:500] + ("..." if len(test.get("output", "")) > 500 else ""),
            "```",
            "",
        ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Report saved to: {output_path}")


def get_system_info() -> dict:
    """Get system information."""
    info = {
        "platform": "macOS",
        "python_version": subprocess.check_output(["python3", "--version"]).decode().strip(),
    }

    # Get macOS version
    try:
        sw_vers = subprocess.check_output(["sw_vers", "-productVersion"]).decode().strip()
        info["macos_version"] = sw_vers
    except Exception:
        pass

    # Get chip info
    try:
        chip = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
        info["chip"] = chip
    except Exception:
        try:
            # For Apple Silicon
            chip = subprocess.check_output(["system_profiler", "SPHardwareDataType"]).decode()
            for line in chip.split("\n"):
                if "Chip" in line:
                    info["chip"] = line.split(":")[-1].strip()
                    break
        except Exception:
            pass

    # Get memory
    mem = get_memory_usage()
    info["total_memory_gb"] = mem["total_gb"]

    return info


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.2f}秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}分{secs:.1f}秒"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}小时{minutes}分"
