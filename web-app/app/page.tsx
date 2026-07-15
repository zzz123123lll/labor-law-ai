export default function HomePage() {
  return (
    <div className="p-4">
      {/* 头部 */}
      <header className="py-8 text-center">
        <h1 className="text-xl font-semibold tracking-tight mb-1">劳动法维权AI</h1>
        <p className="text-xs text-[var(--color-text-muted)]">你的劳动权益保护助手</p>
      </header>

      {/* 主入口 */}
      <div className="card mb-3 cursor-pointer hover:border-[var(--color-accent)] transition-colors">
        <a href="/consultation" className="block no-underline text-inherit">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-md bg-[var(--color-accent)] flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
            </div>
            <div>
              <div className="font-medium text-sm">开始AI咨询</div>
              <div className="text-xs text-[var(--color-text-muted)]">描述你的劳动问题，获取法律分析</div>
            </div>
            <svg className="ml-auto" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="2"><polyline points="9,18 15,12 9,6"/></svg>
          </div>
        </a>
      </div>

      {/* 工具入口 */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <a href="/compensation" className="card py-3 no-underline text-inherit hover:border-[var(--color-accent)] transition-colors">
          <div className="text-xs font-medium">赔偿计算</div>
          <div className="text-[10px] text-[var(--color-text-muted)] mt-0.5">算算能赔多少</div>
        </a>
        <a href="/contract-review" className="card py-3 no-underline text-inherit hover:border-[var(--color-accent)] transition-colors">
          <div className="text-xs font-medium">合同审查</div>
          <div className="text-[10px] text-[var(--color-text-muted)] mt-0.5">上传合同 AI审查</div>
        </a>
        <a href="/evidence/upload" className="card py-3 no-underline text-inherit hover:border-[var(--color-accent)] transition-colors">
          <div className="text-xs font-medium">证据分析</div>
          <div className="text-[10px] text-[var(--color-text-muted)] mt-0.5">上传证据 自动分析</div>
        </a>
        <a href="/documents" className="card py-3 no-underline text-inherit hover:border-[var(--color-accent)] transition-colors">
          <div className="text-xs font-medium">文书生成</div>
          <div className="text-[10px] text-[var(--color-text-muted)] mt-0.5">仲裁申请书等</div>
        </a>
      </div>

      {/* 快速测试 */}
      <div className="card mb-3">
        <div className="text-xs font-medium mb-2">试试这些场景</div>
        <div className="space-y-1.5">
          {[
            "公司突然辞退我不给补偿",
            "试用期6个月合法吗",
            "加班没给加班费怎么办",
            "公司没签劳动合同能赔多少",
          ].map((q, i) => (
            <a
              key={i}
              href={`/consultation?q=${encodeURIComponent(q)}`}
              className="block text-xs text-[var(--color-text-muted)] py-1.5 px-2 rounded-sm hover:bg-[var(--color-bg)] no-underline hover:text-[var(--color-accent)] transition-colors"
            >
              {q} →
            </a>
          ))}
        </div>
      </div>

      <p className="disclaimer">
        本工具基于AI分析，不替代专业律师意见<br />重大权益请咨询律师
      </p>
    </div>
  );
}
