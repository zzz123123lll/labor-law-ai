"use client";
import { useState, useEffect } from "react";

export function useSettings() {
  const [apiKey, setApiKey] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const key = localStorage.getItem("llm_api_key") || "";
    setApiKey(key);
    setLoading(false);
  }, []);

  const saveApiKey = (key: string) => {
    localStorage.setItem("llm_api_key", key);
    setApiKey(key);
  };

  return { apiKey, saveApiKey, loading };
}
