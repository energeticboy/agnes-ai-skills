# Agnes AI Image API Reference

## Overview

Agnes AI provides free, unlimited image generation through an OpenAI-compatible interface.

- **API Base URL**: `https://apihub.agnes-ai.com/v1`
- **Auth Method**: Bearer Token
- **API Key Registration**: https://platform.agnes-ai.com/
- **Pricing**: Free, unlimited (since 2026-06-01), no credit card required

## Models

| Model | Use |
|-------|-----|
| `agnes-image-2.1-flash` | Text-to-image only |
| `agnes-image-2.0-flash` | Image-to-image, editing, multi-image composition |

---

## Text-to-Image

**Model**: `agnes-image-2.1-flash`

**Request** (OpenAI SDK):
```python
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="https://apihub.agnes-ai.com/v1"
)

response = client.images.generate(
    model="agnes-image-2.1-flash",
    prompt="Your prompt here (supports Chinese)",
    size="1024x1024"
)

image_url = response.data[0].url
```

**Important rules**:
- Do NOT pass `extra_body` for text-to-image models — it will error
- Chinese prompts are fully supported
- Supported sizes: `1024x1024`, `1024x768`, `768x1024`, `512x512`

### Response

```json
{
  "created": 1717600000,
  "data": [
    {
      "url": "https://storage.googleapis.com/agnes-aigc-test/images/..."
    }
  ]
}
```

---

## Image-to-Image / Editing

**Model**: `agnes-image-2.0-flash`

```python
response = client.images.generate(
    model="agnes-image-2.0-flash",
    prompt="Describe the desired transformation",
    size="1024x768",
    extra_body={
        "tags": ["img2img"],
        "image": ["https://example.com/source.png"],
        "response_format": "url"
    }
)
```

**extra_body parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `tags` | list | Must include `["img2img"]` for image editing |
| `image` | list | Array of image URLs (1 or more) |
| `response_format` | string | `"url"` or `"b64_json"` |

---

## Python CLI Script

The skill includes `scripts/generate_image.py` which wraps the API calls:

```bash
# Text-to-image
python scripts/generate_image.py --api-key KEY --prompt "prompt" [-o output.png] [-s SIZE]

# Image-to-image
python scripts/generate_image.py --api-key KEY --prompt "prompt" --image URL [-o output.png] [-s SIZE]
```

Supported flags:
- `--api-key`: API key (or `AGNES_API_KEY` env var)
- `--prompt`: Required. Image generation prompt (Chinese/English supported)
- `--size`: Output size, default `1024x1024`. Options: `1024x1024`, `1024x768`, `768x1024`, `512x512`
- `--image`: Reference image URL(s) for img2img. Repeat for multiple: `--image URL1 --image URL2`
- `--output`, `-o`: Output file path, default `output.png`
