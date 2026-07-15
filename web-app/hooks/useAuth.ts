"use client";
import { useState, useEffect } from "react";

interface User {
  id: string;
  nickname: string | null;
  phone: string | null;
  role: string;
  is_vip: boolean;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      fetch("http://localhost:8000/api/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((r) => r.json())
        .then((data) => {
          if (data.id) setUser(data);
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  return { user, loading, isLoggedIn: !!user };
}
