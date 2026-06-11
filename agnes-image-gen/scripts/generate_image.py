#!/usr/bin/env python3
"""
Agnes AI Image Generation Script

Supports:
  - Text-to-Image with agnes-image-2.1-flash
  - Image-to-Image with agnes-image-2.0-flash

Usage:
  # Text-to-image
  python generate_image.py \\
    --api-key YOUR_KEY \\
    --prompt "一只可爱的柴犬在樱花树下睡觉" \\
    --output shiba.png

  # Text-to-image with custom size
  python generate_image.py \\
    --api-key YOUR_KEY \\
    --prompt "A futuristic cyberpunk city at night" \\
    --size 1024x768 \\
    --output cyberpunk.png

  # Image-to-image (edit existing image)
  python generate_image.py \\
    --api-key YOUR_KEY \\
    --prompt "改成水彩画风格" \\
    --image https://example.com/photo.png \\
    --output watercolor.png
"""

import argparse
import os
import sys
from urllib.request import urlopen

from openai import OpenAI


def _safe_print(*args, **kwargs):
    """Print safely on Windows GBK consoles by stripping non-ASCII."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        ascii_args = tuple(str(a).encode("ascii", errors="replace").decode("ascii") for a in args)
        print(*ascii_args, **kwargs)


def download_image(url, output_path):
    """Download an image from a URL and save to disk."""
    _safe_print(f"[DL] Downloading: {url}")
    with urlopen(url) as resp:
        data = resp.read()
    with open(output_path, "wb") as f:
        f.write(data)
    _safe_print(f"[OK] Saved: {output_path}")


def generate_text_to_image(client, prompt, size, output_path):
    """Generate an image from text prompt using agnes-image-2.1-flash."""
    _safe_print("[Art] Text-to-Image generating...")
    _safe_print(f"      Prompt: {prompt}")
    _safe_print(f"      Size:   {size}")

    response = client.images.generate(
        model="agnes-image-2.1-flash",
        prompt=prompt,
        size=size,
    )

    image_url = response.data[0].url
    if not image_url:
        _safe_print("[ERR] No image URL returned", file=sys.stderr)
        sys.exit(1)

    download_image(image_url, output_path)


def generate_image_to_image(client, prompt, image_urls, size, output_path):
    """Generate/transform an image from reference image(s) using agnes-image-2.0-flash."""
    _safe_print("[Img2Img] Image-to-Image generating...")
    _safe_print(f"          Prompt:     {prompt}")
    _safe_print(f"          References: {image_urls}")
    _safe_print(f"          Size:       {size}")

    response = client.images.generate(
        model="agnes-image-2.0-flash",
        prompt=prompt,
        size=size,
        extra_body={
            "tags": ["img2img"],
            "image": image_urls,
            "response_format": "url",
        },
    )

    image_url = response.data[0].url
    if not image_url:
        _safe_print("[ERR] No image URL returned", file=sys.stderr)
        sys.exit(1)

    download_image(image_url, output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Agnes AI Image Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Text-to-image (Chinese prompt)
  python generate_image.py --api-key KEY --prompt "一只柴犬在樱花树下"

  # Text-to-image (English prompt, custom size)
  python generate_image.py --api-key KEY --prompt "A cat wearing a wizard hat" --size 1024x768

  # Image-to-image (style transfer)
  python generate_image.py --api-key KEY --prompt "水彩风格" --image https://example.com/photo.png
        """,
    )

    parser.add_argument("--api-key", required=False, help="Agnes AI API key (or set AGNES_API_KEY env var)")
    parser.add_argument("--prompt", required=True, help="Image generation prompt (supports Chinese and English)")
    parser.add_argument("--size", default="1024x1024", help="Output image size (default: 1024x1024). Options: 1024x1024, 1024x768, 768x1024, 512x512")
    parser.add_argument("--image", action="append", default=[], help="Reference image URL(s) for img2img. Repeat for multiple: --image URL1 --image URL2")
    parser.add_argument("--output", "-o", default="output.png", help="Output file path (default: output.png)")

    args = parser.parse_args()

    # Resolve API key: CLI arg > env var
    api_key = args.api_key or os.environ.get("AGNES_API_KEY")
    if not api_key:
        _safe_print("[ERR] No API Key provided. Use --api-key or set AGNES_API_KEY env var.", file=sys.stderr)
        _safe_print("     Get API Key: https://platform.agnes-ai.com/", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url="https://apihub.agnes-ai.com/v1")

    try:
        if args.image:
            generate_image_to_image(client=client, prompt=args.prompt, image_urls=args.image, size=args.size, output_path=args.output)
        else:
            generate_text_to_image(client=client, prompt=args.prompt, size=args.size, output_path=args.output)
    except Exception as e:
        _safe_print(f"[ERR] Generation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
