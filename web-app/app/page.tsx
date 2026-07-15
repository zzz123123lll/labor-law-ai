export default function HomePage() {
  return (
    <div className="p-4">
      <div className="text-center py-8">
        <h1 className="text-2xl font-bold text-blue-700 mb-2">劳动法智能维权AI</h1>
        <p className="text-gray-500 text-sm">你的劳动权益保护助手</p>
      </div>

      <div className="grid grid-cols-2 gap-3 mt-6">
        <a href="/consultation" className="bg-white rounded-xl p-4 shadow-sm text-center hover:shadow-md transition">
          <div className="text-3xl mb-1">💬</div>
          <div className="text-sm font-semibold">AI智能咨询</div>
          <div className="text-xs text-gray-400">分析你的劳动问题</div>
        </a>
        <a href="/toolbox" className="bg-white rounded-xl p-4 shadow-sm text-center hover:shadow-md transition">
          <div className="text-3xl mb-1">🧮</div>
          <div className="text-sm font-semibold">赔偿计算器</div>
          <div className="text-xs text-gray-400">算算能赔多少</div>
        </a>
        <a href="/contract-review" className="bg-white rounded-xl p-4 shadow-sm text-center hover:shadow-md transition">
          <div className="text-3xl mb-1">📄</div>
          <div className="text-sm font-semibold">合同审查</div>
          <div className="text-xs text-gray-400">上传合同 AI审查</div>
        </a>
        <a href="/evidence/upload" className="bg-white rounded-xl p-4 shadow-sm text-center hover:shadow-md transition">
          <div className="text-3xl mb-1">📎</div>
          <div className="text-sm font-semibold">证据分析</div>
          <div className="text-xs text-gray-400">上传证据 自动分析</div>
        </a>
      </div>

      <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-xs text-yellow-800">
        ⚠️ 本工具基于AI分析，不替代专业律师意见。重大权益请咨询律师。
      </div>
    </div>
  );
}
