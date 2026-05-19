import axios from "axios";

const API = "http://127.0.0.1:8001";

// =========================
// 🔐 AUTH HEADER
// =========================
function authHeader() {
  const token = localStorage.getItem("token");

  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
}

// =========================
// 📚 GET AI CONTENT (FROM PDF)
// =========================
export async function getAIContent(materialId) {
  const res = await axios.get(
    `${API}/student-content/${materialId}`,
    authHeader()
  );

  return res.data;
}

// =========================
// 📂 GET UPLOADED MATERIALS
// =========================
export async function getMaterials() {
  const res = await axios.get(
    `${API}/upload/materials`,
    authHeader()
  );

  return res.data;
}