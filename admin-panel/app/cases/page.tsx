"use client";
import { useEffect, useState } from "react";
import { Table, Tag } from "antd";

const API_BASE = "http://localhost:8000";

const riskColor: Record<string, string> = {
  low: "green", medium: "orange", high: "red", critical: "magenta",
};

export default function CasesPage() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/admin/cases`)
      .then((r) => r.json())
      .then((data) => { setCases(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const columns = [
    { title: "标题", dataIndex: "title", key: "title" },
    { title: "用户", dataIndex: "user_nickname", key: "user" },
    { title: "阶段", dataIndex: "stage", key: "stage" },
    {
      title: "风险", dataIndex: "risk_level", key: "risk",
      render: (v: string) => v ? <Tag color={riskColor[v] || "default"}>{v}</Tag> : "-",
    },
    { title: "创建时间", dataIndex: "created_at", key: "created_at",
      render: (v: string) => v ? new Date(v).toLocaleDateString("zh-CN") : "-",
    },
  ];

  return (
    <div>
      <h1 className="text-xl font-bold mb-6">案件管理</h1>
      <Table dataSource={cases} columns={columns} rowKey="id" loading={loading} />
    </div>
  );
}
