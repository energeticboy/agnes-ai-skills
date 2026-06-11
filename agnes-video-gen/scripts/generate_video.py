#!/usr/bin/env python3
"""
Agnes AI Video Generation Script

Uses agnes-video-v2.0 for text-to-video, image-to-video, multi-image video,
and keyframe animation with automatic audio.

视频生成是异步任务。工作流：
1. POST /v1/videos 创建视频任务
2. GET /agnesapi?video_id=<VIDEO_ID> 轮询结果（推荐方式）

⚠️ 关键规则:
- 创建响应中用 video_id 字段轮询，不要用 id / task_id
- 推荐查询端点: https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>
- 官方建议轮询间隔 5 秒
"""

import argparse
import os
import sys
import time
from urllib.request import urlopen

import requests


BASE_URL = "https://apihub.agnes-ai.com/v1"
POLL_URL = "https://apihub.agnes-ai.com/agnesapi"


def _safe_print(*args, **kwargs):
    """Print safely on Windows GBK consoles by stripping non-ASCII."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        ascii_args = tuple(str(a).encode("ascii", errors="replace").decode("ascii") for a in args)
        print(*ascii_args, **kwargs)


def download_video(url, output_path):
    """Download a video from a URL and save to disk."""
    _safe_print(f"[DL] Downloading: {url}")
    with urlopen(url) as resp:
        data = resp.read()
    with open(output_path, "wb") as f:
        f.write(data)
    _safe_print(f"[OK] Saved: {output_path}")


def calculate_frames(duration_seconds, frame_rate=24):
    """Calculate num_frames for given duration. Must satisfy: <=441 and format 8n+1."""
    target = int(duration_seconds * frame_rate)
    target = min(max(target, 9), 441)
    return ((target - 1) // 8) * 8 + 1


def generate_video(api_key, prompt, width, height, duration, frame_rate, output_path,
                   image=None, images=None, mode="ti2vid", negative_prompt=None,
                   seed=None, num_inference_steps=None,
                   poll_interval=5, max_wait=900):
    """Generate a video from prompt using agnes-video-v2.0."""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    num_frames = calculate_frames(duration, frame_rate)
    actual_duration = num_frames / frame_rate

    _safe_print("[Video] Starting video generation...")
    _safe_print(f"        Prompt:      {prompt}")
    _safe_print(f"        Resolution:  {width}x{height}")
    _safe_print(f"        Frames:      {num_frames} @ {frame_rate}fps")
    _safe_print(f"        Duration:    ~{actual_duration:.1f}s")
    _safe_print(f"        Mode:        {mode}")

    # Build payload
    payload = {
        "model": "agnes-video-v2.0",
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_frames": num_frames,
        "frame_rate": frame_rate,
    }

    if image:
        payload["image"] = image
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt
    if seed is not None:
        payload["seed"] = seed
    if num_inference_steps is not None:
        payload["num_inference_steps"] = num_inference_steps

    if images and mode == "keyframes":
        payload["extra_body"] = {
            "image": [img.strip() for img in images.split(",")],
            "mode": "keyframes"
        }
    elif images:
        payload["extra_body"] = {
            "image": [img.strip() for img in images.split(",")]
        }

    # Step 1: Create task
    _safe_print("[Step 1] Creating video task...")
    resp = requests.post(f"{BASE_URL}/videos", headers=headers, json=payload, timeout=120)
    if resp.status_code != 200:
        _safe_print(f"[ERR] Task creation failed (HTTP {resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    _safe_print(f"[Task] Created: id={data.get('id')}, video_id={data.get('video_id')}, status={data.get('status')}")

    # ⚠️ 关键：必须用 video_id 字段轮询推荐端点，不是 id / task_id
    video_id = data.get("video_id")
    if not video_id:
        _safe_print(f"[ERR] No video_id in response: {data}", file=sys.stderr)
        sys.exit(1)

    _safe_print(f"[Task] Polling with video_id: {video_id}")
    _safe_print(f"[Step 2] Polling for completion (recommended endpoint, every {poll_interval}s)...")

    elapsed = 0
    while elapsed < max_wait:
        time.sleep(poll_interval)
        elapsed += poll_interval

        try:
            # 推荐查询端点: /agnesapi?video_id=<VIDEO_ID>
            poll_params = {"video_id": video_id}
            _safe_print(f"      Polling [{elapsed}s]...")
            resp = requests.get(POLL_URL, headers=headers, params=poll_params, timeout=60)
        except Exception as e:
            _safe_print(f"[Warn] Network error, retrying: {e}")
            elapsed -= poll_interval
            continue

        if resp.status_code != 200:
            _safe_print(f"[Warn] Poll HTTP {resp.status_code}, retrying...")
            continue

        result = resp.json()
        status = result.get("status", "")
        progress = result.get("progress", 0)
        _safe_print(f"      [{elapsed}s] {status} (progress: {progress}%)")

        if status == "completed":
            # 注意：实际响应中视频URL字段名为 remixed_from_video_id
            # 官方文档说 video_url，但实际可能返回 remixed_from_video_id
            video_url = result.get("video_url") or result.get("remixed_from_video_id")
            if not video_url:
                _safe_print(f"[ERR] Completed but no video_url in response: {result}", file=sys.stderr)
                sys.exit(1)
            _safe_print(f"[OK] Generation complete! Elapsed: ~{elapsed}s")
            download_video(video_url, output_path)
            return

        elif status == "failed":
            error_msg = result.get("error", str(result))
            _safe_print(f"[ERR] Video generation failed: {error_msg}", file=sys.stderr)
            sys.exit(1)

    _safe_print(f"[ERR] Timed out ({max_wait}s), task incomplete", file=sys.stderr)
    sys.exit(1)


def parse_size(size_str):
    """Parse 'WIDTHxHEIGHT' string into (width, height) tuple."""
    try:
        w, h = size_str.lower().split("x")
        return int(w), int(h)
    except (ValueError, AttributeError):
        _safe_print(f"[ERR] Invalid size format: {size_str} (expected WIDTHxHEIGHT)", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Agnes AI Video Generation (agnes-video-v2.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Text-to-video (5 seconds)
  python generate_video.py --prompt "A drone flying over mountains at sunrise"

  # Text-to-video (10 seconds)
  python generate_video.py --prompt "Tokyo night market, neon lights" --duration 10

  # Image-to-video
  python generate_video.py --prompt "The character turns around" --image https://example.com/img.png

  # Keyframe animation
  python generate_video.py --prompt "Smooth transition" --images kf1.png,kf2.png --mode keyframes

  # Max duration (18 seconds)
  python generate_video.py --prompt "Flower blooming time-lapse" --duration 18
        """,
    )

    parser.add_argument("--api-key", help="Agnes AI API key (or set AGNES_API_KEY env var)")
    parser.add_argument("--prompt", required=True, help="Video description prompt (English recommended for best results)")
    parser.add_argument("--duration", type=float, default=5.0, help="Target video duration in seconds (default: 5, max: ~18)")
    parser.add_argument("--size", default="1152x768", help="Video resolution WIDTHxHEIGHT (default: 1152x768)")
    parser.add_argument("--frame-rate", type=int, default=24, help="Frame rate (default: 24, range: 1-60)")
    parser.add_argument("--image", default=None, help="Single input image URL for image-to-video")
    parser.add_argument("--images", default=None, help="Comma-separated image URLs for multi-image or keyframe modes")
    parser.add_argument("--mode", default="ti2vid", choices=["ti2vid", "keyframes"], help="Generation mode (default: ti2vid)")
    parser.add_argument("--negative-prompt", default=None, help="Prompt describing content to avoid")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible results")
    parser.add_argument("--steps", type=int, default=None, help="Number of inference steps (num_inference_steps)")
    parser.add_argument("--output", "-o", default="output.mp4", help="Output file path (default: output.mp4)")
    parser.add_argument("--poll-interval", type=int, default=5, help="Polling interval in seconds (default: 5, official recommendation)")
    parser.add_argument("--max-wait", type=int, default=900, help="Maximum wait time in seconds (default: 900)")

    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("AGNES_API_KEY")
    if not api_key:
        _safe_print("[ERR] No API Key provided. Use --api-key or set AGNES_API_KEY env var.", file=sys.stderr)
        _safe_print("     Get API Key: https://platform.agnes-ai.com/", file=sys.stderr)
        sys.exit(1)

    if args.image and args.images:
        _safe_print("[ERR] Cannot use both --image and --images at the same time.", file=sys.stderr)
        sys.exit(1)

    width, height = parse_size(args.size)

    try:
        generate_video(
            api_key=api_key,
            prompt=args.prompt,
            width=width,
            height=height,
            duration=args.duration,
            frame_rate=args.frame_rate,
            output_path=args.output,
            image=args.image,
            images=args.images,
            mode=args.mode,
            negative_prompt=args.negative_prompt,
            seed=args.seed,
            num_inference_steps=args.steps,
            poll_interval=args.poll_interval,
            max_wait=args.max_wait,
        )
    except KeyboardInterrupt:
        _safe_print("\n[Cancelled]")
        sys.exit(130)
    except Exception as e:
        _safe_print(f"[ERR] Generation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
