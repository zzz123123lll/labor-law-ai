"use client";

import { useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";

interface CaseItem {
  id: string;
  title: string;
  stage: string;
  risk_level: string | null;
  updated_at: string;
  created_at: string;
}

const stageLabel: Record<string, string> = {
  consultation: "咨询中",
  evidence: "取证中",
  negotiation: "协商中",
  arbitration: "仲裁中",
  litigation: "诉讼中",
  closed: "已结案",
};

const riskBadge: Record<string, string> = {
  low: "tag-success",
  medium: "tag-info",
  high: "tag-danger",
  critical: "tag-danger",
};

export default function CasesPage() {
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/api/cases")
      .then(r => r.json())
      .then(data => { if (Array.isArray(data)) setCases(data); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-4">
      <header className="py-4 flex items-center justify-between">
        <h1 className="text-lg font-semibold tracking-tight">我的案件</h1>
        <a href="/consultation" className="btn-ghost text-xs no-underline">+ 新建</a>
      </header>

      {loading ? (
        <div className="flex items-center gap-2 justify-center py-12 text-[var(--color-text-muted)] text-sm">
          <span className="w-2 h-2 rounded-full bg-[var(--color-accent)] animate-pulse" />
          加载中...
        </div>
      ) : cases.length === 0 ? (
        <div className="card text-center py-10">
          <svg className="mx-auto mb-3" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/></svg>
          <p className="text-sm text-[var(--color-text-muted)]">暂无案件</p>
          <p className="text-xs text-[var(--color-text-muted)] mt-1 mb-4">遇到劳动问题？开始 AI 咨询</p>
          <a href="/consultation" className="btn-primary no-underline text-sm inline-block">开始咨询</a>
        </div>
      ) : (
        <div className="space-y-2">
          {cases.map(c => (
            <a key={c.id} href={`/cases/${c.id}`} className="card flex items-center justify-between no-underline text-inherit hover:border-[var(--color-accent)] transition-colors">
              <div className="min-w-0">
                <div className="text-sm font-medium truncate">{c.title}</div>
                <div className="text-xs text-[var(--color-text-muted)] mt-0.5">{c.created_at ? new Date(c.created_at).toLocaleDateString("zh-CN") : "--"}</div>
              </div>
              <div className="flex items-center gap-2 shrink-0 ml-3">
                {c.risk_level && <span className={`tag ${riskBadge[c.risk_level] || "tag-info"}`}>{c.risk_level}</span>}
                <span className="tag tag-info">{stageLabel[c.stage] || c.stage}</span>
              </div>
            </a>
          ))}
        </div>
      )}

      <p className="disclaimer">⚠️ 案件信息仅供个人维权参考，不构成法律意见。</p>
    </div>
  );
}
