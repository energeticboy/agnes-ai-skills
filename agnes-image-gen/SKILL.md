---
name: agnes-image-gen
description: "Agnes AI image generation using agnes-image-2.1-flash (text-to-image) and agnes-image-2.0-flash (image-to-image). Generates images and edits images via the OpenAI-compatible API at https://apihub.agnes-ai.com/v1. Use this skill when the user wants to generate images from text prompts, transform images using references, or perform image editing. Trigger keywords: Agnes AI 生图, agnes-image, agnes image gen, agnes 图片, generate image, 文生图, 图生图, image generation."
agent_created: true
---

# Agnes Image Generation Skill

Generate and edit images using Agnes AI multimodal API. Provides text-to-image and image-to-image capabilities through an OpenAI-compatible interface.

## Prerequisites

The user must have an Agnes AI API key. If they do not:

1. Direct them to https://platform.agnes-ai.com/ to register
2. After login, navigate to API Keys and create a new key
3. No credit card required — completely free

## API Basics

- **Base URL**: `https://apihub.agnes-ai.com/v1`
- **Auth**: Bearer token via `Authorization` header
- **Compatibility**: OpenAI SDK compatible
- **Full API docs**: Load `references/api_docs.md` when detailed parameter info is needed

## Models

| Model | Use |
|-------|-----|
| `agnes-image-2.1-flash` | Text-to-image |
| `agnes-image-2.0-flash` | Image-to-image, editing, multi-image composition |

## Image Generation

### Using the Bundled Script (Recommended)

The `scripts/generate_image.py` script handles both text-to-image and image-to-image:

```bash
# Text-to-image (using AGNES_API_KEY env var)
python scripts/generate_image.py \
  --prompt "一只可爱的柴犬在樱花树下睡觉" \
  --size 1024x1024 \
  -o output.png

# Image-to-image (style transfer, editing)
python scripts/generate_image.py \
  --prompt "改成水彩画风格" \
  --image https://example.com/photo.png \
  --size 1024x768 \
  -o output.png
```

> **API Key**: 脚本会自动读取 `AGNES_API_KEY` 环境变量,无需手动传入 `--api-key`。也可以显式传入 `--api-key YOUR_KEY` 覆盖环境变量。

### Direct API Call

When the script cannot be used, make a direct API call:

```python
from openai import OpenAI

client = OpenAI(
    api_key="API_KEY",
    base_url="https://apihub.agnes-ai.com/v1"
)

# Text-to-image — DO NOT pass extra_body
response = client.images.generate(
    model="agnes-image-2.1-flash",
    prompt="prompt text",
    size="1024x1024"
)
image_url = response.data[0].url

# Image-to-image — MUST pass extra_body
response = client.images.generate(
    model="agnes-image-2.0-flash",
    prompt="transformation description",
    size="1024x768",
    extra_body={
        "tags": ["img2img"],
        "image": ["https://example.com/source.png"],
        "response_format": "url"
    }
)
```

### Key Rules for Image Generation

- Text-to-image: use `agnes-image-2.1-flash`, do NOT include `extra_body`
- Image-to-image: use `agnes-image-2.0-flash`, MUST include `extra_body` with `tags=["img2img"]`
- Chinese prompts are fully supported
- Supported sizes: `1024x1024`, `1024x768`, `768x1024`, `512x512`

## Workflow

When the user asks to generate an image or edit an image:

1. Scripts automatically read `AGNES_API_KEY` env var — no need to pass `--api-key`
2. Determine if it is text-to-image, image-to-image, or image editing
3. For image generation: run `scripts/generate_image.py` with appropriate flags (no `--api-key` needed if env var is set)
4. For image-to-image: run `scripts/generate_image.py --image URL --prompt description`
5. After generation, deliver the output file to the user

If direct API calls are preferred (e.g., within a Python environment), use the
OpenAI SDK as shown above. Load
`references/api_docs.md` for comprehensive parameter details, response formats,
and troubleshooting known issues.
