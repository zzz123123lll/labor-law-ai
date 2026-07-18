import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiFetch } from "../lib/api";

const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

beforeEach(() => {
  mockFetch.mockReset();
  mockFetch.mockResolvedValue({ ok: true, json: async () => ({}) });
});

describe("apiFetch —— API 请求基础函数", () => {
  it("请求路径正确拼接", async () => {
    await apiFetch("/api/cases");
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/cases",
      expect.objectContaining({
        headers: expect.objectContaining({ "Content-Type": "application/json" }),
      })
    );
  });

  it("不带 Authorization header（已废弃认证）", async () => {
    await apiFetch("/api/health");
    const headers = mockFetch.mock.calls[0][1].headers;
    expect(headers.Authorization).toBeUndefined();
  });

  it("Content-Type 始终为 application/json", async () => {
    await apiFetch("/api/health", {
      headers: { "X-Custom": "test" },
    });
    const headers = mockFetch.mock.calls[0][1].headers;
    expect(headers["Content-Type"]).toBe("application/json");
    expect(headers["X-Custom"]).toBe("test");
  });

  it("传递 method 和 body", async () => {
    const body = JSON.stringify({ title: "测试" });
    await apiFetch("/api/cases", { method: "POST", body });
    expect(mockFetch).toHaveBeenCalledWith("/api/cases", {
      method: "POST",
      body,
      headers: expect.objectContaining({ "Content-Type": "application/json" }),
    });
  });

  it("没有携带废弃的 Authorization header", async () => {
    await apiFetch("/api/health", {
      headers: { "Content-Type": "text/plain" },
    });
    const headers = mockFetch.mock.calls[0][1].headers;
    expect(headers.Authorization).toBeUndefined();
    expect(headers["Content-Type"]).toBe("text/plain");
  });
});
