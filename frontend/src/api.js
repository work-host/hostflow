import { apiFetch } from "./http";

export async function listStages() {
  const r = await apiFetch("/api/v1/stages/");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function listCandidates(params = {}) {
  const qs = new URLSearchParams(params).toString();
  const url = "/api/v1/candidates/" + (qs ? `?${qs}` : "");
  const r = await apiFetch(url);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function createCandidate(payload) {
  const r = await apiFetch("/api/v1/candidates/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function updateCandidate(id, payload) {
  const r = await apiFetch(`/api/v1/candidates/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
