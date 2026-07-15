"use client";

import { useParams } from "next/navigation";

export default function CaseDetailPage() {
  const params = useParams();
  const caseId = params.id as string;

  return (
    <div className="p-4">
      <a href="/cases" className="text-sm text-blue-600 mb-2 inline-block">
        &larr; 返回案件列表
      </a>

      <h1 className="text-xl font-bold py-2">案件详情</h1>

      <div className="bg-white rounded-xl p-4 shadow-sm space-y-4">
        <div>
          <div className="text-xs text-gray-400">案件 ID</div>
          <div className="text-sm">{caseId}</div>
        </div>

        <div>
          <div className="text-xs text-gray-400">案件状态</div>
          <div className="text-sm">咨询中</div>
        </div>

        <div className="border-t pt-3">
          <h2 className="font-semibold text-sm mb-2">案件时间线</h2>
          <div className="space-y-2">
            <div className="flex gap-2 text-sm">
              <span className="text-gray-400 w-20 shrink-0">2026-07-14</span>
              <span>创建案件</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-xs text-yellow-800">
        ⚠️ 案件信息仅供参考，不构成法律意见。
      </div>
    </div>
  );
}
