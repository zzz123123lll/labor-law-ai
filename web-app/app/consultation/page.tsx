"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  msgType?: string;
}

export default function ConsultationPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "你好！我是劳动法智能维权助手。请描述你遇到的劳动问题，我会帮你分析。",
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
      // SSE 流式接收后端分析
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
                  // 信息采集表单——简单提示
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
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "抱歉，连接后端服务失败。请确保后端已启动。\n\n> ⚠️ 本分析不替代律师正式法律意见" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-lg mx-auto">
      <header className="bg-white px-4 py-3 border-b text-center font-semibold">
        AI 智能咨询
      </header>

      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`max-w-[85%] rounded-xl px-4 py-2 text-sm whitespace-pre-wrap ${
              msg.role === "user"
                ? "bg-blue-600 text-white ml-auto"
                : msg.role === "system"
                ? "bg-yellow-50 border border-yellow-200 text-yellow-800"
                : "bg-white border text-gray-800"
            }`}
          >
            {msg.msgType && msg.role === "assistant" && (
              <div className="text-xs text-gray-400 mb-1">[{msg.msgType}]</div>
            )}
            {msg.content}
          </div>
        ))}
        {loading && (
          <div className="bg-white border rounded-xl px-4 py-2 text-sm text-gray-400">
            AI分析中...
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="bg-white border-t px-3 py-2 flex gap-2">
        <input
          type="text"
          className="flex-1 border rounded-full px-4 py-2 text-sm focus:outline-none focus:border-blue-400"
          placeholder="描述你的劳动问题..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="bg-blue-600 text-white rounded-full w-10 h-10 flex items-center justify-center disabled:opacity-50"
        >
          ➤
        </button>
      </div>
    </div>
  );
}
