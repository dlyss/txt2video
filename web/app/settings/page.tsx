"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";

export default function SettingsPage() {
  const [ttsProvider, setTtsProvider] = useState("aliyun");
  const [enableHeygen, setEnableHeygen] = useState(true);
  const [enableAvatarIv, setEnableAvatarIv] = useState(true);
  const [masked, setMasked] = useState<any>({});
  const [aliyunId, setAliyunId] = useState("");
  const [aliyunSecret, setAliyunSecret] = useState("");
  const [aliyunAppkey, setAliyunAppkey] = useState("");
  const [heygenKey, setHeygenKey] = useState("");
  const [volcAppId, setVolcAppId] = useState("");
  const [volcToken, setVolcToken] = useState("");
  const [volcCluster, setVolcCluster] = useState("");
  const [volcVoice, setVolcVoice] = useState("");
  const [testResult, setTestResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setError(null);
    try {
      const data = await apiFetch<any>("/api/settings");
      setTtsProvider(data.tts_provider || "aliyun");
      setEnableHeygen(!!data.enable_heygen);
      setEnableAvatarIv(!!data.enable_avatar_iv);
      setMasked(data);
      setVolcCluster(data.volcengine_cluster || "");
      setVolcVoice(data.volcengine_voice_type || "");
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
          enable_avatar_iv: enableAvatarIv,
          aliyun_access_key_id: aliyunId || undefined,
          aliyun_access_key_secret: aliyunSecret || undefined,
          aliyun_appkey: aliyunAppkey || undefined,
          heygen_api_key: heygenKey || undefined,
          volcengine_app_id: volcAppId || undefined,
          volcengine_token: volcToken || undefined,
          volcengine_cluster: volcCluster || undefined,
          volcengine_voice_type: volcVoice || undefined
        })
      });
      setAliyunId("");
      setAliyunSecret("");
      setAliyunAppkey("");
      setHeygenKey("");
      setVolcAppId("");
      setVolcToken("");
      await load();
    } catch (err: any) {
      setError(err.message);
    }
  }

  async function testTts() {
    setTestResult(null);
    setError(null);
    try {
      const data = await apiFetch<any>("/api/settings/test/tts", { method: "POST" });
      setTestResult(`TTS OK: ${data.provider}, ${data.duration.toFixed(2)}s`);
    } catch (err: any) {
      setError(err.message);
    }
  }

  async function testHeygen() {
    setTestResult(null);
    setError(null);
    try {
      const data = await apiFetch<any>("/api/settings/test/heygen", { method: "POST" });
      if (data.ok) {
        setTestResult(`HeyGen OK: avatars=${data.avatar_count}`);
      } else {
        setTestResult(`HeyGen Disabled`);
      }
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
          <button className="secondary" onClick={testTts}>测试 TTS</button>
          <button className="secondary" onClick={testHeygen}>测试 HeyGen</button>
        </div>
        {testResult ? <p className="small">{testResult}</p> : null}
        {error ? <p className="small">错误：{error}</p> : null}
      </div>

      <div className="card">
        <h3>密钥管理（加密存储）</h3>
        <div className="row" style={{ marginBottom: 8 }}>
          <div style={{ minWidth: 260 }}>
            <label className="small">阿里云 AccessKeyId（已配置：{masked.aliyun_access_key_id_masked || "未配置"}）</label>
            <input className="input" value={aliyunId} onChange={(e) => setAliyunId(e.target.value)} placeholder="输入新值以更新" />
          </div>
          <div style={{ minWidth: 260 }}>
            <label className="small">阿里云 AccessKeySecret（已配置：{masked.aliyun_access_key_secret_masked || "未配置"}）</label>
            <input className="input" type="password" value={aliyunSecret} onChange={(e) => setAliyunSecret(e.target.value)} placeholder="输入新值以更新" />
          </div>
        </div>
        <div className="row" style={{ marginBottom: 8 }}>
          <div style={{ minWidth: 260 }}>
            <label className="small">阿里云 AppKey（已配置：{masked.aliyun_appkey_masked || "未配置"}）</label>
            <input className="input" value={aliyunAppkey} onChange={(e) => setAliyunAppkey(e.target.value)} placeholder="输入新值以更新" />
          </div>
          <div style={{ minWidth: 260 }}>
            <label className="small">HeyGen API Key（已配置：{masked.heygen_api_key_masked || "未配置"}）</label>
            <input className="input" type="password" value={heygenKey} onChange={(e) => setHeygenKey(e.target.value)} placeholder="输入新值以更新" />
          </div>
        </div>
        <div className="row" style={{ marginBottom: 8 }}>
          <div style={{ minWidth: 260 }}>
            <label className="small">火山引擎 AppId（已配置：{masked.volcengine_app_id_masked || "未配置"}）</label>
            <input className="input" value={volcAppId} onChange={(e) => setVolcAppId(e.target.value)} placeholder="输入新值以更新" />
          </div>
          <div style={{ minWidth: 260 }}>
            <label className="small">火山引擎 Token（已配置：{masked.volcengine_token_masked || "未配置"}）</label>
            <input className="input" type="password" value={volcToken} onChange={(e) => setVolcToken(e.target.value)} placeholder="输入新值以更新" />
          </div>
        </div>
        <div className="row">
          <div style={{ minWidth: 260 }}>
            <label className="small">火山引擎 Cluster</label>
            <input className="input" value={volcCluster} onChange={(e) => setVolcCluster(e.target.value)} placeholder="如: volcano_tts" />
          </div>
          <div style={{ minWidth: 260 }}>
            <label className="small">火山引擎 VoiceType</label>
            <input className="input" value={volcVoice} onChange={(e) => setVolcVoice(e.target.value)} placeholder="如: BV001_streaming" />
          </div>
        </div>
      </div>
    </main>
  );
}
