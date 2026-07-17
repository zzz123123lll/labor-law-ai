export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-[var(--color-accent)] animate-pulse" />
        <span className="text-xs text-[var(--color-text-muted)]">加载中...</span>
      </div>
    </div>
  );
}
