# txt2video

一个将故事脚本转换为短视频的 MVP：
- 脚本解析 → 分镜 → 台词编辑
- 阿里云 TTS 配音（失败降级为静音）
- Avatar IV（HeyGen）按台词/分镜生成视频片段并拼接
- FFmpeg 合成短视频 + 字幕

## 快速开始
### 1) 配置环境变量
```bash
cp api/.env.example api/.env
cp web/.env.local.example web/.env.local
```
编辑 `api/.env` 填入：
- `ALIYUN_ACCESS_KEY_ID`
- `ALIYUN_ACCESS_KEY_SECRET`
- `ALIYUN_APPKEY`

（可选）启用 HeyGen：
- `HEYGEN_API_KEY`
- `PUBLIC_BASE_URL`（必须公网可访问）

### 2) 启动后端
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
uvicorn api.app.main:app --reload
```

### 3) 启动队列
```bash
python -m rq worker txt2video
```

### 4) 启动前端
```bash
cd web
npm install
npm run dev
```

## 使用流程
1) 打开首页 `/` 创建项目
2) 进入 `/project/[id]` 解析脚本、生成分镜、编辑台词
3) （可选）配置 HeyGen 角色/音色/Avatar IV 图片
4) 触发渲染 → `/render/[id]` 查看进度与预览

## 文档
- 开发文档：`docs/DEV_SPEC.md`
- 设计文档：`docs/DESIGN_SPEC.md`
- 使用说明：`docs/USAGE.md`
- Docker 运行：`docs/DOCKER.md`
