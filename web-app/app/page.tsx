export default function HomePage() {
  const problems = [
    {
      key: "被辞退",
      title: "被辞退 / 被开除",
      desc: "被公司辞退、开除、劝退，不给补偿",
      icon: (
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
      ),
    },
    {
      key: "拖欠工资",
      title: "拖欠 / 克扣工资",
      desc: "被欠薪、少发工资、不按时发工资",
      icon: (
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
      ),
    },
    {
      key: "想离职",
      title: "想离职 / 被迫离职",
      desc: "公司逼你走、调岗降薪、协商解除",
      icon: (
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/></svg>
      ),
    },
    {
      key: "其他问题",
      title: "其他劳动问题",
      desc: "加班费、工伤、社保、竞业限制、年假等",
      icon: (
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
      ),
    },
  ];

  return (
    <div className="p-4">
      {/* 头部 */}
      <header className="py-6 text-center">
        <h1 className="text-xl font-semibold tracking-tight mb-1">劳动法维权助手</h1>
        <p className="text-xs text-[var(--color-text-muted)]">AI 帮你分析问题 · 计算赔偿 · 生成仲裁材料</p>
      </header>

      {/* 核心入口：选问题类型 */}
      <div className="mb-4">
        <p className="text-xs text-[var(--color-text-muted)] mb-2">你遇到了什么问题？</p>
        <div className="space-y-2">
          {problems.map((p) => (
            <a
              key={p.key}
              href={`/consultation?type=${encodeURIComponent(p.key)}`}
              className="card flex items-center gap-3 no-underline text-inherit cursor-pointer hover:border-[var(--color-accent)] transition-colors py-3"
            >
              <div className="flex-shrink-0 w-10 h-10 rounded-md bg-[var(--color-bg)] flex items-center justify-center text-[var(--color-accent)]">
                {p.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium">{p.title}</div>
                <div className="text-xs text-[var(--color-text-muted)] mt-0.5">{p.desc}</div>
              </div>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="2"><polyline points="9,18 15,12 9,6"/></svg>
            </a>
          ))}
        </div>
      </div>

      {/* 工具入口 */}
      <p className="text-xs text-[var(--color-text-muted)] mb-2 mt-6">或直接使用工具</p>
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
          <div className="text-xs font-medium">我的文书</div>
          <div className="text-[10px] text-[var(--color-text-muted)] mt-0.5">已生成的法律文书</div>
        </a>
      </div>

      <p className="disclaimer text-xs text-[var(--color-text-muted)] text-center py-4">
        本工具基于 AI 分析，不替代专业律师意见
      </p>
    </div>
  );
}
