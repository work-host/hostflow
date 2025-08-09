import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { getUser, logout } from "../http";

export default function Header() {
  const navigate = useNavigate();
  const user = getUser();

  function onLogout(e) {
    e.preventDefault();
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div style={{display:"flex", justifyContent:"space-between", padding:"10px 16px", borderBottom:"1px solid #ddd"}}>
      <div style={{display:"flex", gap:16}}>
        <Link to="/">Главная</Link>
        <Link to="/candidates">Кандидаты</Link>
        <Link to="/employees">Сотрудники</Link>
      </div>
      <div>
        {user ? (
          <a href="#" onClick={onLogout} title={user.email}>Выйти</a>
        ) : (
          <Link to="/login">Войти</Link>
        )}
      </div>
    </div>
  );
}
