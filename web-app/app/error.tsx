"use client";

import { useEffect } from "react";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("页面错误:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-8 text-center">
      <div className="text-4xl mb-4">⚠</div>
      <h2 className="text-sm font-medium mb-1">页面加载出错</h2>
      <p className="text-xs text-[var(--color-text-muted)] mb-4">
        {error.message || "发生未知错误，请重试"}
      </p>
      <button onClick={reset} className="btn-primary text-xs">
        重新加载
      </button>
      <a href="/" className="text-xs text-[var(--color-text-muted)] mt-3 hover:text-[var(--color-accent)]">
        返回首页
      </a>
    </div>
  );
}
