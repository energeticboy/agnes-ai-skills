# Agnes AI API Reference

## Overview

Agnes AI is a multimodal AI platform providing free, unlimited access to image and video generation APIs. Image APIs are OpenAI-compatible.

- **API Base URL**: `https://apihub.agnes-ai.com/v1`
- **Auth Method**: Bearer Token (`Authorization: Bearer YOUR_API_KEY`)
- **API Key Registration**: https://platform.agnes-ai.com/
- **Pricing**: Free, unlimited (since 2026-06-01), no credit card required
- **Official Docs**: https://agnes-ai.com/doc/overview

## Models

| Model | Type | Use Case |
|-------|------|----------|
| `agnes-image-2.1-flash` | Image | Text-to-image only |
| `agnes-image-2.0-flash` | Image | Image-to-image, editing, multi-image composition |
| `agnes-video-v2.0` | Video | Text-to-video, image-to-video, multi-image video, keyframe animation (with auto audio) |

---

## Image Generation

### Text-to-Image

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

**Response**:

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

### Image-to-Image / Editing

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

## Video Generation

Agnes Video V2.0 supports four generation modes: text-to-video, image-to-video, multi-image video, and keyframe animation. Videos include automatic AAC audio (background music, ambient sounds, speech).

### Workflow

Video generation is **asynchronous** — use a two-step process:

1. **POST** `/v1/videos` → Submit task, get back `task_id` and `video_id`
2. **GET** `/agnesapi?video_id=<VIDEO_ID>` → Poll using `video_id` (recommended endpoint)

> ⚠️ **Must use `video_id` for polling**, not `task_id` or `id`. The recommended polling endpoint is `https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>`.

### Step 1: Create Video Task

**Endpoint**: `POST https://apihub.agnes-ai.com/v1/videos`

#### Text-to-Video

```bash
curl -X POST https://apihub.agnes-ai.com/v1/videos \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-video-v2.0",
    "prompt": "A cinematic shot of a cat walking on the beach at sunset, soft ocean waves, warm golden lighting",
    "height": 768,
    "width": 1152,
    "num_frames": 121,
    "frame_rate": 24
  }'
```

```python
import requests

headers = {"Authorization": "Bearer API_KEY", "Content-Type": "application/json"}
payload = {
    "model": "agnes-video-v2.0",
    "prompt": "A cinematic drone shot of a mountain valley at sunrise",
    "width": 1152, "height": 768,
    "num_frames": 121, "frame_rate": 24
}
resp = requests.post("https://apihub.agnes-ai.com/v1/videos",
                     headers=headers, json=payload, timeout=120)
data = resp.json()
video_id = data.get("video_id")  # ⚠️ Use video_id, not id/task_id
```

#### Image-to-Video

```python
payload = {
    "model": "agnes-video-v2.0",
    "prompt": "The woman slowly turns around and looks back at the camera",
    "image": "https://example.com/image.png",
    "num_frames": 121,
    "frame_rate": 24
}
resp = requests.post("https://apihub.agnes-ai.com/v1/videos",
                     headers=headers, json=payload, timeout=120)
video_id = resp.json().get("video_id")
```

#### Multi-Image Video

```python
payload = {
    "model": "agnes-video-v2.0",
    "prompt": "Create a smooth transformation scene between the two reference images",
    "extra_body": {
        "image": ["https://example.com/img1.png", "https://example.com/img2.png"]
    },
    "num_frames": 121,
    "frame_rate": 24
}
resp = requests.post("https://apihub.agnes-ai.com/v1/videos",
                     headers=headers, json=payload, timeout=120)
video_id = resp.json().get("video_id")
```

#### Keyframe Animation

```python
payload = {
    "model": "agnes-video-v2.0",
    "prompt": "Generate a smooth cinematic transition between the keyframes",
    "extra_body": {
        "image": ["https://example.com/kf1.png", "https://example.com/kf2.png"],
        "mode": "keyframes"
    },
    "num_frames": 121,
    "frame_rate": 24
}
resp = requests.post("https://apihub.agnes-ai.com/v1/videos",
                     headers=headers, json=payload, timeout=120)
video_id = resp.json().get("video_id")
```

**Create Response**:

```json
{
  "id": "task_YOUR_TASK_ID",
  "task_id": "task_YOUR_TASK_ID",
  "video_id": "video_YOUR_VIDEO_ID",
  "object": "video",
  "model": "agnes-video-v2.0",
  "status": "queued",
  "progress": 0,
  "created_at": 1780457477,
  "seconds": "5.0",
  "size": "1152x768"
}
```

### Step 2: Poll for Completion

**Recommended endpoint**: `GET https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>`

**Compatibility endpoint**: `GET https://apihub.agnes-ai.com/v1/videos/{task_id}` (deprecated, leads to long queues)

```python
import time

video_id = data.get("video_id")

while True:
    poll_url = f"https://apihub.agnes-ai.com/agnesapi?video_id={video_id}"
    resp = requests.get(poll_url, headers=headers, timeout=60)
    result = resp.json()

    status = result.get("status")
    progress = result.get("progress", 0)
    print(f"Status: {status}, Progress: {progress}%")

    if status == "completed":
        video_url = result.get("video_url") or result.get("remixed_from_video_id")
        break
    elif status == "failed":
        raise Exception(f"Video generation failed: {result.get('error') or result}")

    time.sleep(5)  # Official recommendation: 5s interval
```

**Completed Response**:

```json
{
  "id": "task_YOUR_TASK_ID",
  "video_id": "video_YOUR_VIDEO_ID",
  "model": "agnes-video-v2.0",
  "object": "video",
  "status": "completed",
  "progress": 100,
  "seconds": "5.0",
  "size": "1152x768",
  "video_url": "https://storage.googleapis.com/agnes-aigc/aigc/videos/2026/06/03/video_xxxxxx.mp4",
  "error": null
}
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | **Yes** | Fixed: `agnes-video-v2.0` |
| `prompt` | string | **Yes** | Video description text |
| `image` | string | No | Input image URL (for image-to-video) |
| `extra_body.image` | array | No | Array of image URLs (for multi-image or keyframe) |
| `extra_body.mode` | string | No | `keyframes` for keyframe animation mode |
| `height` | integer | No | Video height (default: 768) |
| `width` | integer | No | Video width (default: 1152) |
| `num_frames` | integer | No | Frame count, ≤441, must follow `8n+1` |
| `num_inference_steps` | integer | No | Inference steps |
| `seed` | integer | No | Random seed for reproducible results |
| `frame_rate` | number | No | Video FPS, range 1-60 |
| `negative_prompt` | string | No | Text describing content to avoid |

### Duration Control

```
Duration (seconds) = num_frames / frame_rate
```

- `num_frames` ≤ 441, must be `8n+1` (e.g., 81, 121, 161, 241, 441)
- `frame_rate`: 1-60

| Target Duration | num_frames | frame_rate |
|-----------------|------------|------------|
| ~3 seconds | 81 | 24 |
| ~5 seconds | 121 | 24 |
| ~10 seconds | 241 | 24 |
| ~18 seconds | 441 | 24 |

### Task States

| State | Description |
|-------|-------------|
| `queued` | Task waiting in queue |
| `in_progress` | Video being generated |
| `completed` | Generation finished successfully |
| `failed` | Generation failed |

### Error Codes

| Code | Description |
|------|-------------|
| 400 | Invalid request — check request parameters |
| 401 | Unauthorized — check API Key |
| 404 | Task or video not found |
| 500 | Server error |
| 503 | Service busy — retry later |

### Known Issues

1. **Field name**: The actual video URL field may be `video_url` or `remixed_from_video_id`. Always use: `result.get("video_url") or result.get("remixed_from_video_id")`
2. **Polling**: Must use `video_id` with recommended endpoint `/agnesapi?video_id=`. Using `task_id` with old endpoint leads to long queues
3. **Generation time**: ~2-5 minutes for a 5-second video
4. **Prompt language**: English prompts produce more reliable video results
5. **num_frames**: Must satisfy `8n+1` format and be ≤ 441

### Prompt Best Practices

**Text-to-Video**: `[Subject] + [Action] + [Scene] + [Camera Movement] + [Lighting] + [Style]`

> A young astronaut walking across a red desert planet, dust blowing in the wind, slow cinematic tracking shot, dramatic sunset lighting, realistic sci-fi style

**Image-to-Video**: Describe what should move while keeping the subject stable.

> Animate the character with subtle breathing motion, hair moving gently in the wind, background lights flickering softly, while keeping the face and outfit consistent

**Multi-Image**: Describe how input images relate.

> Use the first image as the starting scene and the second image as the target scene. Create a smooth transformation with consistent lighting, natural motion, and cinematic pacing

**Keyframe Animation**: Describe transitions between keyframes.

> Create a smooth transition from the first keyframe to the second keyframe, maintaining character identity, consistent camera angle, and natural motion between scenes
