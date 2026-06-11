# Agnes AI Video API Reference (agnes-video-v2.0)

## Overview

Agnes Video V2.0 is a next-generation cinematic video generation model. Supports text-to-video, image-to-video, multi-image video, and keyframe animation workflows with automatic audio generation.

- **API Base URL**: `https://apihub.agnes-ai.com/v1`
- **Auth Method**: Bearer Token (`Authorization: Bearer YOUR_API_KEY`)
- **API Key Registration**: https://platform.agnes-ai.com/
- **Pricing**: $0.005/second of generated video

## Model

| Model | Use |
|-------|-----|
| `agnes-video-v2.0` | Text-to-video, image-to-video, multi-image video, keyframe animation |

## Core Capabilities

| Capability | Description |
|------------|-------------|
| Text-to-Video | Generate video directly from text prompt |
| Image-to-Video | Animate a static image into a dynamic video |
| Multi-Image Video | Use multiple reference images to guide generation |
| Keyframe Animation | Smooth transitions between multiple keyframes |
| Scene Motion Control | Control subject motion, camera motion, and scene dynamics via prompts |
| Visual Consistency | Maintain strong subject, style, and scene coherence across frames |
| Asynchronous API | Submit task first, then poll results by video ID |

## Workflow

Agnes-Video-V2.0 uses an **asynchronous task** workflow:

1. **POST** `/v1/videos` → Submit video generation task, get back an `id`
2. **GET** `/v1/videos/{id}` → Poll for completion using `id` (video_id)

### Step 1: Create Video Task

**Endpoint**: `POST https://apihub.agnes-ai.com/v1/videos`

**Text-to-Video Example**:
```bash
curl -X POST https://apihub.agnes-ai.com/v1/videos \
-H "Authorization: Bearer YOUR_API_KEY" \
-H "Content-Type: application/json" \
-d '{
    "model": "agnes-video-v2.0",
    "prompt": "A cinematic shot of a cat walking on the beach at sunset, soft ocean waves, warm golden lighting, realistic motion",
    "height": 768,
    "width": 1152,
    "num_frames": 121,
    "frame_rate": 24
}'
```

**Response**:
```json
{
    "id": "task_123456",
    "object": "video",
    "model": "agnes-video-v2.0",
    "status": "queued",
    "progress": 0,
    "created_at": 1774344160
}
```

**Image-to-Video Example**:
```bash
curl -X POST https://apihub.agnes-ai.com/v1/videos \
-H "Authorization: Bearer YOUR_API_KEY" \
-H "Content-Type: application/json" \
-d '{
    "model": "agnes-video-v2.0",
    "prompt": "The woman slowly turns around and looks back at the camera",
    "image": "https://example.com/image.png",
    "num_frames": 121,
    "frame_rate": 24
}'
```

**Multi-Image Video Example**:
```bash
curl -X POST https://apihub.agnes-ai.com/v1/videos \
-H "Authorization: Bearer YOUR_API_KEY" \
-H "Content-Type: application/json" \
-d '{
    "model": "agnes-video-v2.0",
    "prompt": "Create a smooth transformation scene between the two reference images",
    "extra_body": {
      "image": [
        "https://example.com/image1.png",
        "https://example.com/image2.png"
      ]
    },
    "num_frames": 121,
    "frame_rate": 24
}'
```

**Keyframe Animation Example**:
```bash
curl -X POST https://apihub.agnes-ai.com/v1/videos \
-H "Authorization: Bearer YOUR_API_KEY" \
-H "Content-Type: application/json" \
-d '{
    "model": "agnes-video-v2.0",
    "prompt": "Generate a smooth cinematic transition between the keyframes",
    "extra_body": {
      "image": [
        "https://example.com/keyframe1.png",
        "https://example.com/keyframe2.png"
      ],
      "mode": "keyframes"
    },
    "num_frames": 121,
    "frame_rate": 24
}'
```

### Step 2: Poll for Completion

**Endpoint**: `GET https://apihub.agnes-ai.com/v1/videos/{video_id}`

**CRITICAL: Use the `id` field from the create response (video_id) for polling.**

```bash
curl -X GET https://apihub.agnes-ai.com/v1/videos/{video_id} \
-H "Authorization: Bearer YOUR_API_KEY"
```

**Response (completed)**:
```json
{
    "id": "task_123456",
    "object": "video",
    "model": "agnes-video-v2.0",
    "status": "completed",
    "progress": 100,
    "created_at": 1774344160,
    "completed_at": 1774344311,
    "video_url": "https://storage.googleapis.com/...",
    "size": "1152x768",
    "seconds": "5.0",
    "usage": {
        "duration_seconds": 151
    }
}
```

## Request Parameters

### Video Creation Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | **Yes** | Fixed value: `agnes-video-v2.0` |
| `prompt` | string | **Yes** | Video description text |
| `image` | string | No | Input image URL (for image-to-video) |
| `extra_body.image` | array | No | Array of image URLs (for multi-image or keyframe modes) |
| `mode` | string | No | Generation mode: `ti2vid` (default) or `keyframes` |
| `height` | integer | No | Video height (default: 768) |
| `width` | integer | No | Video width (default: 1152) |
| `num_frames` | integer | No | Frame count, must be <=441 and follow 8n+1 rule |
| `num_inference_steps` | integer | No | Inference steps |
| `seed` | integer | No | Random seed for reproducible results |
| `frame_rate` | number | No | Video FPS, range 1-60 |
| `negative_prompt` | string | No | Text describing content to avoid |
| `extra_body.mode` | string | No | Extra mode setting: `keyframes` for keyframe animation |

### Duration Settings

```
Duration (seconds) = num_frames / frame_rate
```

**num_frames rules**:
- Must be <= 441
- Must follow `8n + 1` format (e.g., 81, 121, 161, 241, 441)

**Recommended Settings**:

| Target Duration | num_frames | frame_rate |
|-----------------|------------|------------|
| ~5 seconds | 121 | 24 |
| ~10 seconds | 241 | 24 |
| ~18 seconds | 441 | 24 |

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | **Unique video ID — use this for polling** |
| `object` | string | Fixed: `"video"` |
| `model` | string | Fixed: `"agnes-video-v2.0"` |
| `status` | string | `queued`, `in_progress`, `completed`, `failed` |
| `progress` | integer | Progress percentage, 0-100 |
| `created_at` | integer | Unix timestamp of task creation |
| `completed_at` | integer | Unix timestamp of completion (null if not completed) |
| `video_url` | string | Generated video URL (only available when status is `completed`) |
| `size` | string | Resolution in `"WIDTHxHEIGHT"` format |
| `seconds` | string | Duration in seconds |
| `usage` | object | Usage information |

### Usage Fields

| Field | Description |
|-------|-------------|
| `usage.duration_seconds` | Total processing time in seconds |

## Task States

| State | Description |
|-------|-------------|
| `queued` | Task is waiting in the queue |
| `in_progress` | Video is being generated |
| `completed` | Video generation finished successfully |
| `failed` | Video generation failed |

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Invalid request — check request parameters |
| 401 | Unauthorized — check your API Key |
| 404 | Task not found |
| 500 | Server error |
| 503 | Service busy — retry later |

## Pricing

| Type | Price |
|------|-------|
| Video duration | $0.005 per second |

## Prompt Writing Best Practices

### Text-to-Video Structure

```
[Subject] + [Action] + [Scene/Environment] + [Camera Movement] + [Lighting] + [Style]
```

**Example**:
> A young astronaut walking across a red desert planet, dust blowing in the wind, slow cinematic tracking shot, dramatic sunset lighting, realistic sci-fi style

### Image-to-Video

Describe what should move/animate while keeping the main subject stable.

> Animate the character with subtle breathing motion, hair moving gently in the wind, background lights flickering softly, while keeping the face and outfit consistent

### Multi-Image

Describe how input images should relate to each other.

> Use the first image as the starting scene and the second image as the target scene. Create a smooth transformation with consistent lighting, natural motion, and cinematic pacing.

### Keyframe Animation

Clearly describe transitions between keyframes.

> Create a smooth transition from the first keyframe to the second keyframe, maintaining character identity, consistent camera angle, and natural motion between scenes.

## Known Issues & Notes

1. Model name must be exactly `agnes-video-v2.0`
2. Video generation is **asynchronous** — always create task first, then poll
3. `video_url` is only available when status is `completed`
4. `num_frames` must be <= 441 and follow `8n+1` format
5. Text-to-video: only `model` and `prompt` are required fields
6. Image-to-video: provide image URL via `image` parameter
7. Multi-image video: provide image URLs via `extra_body.image`
8. Keyframe animation: set `extra_body.mode` to `keyframes`
9. Polling: always use the `id` field from the create response for polling
10. English prompts produce more reliable video generation results
11. Videos include automatic AAC audio (background music, ambient sounds, speech)
