# Agnes AI Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Free](https://img.shields.io/badge/Pricing-Free-brightgreen.svg)](https://platform.agnes-ai.com/)

一套基于 [Agnes AI](https://platform.agnes-ai.com/) 免费 API 的图像/视频生成工具集，包含命令行脚本和 WorkBuddy Skill 定义文件。

> 💡 **无需信用卡，完全免费** — Agnes AI 提供免费不限量的图像生成 API 和视频生成 API。

---

## 📦 包含的 Skills

| Skill | 说明 | 模型 |
|-------|------|------|
| **agnes-ai** | 🌟 全功能 Skill：图片 + 视频一站式生成 | `agnes-image-2.1-flash` / `agnes-image-2.0-flash` / `agnes-video-v2.0` |
| **agnes-image-gen** | 文生图 / 图生图（独立版） | `agnes-image-2.1-flash` / `agnes-image-2.0-flash` |
| **agnes-video-gen** | 文生视频 / 图生视频 / 多图视频 / 关键帧动画（独立版） | `agnes-video-v2.0` |

> 💡 **怎么选？** `agnes-ai` 是**全功能合体版**，安装这一个就能同时处理图片和视频生成。`agnes-image-gen` 和 `agnes-video-gen` 是**独立拆分包**，适合只需要单一功能的场景。三个可以同时安装，不会冲突。

---

## 🚀 快速开始

### 1. 获取 API Key

前往 [Agnes AI 平台](https://platform.agnes-ai.com/) 注册账号，登录后在 **API Keys** 页面创建 Key。

### 2. 设置环境变量

```bash
# Linux / macOS
export AGNES_API_KEY="your-api-key-here"

# Windows PowerShell
$env:AGNES_API_KEY="your-api-key-here"

# Windows CMD
set AGNES_API_KEY=your-api-key-here
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 开始生成！

---

## 🌟 agnes-ai — 全功能（推荐）

`agnes-ai` 是一个 WorkBuddy 全功能 Skill，将图片和视频生成合为一体。安装后在 WorkBuddy 中说话就能自动判断意图：

```bash
# 文生图
python agnes-ai/scripts/generate_image.py \
  --prompt "一只可爱的柴犬在樱花树下睡觉" \
  --size 1024x1024 \
  -o shiba.png

# 图生图
python agnes-ai/scripts/generate_image.py \
  --prompt "变成水彩画风格" \
  --image https://example.com/photo.png \
  -o watercolor.png

# 文生视频
python agnes-ai/scripts/generate_video.py \
  --prompt "A cinematic shot of a cat walking on the beach at sunset" \
  -o beach.mp4

# 图生视频
python agnes-ai/scripts/generate_video.py \
  --prompt "The woman slowly turns around and looks back at the camera" \
  --image https://example.com/portrait.png \
  -o animated.mp4
```

| 特性 | 说明 |
|------|------|
| 模型 | `agnes-image-2.1-flash` · `agnes-image-2.0-flash` · `agnes-video-v2.0` |
| 文生图 | ✅ |
| 图生图 / 图片编辑 | ✅ |
| 文生视频 | ✅ |
| 图生视频 | ✅ |
| 多图视频 | ✅ |
| 关键帧动画 | ✅ |
| 自动音频 | ✅ 视频自带 |
| WorkBuddy 自动触发 | ✅ 说了就做 |

---

## 🎨 agnes-image-gen — 图片生成

### 文生图

```bash
cd agnes-image-gen
python scripts/generate_image.py \
  --prompt "一只可爱的柴犬在樱花树下睡觉" \
  --size 1024x1024 \
  -o shiba.png
```

```bash
# 英文 prompt
python scripts/generate_image.py \
  --prompt "A futuristic cyberpunk city at night, neon lights, rain, cinematic lighting" \
  --size 1024x768 \
  -o cyberpunk.png
```

### 图生图（风格转换 / 图片编辑）

```bash
python scripts/generate_image.py \
  --prompt "变成水彩画风格，柔和色调" \
  --image https://example.com/photo.png \
  --size 1024x768 \
  -o watercolor.png
```

支持多张参考图：

```bash
python scripts/generate_image.py \
  --prompt "将两幅图的风格融合为日系动画风格" \
  --image https://example.com/img1.png \
  --image https://example.com/img2.png \
  -o blended.png
```

### 支持的分辨率

`1024x1024` | `1024x768` | `768x1024` | `512x512`

### 直接使用 Python API

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="https://apihub.agnes-ai.com/v1"
)

# 文生图
response = client.images.generate(
    model="agnes-image-2.1-flash",
    prompt="A cat wearing a wizard hat",
    size="1024x1024"
)
image_url = response.data[0].url
print(image_url)
```

---

## 🎬 agnes-video-gen — 视频生成

### 文生视频（默认 ~5 秒）

```bash
cd agnes-video-gen
python scripts/generate_video.py \
  --prompt "A cinematic shot of a cat walking on the beach at sunset, soft ocean waves, warm golden lighting" \
  -o beach.mp4
```

### 调整时长和分辨率

```bash
# 10 秒视频
python scripts/generate_video.py \
  --prompt "Tokyo night market, neon lights, people walking, rain" \
  --duration 10 \
  --size 1152x768 \
  -o nightmarket.mp4
```

### 图生视频

```bash
python scripts/generate_video.py \
  --prompt "The woman slowly turns around and looks back at the camera, natural motion" \
  --image https://example.com/portrait.png \
  -o animated.mp4
```

### 多图视频

```bash
python scripts/generate_video.py \
  --prompt "Create a smooth transformation scene between the two reference images" \
  --images https://example.com/img1.png,https://example.com/img2.png \
  -o transition.mp4
```

### 关键帧动画

```bash
python scripts/generate_video.py \
  --prompt "Generate a smooth cinematic transition between the keyframes" \
  --images https://example.com/kf1.png,https://example.com/kf2.png \
  --mode keyframes \
  -o keyframe.mp4
```

### Prompt 编写建议

**文生视频推荐结构**：`[主体] + [动作] + [场景] + [镜头运动] + [光照] + [风格]`

示例：
> A young astronaut walking across a red desert planet, dust blowing in the wind, slow cinematic tracking shot, dramatic sunset lighting, realistic sci-fi style

**图生视频**：描述需要运动的内容，保持主体稳定。
> The character gently breathes, hair sways softly in the wind, background lights flicker, keep the face and outfit consistent

### 视频时长参数

| 目标时长 | num_frames | frame_rate |
|----------|------------|------------|
| ~3 秒 | 81 | 24 |
| ~5 秒 | 121 | 24 |
| ~10 秒 | 241 | 24 |
| ~18 秒 | 441 | 24 |

> ⚠️ `num_frames` 必须 ≤ 441 且满足 `8n+1` 格式。

---

## 📂 目录结构

```
agnes-ai-skills/
├── README.md                     # 本文件
├── requirements.txt              # Python 依赖
├── agnes-ai/                     # 🌟 全功能 Skill（推荐）
│   ├── SKILL.md                  # WorkBuddy Skill 定义
│   ├── scripts/
│   │   ├── generate_image.py     # 图片生成脚本
│   │   └── generate_video.py     # 视频生成脚本
│   ├── references/
│   │   └── api_docs.md           # API 详细文档
│   └── assets/                   # 资源目录
├── agnes-image-gen/
│   ├── SKILL.md                  # WorkBuddy Skill 定义
│   ├── scripts/
│   │   └── generate_image.py     # 图片生成脚本
│   └── references/
│       └── api_docs.md           # API 详细文档
└── agnes-video-gen/
    ├── SKILL.md                  # WorkBuddy Skill 定义
    ├── scripts/
    │   └── generate_video.py     # 视频生成脚本
    └── references/
        └── api_docs.md           # API 详细文档
```

---

## 🤖 WorkBuddy 集成

这两个 Skill 可以直接安装到 [WorkBuddy](https://www.codebuddy.cn/) 中使用。

### 安装方法

将 `agnes-ai`（推荐）和/或独立版 `agnes-image-gen`、`agnes-video-gen` 文件夹复制到 WorkBuddy 的 skills 目录：

```bash
# 用户级别（所有项目可用）— 推荐全功能版
cp -r agnes-ai ~/.workbuddy/skills/

# 或者安装独立版
cp -r agnes-image-gen ~/.workbuddy/skills/
cp -r agnes-video-gen ~/.workbuddy/skills/

# 项目级别（仅当前项目）
cp -r agnes-ai .workbuddy/skills/
```

安装后在 WorkBuddy 中直接对话即可触发：

- `"帮我生成一张..."` → 自动使用图片生成
- `"用这个图片生成视频..."` → 自动使用视频生成
- `"把这张图改成水彩画风格"` → 自动使用图生图

### 前提条件

确保已设置 `AGNES_API_KEY` 环境变量。

---

## 🔧 参数速查

### generate_image.py

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--prompt` | 生成提示词（支持中英文） | **必填** |
| `--size` | 输出尺寸 | `1024x1024` |
| `--image` | 参考图 URL（可重复） | 无 |
| `--output, -o` | 输出路径 | `output.png` |
| `--api-key` | API Key（或使用环境变量） | `AGNES_API_KEY` |

### generate_video.py

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--prompt` | 视频描述（英文效果更佳） | **必填** |
| `--duration` | 时长（秒），最大 ~18 | `5.0` |
| `--size` | 分辨率 WxH | `1152x768` |
| `--frame-rate` | 帧率 (1-60) | `24` |
| `--image` | 参考图 URL | 无 |
| `--images` | 多图 URLs（逗号分隔） | 无 |
| `--mode` | `ti2vid` / `keyframes` | `ti2vid` |
| `--seed` | 随机种子 | 无 |
| `--negative-prompt` | 排除内容 | 无 |
| `--poll-interval` | 轮询间隔（秒） | `5` |
| `--max-wait` | 最大等待（秒） | `900` |
| `--output, -o` | 输出路径 | `output.mp4` |
| `--api-key` | API Key（或使用环境变量） | `AGNES_API_KEY` |

---

## 📄 许可

MIT License — 可自由使用、修改和分发。

---

## 🔗 相关链接

- [Agnes AI 平台](https://platform.agnes-ai.com/) — 注册获取 API Key
- [Agnes AI Video 文档](https://agnes-ai.com/doc/agnes-video-v20) — 官方视频 API 文档
- [WorkBuddy](https://www.codebuddy.cn/) — AI 编程助手
