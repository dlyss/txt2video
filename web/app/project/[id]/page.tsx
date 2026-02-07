"use client";

import { useEffect, useState } from "react";
import { apiFetch, API_BASE } from "../../../lib/api";

interface Dialogue {
  speaker: string;
  text: string;
}

export default function ProjectPage({ params }: { params: { id: string } }) {
  const projectId = params.id;
  const [parsed, setParsed] = useState<any>(null);
  const [dialogues, setDialogues] = useState<Dialogue[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [renderId, setRenderId] = useState<number | null>(null);
  const [avatars, setAvatars] = useState<any[]>([]);
  const [voices, setVoices] = useState<any[]>([]);
  const [settings, setSettings] = useState<{ avatar_id?: string; voice_id?: string; avatar_image_url?: string; avatar_iv_image_key?: string; background_style?: string; use_shots_for_avatar_iv?: boolean }>({});
  const [uploading, setUploading] = useState(false);

  async function handleParse() {
    setError(null);
    try {
      const data = await apiFetch<any>(`/api/projects/${projectId}/parse`, { method: "POST" });
      setParsed(data);
      const extracted: Dialogue[] = [];
      for (const scene of data.scenes || []) {
        for (const item of scene.dialogue || []) {
          extracted.push({ speaker: item.speaker, text: item.text });
        }
      }
      setDialogues(extracted);
    } catch (err: any) {
      setError(err.message);
    }
  }

  async function handleStoryboard() {
    setError(null);
    try {
      await apiFetch(`/api/projects/${projectId}/storyboard`, { method: "POST" });
    } catch (err: any) {
      setError(err.message);
    }
  }

  async function handleSaveDialogues() {
    setError(null);
    try {
      await apiFetch(`/api/projects/${projectId}/dialogues`, {
        method: "PUT",
        body: JSON.stringify({ dialogues })
      });
    } catch (err: any) {
      setError(err.message);
    }
  }

  async function handleRender() {
    setError(null);
    try {
      const data = await apiFetch<{ render_id: number }>(`/api/projects/${projectId}/render`, {
        method: "POST"
      });
      setRenderId(data.render_id);
    } catch (err: any) {
      setError(err.message);
    }
  }

  async function loadHeygenLists() {
    try {
      const av = await apiFetch<{ data: any[] }>("/api/heygen/avatars");
      setAvatars(av.data || []);
      const vo = await apiFetch<{ data: any[] }>("/api/heygen/voices");
      setVoices(vo.data || []);
    } catch (err: any) {
      setError(err.message);
    }
  }

  async function loadSettings() {
    try {
      const data = await apiFetch<any>(`/api/projects/${projectId}/settings`);
      setSettings(data);
    } catch (err: any) {
      setError(err.message);
    }
  }

  async function saveSettings(next: { avatar_id?: string; voice_id?: string; avatar_iv_image_key?: string; background_style?: string; use_shots_for_avatar_iv?: boolean }) {
    try {
      const data = await apiFetch<any>(`/api/projects/${projectId}/settings`, {
        method: "PUT",
        body: JSON.stringify(next)
      });
      setSettings(data);
    } catch (err: any) {
      setError(err.message);
    }
  }

  async function handleAvatarUpload(file: File) {
    setUploading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_BASE}/api/projects/${projectId}/avatar`, {
        method: "POST",
        body: form
      });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      await loadSettings();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleAvatarIvUpload(file: File) {
    setUploading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_BASE}/api/projects/${projectId}/avatar-iv/upload`, {
        method: "POST",
        body: form
      });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      await loadSettings();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  useEffect(() => {
    loadSettings();
  }, [projectId]);

  return (
    <main>
      <div className="card">
        <div className="row">
          <button onClick={handleParse}>解析脚本</button>
          <button className="secondary" onClick={handleStoryboard}>生成分镜</button>
        </div>
        {parsed ? <pre className="small">{JSON.stringify(parsed, null, 2)}</pre> : null}
      </div>

      <div className="card">
        <label>台词编辑</label>
        {dialogues.map((d, i) => (
          <div className="row" key={i} style={{ marginBottom: 8 }}>
            <input
              className="input"
              value={d.speaker}
              onChange={(e) => {
                const next = [...dialogues];
                next[i] = { ...next[i], speaker: e.target.value };
                setDialogues(next);
              }}
              style={{ maxWidth: 140 }}
            />
            <input
              className="input"
              value={d.text}
              onChange={(e) => {
                const next = [...dialogues];
                next[i] = { ...next[i], text: e.target.value };
                setDialogues(next);
              }}
            />
          </div>
        ))}
        <div className="row">
          <button onClick={handleSaveDialogues}>保存台词</button>
          <button className="secondary" onClick={handleRender}>开始生成</button>
        </div>
        {renderId ? (
          <p className="small">渲染任务：{renderId}，访问 /render/{renderId}</p>
        ) : null}
        {error ? <p className="small">错误：{error}</p> : null}
      </div>

      <div className="card">
        <label>角色素材（HeyGen）</label>
        <div className="row" style={{ marginBottom: 12 }}>
          <button onClick={loadHeygenLists}>加载 HeyGen 角色/音色</button>
        </div>

        <div className="row" style={{ marginBottom: 12 }}>
          <div style={{ minWidth: 260 }}>
            <label className="small">选择角色</label>
            <select
              className="input"
              value={settings.avatar_id || ""}
              onChange={(e) => saveSettings({ avatar_id: e.target.value || undefined, voice_id: settings.voice_id })}
            >
              <option value="">未选择</option>
              {avatars.map((a) => (
                <option key={a.avatar_id || a.id} value={a.avatar_id || a.id}>
                  {a.name || a.avatar_id || a.id}
                </option>
              ))}
            </select>
          </div>

          <div style={{ minWidth: 260 }}>
            <label className="small">选择音色（预留）</label>
            <select
              className="input"
              value={settings.voice_id || ""}
              onChange={(e) => saveSettings({ avatar_id: settings.avatar_id, voice_id: e.target.value || undefined })}
            >
              <option value="">未选择</option>
              {voices.map((v) => (
                <option key={v.voice_id || v.id} value={v.voice_id || v.id}>
                  {v.name || v.voice_id || v.id}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="row" style={{ marginBottom: 12 }}>
          <div>
            <label className="small">上传头像（本地保存，仅用于预览）</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleAvatarUpload(file);
              }}
            />
            {uploading ? <p className="small">上传中...</p> : null}
          </div>
          {settings.avatar_image_url ? (
            <div>
              <label className="small">头像预览</label>
              <img
                src={`${API_BASE}${settings.avatar_image_url}`}
                alt="avatar"
                style={{ width: 120, height: 120, objectFit: "cover", borderRadius: 8 }}
              />
            </div>
          ) : null}
        </div>

        <div className="row" style={{ marginBottom: 12 }}>
          <div>
            <label className="small">Avatar IV 上传照片（用于生成口型视频）</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleAvatarIvUpload(file);
              }}
            />
            {uploading ? <p className="small">上传中...</p> : null}
            {settings.avatar_iv_image_key ? (
              <p className="small">已上传 image_key：{settings.avatar_iv_image_key}</p>
            ) : null}
          </div>
        </div>

        <div className="row" style={{ marginBottom: 12 }}>
          <div style={{ minWidth: 220 }}>
            <label className="small">背景模板</label>
            <select
              className="input"
              value={settings.background_style || "paper"}
              onChange={(e) => saveSettings({ background_style: e.target.value })}
            >
              <option value="paper">纸张</option>
              <option value="mint">薄荷</option>
              <option value="sky">天空</option>
              <option value="sunset">夕阳</option>
            </select>
          </div>
        </div>

        <div className="row" style={{ marginBottom: 12 }}>
          <label className="small" style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <input
              type="checkbox"
              checked={settings.use_shots_for_avatar_iv ?? true}
              onChange={(e) => saveSettings({ use_shots_for_avatar_iv: e.target.checked })}
            />
            Avatar IV 按分镜生成
          </label>
        </div>
      </div>
    </main>
  );
}
