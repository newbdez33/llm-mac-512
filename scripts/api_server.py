#!/usr/bin/env python3
"""
MLX MiniMax M2.1 OpenAI-compatible API Server

为OpenClaw等应用提供本地API服务

使用方法:
    python scripts/api_server.py
    python scripts/api_server.py --model mlx-community/MiniMax-M2.1-4bit --port 8000
"""

import argparse
import json
import re
import time
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量
model = None
tokenizer = None
model_name = None
strip_think = False  # 是否去除<think>块


def strip_think_blocks(text: str) -> str:
    """去除<think>...</think>块，只保留最终回复"""
    # 匹配 <think>...</think> 或未闭合的 <think>... 到 </think>
    # 使用 DOTALL 模式让 . 匹配换行符
    cleaned = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL)
    # 处理可能没有闭合标签的情况（模型输出被截断）
    cleaned = re.sub(r'<think>.*$', '', cleaned, flags=re.DOTALL)
    # 去除开头的空白
    cleaned = cleaned.strip()
    return cleaned if cleaned else text  # 如果清理后为空，返回原文


def parse_think_blocks(text: str) -> tuple[str, str]:
    """解析<think>块，返回 (reasoning_content, final_content)"""
    reasoning = ""
    final = text

    # 情况1: 完整的 <think>...</think> 块
    think_matches = re.findall(r'<think>(.*?)</think>', text, flags=re.DOTALL)
    if think_matches:
        reasoning = '\n'.join(think_matches).strip()
        final = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL).strip()

    # 情况2: 没有开头<think>，但有</think>结尾（模型直接输出thinking后跟</think>）
    elif '</think>' in text:
        parts = text.split('</think>', 1)
        if len(parts) == 2:
            reasoning = parts[0].strip()
            final = parts[1].strip()

    # 情况3: 只有开头<think>没有结尾（被截断）
    elif '<think>' in text:
        final = re.sub(r'<think>.*$', '', text, flags=re.DOTALL).strip()
        reasoning = re.search(r'<think>(.*)', text, flags=re.DOTALL)
        reasoning = reasoning.group(1).strip() if reasoning else ""

    return reasoning, final if final else text


def parse_args():
    parser = argparse.ArgumentParser(description="MLX API Server")
    parser.add_argument(
        "--model",
        type=str,
        default="mlx-community/MiniMax-M2.1-4bit",
        help="模型名称 (default: MiniMax-M2.1-4bit)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="服务器地址 (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="端口号 (default: 8000)",
    )
    parser.add_argument(
        "--strip-think",
        action="store_true",
        help="去除<think>块，只返回最终回复 (适用于MiniMax M2.1等reasoning模型)",
    )
    return parser.parse_args()


def load_model(model_path: str):
    """加载模型"""
    global model, tokenizer, model_name

    print(f"\n{'='*60}")
    print(f"正在加载模型: {model_path}")
    print(f"{'='*60}\n")

    start_time = time.time()
    model, tokenizer = load(model_path)
    model_name = model_path
    load_time = time.time() - start_time

    print(f"✓ 模型加载完成！用时 {load_time:.2f} 秒\n")


def format_prompt(messages: List[Dict[str, str]]) -> str:
    """将OpenAI格式的messages转换为prompt"""
    if hasattr(tokenizer, 'apply_chat_template'):
        # 使用模型自带的chat template
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
    else:
        # 简单拼接
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"
        prompt += "Assistant: "
        return prompt


@app.route("/v1/models", methods=["GET"])
def list_models():
    """列出可用模型"""
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": model_name,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "local",
            }
        ]
    })


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    """OpenAI兼容的chat completions端点"""
    try:
        data = request.json

        # 解析参数
        messages = data.get("messages", [])
        max_tokens = data.get("max_tokens", 500)
        temperature = data.get("temperature", 0.7)
        stream = data.get("stream", False)

        if not messages:
            return jsonify({"error": "messages is required"}), 400

        # 格式化prompt
        prompt = format_prompt(messages)

        # 创建采样器
        sampler = make_sampler(temp=temperature)

        # 生成回复
        start_time = time.time()

        if stream:
            # 流式响应（简化版本，实际流式需要更复杂的实现）
            def generate_stream():
                response = generate(
                    model,
                    tokenizer,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    sampler=sampler,
                    verbose=False
                )

                # 创建响应ID
                response_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"

                # 解析thinking内容
                reasoning_content, final_content = parse_think_blocks(response)

                # 发送完整响应（简化的流式）
                delta = {"content": final_content}
                if reasoning_content:
                    delta["reasoning_content"] = reasoning_content

                chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model_name,
                    "choices": [{
                        "index": 0,
                        "delta": delta,
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: [DONE]\n\n"

            return Response(
                stream_with_context(generate_stream()),
                mimetype="text/event-stream"
            )

        else:
            # 非流式响应
            response = generate(
                model,
                tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                sampler=sampler,
                verbose=False
            )

            generation_time = time.time() - start_time

            # 解析thinking内容
            reasoning_content, final_content = parse_think_blocks(response)

            # 根据设置选择输出
            if strip_think:
                output_content = final_content
            else:
                output_content = response  # 保留原始响应

            # 计算tokens
            prompt_tokens = len(tokenizer.encode(prompt))
            completion_tokens = len(tokenizer.encode(response))
            total_tokens = prompt_tokens + completion_tokens

            # 构建消息对象
            message = {
                "role": "assistant",
                "content": final_content  # 总是返回清理后的内容作为主要content
            }

            # 如果有reasoning内容，添加到响应中（类似云API）
            if reasoning_content:
                message["reasoning_content"] = reasoning_content

            # 返回OpenAI格式的响应
            return jsonify({
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model_name,
                "choices": [{
                    "index": 0,
                    "message": message,
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                },
                "system_fingerprint": f"mlx-{model_name}",
                # 自定义字段
                "_mlx_stats": {
                    "generation_time": round(generation_time, 2),
                    "tokens_per_second": round(completion_tokens / generation_time, 2) if generation_time > 0 else 0
                }
            })

    except Exception as e:
        return jsonify({
            "error": {
                "message": str(e),
                "type": "internal_error",
                "code": 500
            }
        }), 500


@app.route("/v1/responses", methods=["POST"])
def responses():
    """OpenAI Responses API端点（用于openai-responses API类型）"""
    try:
        data = request.json

        # Responses API使用input字段
        input_data = data.get("input", data.get("messages", []))
        max_tokens = data.get("max_output_tokens", data.get("max_tokens", 500))
        temperature = data.get("temperature", 0.7)

        # 转换input格式为messages
        if isinstance(input_data, str):
            messages = [{"role": "user", "content": input_data}]
        elif isinstance(input_data, list):
            messages = input_data
        else:
            messages = [{"role": "user", "content": str(input_data)}]

        if not messages:
            return jsonify({"error": "input is required"}), 400

        # 格式化prompt
        prompt = format_prompt(messages)

        # 创建采样器
        sampler = make_sampler(temp=temperature)

        # 生成
        start_time = time.time()
        response = generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            sampler=sampler,
            verbose=False
        )
        generation_time = time.time() - start_time

        # 解析thinking内容
        reasoning_content, final_content = parse_think_blocks(response)

        # 计算tokens
        prompt_tokens = len(tokenizer.encode(prompt))
        completion_tokens = len(tokenizer.encode(response))

        # 构建output数组（Responses API格式）
        output = []

        # 如果有reasoning，添加reasoning output
        if reasoning_content:
            output.append({
                "type": "reasoning",
                "id": f"rs_{uuid.uuid4().hex[:12]}",
                "summary": [{"type": "summary_text", "text": reasoning_content[:200] + "..." if len(reasoning_content) > 200 else reasoning_content}]
            })

        # 添加message output
        output.append({
            "type": "message",
            "id": f"msg_{uuid.uuid4().hex[:12]}",
            "role": "assistant",
            "content": [{"type": "output_text", "text": final_content}]
        })

        # 返回Responses API格式
        return jsonify({
            "id": f"resp_{uuid.uuid4().hex[:12]}",
            "object": "response",
            "created_at": int(time.time()),
            "model": model_name,
            "output": output,
            "usage": {
                "input_tokens": prompt_tokens,
                "output_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            },
            "status": "completed"
        })

    except Exception as e:
        return jsonify({
            "error": {
                "message": str(e),
                "type": "internal_error",
                "code": 500
            }
        }), 500


@app.route("/v1/completions", methods=["POST"])
def completions():
    """OpenAI兼容的completions端点（非chat）"""
    try:
        data = request.json

        prompt = data.get("prompt", "")
        max_tokens = data.get("max_tokens", 500)
        temperature = data.get("temperature", 0.7)

        if not prompt:
            return jsonify({"error": "prompt is required"}), 400

        # 创建采样器
        sampler = make_sampler(temp=temperature)

        # 生成
        start_time = time.time()
        response = generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            sampler=sampler,
            verbose=False
        )
        generation_time = time.time() - start_time

        # 计算tokens
        prompt_tokens = len(tokenizer.encode(prompt))
        completion_tokens = len(tokenizer.encode(response))

        return jsonify({
            "id": f"cmpl-{uuid.uuid4().hex[:8]}",
            "object": "text_completion",
            "created": int(time.time()),
            "model": model_name,
            "choices": [{
                "text": response,
                "index": 0,
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        })

    except Exception as e:
        return jsonify({
            "error": {
                "message": str(e),
                "type": "internal_error",
                "code": 500
            }
        }), 500


@app.route("/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "model": model_name,
        "model_loaded": model is not None
    })


@app.route("/", methods=["GET"])
def index():
    """API信息"""
    return jsonify({
        "message": "MLX MiniMax M2.1 API Server",
        "model": model_name,
        "endpoints": {
            "chat": "/v1/chat/completions",
            "completions": "/v1/completions",
            "models": "/v1/models",
            "health": "/health"
        },
        "documentation": "https://platform.openai.com/docs/api-reference"
    })


def main():
    global strip_think
    args = parse_args()

    # 设置是否去除think块
    strip_think = args.strip_think

    print("""
╔══════════════════════════════════════════════════════════╗
║         MLX MiniMax M2.1 API Server                      ║
║         OpenAI-Compatible API                            ║
╚══════════════════════════════════════════════════════════╝
""")

    # 加载模型
    load_model(args.model)

    print(f"{'='*60}")
    print(f"API 服务器配置")
    print(f"{'='*60}")
    print(f"模型: {args.model}")
    print(f"地址: http://{args.host}:{args.port}")
    print(f"去除<think>块: {'是' if strip_think else '否'}")
    print(f"端点:")
    print(f"  • Chat: http://{args.host}:{args.port}/v1/chat/completions")
    print(f"  • Completions: http://{args.host}:{args.port}/v1/completions")
    print(f"  • Models: http://{args.host}:{args.port}/v1/models")
    print(f"  • Health: http://{args.host}:{args.port}/health")
    print(f"\n按 Ctrl+C 停止服务器")
    print(f"{'='*60}\n")

    # 启动服务器
    app.run(
        host=args.host,
        port=args.port,
        debug=False,
        threaded=True
    )


if __name__ == "__main__":
    main()
