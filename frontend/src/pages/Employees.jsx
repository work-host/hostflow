import React, { useEffect, useState } from "react";
import { listEmployees, createEmployee } from "../api/hr";

const ROLES = [
  ["manager", "Менеджер"],
  ["lead_recruiter", "Старший рекрутер"],
  ["recruiter", "Рекрутер"],
  ["marketer", "Маркетолог"],
  ["admin", "Админ"],
];

function normalizeErr(e) {
  if (!e) return "Ошибка";
  if (typeof e === "string") return e;
  if (e.message) {
    try {
      const j = JSON.parse(e.message);
      return j?.detail || e.message;
    } catch {
      return e.message;
    }
  }
  return String(e);
}

export default function Employees() {
  const [items, setItems] = useState([]);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("manager");
  const [first, setFirst] = useState("");
  const [last, setLast] = useState("");
  const [position, setPosition] = useState("");
  const [error, setError] = useState("");
  const [creating, setCreating] = useState(false);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await listEmployees();
      setItems(data);
    } catch (e) {
      console.error(e);
      setError(normalizeErr(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function onCreate(e) {
    e.preventDefault();
    setError("");

    if (!email.includes("@")) return setError("Укажите корректный email.");
    if (!first.trim() || !last.trim()) return setError("Имя и фамилия обязательны.");

    try {
      setCreating(true);
      await createEmployee({
        email: email.trim().toLowerCase(),
        role,
        is_active: true,
        profile: {
          first_name: first.trim(),
          last_name: last.trim(),
          middle_name: null,
          phone: null,
          telegram: null,
          position: position.trim() || null,
          employment_type: null,
          manager_id: null,
          hire_date: null,
          fire_date: null
        },
        terms: null
      });
      // очистим форму
      setEmail(""); setFirst(""); setLast(""); setPosition("");
      await load();
    } catch (e) {
      console.error(e);
      setError(normalizeErr(e));
    } finally {
      setCreating(false);
    }
  }

  return (
    <div style={{padding:20}}>
      <h2>Сотрудники</h2>

      <form onSubmit={onCreate} style={{display:"grid", gap:8, maxWidth:640}}>
        <input placeholder="Email *" value={email} onChange={e=>setEmail(e.target.value)} />
        <select value={role} onChange={e=>setRole(e.target.value)}>
          {ROLES.map(([v, label]) => <option key={v} value={v}>{label}</option>)}
        </select>
        <div style={{display:"flex", gap:8}}>
          <input placeholder="Имя *" value={first} onChange={e=>setFirst(e.target.value)} />
          <input placeholder="Фамилия *" value={last} onChange={e=>setLast(e.target.value)} />
        </div>
        <input placeholder="Должность" value={position} onChange={e=>setPosition(e.target.value)} />
        <button type="submit" disabled={creating}>{creating ? "Добавляем..." : "Добавить"}</button>
      </form>

      {error && <p style={{color:"crimson"}}>Ошибка: {error}</p>}
      {loading ? <p>Загрузка...</p> : (
        <table border="1" cellPadding="6" style={{borderCollapse:"collapse", minWidth:800, marginTop:16}}>
          <thead>
            <tr><th>ID</th><th>Email</th><th>Роль</th><th>Имя</th><th>Фамилия</th><th>Должность</th></tr>
          </thead>
          <tbody>
            {items.map(x => (
              <tr key={x.user.id}>
                <td>{x.user.id}</td>
                <td>{x.user.email}</td>
                <td>{x.user.role}</td>
                <td>{x.profile.first_name || "-"}</td>
                <td>{x.profile.last_name || "-"}</td>
                <td>{x.profile.position || "-"}</td>
              </tr>
            ))}
            {items.length===0 && !loading && !error && <tr><td colSpan="6">Пусто</td></tr>}
          </tbody>
        </table>
      )}
    </div>
  );
}
