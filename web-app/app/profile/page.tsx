"use client";

import { useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";

export default function ProfilePage() {
  const [user, setUser] = useState<any>(null);
  const [sub, setSub] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/api/auth/me")
      .then(r => r.json())
      .then(data => { if (data.id) setUser(data); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (user) {
      apiFetch("/api/payment/my-subscription")
        .then(r => r.json())
        .then(data => { if (data) setSub(data); })
        .catch(() => {});
    }
  }, [user]);

  if (loading) {
    return <div className="flex items-center gap-2 justify-center py-20 text-[var(--color-text-muted)] text-sm"><span className="w-2 h-2 rounded-full bg-[var(--color-accent)] animate-pulse"/>加载中...</div>;
  }

  return (
    <div className="p-4">
      <header className="py-6 text-center">
        <h1 className="text-lg font-semibold tracking-tight">我的</h1>
      </header>

      {/* 用户信息 */}
      <div className="card text-center mb-3">
        {user ? (
          <>
            <div className="w-14 h-14 mx-auto rounded-full bg-[var(--color-bg)] flex items-center justify-center mb-3">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="1.5"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <div className="text-sm font-medium">{user.nickname || "用户"}</div>
            <div className="text-xs text-[var(--color-text-muted)] mt-0.5">{user.phone || "未绑定手机"}</div>
            {user.is_vip ? (
              <span className="tag tag-success mt-2 inline-flex">VIP 会员</span>
            ) : (
              <a href="/profile/subscription" className="btn-primary text-xs inline-block mt-2 no-underline">开通专业版</a>
            )}
          </>
        ) : (
          <>
            <div className="w-14 h-14 mx-auto rounded-full bg-[var(--color-bg)] flex items-center justify-center mb-3">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="1.5"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <p className="text-sm text-[var(--color-text-muted)] mb-3">登录后使用全部功能</p>
            <button disabled className="btn-primary text-sm disabled:opacity-50">微信登录（即将开放）</button>
          </>
        )}
      </div>

      {/* 订阅信息 */}
      {sub && (
        <div className="card mb-3">
          <div className="text-xs font-medium mb-1">当前方案</div>
          <div className="flex items-center justify-between">
            <span className="text-sm">{sub.plan_id === "yearly" ? "企业版" : sub.plan_id === "monthly" ? "专业版" : "免费版"}</span>
            {sub.end_at && <span className="text-xs text-[var(--color-text-muted)]">到期 {new Date(sub.end_at).toLocaleDateString("zh-CN")}</span>}
          </div>
        </div>
      )}

      {/* 导航 */}
      <div className="card !p-0 divide-y divide-[var(--color-border)]">
        <a href="/cases" className="flex items-center justify-between px-4 py-3 text-sm text-inherit no-underline">
          <span>我的案件</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="2"><polyline points="9,18 15,12 9,6"/></svg>
        </a>
        <a href="/documents" className="flex items-center justify-between px-4 py-3 text-sm text-inherit no-underline">
          <span>我的文书</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="2"><polyline points="9,18 15,12 9,6"/></svg>
        </a>
        <a href="/profile/subscription" className="flex items-center justify-between px-4 py-3 text-sm text-inherit no-underline">
          <span>订阅管理</span>
          <span className="tag tag-info text-[10px]">{user?.is_vip ? "VIP" : "免费"}</span>
        </a>
        <div className="flex items-center justify-between px-4 py-3 text-sm text-[var(--color-text-muted)]">
          <span>版本</span>
          <span>1.0.0</span>
        </div>
      </div>

      <p className="disclaimer">⚠️ 本工具基于AI分析，不替代专业律师意见。</p>
    </div>
  );
}
