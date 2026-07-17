"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export default function EvidenceUploadPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    if (!files.length) return;
    setLoading(true);
    setError("");
    setAnalyses([]);

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      for (const file of files) {
        const form = new FormData();
        form.append("file", file);
        const headers: Record<string, string> = {};
        if (token) headers["Authorization"] = `Bearer ${token}`;

        const upResp = await fetch(`${API_BASE}/api/evidence/upload`, { method: "POST", headers, body: form });
        if (!upResp.ok) { setError(`${file.name} 上传失败`); continue; }
        const uploaded = await upResp.json();

        const anaResp = await apiFetch(`/api/evidence/analyze/${uploaded.id}`, { method: "POST" });
        const data = await anaResp.json();
        setAnalyses(prev => [...prev, {...data, filename: file.name}]);
      }
    } catch {
      setError("连接后端失败，请确认服务已启动");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4">
      <header className="flex items-center gap-3 py-4">
        <a href="/toolbox" className="text-[var(--color-text-muted)] no-underline hover:text-[var(--color-accent)]">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15,18 9,12 15,6"/></svg>
        </a>
        <h1 className="text-lg font-semibold tracking-tight">证据分析</h1>
      </header>

      <div className="card">
        <p className="text-xs text-[var(--color-text-muted)] mb-4">
          上传聊天截图、工资单、考勤记录等证据，AI 自动识别关键信息并评估证据强度。
        </p>

        <div className="input-field !p-6 text-center !border-dashed cursor-pointer" onClick={() => document.getElementById("evidence-files")?.click()}>
          <input id="evidence-files" type="file" multiple accept=".pdf,.doc,.docx,.jpg,.png,.xlsx" className="hidden" onChange={e => setFiles(Array.from(e.target.files || []))} />
          <svg className="mx-auto mb-2" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="1.5"><path d="M21.44 11.05l-9.19 9.19a4 4 0 01-5.66-5.66l9.19-9.19M11.05 21.44l1.41-1.41M15 9l2.12 2.12"/></svg>
          <div className="text-sm text-[var(--color-text-muted)]">
            {files.length ? `已选 ${files.length} 个文件` : "点击选择证据文件（支持多选）"}
          </div>
        </div>

        {files.length > 0 && (
          <ul className="mt-3 space-y-1">
            {files.map((f, i) => (
              <li key={i} className="text-xs text-[var(--color-text-muted)] flex justify-between">
                <span>{f.name}</span>
                <span>{(f.size / 1024).toFixed(1)} KB</span>
              </li>
            ))}
          </ul>
        )}

        <button onClick={handleAnalyze} disabled={!files.length || loading} className="btn-primary w-full text-center py-2.5 mt-4">
          {loading ? "分析中..." : "开始分析"}
        </button>

        {error && <div className="text-xs text-[var(--color-danger)] bg-[#FEF2F2] p-3 rounded-sm mt-3">{error}</div>}
      </div>

      {analyses.map((a, i) => (
        <div key={i} className="card mt-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium truncate">{a.filename}</span>
            {a.analysis?.strength_score != null && (
              <span className={`tag ${a.analysis.strength_score >= 70 ? "tag-success" : a.analysis.strength_score >= 40 ? "tag-info" : "tag-danger"}`}>
                强度 {a.analysis.strength_score} 分
              </span>
            )}
          </div>
          {a.analysis?.category && <div className="text-xs text-[var(--color-text-muted)]">类型：{a.analysis.category}</div>}
          {a.analysis?.key_facts?.length > 0 && (
            <div className="mt-2">
              <div className="text-xs font-medium mb-1">识别到的关键信息</div>
              <ul className="text-xs text-[var(--color-text-muted)] space-y-0.5">
                {a.analysis.key_facts.map((f: string, j: number) => <li key={j} className="law-ref">{f}</li>)}
              </ul>
            </div>
          )}
          {a.ocr_text && (
            <details className="mt-2">
              <summary className="text-xs text-[var(--color-text-muted)] cursor-pointer">OCR 识别文本</summary>
              <pre className="text-xs mt-1 p-2 bg-[var(--color-bg)] rounded-sm whitespace-pre-wrap max-h-32 overflow-y-auto">{a.ocr_text}</pre>
            </details>
          )}
        </div>
      ))}

      <p className="disclaimer">⚠️ AI 分析结果仅供参考，证据效力以劳动仲裁或法院认定为准。</p>
    </div>
  );
}
