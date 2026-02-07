# txt2video MVP 技术方案（Next.js + FastAPI）

日期：2026-02-07

> 目标：从零起步，完成“脚本上传 → 分镜 → 台词编辑 → 配音 → 字幕 → 合成短视频”的 MVP。
> 风格：卡通（后期配置化），成本低，第三方 API。

---

## 1. 功能范围（MVP）
**包含**
- 上传脚本文本
- 解析脚本为场景/台词结构化 JSON
- 自动生成基础分镜（按台词拆镜头）
- 台词编辑
- TTS 配音（阿里云语音合成）
- SRT 字幕生成
- FFmpeg 合成短视频

**不包含**
- 高质量角色动画或复杂镜头运镜
- 复杂角色建模（MVP 仅静态背景 + 字幕 + 音频）
- 真实口型视频（先占位，后续接入 HeyGen）

---

## 2. 目录结构（已生成）
```
/txt2video
  /api                 # FastAPI 后端
    /app
      /routers          # API 路由
      /services         # 解析、TTS、字幕
      /tasks            # 队列任务与合成脚本
      /storage          # 本地存储
  /web                 # Next.js 前端
  /docs                # 技术文档
```

---

## 3. 技术栈
- 前端：Next.js (App Router)
- 后端：FastAPI
- 任务队列：Redis + RQ
- 数据库：SQLite
- 合成：FFmpeg
- TTS：阿里云语音合成（NLS RESTful）
- 口型（可选）：HeyGen API

---

## 4. 从零起步部署步骤
### 4.1 系统依赖
- Python 3.10+
- Node.js 18+
- Redis（队列）
- FFmpeg（视频合成）

**常见安装方式（macOS）**
- Redis：`brew install redis`
- FFmpeg：`brew install ffmpeg`

### 4.2 后端启动
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
cp api/.env.example api/.env
uvicorn api.app.main:app --reload
```

### 4.3 队列启动
```bash
python -m rq worker txt2video
```

### 4.4 前端启动
```bash
cd web
cp .env.local.example .env.local
npm install
npm run dev
```

---

## 5. 阿里云 TTS 配置（大陆访问友好、成本低）
### 5.1 开通服务与获取 AppKey
1) 在阿里云控制台开通“智能语音交互（NLS）”
2) 创建项目，获取 **AppKey**

### 5.2 生成 Token
阿里云 Token 通过 CreateToken API 生成：
- domain: `nlsmeta.ap-southeast-1.aliyuncs.com`
- action: `CreateToken`
- version: `2019-07-17`

### 5.3 调用 TTS RESTful
TTS RESTful 端点：
- `https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/tts`

必须参数：
- `appkey`
- `token`
- `text`
- `format`（建议 wav）
- `sample_rate`（16000）

可选参数：
- `voice`（默认 xiaoyun）
- `volume`（0–100）
- `speech_rate`（-500–500）
- `pitch_rate`（-500–500）

### 5.4 项目环境变量
在 `api/.env` 中配置：
```
TTS_PROVIDER=aliyun
ALIYUN_ACCESS_KEY_ID=你的AccessKeyId
ALIYUN_ACCESS_KEY_SECRET=你的AccessKeySecret
ALIYUN_APPKEY=你的AppKey
ALIYUN_REGION=ap-southeast-1
```

---

## 6. HeyGen 口型（可选）
### 6.1 准备
- 获取 HeyGen API Key
- 获取可用的 Avatar ID
- 设置公共访问地址 `PUBLIC_BASE_URL`
  - HeyGen 需要访问 `audio_url`，必须是公网 URL（不能是 localhost）

### 6.2 使用音频作为语音
HeyGen Create Avatar Video (V2) 支持在 Voice Settings 中设置 `type=audio`，并提供 `audio_url` 或 `audio_asset_id`。

### 6.3 环境变量
```
LIP_SYNC_PROVIDER=heygen
PUBLIC_BASE_URL=https://你的域名
HEYGEN_API_KEY=你的heygen_api_key
HEYGEN_AVATAR_ID=你的avatar_id
```

### 6.4 Avatar IV（上传照片生成视频）
流程：\n
1) 上传照片 → HeyGen Upload Asset API → 返回 image_key\n
2) 调用 Avatar IV 生成接口 → 返回 video_id\n
3) 轮询状态 → 下载视频\n

当前项目实现：\n
- `POST /api/projects/{id}/avatar-iv/upload` 上传照片并保存 image_key\n
- 渲染时若配置 `avatar_iv_image_key + voice_id`，优先走 Avatar IV 生成\n

---

## 7. API 设计
### 7.1 创建项目
`POST /api/projects`
```json
{ "title": "我的故事", "raw_text": "# 公园\n小明: 今天天气真好" }
```

### 7.2 解析脚本
`POST /api/projects/{id}/parse`
返回：
```json
{ "scenes": [ { "scene_id": 1, "location": "公园", "characters": ["小明"], "dialogue": [ ... ] } ] }
```

### 7.3 生成分镜
`POST /api/projects/{id}/storyboard`
返回：
```json
[ { "shot_id": 1, "shot_index": 1, "description": "小明对话...", "duration_sec": 3 } ]
```

### 7.4 更新台词
`PUT /api/projects/{id}/dialogues`
```json
{ "dialogues": [ { "speaker": "小明", "text": "今天天气真好" } ] }
```

### 7.5 获取台词
`GET /api/projects/{id}/dialogues`

### 7.6 触发渲染
`POST /api/projects/{id}/render`
返回：
```json
{ "render_id": 12 }
```

### 7.7 查询状态
`GET /api/renders/{render_id}/status`
返回：
```json
{ "status": "processing", "progress": 60, "output_video_path": null }
```

### 7.8 下载视频
`GET /api/renders/{render_id}/download`

### 7.9 渲染详情（阶段与分片进度）
`GET /api/renders/{render_id}/detail`
返回：
```json
{
  "status": "processing",
  "progress": 85,
  "detail": { "phase": "avatar_iv", "current": 3, "total": 6, "progress": 85 },
  "output_video_path": null
}
```

### 7.9 HeyGen 列表接口
`GET /api/heygen/avatars`  
`GET /api/heygen/voices`

### 7.10 项目角色设置
`GET /api/projects/{id}/settings`  
`PUT /api/projects/{id}/settings`

### 7.11 上传项目头像（本地预览）
`POST /api/projects/{id}/avatar`

### 7.12 Avatar IV 上传照片（生成 image_key）
`POST /api/projects/{id}/avatar-iv/upload`

### 7.13 系统配置
`GET /api/settings`  
`PUT /api/settings`

---

## 8. API 快速联调（curl 示例）
```bash
# 1) 创建项目
curl -X POST http://localhost:8000/api/projects \
  -H 'Content-Type: application/json' \
  -d '{"title":"示例","raw_text":"# 公园\n小明: 你好\n小红: 你好"}'

# 2) 解析脚本
curl -X POST http://localhost:8000/api/projects/1/parse

# 3) 生成分镜
curl -X POST http://localhost:8000/api/projects/1/storyboard

# 4) 保存台词
curl -X PUT http://localhost:8000/api/projects/1/dialogues \
  -H 'Content-Type: application/json' \
  -d '{"dialogues":[{"speaker":"小明","text":"你好"},{"speaker":"小红","text":"你好"}]}'

# 5) 触发渲染
curl -X POST http://localhost:8000/api/projects/1/render

# 6) 查询状态
curl http://localhost:8000/api/renders/1/status
```

---

## 9. 数据模型
- **projects**：id, title, created_at
- **scripts**：id, project_id, raw_text, parsed_json
- **dialogues**：id, project_id, speaker, text, audio_path
- **shots**：id, project_id, shot_index, description, duration_sec
- **renders**：id, project_id, status, progress, output_video_path, created_at

---

## 10. 任务队列执行细节
渲染任务流程：
1) 读取对话
2) TTS 生成每句音频
3) 合并音频为单条 wav
4) 生成字幕 SRT
5) 若 Avatar IV 开启（`avatar_iv_image_key + voice_id`），按台词或分镜逐句生成视频片段并拼接（可切换 `use_shots_for_avatar_iv`）
6) 若拼接完成，进行字幕烧录
7) 否则使用 FFmpeg 合成 mp4（支持背景模板）
8) 若 HeyGen 口型启用且 `PUBLIC_BASE_URL` 为公网地址，则调用 HeyGen 生成口型视频并下载（作为替代方案）

状态流转：`queued → processing → completed/failed`

---

## 11. 现有实现细节（对应代码）
- 脚本解析：`api/app/services/parser.py`
- 分镜生成：`api/app/services/storyboard.py`
- TTS（阿里云/占位）：`api/app/services/tts.py`
- 音频处理：`api/app/services/audio.py`
- 字幕生成：`api/app/services/subtitles.py`
- 渲染任务：`api/app/tasks/worker.py`
- 合成：`api/app/tasks/compose.py`
- HeyGen 调用：`api/app/services/heygen.py`
- 音频资源访问：`api/app/routers/assets.py`

---

## 12. 调试与验证
**快速验证流程**
1) 前端上传脚本
2) 解析 → 生成分镜
3) 修改台词 → 保存
4) 触发渲染
5) `/render/[id]` 页面查看状态
6) 下载 mp4 验证

**失败降级**
- 若阿里云 TTS 失败，会回退为静音 wav
- 若 HeyGen 失败或无法访问音频 URL，会回退为 FFmpeg 合成

---

## 13. 参考链接
- 阿里云 TTS RESTful API：https://www.alibabacloud.com/help/doc-detail/94737.html
- 阿里云 TTS RESTful API（新版）：https://www.alibabacloud.com/help/en/isi/developer-reference/restful-api-3
- 阿里云 CreateToken：https://www.alibabacloud.com/help/en/isi/getting-started/obtain-an-access-token
- HeyGen 使用音频作为语音：https://docs.heygen.com/docs/using-audio-source-as-voice
- HeyGen 创建视频参考：https://docs.heygen.com/reference/create-video
