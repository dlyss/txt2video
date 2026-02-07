# Docker 本地运行

目标：无需本地安装 Python/Node/Redis/FFmpeg，直接 `docker compose up` 运行。

---

## 1. 准备 .env
在项目根目录新建 `.env`（供 docker compose 读取）：
```
TTS_PROVIDER=aliyun
ALIYUN_ACCESS_KEY_ID=你的AccessKeyId
ALIYUN_ACCESS_KEY_SECRET=你的AccessKeySecret
ALIYUN_APPKEY=你的AppKey
ALIYUN_REGION=ap-southeast-1

LIP_SYNC_PROVIDER=heygen
PUBLIC_BASE_URL=http://localhost:8000
HEYGEN_API_KEY=
HEYGEN_AVATAR_ID=
```

> 如果暂时不使用 HeyGen，可以留空。

---

## 2. 启动
```bash
docker compose up --build
```

也可以使用快捷命令：
- `make up`
- `./run.sh`

访问：
- 前端：http://localhost:3000
- 后端：http://localhost:8000

---

## 3. 常见问题
- 修改代码后自动生效：compose 已挂载本地目录（`volumes`）。
- 数据库位置：`api/app/storage/app.db`（会落在本地目录）。
