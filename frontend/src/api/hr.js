import { apiFetch } from "../http";

async function handle(res){
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function listEmployees() {
  const r = await apiFetch("/api/v1/hr/employees");
  return handle(r);
}

export async function createEmployee(payload) {
  // payload: { email, role, is_active?, password?, profile:{...}, terms?:{...} }
  const r = await apiFetch("/api/v1/hr/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handle(r);
}
