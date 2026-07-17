"use client";

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

type ProblemType = "fired" | "wage" | "resign" | "other";
type Step = 1 | 2 | 3;

interface AgentMessage {
  agent: string;
  content: string;
}

interface FormData {
  companyName: string;
  city: string;
  hireDate: string;
  monthlySalary: string;
}

interface ProblemTypeConfig {
  id: ProblemType;
  icon: React.ReactNode;
  title: string;
  desc: string;
}

const PROBLEM_TYPES: ProblemTypeConfig[] = [
  {
    id: "fired",
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4" />
        <polyline points="10 17 15 12 10 7" />
        <line x1="15" y1="12" x2="3" y2="12" />
      </svg>
    ),
    title: "被辞退",
    desc: "被公司辞退、开除、劝退",
  },
  {
    id: "wage",
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <path d="M16 8h-6a2 2 0 100 4h4a2 2 0 110 4H8" />
        <line x1="12" y1="6" x2="12" y2="8" />
        <line x1="12" y1="16" x2="12" y2="18" />
      </svg>
    ),
    title: "拖欠工资",
    desc: "被欠薪、少发、不发工资",
  },
  {
    id: "resign",
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="7" r="3" />
        <path d="M12 14c-4 0-6 2-6 4v1h12v-1c0-2-2-4-6-4z" />
        <polyline points="17 4 21 8 17 12" />
        <line x1="21" y1="8" x2="11" y2="8" />
      </svg>
    ),
    title: "想离职",
    desc: "想辞职、被逼离职、协商解除",
  },
  {
    id: "other",
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="5" r="1.5" fill="currentColor" />
        <circle cx="12" cy="12" r="1.5" fill="currentColor" />
        <circle cx="12" cy="19" r="1.5" fill="currentColor" />
      </svg>
    ),
    title: "其他问题",
    desc: "加班费、工伤、社保、竞业限制等",
  },
];

const AGENT_LABELS: Record<string, string> = {
  case_analysis: "案件分析",
  violation_detect: "违法识别",
  compensation: "赔偿计算",
  strategy: "维权路线",
  arbitration: "仲裁指导",
  document_draft: "文书起草",
};

export default function ConsultationPage() {
  const [step, setStep] = useState<Step>(1);
  const [problemType, setProblemType] = useState<ProblemType | null>(null);
  const [form, setForm] = useState<FormData>({
    companyName: "",
    city: "",
    hireDate: "",
    monthlySalary: "",
  });
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [caseId, setCaseId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  /* ---------- sessionStorage 恢复/保存 ---------- */
  useEffect(() => {
    try {
      const saved = sessionStorage.getItem("consultation_wizard");
      if (saved) {
        const data = JSON.parse(saved);
        if (data.step) setStep(data.step);
        if (data.problemType) setProblemType(data.problemType);
        if (data.form) setForm(data.form);
        if (data.messages) setMessages(data.messages);
        if (data.done) setDone(data.done);
        if (data.caseId) setCaseId(data.caseId);
      }
    } catch {
      /* ignore corrupt sessionStorage */
    }
  }, []);

  useEffect(() => {
    try {
      sessionStorage.setItem(
        "consultation_wizard",
        JSON.stringify({ step, problemType, form, messages, done, caseId })
      );
    } catch {
      /* quota exceeded etc */
    }
  }, [step, problemType, form, messages, done, caseId]);

  /* ---------- 自动滚动 ---------- */
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /* ---------- 辅助函数 ---------- */
  const isFormValid =
    form.companyName.trim() !== "" &&
    form.city.trim() !== "" &&
    form.hireDate.trim() !== "" &&
    form.monthlySalary.trim() !== "";

  const formatAgentLabel = (agent: string): string =>
    AGENT_LABELS[agent] || agent;

  /* ---------- 事件处理 ---------- */
  const handleSelectType = (type: ProblemType) => {
    // 如果点了和当前相同的类型也不影响
    setProblemType(type);
    setStep(2);
  };

  const handleStartAnalysis = async () => {
    if (!isFormValid || !problemType) return;

    setStep(3);
    setLoading(true);
    setDone(false);
    setError(null);
    setMessages([]);

    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

    try {
      // 1. 创建案件
      const startResp = await fetch(`${API_BASE}/api/consultation/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          problem_type: problemType,
          company_name: form.companyName,
          city: form.city,
          hire_date: form.hireDate,
          monthly_salary: form.monthlySalary,
        }),
      });

      if (!startResp.ok) {
        throw new Error(`服务返回 ${startResp.status}`);
      }

      const { case_id } = await startResp.json();
      setCaseId(case_id);

      // 2. SSE 流式对话
      const resp = await fetch(`${API_BASE}/api/consultation/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "开始分析", case_id }),
      });

      if (!resp.ok) {
        throw new Error(`服务返回 ${resp.status}`);
      }

      const reader = resp.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        let buffer = "";
        while (true) {
          const { done: readerDone, value } = await reader.read();
          if (readerDone) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          // 保留最后一个可能不完整的行
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.type === "agent_result") {
                  setMessages((prev) => [
                    ...prev,
                    { agent: data.agent, content: data.content },
                  ]);
                }
              } catch {
                /* 跳过解析失败的行 */
              }
            }
          }
        }
      }
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : "未知错误";
      setError(msg);
      setMessages([
        {
          agent: "error",
          content:
            "连接服务失败，请确认后端已启动。\n\n> 本分析不替代律师正式法律意见",
        },
      ]);
    } finally {
      setLoading(false);
      setDone(true);
    }
  };

  /* ========== Step 1: 选问题类型 ========== */
  if (step === 1) {
    return (
      <div className="flex flex-col min-h-dvh max-w-[640px] mx-auto bg-[var(--color-bg)]">
        <header className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] bg-[var(--color-surface)] shrink-0">
          <a
            href="/"
            className="text-[var(--color-text-muted)] no-underline hover:text-[var(--color-accent)]"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="15,18 9,12 15,6" />
            </svg>
          </a>
          <span className="text-sm font-medium">AI 咨询</span>
          <span className="w-5" />
        </header>

        <div className="flex-1 px-4 pt-6 pb-4">
          <h1 className="text-lg font-semibold mb-1">遇到什么问题？</h1>
          <p className="text-sm text-[var(--color-text-muted)] mb-5">
            选择你的情况，我们会自动分析
          </p>

          <div className="grid gap-3">
            {PROBLEM_TYPES.map((item) => {
              const selected = problemType === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSelectType(item.id)}
                  className={`flex items-start gap-3 p-4 rounded-[var(--radius-md)] text-left w-full transition-all duration-100 ${
                    selected
                      ? "border-2 border-[var(--color-accent)] bg-[#EFF6FF]"
                      : "border border-[var(--color-border)] bg-[var(--color-surface)] hover:border-[var(--color-accent)]"
                  }`}
                  type="button"
                >
                  <span
                    className={`mt-0.5 shrink-0 ${
                      selected
                        ? "text-[var(--color-accent)]"
                        : "text-[var(--color-text-muted)]"
                    }`}
                  >
                    {item.icon}
                  </span>
                  <div>
                    <div
                      className={`text-sm font-medium ${
                        selected
                          ? "text-[var(--color-accent)]"
                          : "text-[var(--color-text)]"
                      }`}
                    >
                      {item.title}
                    </div>
                    <div className="text-xs text-[var(--color-text-muted)] mt-0.5">
                      {item.desc}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className="px-4 py-3 shrink-0">
          <p className="disclaimer !py-0">本分析不替代律师正式法律意见</p>
        </div>
      </div>
    );
  }

  /* ========== Step 2: 填表 ========== */
  if (step === 2) {
    return (
      <div className="flex flex-col min-h-dvh max-w-[640px] mx-auto bg-[var(--color-bg)]">
        <header className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] bg-[var(--color-surface)] shrink-0">
          <button
            onClick={() => {
              setStep(1);
              setProblemType(null);
            }}
            className="text-[var(--color-text-muted)] hover:text-[var(--color-accent)] bg-transparent border-none cursor-pointer p-0"
            type="button"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="15,18 9,12 15,6" />
            </svg>
          </button>
          <span className="text-sm font-medium">补充信息</span>
          <span className="w-5" />
        </header>

        <div className="flex-1 px-4 pt-6 pb-4">
          {/* 已选类型 */}
          {problemType && (
            <div className="flex items-center gap-2 mb-5">
              <span className="tag tag-info">
                {PROBLEM_TYPES.find((t) => t.id === problemType)?.title}
              </span>
              <button
                onClick={() => setStep(1)}
                className="text-xs text-[var(--color-text-muted)] bg-transparent border-none cursor-pointer underline hover:text-[var(--color-accent)]"
                type="button"
              >
                修改
              </button>
            </div>
          )}

          <div className="grid gap-4">
            <div>
              <label className="block text-xs text-[var(--color-text-muted)] mb-1">
                公司全称
              </label>
              <input
                type="text"
                className="input-field w-full"
                placeholder="输入公司全称"
                value={form.companyName}
                onChange={(e) =>
                  setForm({ ...form, companyName: e.target.value })
                }
              />
            </div>
            <div>
              <label className="block text-xs text-[var(--color-text-muted)] mb-1">
                工作城市
              </label>
              <input
                type="text"
                className="input-field w-full"
                placeholder="如：深圳"
                value={form.city}
                onChange={(e) => setForm({ ...form, city: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs text-[var(--color-text-muted)] mb-1">
                入职时间
              </label>
              <input
                type="text"
                className="input-field w-full"
                placeholder="如：2024-03"
                value={form.hireDate}
                onChange={(e) => setForm({ ...form, hireDate: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs text-[var(--color-text-muted)] mb-1">
                月薪
              </label>
              <input
                type="number"
                className="input-field w-full"
                placeholder="税前月薪，如：8000"
                value={form.monthlySalary}
                onChange={(e) =>
                  setForm({ ...form, monthlySalary: e.target.value })
                }
              />
            </div>
          </div>

          <button
            onClick={handleStartAnalysis}
            disabled={!isFormValid}
            className="btn-primary w-full mt-6 text-center"
            type="button"
          >
            开始分析
          </button>
        </div>

        <div className="px-4 py-3 shrink-0">
          <p className="disclaimer !py-0">本分析不替代律师正式法律意见</p>
        </div>
      </div>
    );
  }

  /* ========== Step 3: 看结果 ========== */
  return (
    <div className="flex flex-col min-h-dvh max-w-[640px] mx-auto bg-[var(--color-bg)]">
      <header className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] bg-[var(--color-surface)] shrink-0">
        <a
          href="/"
          className="text-[var(--color-text-muted)] no-underline hover:text-[var(--color-accent)]"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15,18 9,12 15,6" />
          </svg>
        </a>
        <span className="text-sm font-medium">分析报告</span>
        <span className="w-5" />
      </header>

      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i}>
            {msg.agent !== "error" && (
              <div className="text-[10px] text-[var(--color-text-muted)] ml-1 mb-1 tracking-wide">
                {formatAgentLabel(msg.agent)}
              </div>
            )}
            <div className="msg-ai" style={{ maxWidth: "100%" }}>
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          </div>
        ))}

        {/* 加载指示（无闪烁动画） */}
        {loading && (
          <div className="flex items-center gap-2 px-1">
            <span className="w-2 h-2 rounded-full bg-[var(--color-accent)]" />
            <span className="text-xs text-[var(--color-text-muted)]">
              分析中...
            </span>
          </div>
        )}

        {/* 分析完成状态 */}
        {done && messages.length > 0 && !error && (
          <div className="flex items-center justify-end gap-1 px-1">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" strokeWidth="2.5">
              <polyline points="20,6 9,17 4,12" />
            </svg>
            <span className="text-[10px] text-[var(--color-success)]">
              分析完成
            </span>
          </div>
        )}

        {done && error && (
          <div className="flex items-center justify-center px-1">
            <span className="text-[10px] text-[var(--color-danger)]">
              {error}
            </span>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* 底部操作按钮 */}
      {done && caseId && !error && (
        <div className="bg-[var(--color-surface)] border-t border-[var(--color-border)] px-4 py-4 space-y-2 shrink-0">
          <a
            href={`/documents?case_id=${caseId}`}
            className="btn-primary block text-center w-full no-underline"
          >
            生成仲裁申请书
          </a>
          <a
            href={`/evidence/upload?case_id=${caseId}`}
            className="btn-ghost block text-center w-full no-underline"
          >
            查看证据清单
          </a>
        </div>
      )}

      <div className="px-4 py-3 shrink-0">
        <p className="disclaimer !py-0">本分析不替代律师正式法律意见</p>
      </div>
    </div>
  );
}
