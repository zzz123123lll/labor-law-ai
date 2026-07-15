"use client";
import { useEffect, useState } from "react";
import { Table, Tag, Button, message } from "antd";

const API_BASE = "http://localhost:8000";

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadUsers = () => {
    setLoading(true);
    fetch(`${API_BASE}/api/admin/users`)
      .then((r) => r.json())
      .then((data) => { setUsers(data); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { loadUsers(); }, []);

  const toggleVip = async (userId: string) => {
    await fetch(`${API_BASE}/api/admin/users/${userId}/toggle-vip`, { method: "POST" });
    message.success("VIP状态已更新");
    loadUsers();
  };

  const columns = [
    { title: "昵称", dataIndex: "nickname", key: "nickname" },
    { title: "手机号", dataIndex: "phone", key: "phone" },
    {
      title: "VIP", dataIndex: "is_vip", key: "is_vip",
      render: (v: boolean, record: any) => (
        <Tag color={v ? "gold" : "default"}>{v ? "VIP" : "免费"}</Tag>
      ),
    },
    { title: "案件数", dataIndex: "case_count", key: "case_count" },
    {
      title: "操作", key: "action",
      render: (_: any, record: any) => (
        <Button size="small" onClick={() => toggleVip(record.id)}>
          {record.is_vip ? "取消VIP" : "开通VIP"}
        </Button>
      ),
    },
  ];

  return (
    <div>
      <h1 className="text-xl font-bold mb-6">用户管理</h1>
      <Table dataSource={users} columns={columns} rowKey="id" loading={loading} />
    </div>
  );
}
