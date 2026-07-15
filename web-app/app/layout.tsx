import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "劳动法维权AI",
  description: "劳动法智能维权助手——帮你分析劳动问题，计算赔偿，生成文书",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen">
        {/* 移动端居中窄栏 / PC 端全宽 */}
        <main className="mx-auto pb-14 md:pt-14 max-w-[640px] md:max-w-[960px] lg:max-w-[1200px] px-4 md:px-8">
          {children}
        </main>
        {/* 移动端底部Tab / PC 端顶部导航 */}
        <nav className="tab-bar md:bottom-auto md:top-0 md:h-12 md:items-center md:border-b md:border-[var(--color-border)] md:justify-start md:gap-8 md:px-8">
          <a href="/" className="tab-item active md:flex-row md:gap-1.5 md:text-sm">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>
            首页
          </a>
          <a href="/consultation" className="tab-item md:flex-row md:gap-1.5 md:text-sm">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
            咨询
          </a>
          <a href="/toolbox" className="tab-item md:flex-row md:gap-1.5 md:text-sm">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
            工具
          </a>
          <a href="/cases" className="tab-item md:flex-row md:gap-1.5 md:text-sm">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/></svg>
            案件
          </a>
          <a href="/profile" className="tab-item md:flex-row md:gap-1.5 md:text-sm">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            我的
          </a>
        </nav>
      </body>
    </html>
  );
}
