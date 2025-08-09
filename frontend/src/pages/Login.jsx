import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../http";

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("biuro@work-host.com");
  const [password, setPassword] = useState("ChangeMe123!");
  const [error, setError] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      navigate("/candidates", { replace: true });
    } catch (err) {
      setError("Неверный логин или пароль");
      console.error("[login] error:", err);
    }
  }

  return (
    <div style={{padding:24, maxWidth:520}}>
      <h1>Вход</h1>
      <form onSubmit={onSubmit} style={{display:"grid", gap:8}}>
        <input
          name="username"
          autoComplete="username"
          placeholder="Email"
          value={email}
          onChange={(e)=>setEmail(e.target.value)}
        />
        <input
          name="password"
          autoComplete="current-password"
          placeholder="Пароль"
          type="password"
          value={password}
          onChange={(e)=>setPassword(e.target.value)}
        />
        <button type="submit">Войти</button>
        {error && <div style={{color:"crimson"}}>{error}</div>}
      </form>
    </div>
  );
}
