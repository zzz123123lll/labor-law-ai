import type { Metadata } from "next";
import { AntdRegistry } from "@ant-design/nextjs-registry";
import "./globals.css";

export const metadata: Metadata = {
  title: "劳动法智能维权 - 管理后台",
};

const API_BASE = "http://localhost:8000";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <AntdRegistry>
          <div className="flex min-h-screen">
            {/* 侧边栏 */}
            <aside className="w-52 bg-slate-800 text-white min-h-screen p-4">
              <div className="text-lg font-bold mb-6 px-2">🔧 管理后台</div>
              <nav className="space-y-1 text-sm">
                <a href="/" className="block px-3 py-2 rounded hover:bg-slate-700">📊 数据面板</a>
                <a href="/users" className="block px-3 py-2 rounded hover:bg-slate-700">👥 用户管理</a>
                <a href="/cases" className="block px-3 py-2 rounded hover:bg-slate-700">📋 案件管理</a>
              </nav>
            </aside>
            <main className="flex-1 bg-gray-100 p-6">{children}</main>
          </div>
        </AntdRegistry>
      </body>
    </html>
  );
}
