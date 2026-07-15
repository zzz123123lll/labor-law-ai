"use client";

import { useState } from "react";

export default function CompensationPage() {
  const [form, setForm] = useState({
    monthlySalary: "",
   入职日期: "",
    离职日期: "",
    dismissalType: "voluntary",
  });
  const [result, setResult] = useState<string | null>(null);

  const handleChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const calculate = () => {
    // TODO: 连接后端 API 计算
    setResult(`根据你提供的信息，初步估算经济补偿/赔偿金如下：

⚠️ 此结果为初步估算，实际金额需结合具体情况由劳动仲裁或法院裁定。`);
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-center py-4">赔偿计算器</h1>

      <div className="bg-white rounded-xl p-4 shadow-sm space-y-3">
        <div>
          <label className="block text-sm font-medium mb-1">月平均工资（元）</label>
          <input
            type="number"
            className="w-full border rounded-lg px-3 py-2 text-sm"
            placeholder="例如：8000"
            value={form.monthlySalary}
            onChange={(e) => handleChange("monthlySalary", e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">入职日期</label>
          <input
            type="date"
            className="w-full border rounded-lg px-3 py-2 text-sm"
            value={form.入职日期}
            onChange={(e) => handleChange("入职日期", e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">离职日期</label>
          <input
            type="date"
            className="w-full border rounded-lg px-3 py-2 text-sm"
            value={form.离职日期}
            onChange={(e) => handleChange("离职日期", e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">离职类型</label>
          <select
            className="w-full border rounded-lg px-3 py-2 text-sm"
            value={form.dismissalType}
            onChange={(e) => handleChange("dismissalType", e.target.value)}
          >
            <option value="voluntary">主动辞职</option>
            <option value="negotiated">协商解除</option>
            <option value="unlawful">违法解除</option>
            <option value="contract_expire">合同到期不续</option>
          </select>
        </div>

        <button
          onClick={calculate}
          className="w-full bg-blue-600 text-white rounded-lg py-2 font-semibold"
        >
          开始计算
        </button>

        {result && (
          <div className="mt-2 p-3 bg-gray-50 rounded-lg text-sm text-gray-700 whitespace-pre-wrap">
            {result}
          </div>
        )}
      </div>

      <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-xs text-yellow-800">
        ⚠️ 计算结果仅供参考，具体金额以劳动仲裁或法院裁定为准。
      </div>
    </div>
  );
}
