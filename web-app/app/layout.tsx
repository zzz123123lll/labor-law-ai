import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "劳动法智能维权AI",
  description: "劳动法智能维权助手",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="bg-gray-50 min-h-screen">
        <main className="max-w-lg mx-auto pb-16">{children}</main>
        <nav className="fixed bottom-0 left-0 right-0 max-w-lg mx-auto bg-white border-t flex justify-around py-2 text-xs text-gray-500 z-50">
          <a href="/" className="flex flex-col items-center">
            <span className="text-lg">🏠</span>首页
          </a>
          <a href="/consultation" className="flex flex-col items-center">
            <span className="text-lg">💬</span>AI咨询
          </a>
          <a href="/toolbox" className="flex flex-col items-center">
            <span className="text-lg">🧰</span>工具箱
          </a>
          <a href="/cases" className="flex flex-col items-center">
            <span className="text-lg">📋</span>案件
          </a>
          <a href="/profile" className="flex flex-col items-center">
            <span className="text-lg">👤</span>我的
          </a>
        </nav>
      </body>
    </html>
  );
}
