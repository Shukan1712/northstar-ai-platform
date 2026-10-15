export type User = { email: string; name: string; role: string; title: string };

const TOKEN_KEY = "northstar_session";

export const auth = {
  token: () => localStorage.getItem(TOKEN_KEY),
  save: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY)
};

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = auth.token();
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {})
    }
  });
  if (response.status === 401) {
    auth.clear();
    window.dispatchEvent(new Event("northstar:unauthorized"));
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(body.detail || "Request failed");
  }
  return response.json();
}

export const currency = (value: number) =>
  new Intl.NumberFormat("en-CA", { style: "currency", currency: "CAD", maximumFractionDigits: 0 }).format(value);

export const roleLabel = (role: string) =>
  role.split("_").map((part) => part.toLowerCase() === "ai" ? "AI" : part[0].toUpperCase() + part.slice(1)).join(" ");
