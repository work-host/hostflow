import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header.jsx";
import RequireAuth from "./RequireAuth.jsx";
import LoginPage from "./pages/Login.jsx";
import CandidatesList from "./pages/CandidatesList.jsx";
import Employees from "./pages/Employees.jsx";

function Home() {
  return <div style={{padding:24}}>Главная</div>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Header />
      <div style={{padding:"16px 24px"}}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/candidates" element={<RequireAuth><CandidatesList /></RequireAuth>} />
          <Route path="/employees" element={<RequireAuth><Employees /></RequireAuth>} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
