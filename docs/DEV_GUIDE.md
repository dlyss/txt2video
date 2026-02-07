# 开发指引（MVP）

## 后端
1) 安装依赖
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r api/requirements.txt`

2) 启动 API
- `uvicorn api.app.main:app --reload`

## 队列
1) 启动 Redis
2) 启动 worker
- `python -m rq worker txt2video`

## 前端
1) 安装依赖
- `cd web`
- `npm install`

2) 启动
- `npm run dev`

## FFmpeg
- 合成脚本位置：`api/app/tasks/`（预留）
- 需本机安装 FFmpeg

