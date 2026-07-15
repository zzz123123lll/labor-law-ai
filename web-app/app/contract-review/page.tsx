"use client";

import { useState } from "react";

export default function ContractReviewPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    // TODO: 连接后端 API 上传合同
    setTimeout(() => {
      setResult("合同审查功能即将上线，敬请期待。");
      setUploading(false);
    }, 1000);
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-center py-4">合同审查</h1>

      <div className="bg-white rounded-xl p-4 shadow-sm">
        <p className="text-sm text-gray-600 mb-4">上传你的劳动合同，AI 将自动审查条款合法性、公平性。</p>

        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
          <input
            type="file"
            accept=".pdf,.doc,.docx,.jpg,.png"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="hidden"
            id="file-upload"
          />
          <label htmlFor="file-upload" className="cursor-pointer">
            <div className="text-3xl mb-2">📄</div>
            <div className="text-sm text-gray-500">
              {file ? file.name : "点击选择合同文件（PDF/Word/图片）"}
            </div>
          </label>
        </div>

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full mt-4 bg-blue-600 text-white rounded-lg py-2 font-semibold disabled:opacity-50"
        >
          {uploading ? "分析中..." : "开始审查"}
        </button>

        {result && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg text-sm text-gray-700 whitespace-pre-wrap">
            {result}
          </div>
        )}
      </div>

      <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-xs text-yellow-800">
        ⚠️ AI 审查结果仅供参考，不构成法律意见。建议咨询专业律师。
      </div>
    </div>
  );
}
