export function setAuth(token, user){
  localStorage.setItem("hf_token", token);
  localStorage.setItem("hf_user", JSON.stringify(user||{}));
}
export function getToken(){ return localStorage.getItem("hf_token"); }
export function getUser(){
  try { return JSON.parse(localStorage.getItem("hf_user")||"null"); } catch { return null; }
}
export function clearAuth(){
  localStorage.removeItem("hf_token");
  localStorage.removeItem("hf_user");
}
