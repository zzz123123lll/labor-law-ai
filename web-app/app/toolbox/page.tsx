export default function ToolboxPage() {
  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-center py-4">工具箱</h1>

      <div className="space-y-3">
        <a href="/compensation" className="block bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🧮</span>
            <div>
              <div className="font-semibold text-sm">赔偿计算器</div>
              <div className="text-xs text-gray-400">经济补偿金、赔偿金一键计算</div>
            </div>
          </div>
        </a>

        <a href="/contract-review" className="block bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition">
          <div className="flex items-center gap-3">
            <span className="text-3xl">📄</span>
            <div>
              <div className="font-semibold text-sm">合同审查</div>
              <div className="text-xs text-gray-400">AI 审查劳动合同条款</div>
            </div>
          </div>
        </a>

        <a href="/documents" className="block bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition">
          <div className="flex items-center gap-3">
            <span className="text-3xl">📝</span>
            <div>
              <div className="font-semibold text-sm">文书生成</div>
              <div className="text-xs text-gray-400">仲裁申请书、起诉状自动生成</div>
            </div>
          </div>
        </a>

        <a href="/evidence/upload" className="block bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition">
          <div className="flex items-center gap-3">
            <span className="text-3xl">📎</span>
            <div>
              <div className="font-semibold text-sm">证据分析</div>
              <div className="text-xs text-gray-400">上传证据材料，自动分析证明力</div>
            </div>
          </div>
        </a>
      </div>

      <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-xs text-yellow-800">
        ⚠️ 计算结果仅供参考，具体金额以劳动仲裁或法院裁定为准。
      </div>
    </div>
  );
}
