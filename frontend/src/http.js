const LS_TOKEN = "auth_token";
const LS_USER  = "auth_user";

function dispatchAuthChanged() {
  window.dispatchEvent(new Event("auth-changed"));
}

export function getToken() {
  return localStorage.getItem(LS_TOKEN) || "";
}

export function getUser() {
  const raw = localStorage.getItem(LS_USER);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { return null; }
}

export function setAuth(token, user) {
  localStorage.setItem(LS_TOKEN, token);
  localStorage.setItem(LS_USER, JSON.stringify(user));
  dispatchAuthChanged();
}

export function clearAuth() {
  localStorage.removeItem(LS_TOKEN);
  localStorage.removeItem(LS_USER);
  dispatchAuthChanged();
}

export async function login(email, password) {
  const body = new URLSearchParams({ username: email, password });
  const r = await fetch("/api/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body
  });
  if (!r.ok) throw new Error(await r.text());
  const data = await r.json();
  setAuth(data.access_token, data.user);
  return data.user;
}

export function logout() {
  clearAuth();
}

export async function apiFetch(url, opts = {}) {
  const token = getToken();
  const headers = new Headers(opts.headers || {});
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(url, { ...opts, headers });
  if (res.status === 401) {
    clearAuth();
    if (!location.pathname.startsWith("/login")) {
      location.replace("/login");
    }
    throw new Error("Unauthorized");
  }
  return res;
}

// Подписка для компонентов (Header)
export function onAuthChange(cb) {
  const handler = () => cb(getUser());
  window.addEventListener("auth-changed", handler);
  window.addEventListener("storage", handler);
  return () => {
    window.removeEventListener("auth-changed", handler);
    window.removeEventListener("storage", handler);
  };
}
