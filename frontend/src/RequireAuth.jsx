import React from "react";
import { Navigate } from "react-router-dom";
import { getUser } from "./http";

export default function RequireAuth({ children }) {
  const user = getUser();
  if (!user) return <Navigate to="/login" replace />;
  return children;
}
