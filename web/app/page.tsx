"use client";

import { useState } from "react";
import { apiFetch } from "../lib/api";

export default function Home() {
  const [title, setTitle] = useState("我的故事");
  const [rawText, setRawText] = useState("");
  const [projectId, setProjectId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleCreate() {
    setError(null);
    try {
      const data = await apiFetch<{ id: number; title: string }>("/api/projects", {
        method: "POST",
        body: JSON.stringify({ title, raw_text: rawText })
      });
      setProjectId(data.id);
    } catch (err: any) {
      setError(err.message);
    }
  }

  return (
    <main>
      <div className="card">
        <label>项目标题</label>
        <input
          className="input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>
      <div className="card">
        <label>脚本内容</label>
        <textarea
          placeholder="示例：\n# 公园-白天\n小明: 今天天气真好！\n小红: 是啊，我们去散步吧。"
          value={rawText}
          onChange={(e) => setRawText(e.target.value)}
        />
        <div className="row" style={{ marginTop: 12 }}>
          <button onClick={handleCreate}>创建项目</button>
        </div>
        {error ? <p className="small">错误：{error}</p> : null}
        {projectId ? (
          <p className="small">
            已创建项目：{projectId}，访问 /project/{projectId}
          </p>
        ) : null}
      </div>
    </main>
  );
}
