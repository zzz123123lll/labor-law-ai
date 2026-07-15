"use client";
import { useState } from "react";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  msgType?: string;
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const send = async (text: string) => {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);
    // SSE 连接逻辑（与 consultation page 类似）
    setLoading(false);
  };

  return { messages, loading, send };
}
