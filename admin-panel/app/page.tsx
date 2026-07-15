"use client";
import { useEffect, useState } from "react";
import { Card, Statistic, Row, Col } from "antd";
import { UserOutlined, FileTextOutlined, DollarOutlined, RiseOutlined } from "@ant-design/icons";

const API_BASE = "http://localhost:8000";

export default function DashboardPage() {
  const [stats, setStats] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/admin/dashboard`)
      .then((r) => r.json())
      .then((data) => { setStats(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="text-xl font-bold mb-6">数据面板</h1>
      <Row gutter={16}>
        <Col span={6}><Card><Statistic title="总用户" value={stats.total_users || 0} prefix={<UserOutlined />} loading={loading} /></Card></Col>
        <Col span={6}><Card><Statistic title="总案件" value={stats.total_cases || 0} prefix={<FileTextOutlined />} loading={loading} /></Card></Col>
        <Col span={6}><Card><Statistic title="付费订单" value={stats.total_orders || 0} prefix={<DollarOutlined />} loading={loading} /></Card></Col>
        <Col span={6}><Card><Statistic title="营收总额" value={stats.total_revenue || 0} prefix={<RiseOutlined />} precision={2} suffix="元" loading={loading} /></Card></Col>
      </Row>
    </div>
  );
}
