"use client";

import { useEffect, useState } from "react";
import { apiFetch, API_BASE } from "../../../lib/api";

export default function RenderPage({ params }: { params: { id: string } }) {
  const renderId = params.id;
  const [status, setStatus] = useState<string>("unknown");
  const [progress, setProgress] = useState<number>(0);
  const [videoPath, setVideoPath] = useState<string | null>(null);
  const [detail, setDetail] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const timer = setInterval(async () => {
      try {
        const data = await apiFetch<any>(`/api/renders/${renderId}/detail`);
        setStatus(data.status);
        setProgress(data.progress);
        setVideoPath(data.output_video_path || null);
        setDetail(data.detail || null);
      } catch (err: any) {
        setError(err.message);
        clearInterval(timer);
      }
    }, 1500);
    return () => clearInterval(timer);
  }, [renderId]);

  return (
    <main>
      <div className="card">
        <p>状态：{status}</p>
        <p>进度：{progress}%</p>
        {detail ? <p className="small">阶段：{detail.phase || "unknown"}</p> : null}
        {detail && detail.total ? (
          <p className="small">
            片段：{detail.current || 0}/{detail.total}
          </p>
        ) : null}
        {videoPath ? (
          <div>
            <div style={{ marginBottom: 8 }}>
              <a href={`${API_BASE}/api/renders/${renderId}/download`}>下载视频</a>
            </div>
            <video
              controls
              style={{ width: "100%", maxWidth: 720, borderRadius: 8 }}
              src={`${API_BASE}/api/renders/${renderId}/download`}
            />
          </div>
        ) : null}
        {error ? <p className="small">错误：{error}</p> : null}
      </div>
    </main>
  );
}
