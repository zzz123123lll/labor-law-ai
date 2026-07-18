import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";

// Mock whole api module before importing page
vi.mock("../lib/api", () => ({
  apiFetch: vi.fn(),
}));

// Mock sessionStorage
const sessionStore: Record<string, string> = {};
vi.stubGlobal("sessionStorage", {
  getItem: vi.fn((key: string) => sessionStore[key] ?? null),
  setItem: vi.fn((key: string, value: string) => { sessionStore[key] = value; }),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
});

import CompensationPage from "../app/compensation/page";

beforeEach(() => {
  vi.clearAllMocks();
  Object.keys(sessionStore).forEach(k => delete sessionStore[k]);
});

describe("赔偿计算器 —— 表单验证", () => {
  it("月薪和入职日期为空时显示错误", () => {
    render(<CompensationPage />);
    fireEvent.click(screen.getByText("开始计算"));
    expect(screen.getByText("请至少填写月工资和入职日期")).toBeTruthy();
  });

  it("渲染所有表单字段", () => {
    render(<CompensationPage />);
    expect(screen.getByPlaceholderText("如 8000")).toBeTruthy();
    expect(screen.getByLabelText("入职日期")).toBeTruthy();
    expect(screen.getByLabelText("离职日期")).toBeTruthy();
  });
});

describe("赔偿计算器 —— sessionStorage 预填", () => {
  it("从 Wizard 读月薪自动填入", () => {
    sessionStore["consultation_wizard"] = JSON.stringify({
      step: 3,
      problemType: "被辞退",
      form: { monthly_salary: "9000", hire_date: "2023-03" },
      caseId: "test-uuid",
    });

    render(<CompensationPage />);

    const salaryInput = screen.getByPlaceholderText("如 8000") as HTMLInputElement;
    expect(salaryInput.value).toBe("9000");
  });

  it("预填数据时显示提示条", () => {
    sessionStore["consultation_wizard"] = JSON.stringify({
      step: 3,
      form: { monthly_salary: "8000", hire_date: "2024-01" },
    });

    render(<CompensationPage />);
    expect(screen.getByText("已从咨询案件自动填入数据，可直接计算")).toBeTruthy();
  });

  it("无 sessionStorage 不显示提示", () => {
    render(<CompensationPage />);
    expect(screen.queryByText("已从咨询案件自动填入数据，可直接计算")).toBeFalsy();
  });
});
