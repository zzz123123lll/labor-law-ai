"use client";

import { useState, useEffect } from "react";

export default function ProfilePage() {
  const [user, setUser] = useState<{
    nickname: string | null;
    phone: string | null;
    is_vip: boolean;
  } | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      // TODO: 连接后端 API 获取用户信息
      setUser({ nickname: null, phone: null, is_vip: false });
    }
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-center py-4">我的</h1>

      <div className="bg-white rounded-xl p-4 shadow-sm">
        {user ? (
          <div className="text-center">
            <div className="text-4xl mb-2">👤</div>
            <div className="font-semibold">{user.nickname || "未设置昵称"}</div>
            <div className="text-xs text-gray-400 mt-1">
              {user.phone || "未绑定手机"}
            </div>
            {user.is_vip ? (
              <span className="inline-block mt-2 bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5 rounded-full">
                VIP 会员
              </span>
            ) : (
              <a
                href="/profile"
                className="inline-block mt-2 bg-blue-600 text-white text-xs px-3 py-1 rounded-full"
              >
                开通专业版
              </a>
            )}
          </div>
        ) : (
          <div className="text-center py-4">
            <div className="text-4xl mb-2">👤</div>
            <p className="text-sm text-gray-500 mb-3">登录后使用全部功能</p>
            <button className="bg-blue-600 text-white rounded-lg px-6 py-2 text-sm">
              微信登录
            </button>
          </div>
        )}
      </div>

      <div className="mt-3 bg-white rounded-xl shadow-sm divide-y">
        <a href="/cases" className="flex items-center justify-between px-4 py-3 text-sm">
          <span>我的案件</span>
          <span className="text-gray-400">&gt;</span>
        </a>
        <a href="/documents" className="flex items-center justify-between px-4 py-3 text-sm">
          <span>我的文书</span>
          <span className="text-gray-400">&gt;</span>
        </a>
        <div className="flex items-center justify-between px-4 py-3 text-sm">
          <span>版本</span>
          <span className="text-gray-400">1.0.0</span>
        </div>
      </div>

      <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-xs text-yellow-800">
        ⚠️ 本工具基于AI分析，不替代专业律师意见。重大权益请咨询律师。
      </div>
    </div>
  );
}
