# 使用说明（配置 / 启动 / 使用）

本说明覆盖：必须配置项、启动步骤、完整使用流程。

---

## 1. 必须配置
### 1.1 后端环境变量 `api/.env`
复制示例：
```bash
cp api/.env.example api/.env
```

必填项：
- `ALIYUN_ACCESS_KEY_ID`
- `ALIYUN_ACCESS_KEY_SECRET`
- `ALIYUN_APPKEY`

若启用 HeyGen（Avatar IV / 口型）：
- `HEYGEN_API_KEY`
- `PUBLIC_BASE_URL`（必须是公网可访问域名，不能是 localhost）
- `LIP_SYNC_PROVIDER=heygen`

### 1.2 前端环境变量 `web/.env.local`
复制示例：
```bash
cp web/.env.local.example web/.env.local
```

默认配置：
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

---

## 2. 启动步骤
### 2.1 后端
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
uvicorn api.app.main:app --reload
```

### 2.2 队列
```bash
python -m rq worker txt2video
```

### 2.3 前端
```bash
cd web
npm install
npm run dev
```

---

## 3. 使用流程
1) 打开首页 `/`
2) 输入项目标题 + 脚本文本 → 点击「创建项目」
3) 进入 `/project/[id]`
4) 点击「解析脚本」→ 点击「生成分镜」
5) 在台词编辑区修改台词 → 点击「保存台词」
6) （可选）加载 HeyGen 角色/音色 → 选择 avatar_id / voice_id
7) （可选）上传 Avatar IV 照片（生成 image_key）
8) 选择背景模板 / 是否按分镜生成
9) 点击「开始生成」
10) 进入 `/render/[id]` 查看进度与预览视频

---

## 4. 注意事项
- 如果变更了数据库结构，需删除旧 `api/app/storage/app.db` 或自行迁移
- Avatar IV 生成需 HeyGen API Key + voice_id + image_key
- HeyGen 口型需要公网可访问的 `PUBLIC_BASE_URL`

