export default function ToolboxPage() {
  const tools = [
    { href: "/compensation", icon: "M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5", label: "赔偿计算", desc: "经济补偿金、赔偿金、加班费一键计算" },
    { href: "/contract-review", icon: "M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8zM14 2v6h6M16 13H8M16 17H8M10 9H8", label: "合同审查", desc: "上传劳动合同，AI 逐条审查风险" },
    { href: "/documents", icon: "M11 5H6a2 2 0 00-2 2v12a2 2 0 002 2h8M12 13l3-3 3 3M21 10v9M12 3l9 4v2l-9-4-9 4V7l9-4z", label: "文书生成", desc: "仲裁申请书、投诉信、证据清单自动生成" },
    { href: "/evidence/upload", icon: "M21.44 11.05l-9.19 9.19a4 4 0 01-5.66-5.66l9.19-9.19M11.05 21.44l1.41-1.41M15 9l2.12 2.12", label: "证据分析", desc: "上传证据材料，AI 评估证明力与完整性" },
  ];

  return (
    <div className="p-4">
      <header className="py-6 text-center">
        <h1 className="text-lg font-semibold tracking-tight">工具箱</h1>
        <p className="text-xs text-[var(--color-text-muted)] mt-1">常用维权工具</p>
      </header>

      <div className="space-y-2">
        {tools.map((t, i) => (
          <a key={i} href={t.href} className="card flex items-center gap-3 no-underline text-inherit hover:border-[var(--color-accent)] transition-colors">
            <div className="w-10 h-10 rounded-md bg-[var(--color-bg)] flex items-center justify-center shrink-0">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" strokeWidth="1.5"><path d={t.icon}/></svg>
            </div>
            <div>
              <div className="text-sm font-medium">{t.label}</div>
              <div className="text-xs text-[var(--color-text-muted)]">{t.desc}</div>
            </div>
            <svg className="ml-auto shrink-0" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="2"><polyline points="9,18 15,12 9,6"/></svg>
          </a>
        ))}
      </div>

      <p className="disclaimer mt-4">⚠️ 工具计算结果仅供参考，具体以劳动仲裁或法院裁定为准。</p>
    </div>
  );
}
