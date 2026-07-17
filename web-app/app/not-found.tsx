import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-8 text-center">
      <div className="text-4xl mb-4 text-[var(--color-text-muted)]">404</div>
      <h2 className="text-sm font-medium mb-1">页面不存在</h2>
      <p className="text-xs text-[var(--color-text-muted)] mb-4">请检查链接是否正确</p>
      <Link href="/" className="btn-primary text-xs no-underline inline-block">
        返回首页
      </Link>
    </div>
  );
}
