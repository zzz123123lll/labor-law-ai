"use client";

import { useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";

interface Doc {
  id: string;
  doc_type: string;
  title: string;
  status: string;
  created_at: string;
}

const docTypeLabel: Record<string, string> = {
  arbitration_request: "仲裁申请书",
  complaint_letter: "投诉信",
  evidence_list: "证据清单",
};

export default function DocumentsPage() {
  const [docs, setDocs] = useState<Doc[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState<string | null>(null);

  useEffect(() => {
    apiFetch("/api/cases")
      .then(r => r.json())
      .then(async cases => {
        if (!Array.isArray(cases)) { setLoading(false); return; }
        // 遍历案件获取文书
        const allDocs: Doc[] = [];
        for (const c of cases) {
          try {
            const r = await apiFetch(`/api/cases/${c.id}`);
            const detail = await r.json();
            if (detail.generated_documents?.length) {
              allDocs.push(...detail.generated_documents);
            }
          } catch {}
        }
        setDocs(allDocs);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleDownload = async (docId: string) => {
    setDownloading(docId);
    try {
      const r = await apiFetch(`/api/document/download/${docId}`);
      const data = await r.json();
      // 下载 Markdown 文本
      const blob = new Blob([data.content || ""], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = `${data.title || "文书"}.md`;
      a.click(); URL.revokeObjectURL(url);
    } catch {}
    setDownloading(null);
  };

  return (
    <div className="p-4">
      <header className="py-4">
        <h1 className="text-lg font-semibold tracking-tight">我的文书</h1>
      </header>

      {loading ? (
        <div className="flex items-center gap-2 justify-center py-12 text-[var(--color-text-muted)] text-sm">
          <span className="w-2 h-2 rounded-full bg-[var(--color-accent)] animate-pulse"/>加载中...
        </div>
      ) : docs.length === 0 ? (
        <div className="card text-center py-10">
          <svg className="mx-auto mb-3" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="1.5"><path d="M11 5H6a2 2 0 00-2 2v12a2 2 0 002 2h8M12 13l3-3 3 3M21 10v9M12 3l9 4v2l-9-4-9 4V7l9-4z"/></svg>
          <p className="text-sm text-[var(--color-text-muted)]">暂无文书</p>
          <p className="text-xs text-[var(--color-text-muted)] mt-1 mb-4">完成 AI 咨询后可自动生成法律文书</p>
          <a href="/consultation" className="btn-primary no-underline text-sm inline-block">开始咨询</a>
        </div>
      ) : (
        <div className="space-y-2">
          {docs.map(d => (
            <div key={d.id} className="card flex items-center justify-between">
              <div>
                <div className="text-sm font-medium">{d.title}</div>
                <div className="text-xs text-[var(--color-text-muted)] mt-0.5">
                  {docTypeLabel[d.doc_type] || d.doc_type} · {d.created_at ? new Date(d.created_at).toLocaleDateString("zh-CN") : "--"}
                </div>
              </div>
              <button
                onClick={() => handleDownload(d.id)}
                disabled={downloading === d.id}
                className="btn-ghost text-xs"
              >
                {downloading === d.id ? "下载中" : "下载"}
              </button>
            </div>
          ))}
        </div>
      )}

      <p className="disclaimer">⚠️ 生成文书为草稿，建议由专业律师审核后使用。</p>
    </div>
  );
}
