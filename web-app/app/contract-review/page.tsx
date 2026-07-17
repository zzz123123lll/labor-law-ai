"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export default function ContractReviewPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState("");

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError("");
    setReport(null);

    try {
      const form = new FormData();
      form.append("file", file);

      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;

      // 上传文件
      const upResp = await fetch(`${API_BASE}/api/contract/upload`, { method: "POST", headers, body: form });
      if (!upResp.ok) { setError("上传失败"); setUploading(false); return; }
      const uploaded = await upResp.json();

      // 发起审查
      const revResp = await apiFetch(`/api/contract/review/${uploaded.id}`, { method: "POST" });
      const data = await revResp.json();
      if (revResp.ok) { setReport(data); }
      else { setError(data.detail || "审查失败"); }
    } catch {
      setError("连接后端失败，请确认服务已启动");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-4">
      <header className="flex items-center gap-3 py-4">
        <a href="/toolbox" className="text-[var(--color-text-muted)] no-underline hover:text-[var(--color-accent)]">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15,18 9,12 15,6"/></svg>
        </a>
        <h1 className="text-lg font-semibold tracking-tight">合同审查</h1>
      </header>

      <div className="card">
        <p className="text-xs text-[var(--color-text-muted)] mb-4">上传劳动合同（PDF/Word/图片），AI 自动审查试用期、工资、竞业限制等条款。</p>

        <div className="input-field !p-6 text-center !border-dashed cursor-pointer" onClick={() => document.getElementById("contract-file")?.click()}>
          <input id="contract-file" type="file" accept=".pdf,.doc,.docx,.jpg,.png" className="hidden" onChange={e => setFile(e.target.files?.[0] || null)} />
          <svg className="mx-auto mb-2" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="1.5"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
          <div className="text-sm text-[var(--color-text-muted)]">{file ? file.name : "点击选择合同文件"}</div>
          {file && <div className="text-xs text-[var(--color-text-muted)] mt-1">{(file.size / 1024).toFixed(1)} KB</div>}
        </div>

        <button onClick={handleUpload} disabled={!file || uploading} className="btn-primary w-full text-center py-2.5 mt-4">
          {uploading ? "审查中..." : "开始审查"}
        </button>

        {error && <div className="text-xs text-[var(--color-danger)] bg-[#FEF2F2] p-3 rounded-sm mt-3">{error}</div>}
      </div>

      {report && (
        <div className="card mt-3">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium">审查报告</span>
            <span className="tag tag-info">评分 {report.score} 分</span>
          </div>

          {report.findings?.map((f: any, i: number) => (
            <div key={i} className="border border-[var(--color-border)] rounded-sm p-3 mb-2 last:mb-0">
              <div className="flex items-center gap-2 mb-1">
                <span className={`tag ${f.risk === "high" ? "tag-danger" : f.risk === "medium" ? "tag-info" : "tag-success"}`}>
                  {f.risk === "high" ? "高风险" : f.risk === "medium" ? "中风险" : "低风险"}
                </span>
                <span className="text-sm font-medium">{f.clause || "条款"}</span>
              </div>
              <p className="text-xs text-[var(--color-text-muted)]">{f.problem}</p>
              {f.suggestion && <p className="text-xs text-[var(--color-success)] mt-1">建议：{f.suggestion}</p>}
              {f.law_ref && <div className="law-ref mt-2">{f.law_ref}</div>}
            </div>
          ))}

          {report.full_report && (
            <details className="mt-3">
              <summary className="text-xs text-[var(--color-text-muted)] cursor-pointer">完整报告</summary>
              <pre className="text-xs mt-2 whitespace-pre-wrap">{report.full_report}</pre>
            </details>
          )}
        </div>
      )}

      <p className="disclaimer">⚠️ AI 审查结果仅供参考，不构成法律意见。建议咨询专业律师。</p>
    </div>
  );
}
