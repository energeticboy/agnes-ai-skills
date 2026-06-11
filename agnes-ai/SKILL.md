---
name: agnes-ai
description: "Agnes AI multimodal generation using agnes-image-2.1-flash (文生图), agnes-image-2.0-flash (图生图), and agnes-video-v2.0 (文生视频/图生视频/多图视频/关键帧动画). Supports image generation, image editing, and video generation with automatic audio via the OpenAI-compatible API at https://apihub.agnes-ai.com/v1. Trigger keywords: Agnes AI, agnes image, agnes video, agnes 生图, agnes 生视频, agnes 图片, agnes 视频, generate image, generate video, 文生图, 图生图, 文生视频, 图生视频."
agent_created: true
---

# Agnes AI 多模态生成

使用 Agnes AI 多模态 API 生成图片和视频。Agnes AI 提供免费且不限量的图片生成（文生图 / 图生图）和视频生成（文生视频 / 图生视频 / 多图视频 / 关键帧动画，自动附带音频），接口兼容 OpenAI SDK。

## 前提条件

用户必须有 Agnes AI API Key。如果没有：

1. 前往 https://platform.agnes-ai.com/ 注册
2. 登录后进入 API Keys 创建新 Key
3. 无需信用卡，完全免费

## API 基础

- **Base URL**: `https://apihub.agnes-ai.com/v1`
- **Auth**: Bearer Token（`Authorization` 请求头）
- **图片兼容**: OpenAI SDK 兼容
- **官方文档**: https://agnes-ai.com/doc/agnes-video-v20（视频）、https://agnes-ai.com/doc/agnes-image-v21（图片）

## 模型

| 模型 | 用途 |
|------|------|
| `agnes-image-2.1-flash` | 文生图（Text-to-Image） |
| `agnes-image-2.0-flash` | 图生图、编辑、多图合成（Image-to-Image） |
| `agnes-video-v2.0` | 文生视频 / 图生视频 / 多图视频 / 关键帧动画（自动音频） |

---

# 图片生成

## 脚本使用（推荐）

`scripts/generate_image.py` 同时支持文生图和图生图：

```bash
# 文生图（脚本自动读取 AGNES_API_KEY 环境变量）
python scripts/generate_image.py \
  --prompt "一只可爱的柴犬在樱花树下睡觉" \
  --size 1024x1024 \
  -o shiba.png

# 图生图（风格转换、编辑）
python scripts/generate_image.py \
  --prompt "改成水彩画风格" \
  --image https://example.com/photo.png \
  --size 1024x768 \
  -o watercolor.png
```

> **API Key**: 脚本自动读取 `AGNES_API_KEY` 环境变量。也可显式传入 `--api-key YOUR_KEY` 覆盖。

## 直接 API 调用

```python
from openai import OpenAI

client = OpenAI(
    api_key="API_KEY",
    base_url="https://apihub.agnes-ai.com/v1"
)

# 文生图 — 不要传 extra_body
response = client.images.generate(
    model="agnes-image-2.1-flash",
    prompt="一只可爱的柴犬",
    size="1024x1024"
)
image_url = response.data[0].url

# 图生图 — 必须传 extra_body
response = client.images.generate(
    model="agnes-image-2.0-flash",
    prompt="改成水彩画风格",
    size="1024x768",
    extra_body={
        "tags": ["img2img"],
        "image": ["https://example.com/source.png"],
        "response_format": "url"
    }
)
image_url = response.data[0].url
```

## 图片生成关键规则

- 文生图：使用 `agnes-image-2.1-flash`，**不要**传 `extra_body`
- 图生图：使用 `agnes-image-2.0-flash`，**必须**传 `extra_body` 含 `tags=["img2img"]`
- 中文 prompt 完全支持
- 支持尺寸：`1024x1024`、`1024x768`、`768x1024`、`512x512`

---

# 视频生成

## 支持的生成模式

### 1. 文生视频（默认 mode=ti2vid）

```bash
python scripts/generate_video.py \
  --prompt "A cinematic shot of a cat walking on the beach at sunset, soft ocean waves, warm golden lighting" \
  -o beach.mp4
```

### 2. 图生视频

```bash
python scripts/generate_video.py \
  --prompt "The woman slowly turns around and looks back at the camera, natural facial expression" \
  --image https://example.com/portrait.png \
  -o animated.mp4
```

### 3. 多图视频生成

```bash
python scripts/generate_video.py \
  --prompt "Create a smooth transformation scene between the two reference images, cinematic lighting" \
  --images https://example.com/img1.png,https://example.com/img2.png \
  -o transition.mp4
```

### 4. 关键帧动画（mode=keyframes）

```bash
python scripts/generate_video.py \
  --prompt "Generate a smooth cinematic transition between the keyframes" \
  --images https://example.com/kf1.png,https://example.com/kf2.png \
  --mode keyframes \
  -o transition.mp4
```

## 视频脚本参数

| 参数 | Flag | 默认值 | 说明 |
|------|------|--------|------|
| API Key | `--api-key` | `AGNES_API_KEY` 环境变量 | API 认证 |
| Prompt | `--prompt` | 必填 | 视频描述（英文效果更佳） |
| 单张图片URL | `--image` | 无 | 图生视频输入 |
| 多张图片URLs | `--images` | 无 | 逗号分隔的多张图片URL |
| 模式 | `--mode` | `ti2vid` | `ti2vid`（文生视频）或 `keyframes` |
| 分辨率 | `--size` | `1152x768` | WIDTHxHEIGHT 格式 |
| 时长 | `--duration` | 5.0 | 目标时长（秒） |
| 帧率 | `--frame-rate` | 24 | 1-60 fps |
| 推理步数 | `--steps` | 无 | num_inference_steps |
| 输出路径 | `-o` / `--output` | `output.mp4` | 输出文件路径 |
| 反向提示词 | `--negative-prompt` | 无 | 不希望出现的内容 |
| 随机种子 | `--seed` | 无 | 可复现结果 |
| 轮询间隔 | `--poll-interval` | 5 | 秒（官方建议5s） |
| 最大等待 | `--max-wait` | 900 | 秒 |

> **API Key**: 脚本自动读取 `AGNES_API_KEY` 环境变量。可显式传入 `--api-key YOUR_KEY` 覆盖。

## API Endpoints

| 操作 | Endpoint | 方法 |
|------|----------|------|
| **创建视频任务** | `https://apihub.agnes-ai.com/v1/videos` | POST |
| **查询结果（推荐）** | `https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>` | GET |
| **查询结果（兼容旧版）** | `https://apihub.agnes-ai.com/v1/videos/{task_id}` | GET |

> ⚠️ **关键规则**：
> 1. 创建任务响应中同时返回 `task_id` 和 `video_id`。**必须用 `video_id` 轮询推荐端点**，不要用 `task_id`/`id` 轮询旧版接口（会导致长队）。
> 2. 完成后的响应中视频下载 URL 字段可能为 `video_url` 或 `remixed_from_video_id`，代码需兼容两者：`result.get("video_url") or result.get("remixed_from_video_id")`

## 直接 API 调用

### Step 1 — 创建视频任务

**文生视频**：

```python
import requests

headers = {"Authorization": "Bearer API_KEY", "Content-Type": "application/json"}
payload = {
    "model": "agnes-video-v2.0",
    "prompt": "A cinematic drone shot of a mountain valley at sunrise",
    "width": 1152,
    "height": 768,
    "num_frames": 121,
    "frame_rate": 24
}
resp = requests.post("https://apihub.agnes-ai.com/v1/videos",
                     headers=headers, json=payload, timeout=120)
data = resp.json()
# ⚠️ 轮询必须用 video_id，不要用 data["id"] 或 data["task_id"]
video_id = data.get("video_id")
```

**图生视频**：

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
data = resp.json()
video_id = data.get("video_id")
```

**多图视频生成**：

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
data = resp.json()
video_id = data.get("video_id")
```

**关键帧动画**：

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
data = resp.json()
video_id = data.get("video_id")
```

### 创建任务响应

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
  "seconds": "10.0",
  "size": "1280x768"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 任务 ID（旧版查询用） |
| `task_id` | string | 任务 ID（与 id 相同） |
| `video_id` | **string** | **✅ 视频 ID — 轮询用这个** |
| `object` | string | 固定为 `"video"` |
| `model` | string | 使用的模型 |
| `status` | string | 任务状态 |
| `progress` | integer | 进度百分比 0-100 |
| `created_at` | integer | 创建时间（Unix 时间戳） |
| `seconds` | string | 视频时长（秒） |
| `size` | string | 视频分辨率 |

### Step 2 — 查询视频结果（推荐方式）

**🚨 关键规则：必须用 `video_id` 查询推荐端点，不要用 `task_id` 查旧版接口！**

```python
import time

# 从创建任务的响应中提取 video_id
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
        if video_url:
            print(f"Video URL: {video_url}")
        break
    elif status == "failed":
        error = result.get("error")
        print(f"Generation failed: {error or result}")
        break

    time.sleep(5)  # 官方建议轮询间隔 5s
```

可选：查询时传入 `model_name` 显式指定模型名：

```python
poll_url = f"https://apihub.agnes-ai.com/agnesapi?video_id={video_id}&model_name=agnes-video-v2.0"
```

### 查询结果响应（完成时）

```json
{
  "id": "task_YOUR_TASK_ID",
  "video_id": "video_YOUR_VIDEO_ID",
  "model": "agnes-video-v2.0",
  "object": "video",
  "status": "completed",
  "progress": 100,
  "seconds": "10.0",
  "size": "1280x768",
  "video_url": "https://storage.googleapis.com/agnes-aigc/aigc/videos/2026/06/03/video_xxxxxx.mp4",
  "error": null
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 任务 ID |
| `video_id` | string | 视频 ID |
| `model` | string | 使用的模型 |
| `object` | string | 对象类型 |
| `status` | string | 任务状态 |
| `progress` | integer | 进度百分比 |
| `seconds` | string | 视频时长（秒） |
| `size` | string | 视频分辨率 |
| `video_url` | **string** | **✅ 最终视频 URL（仅 completed 时可用）** |
| `error` | object / null | 错误信息（失败时返回） |

## 任务状态

| 状态 | 说明 |
|------|------|
| `queued` | 任务在队列中等待 |
| `in_progress` | 视频正在生成中 |
| `completed` | 视频已生成完成 |
| `failed` | 视频生成失败 |

## 视频时长控制

`seconds = num_frames / frame_rate`

- `num_frames` ≤ 441，且必须满足 `8n + 1`（如 81, 121, 161, 241, 441）
- `frame_rate`：1-60

### 常用时长参数

| 目标时长 | 推荐参数 |
|----------|----------|
| ~3 秒 | num_frames: 81, frame_rate: 24 |
| ~5 秒 | num_frames: 121, frame_rate: 24 |
| ~10 秒 | num_frames: 241, frame_rate: 24 |
| ~18 秒 | num_frames: 441, frame_rate: 24 |

## 推荐参数

| 使用场景 | 推荐设置 |
|----------|----------|
| 标准视频生成 | width: 1152, height: 768, num_frames: 121, frame_rate: 24 |
| 短视频社交内容 | num_frames: 81 或 121, frame_rate: 24 |
| 更长视频 | 增加 num_frames 或降低 frame_rate |
| 更平滑运动 | frame_rate: 24 或 30 |
| 可复现结果 | 设置固定 seed |
| 关键帧过渡 | extra_body.mode: "keyframes" |
| 避免不需要的内容 | 使用 negative_prompt |

## Prompt 最佳实践

**文生视频结构**：`[主体] + [动作] + [场景] + [镜头运动] + [光照] + [风格]`

**示例**：
> A young astronaut walking across a red desert planet, dust blowing in the wind, slow cinematic tracking shot, dramatic sunset lighting, realistic sci-fi style

**图生视频**：描述哪些内容需要运动，哪些主体需要保持稳定。
> Animate the character with subtle breathing motion, hair moving gently in the wind, background lights flickering softly, while keeping the face and outfit consistent

**多图视频**：描述输入图片之间的关系以及画面如何过渡。
> Use the first image as the starting scene and the second image as the target scene. Create a smooth transformation with consistent lighting, natural motion, and cinematic pacing

**关键帧动画**：清晰描述关键帧之间的过渡关系。
> Create a smooth transition from the first keyframe to the second keyframe, maintaining character identity, consistent camera angle, and natural motion between scenes

## 错误码

| 状态码 | 说明 |
|--------|------|
| 400 | 请求无效，请检查请求参数 |
| 401 | 未授权，请检查 API Key |
| 404 | 任务或视频不存在 |
| 500 | 服务器错误 |
| 503 | 服务繁忙，请稍后重试 |

## 价格

当前完全免费：图片 **$0/image**，视频 **$0/second**

---

# 工作流

当用户要求生成图片或视频时：

1. 脚本自动读取 `AGNES_API_KEY` 环境变量，无需传 `--api-key`
2. 判断是图片还是视频生成
3. **图片生成**：判断文生图或图生图 → 运行 `scripts/generate_image.py`
4. **视频生成**：判断模式（文生视频/图生视频/多图/关键帧） → 确定时长和分辨率 → 运行 `scripts/generate_video.py`（脚本自动用 `video_id` 通过推荐端点轮询）
5. 生成完毕后用 `deliver_attachments` 交付输出文件给用户

如果需要在 Python 环境中直接调用 API，图片使用 OpenAI SDK，视频使用 `requests` 按上述两步流程操作。详细参数信息见 `references/api_docs.md`。
