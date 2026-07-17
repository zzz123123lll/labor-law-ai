"use client";

import { useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";

export default function CompensationPage() {
  const [salary, setSalary] = useState("");
  const [hireDate, setHireDate] = useState("");
  const [leaveDate, setLeaveDate] = useState("");
  const [leaveType, setLeaveType] = useState("unlawful");
  const [hasContract, setHasContract] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  // 从 Wizard 预填数据
  useEffect(() => {
    try {
      const saved = sessionStorage.getItem("consultation_wizard");
      if (saved) {
        const data = JSON.parse(saved);
        if (data.form) {
          if (data.form.monthly_salary && !salary) setSalary(data.form.monthly_salary);
          if (data.form.hire_date && !hireDate) setHireDate(data.form.hire_date);
        }
      }
    } catch {}
  }, []);

  const handleCalc = async () => {
    if (!salary || !hireDate) { setError("请至少填写月工资和入职日期"); return; }
    setError("");
    setLoading(true);
    setResult(null);

    try {
      const r = await apiFetch("/api/compensation/calculate", {
        method: "POST",
        body: JSON.stringify({
          monthly_salary: parseFloat(salary),
          hire_date: hireDate,
          leave_date: leaveDate || undefined,
          leave_type: leaveType,
          has_contract: hasContract === "yes",
          ...(() => {
            try {
              const saved = sessionStorage.getItem("consultation_wizard");
              const data = saved ? JSON.parse(saved) : null;
              return data?.caseId ? { case_id: data.caseId } : {};
            } catch { return {}; }
          })(),
        }),
      });
      const data = await r.json();
      if (r.ok) setResult(data);
      else setError(data.detail || "计算失败");
    } catch {
      setError("连接后端失败，请确认服务已启动");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4">
      <header className="flex items-center gap-3 py-4">
        <a href="/toolbox" className="text-[var(--color-text-muted)] no-underline hover:text-[var(--color-accent)]">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15,18 9,12 15,6"/></svg>
        </a>
        <h1 className="text-lg font-semibold tracking-tight">赔偿计算器</h1>
      </header>

      {salary && hireDate && (
        <div className="text-xs bg-[#EFF6FF] text-[var(--color-accent)] px-3 py-2 rounded-sm mb-3">
          已从咨询案件自动填入数据，可直接计算
        </div>
      )}

      <div className="card space-y-4">
        <div>
          <label className="block text-xs font-medium text-[var(--color-text-muted)] mb-1">月平均工资（税前·元）</label>
          <input type="number" className="input-field w-full" placeholder="如 8000" value={salary} onChange={e => setSalary(e.target.value)} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-muted)] mb-1">入职日期</label>
            <input type="date" className="input-field w-full" value={hireDate} onChange={e => setHireDate(e.target.value)} />
          </div>
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-muted)] mb-1">离职日期</label>
            <input type="date" className="input-field w-full" value={leaveDate} onChange={e => setLeaveDate(e.target.value)} />
          </div>
        </div>
        <div>
          <label className="block text-xs font-medium text-[var(--color-text-muted)] mb-1">离职类型</label>
          <select className="input-field w-full" value={leaveType} onChange={e => setLeaveType(e.target.value)}>
            <option value="unlawful">违法解除（被辞退不给补偿）</option>
            <option value="negotiated">协商解除</option>
            <option value="voluntary">主动辞职</option>
            <option value="expired">合同到期不续</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-[var(--color-text-muted)] mb-1">是否签劳动合同</label>
          <select className="input-field w-full" value={hasContract} onChange={e => setHasContract(e.target.value)}>
            <option value="">请选择</option>
            <option value="yes">已签订</option>
            <option value="no">未签订（可主张双倍工资）</option>
          </select>
        </div>

        <button onClick={handleCalc} disabled={loading} className="btn-primary w-full text-center py-2.5">
          {loading ? "计算中..." : "开始计算"}
        </button>

        {error && <div className="text-xs text-[var(--color-danger)] bg-[#FEF2F2] p-3 rounded-sm">{error}</div>}

        {result && (
          <div className="report-card mt-2">
            <div className="text-xs font-medium mb-3">计算结果</div>
            <div className="space-y-3">
              {result.items?.map((item: any, i: number) => (
                <div key={i} className="flex justify-between items-start border-b border-[var(--color-border)] pb-2 last:border-0">
                  <div>
                    <div className="text-sm">{item.category}</div>
                    <div className="text-xs text-[var(--color-text-muted)]">{item.basis}</div>
                  </div>
                  <div className="text-sm font-mono text-[var(--color-success)] font-medium">¥{item.amount?.toLocaleString() || "--"}</div>
                </div>
              ))}
            </div>
            <div className="flex justify-between items-center mt-3 pt-3 border-t border-[var(--color-border)]">
              <span className="text-sm font-medium">合计可主张</span>
              <div>
                <span className="text-xs text-[var(--color-text-muted)]">最低 </span>
                <span className="font-mono text-[var(--color-success)] font-semibold">¥{result.total_min?.toLocaleString() || "--"}</span>
                <span className="text-xs text-[var(--color-text-muted)] mx-1">~</span>
                <span className="text-xs text-[var(--color-text-muted)]">最高 </span>
                <span className="font-mono text-[var(--color-success)] font-semibold">¥{result.total_max?.toLocaleString() || "--"}</span>
              </div>
            </div>
            {result.calculation && (
              <details className="mt-3">
                <summary className="text-xs text-[var(--color-text-muted)] cursor-pointer">计算过程</summary>
                <pre className="text-xs mt-2 text-[var(--color-text-muted)] whitespace-pre-wrap">{result.calculation}</pre>
              </details>
            )}
            {(() => {
              try {
                const saved = sessionStorage.getItem("consultation_wizard");
                const data = saved ? JSON.parse(saved) : null;
                if (data?.caseId) {
                  return (
                    <div className="mt-4 pt-3 border-t border-[var(--color-border)]">
                      <a
                        href={`/consultation/cases/${data.caseId}`}
                        className="text-xs text-[var(--color-accent)] hover:underline"
                      >
                        返回案件
                      </a>
                    </div>
                  );
                }
              } catch {}
              return null;
            })()}
          </div>
        )}
      </div>

      <p className="disclaimer">⚠️ 计算结果仅供参考，具体金额以劳动仲裁或法院裁定为准。</p>
    </div>
  );
}
