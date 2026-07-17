"use client";

import { useState, useEffect } from "react";

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState("");
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const key = localStorage.getItem("llm_api_key") || "";
    setApiKey(key);
  }, []);

  const handleSave = () => {
    localStorage.setItem("llm_api_key", apiKey);
    // 同时保存到后端
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";
    fetch(`${API_BASE}/api/settings/ai-key`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ llm_api_key: apiKey }),
    }).catch(() => setError("同步到后端失败，本地已保存")); // 后端不可用时静默失败，localStorage 仍然有效
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleClear = () => {
    setApiKey("");
    localStorage.removeItem("llm_api_key");
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="p-4">
      <header className="py-6 text-center">
        <h1 className="text-lg font-semibold tracking-tight">设置</h1>
      </header>

      {/* API Key 配置 */}
      <div className="card mb-3">
        <div className="text-xs font-medium mb-2">API Key 配置</div>
        <p className="text-xs text-[var(--color-text-muted)] mb-3">
          输入你的 DeepSeek / OpenAI API Key，用于 AI 咨询功能。
        </p>
        <input
          type="password"
          className="input-field w-full mb-2"
          placeholder="sk-..."
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
        />
        {error && <p className="text-xs text-[var(--color-danger)] mb-2">{error}</p>}
        <div className="flex gap-2">
          <button onClick={handleSave} className="btn-primary text-xs flex-1">
            {saved ? "已保存" : "保存"}
          </button>
          {apiKey && (
            <button onClick={handleClear} className="text-xs px-3 py-1.5 rounded-md border border-[var(--color-border)] text-[var(--color-text-muted)] hover:bg-[var(--color-bg)]">
              清除
            </button>
          )}
        </div>
      </div>

      {/* 快捷入口 */}
      <div className="card !p-0 divide-y divide-[var(--color-border)]">
        <a href="/cases" className="flex items-center justify-between px-4 py-3 text-sm text-inherit no-underline">
          <span>我的案件</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="2"><polyline points="9,18 15,12 9,6"/></svg>
        </a>
        <a href="/documents" className="flex items-center justify-between px-4 py-3 text-sm text-inherit no-underline">
          <span>我的文书</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="2"><polyline points="9,18 15,12 9,6"/></svg>
        </a>
        <a href="/toolbox" className="flex items-center justify-between px-4 py-3 text-sm text-inherit no-underline">
          <span>法律工具</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="2"><polyline points="9,18 15,12 9,6"/></svg>
        </a>
        <div className="flex items-center justify-between px-4 py-3 text-sm text-[var(--color-text-muted)]">
          <span>版本</span>
          <span>1.0.0</span>
        </div>
      </div>

      <p className="disclaimer">本工具基于AI分析，不替代专业律师意见。</p>
    </div>
  );
}
