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

                # 发送完整响应（简化的流式）
                chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model_name,
                    "choices": [{
                        "index": 0,
                        "delta": {"content": response},
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

            # 计算tokens
            prompt_tokens = len(tokenizer.encode(prompt))
            completion_tokens = len(tokenizer.encode(response))
            total_tokens = prompt_tokens + completion_tokens

            # 返回OpenAI格式的响应
            return jsonify({
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model_name,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response
                    },
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
    args = parse_args()

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
