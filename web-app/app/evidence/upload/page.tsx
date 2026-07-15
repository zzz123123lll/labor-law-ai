"use client";

import { useState } from "react";

export default function EvidenceUploadPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const handleUpload = async () => {
    if (files.length === 0) return;
    setUploading(true);
    // TODO: 连接后端 API 上传证据
    setTimeout(() => {
      setResult("证据分析功能即将上线，敬请期待。");
      setUploading(false);
    }, 1000);
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-center py-4">证据分析</h1>

      <div className="bg-white rounded-xl p-4 shadow-sm">
        <p className="text-sm text-gray-600 mb-4">
          上传你的证据材料（聊天记录、工资单、合同、考勤记录等），AI 将自动分析证据链完整性。
        </p>

        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
          <input
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.jpg,.png,.xlsx"
            onChange={(e) => setFiles(Array.from(e.target.files || []))}
            className="hidden"
            id="evidence-upload"
          />
          <label htmlFor="evidence-upload" className="cursor-pointer">
            <div className="text-3xl mb-2">📎</div>
            <div className="text-sm text-gray-500">
              {files.length > 0
                ? `已选择 ${files.length} 个文件`
                : "点击选择证据文件"}
            </div>
          </label>
        </div>

        {files.length > 0 && (
          <ul className="mt-3 space-y-1">
            {files.map((f, i) => (
              <li key={i} className="text-xs text-gray-500">
                {f.name} ({(f.size / 1024).toFixed(1)} KB)
              </li>
            ))}
          </ul>
        )}

        <button
          onClick={handleUpload}
          disabled={files.length === 0 || uploading}
          className="w-full mt-4 bg-blue-600 text-white rounded-lg py-2 font-semibold disabled:opacity-50"
        >
          {uploading ? "分析中..." : "开始分析"}
        </button>

        {result && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg text-sm text-gray-700 whitespace-pre-wrap">
            {result}
          </div>
        )}
      </div>

      <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-xs text-yellow-800">
        ⚠️ AI 分析结果仅供参考，不构成法律意见。建议咨询专业律师。
      </div>
    </div>
  );
}
