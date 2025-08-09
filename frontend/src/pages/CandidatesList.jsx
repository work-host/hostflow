import React, { useEffect, useState } from "react";
import { listCandidates, createCandidate, listStages, updateCandidate } from "../api";

export default function CandidatesList() {
  const [items, setItems] = useState([]);
  const [stages, setStages] = useState([]);
  const [stageFilter, setStageFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [creating, setCreating] = useState(false);

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

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [st, data] = await Promise.all([
        stages.length ? Promise.resolve(stages) : listStages(),
        listCandidates(stageFilter ? { stage_code: stageFilter } : {})
      ]);
      if (!stages.length) setStages(st);
      setItems(data);
    } catch (e) {
      console.error(e);
      setError(normalizeErr(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);               // initial
  useEffect(() => { load(); }, [stageFilter]);    // on filter change

  async function onAdd(e) {
    e.preventDefault();
    setError("");

    const name = fullName.trim();
    if (name.length < 3) {
      setError("Укажите ФИО (не короче 3 символов).");
      return;
    }

    try {
      setCreating(true);
      await createCandidate({
        full_name: name,
        phone: phone.trim() || null,
        stage_code: "new",
        tenant_id: 1
      });
      setFullName("");
      setPhone("");
      await load();
    } catch (e) {
      console.error(e);
      setError(normalizeErr(e));
    } finally {
      setCreating(false);
    }
  }

  async function onChangeStage(id, newStage) {
    setError("");
    // оптимистично обновим UI
    const prev = items;
    const next = items.map(x => x.id === id ? { ...x, stage_code: newStage } : x);
    setItems(next);
    try {
      await updateCandidate(id, { stage_code: newStage });
    } catch (e) {
      console.error(e);
      setError(normalizeErr(e));
      setItems(prev); // откат, если ошибка
    }
  }

  return (
    <div style={{padding:20}}>
      <h2>Кандидаты</h2>

      <div style={{display:"flex", gap:12, alignItems:"center", marginBottom:12}}>
        <label>Фильтр по этапу:</label>
        <select value={stageFilter} onChange={e => setStageFilter(e.target.value)}>
          <option value="">— все —</option>
          {stages.map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
        </select>
      </div>

      <form onSubmit={onAdd} style={{margin:"16px 0", display:"flex", gap:8, alignItems:"center"}}>
        <input
          placeholder="ФИО *"
          value={fullName}
          onChange={e=>setFullName(e.target.value)}
        />
        <input
          placeholder="Телефон"
          value={phone}
          onChange={e=>setPhone(e.target.value)}
        />
        <button type="submit" disabled={creating}>
          {creating ? "Добавляем..." : "Добавить"}
        </button>
      </form>

      {error && <p style={{color:"crimson"}}>Ошибка: {error}</p>}
      {loading ? <p>Загрузка...</p> : (
        <table border="1" cellPadding="6" style={{borderCollapse:"collapse", minWidth:680}}>
          <thead><tr><th>ID</th><th>ФИО</th><th>Телефон</th><th>Этап</th></tr></thead>
          <tbody>
            {items.map(x => (
              <tr key={x.id}>
                <td>{x.id}</td>
                <td>{x.full_name}</td>
                <td>{x.phone || "-"}</td>
                <td>
                  <select value={x.stage_code} onChange={e=>onChangeStage(x.id, e.target.value)}>
                    {stages.map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
                  </select>
                </td>
              </tr>
            ))}
            {items.length===0 && !loading && !error && <tr><td colSpan="4">Пусто</td></tr>}
          </tbody>
        </table>
      )}
    </div>
  );
}
