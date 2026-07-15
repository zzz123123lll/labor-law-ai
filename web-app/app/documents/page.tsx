export default function DocumentsPage() {
  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-center py-4">我的文书</h1>

      <div className="bg-white rounded-xl p-4 shadow-sm text-center py-8">
        <div className="text-4xl mb-2">📝</div>
        <p className="text-sm text-gray-500">暂无文书</p>
        <p className="text-xs text-gray-400 mt-1">完成咨询后，可自动生成法律文书</p>
        <a
          href="/consultation"
          className="inline-block mt-4 bg-blue-600 text-white rounded-lg px-4 py-2 text-sm"
        >
          开始咨询
        </a>
      </div>

      <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-xs text-yellow-800">
        ⚠️ 生成的文书草稿仅供参考，建议由专业律师审核后使用。
      </div>
    </div>
  );
}
