"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";

export default function SettingsPage() {
  const [ttsProvider, setTtsProvider] = useState("aliyun");
  const [enableHeygen, setEnableHeygen] = useState(true);
  const [enableAvatarIv, setEnableAvatarIv] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setError(null);
    try {
      const data = await apiFetch<any>("/api/settings");
      setTtsProvider(data.tts_provider || "aliyun");
      setEnableHeygen(!!data.enable_heygen);
      setEnableAvatarIv(!!data.enable_avatar_iv);
    } catch (err: any) {
      setError(err.message);
    }
  }

  async function save() {
    setError(null);
    try {
      await apiFetch<any>("/api/settings", {
        method: "PUT",
        body: JSON.stringify({
          tts_provider: ttsProvider,
          enable_heygen: enableHeygen,
          enable_avatar_iv: enableAvatarIv
        })
      });
    } catch (err: any) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <main>
      <div className="card">
        <h2>系统配置</h2>
        <label>语音合成（TTS）</label>
        <select
          className="input"
          value={ttsProvider}
          onChange={(e) => setTtsProvider(e.target.value)}
          style={{ maxWidth: 280 }}
        >
          <option value="aliyun">阿里云</option>
          <option value="volcengine">火山引擎</option>
          <option value="mock">Mock</option>
        </select>

        <div className="row" style={{ marginTop: 16 }}>
          <label className="small" style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <input
              type="checkbox"
              checked={enableHeygen}
              onChange={(e) => setEnableHeygen(e.target.checked)}
            />
            启用 HeyGen
          </label>
        </div>

        <div className="row" style={{ marginTop: 8 }}>
          <label className="small" style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <input
              type="checkbox"
              checked={enableAvatarIv}
              onChange={(e) => setEnableAvatarIv(e.target.checked)}
            />
            启用 Avatar IV
          </label>
        </div>

        <div className="row" style={{ marginTop: 16 }}>
          <button onClick={save}>保存配置</button>
        </div>
        {error ? <p className="small">错误：{error}</p> : null}
      </div>
    </main>
  );
}
