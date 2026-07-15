"use client";

import { useState, useEffect } from "react";

interface CaseItem {
  id: string;
  title: string;
  stage: string;
  updated_at: string;
}

export default function CasesPage() {
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: 连接后端 API 获取案件列表
    setTimeout(() => {
      // 示例数据
      setCases([
        {
          id: "1",
          title: "示例案件 - 劳动报酬纠纷",
          stage: "consultation",
          updated_at: "2026-07-14",
        },
      ]);
      setLoading(false);
    }, 500);
  }, []);

  const stageLabel: Record<string, string> = {
    consultation: "咨询中",
    evidence: "取证中",
    arbitration: "仲裁中",
    completed: "已完成",
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-center py-4">我的案件</h1>

      {loading ? (
        <div className="text-center text-gray-400 py-8">加载中...</div>
      ) : cases.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          <div className="text-4xl mb-2">📋</div>
          <div className="text-sm">暂无案件</div>
          <a
            href="/consultation"
            className="inline-block mt-3 bg-blue-600 text-white rounded-lg px-4 py-2 text-sm"
          >
            开始咨询
          </a>
        </div>
      ) : (
        <div className="space-y-3">
          {cases.map((c) => (
            <a
              key={c.id}
              href={`/cases/${c.id}`}
              className="block bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition"
            >
              <div className="flex justify-between items-start">
                <div className="font-semibold text-sm">{c.title}</div>
                <span className="text-xs bg-blue-100 text-blue-700 rounded-full px-2 py-0.5">
                  {stageLabel[c.stage] || c.stage}
                </span>
              </div>
              <div className="text-xs text-gray-400 mt-1">更新于 {c.updated_at}</div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
