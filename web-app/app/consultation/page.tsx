"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  msgType?: string;
}

export default function ConsultationPage() {
  const { user, loading: authLoading } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "你好，我是劳动法维权助手。\n\n请告诉我你遇到了什么问题？",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const token = localStorage.getItem("access_token") || "";
      const resp = await fetch("http://localhost:8000/api/consultation/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: userMsg }),
      });

      const reader = resp.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.type === "agent_result") {
                  setMessages((prev) => [
                    ...prev,
                    { role: "assistant", content: data.content, msgType: data.agent },
                  ]);
                } else if (data.type === "form_collect") {
                  setMessages((prev) => [
                    ...prev,
                    {
                      role: "system",
                      content: `请补充以下信息：${data.questions.join("、")}`,
                    },
                  ]);
                }
              } catch {}
            }
          }
        }
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "连接服务失败。请确认后端已启动。\n\n> 本分析不替代律师正式法律意见",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-[640px] mx-auto">
      {/* 顶栏 */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <a href="/" className="text-[var(--color-text-muted)] no-underline hover:text-[var(--color-accent)]">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15,18 9,12 15,6"/></svg>
        </a>
        <span className="text-sm font-medium">AI 咨询</span>
        <span className="w-5" />
      </header>

      {/* 未登录时显示登录提示 */}
      {authLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <span className="w-2 h-2 rounded-full bg-[var(--color-accent)] animate-pulse" />
        </div>
      ) : !user ? (
        <div className="flex-1 flex flex-col items-center justify-center px-8 text-center" style={{ background: "var(--color-bg)" }}>
          <div className="w-16 h-16 rounded-full bg-[var(--color-bg)] mb-4 flex items-center justify-center">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="1.5"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </div>
          <h2 className="text-sm font-medium mb-1">请先登录</h2>
          <p className="text-xs text-[var(--color-text-muted)] mb-4">AI 智能咨询需要登录后才能使用</p>
          <a
            href="/profile"
            className="btn-primary no-underline text-sm inline-block px-8"
          >
            去登录
          </a>
        </div>
      ) : (
        <>
      {/* 消息区 */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3" style={{ background: "var(--color-bg)" }}>
        {messages.map((msg, i) =>
          msg.role === "user" ? (
            <div key={i} className="msg-user">{msg.content}</div>
          ) : msg.role === "system" ? (
            <div key={i} className="text-center">
              <span className="inline-block text-xs bg-[#F3F4F6] text-[var(--color-text-muted)] px-3 py-1.5 rounded-sm">
                {msg.content}
              </span>
            </div>
          ) : (
            <div key={i}>
              {msg.msgType && (
                <div className="text-[10px] text-[var(--color-text-muted)] ml-1 mb-1 tracking-wide">
                  {msg.msgType === "case_analysis" ? "案件分析" :
                   msg.msgType === "violation_detect" ? "违法识别" :
                   msg.msgType === "compensation" ? "赔偿计算" :
                   msg.msgType === "strategy" ? "维权路线" :
                   msg.msgType === "arbitration" ? "仲裁指导" :
                   msg.msgType === "document_draft" ? "文书起草" : msg.msgType}
                </div>
              )}
              <div
                className="msg-ai"
                dangerouslySetInnerHTML={{ __html: msg.content
                  .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                  .replace(/^- (.*)/gm, "<span style='display:block;padding-left:8px;margin:2px 0'>· $1</span>")
                  .replace(/\n/g, "<br/>")
                }}
              />
            </div>
          )
        )}
        {loading && (
          <div className="flex items-center gap-2 px-1">
            <span className="w-2 h-2 rounded-full bg-[var(--color-accent)] animate-pulse" />
            <span className="text-xs text-[var(--color-text-muted)]">分析中...</span>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* 输入栏 */}
      <div className="bg-[var(--color-surface)] border-t border-[var(--color-border)] px-3 py-2.5 flex gap-2 items-center">
        <input
          type="text"
          className="input-field flex-1 rounded-full"
          placeholder="描述你的劳动问题..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="btn-primary rounded-full w-9 h-9 flex items-center justify-center p-0 disabled:opacity-30"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5,12 12,5 19,12"/></svg>
        </button>
      </div>
        </>
      )}
    </div>
  );
}
