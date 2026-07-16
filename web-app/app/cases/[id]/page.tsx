"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";

const stageLabel: Record<string, string> = { consultation: "咨询中", evidence: "取证中", negotiation: "协商中", arbitration: "仲裁中", litigation: "诉讼中", closed: "已结案" };

export default function CaseDetailPage() {
  const params = useParams();
  const caseId = params.id as string;
  const [detail, setDetail] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch(`/api/cases/${caseId}`)
      .then(r => r.json())
      .then(data => setDetail(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [caseId]);

  if (loading) {
    return <div className="flex items-center gap-2 justify-center py-20 text-[var(--color-text-muted)] text-sm"><span className="w-2 h-2 rounded-full bg-[var(--color-accent)] animate-pulse"/>加载中...</div>;
  }

  if (!detail) {
    return <div className="p-4 text-center py-20 text-sm text-[var(--color-text-muted)]">案件不存在</div>;
  }

  const profile = detail.profile || {};

  return (
    <div className="p-4">
      <header className="flex items-center gap-3 py-4">
        <a href="/cases" className="text-[var(--color-text-muted)] no-underline hover:text-[var(--color-accent)]">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15,18 9,12 15,6"/></svg>
        </a>
        <h1 className="text-lg font-semibold truncate">{detail.title}</h1>
      </header>

      {/* 案件状态 */}
      <div className="card mb-3">
        <div className="flex items-center justify-between mb-3">
          <span className={`tag tag-info`}>{stageLabel[detail.stage] || detail.stage}</span>
          {detail.risk_level && (
            <span className={`tag ${detail.risk_level === "critical" || detail.risk_level === "high" ? "tag-danger" : "tag-info"}`}>
              {detail.risk_level === "critical" ? "严重" : detail.risk_level === "high" ? "高风险" : detail.risk_level === "medium" ? "中风险" : "低风险"}
            </span>
          )}
        </div>

        {/* 案件画像 */}
        {Object.keys(profile).length > 0 && (
          <div className="grid grid-cols-2 gap-2 text-xs">
            {profile.company_name && <div><span className="text-[var(--color-text-muted)]">公司：</span>{profile.company_name}</div>}
            {profile.city && <div><span className="text-[var(--color-text-muted)]">地点：</span>{profile.city}</div>}
            {profile.monthly_salary && <div><span className="text-[var(--color-text-muted)]">月薪：</span>¥{profile.monthly_salary?.toLocaleString()}</div>}
            {profile.hire_date && <div><span className="text-[var(--color-text-muted)]">入职：</span>{profile.hire_date}</div>}
            {profile.has_contract !== undefined && <div><span className="text-[var(--color-text-muted)]">合同：</span>{profile.has_contract ? "已签" : "未签"}</div>}
            {profile.has_social_insurance !== undefined && <div><span className="text-[var(--color-text-muted)]">社保：</span>{profile.has_social_insurance ? "已缴" : "未缴"}</div>}
          </div>
        )}
      </div>

      {/* 赔偿摘要 */}
      {(detail.total_claim_min || detail.total_claim_max) && (
        <div className="card mb-3">
          <div className="text-xs font-medium mb-2">可主张金额</div>
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-[var(--color-success)] text-lg font-semibold">¥{detail.total_claim_min?.toLocaleString() || "--"}</span>
            <span className="text-xs text-[var(--color-text-muted)]">~</span>
            <span className="font-mono text-[var(--color-success)] font-semibold">¥{detail.total_claim_max?.toLocaleString() || "--"}</span>
          </div>
        </div>
      )}

      {/* 操作入口 */}
      <div className="card mb-3">
        <div className="text-xs font-medium mb-2">快捷操作</div>
        <div className="space-y-1.5">
          <a href={`/consultation`} className="flex items-center justify-between text-xs no-underline hover:text-[var(--color-accent)] py-1.5 text-inherit">
            <span>继续AI咨询</span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9,18 15,12 9,6"/></svg>
          </a>
          <a href="/compensation" className="flex items-center justify-between text-xs no-underline hover:text-[var(--color-accent)] py-1.5 text-inherit">
            <span>赔偿计算</span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9,18 15,12 9,6"/></svg>
          </a>
          <a href="/documents" className="flex items-center justify-between text-xs no-underline hover:text-[var(--color-accent)] py-1.5 text-inherit">
            <span>生成文书</span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9,18 15,12 9,6"/></svg>
          </a>
        </div>
      </div>

      <p className="disclaimer">⚠️ 案件信息仅供个人维权参考，不构成法律意见。</p>
    </div>
  );
}
