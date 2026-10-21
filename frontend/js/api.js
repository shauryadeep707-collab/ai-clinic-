/**
 * AI HEALTH CLINIC - CENTRALIZED API CLIENT
 */

const API_BASE = (typeof window !== "undefined" && (window.location.protocol === "file:" || window.location.port === "5500" || window.location.port === "3000"))
  ? "http://localhost:5000"
  : (window.location.origin || "");

function getAuthToken() {
  return localStorage.getItem("token");
}

function getCurrentUser() {
  const user = localStorage.getItem("user");
  return user ? JSON.parse(user) : null;
}

function setAuthSession(token, user) {
  localStorage.setItem("token", token);
  localStorage.setItem("user", JSON.stringify(user));
}

function clearAuthSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

function showToast(message, type = "info") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerText = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 4000);
}

async function apiRequest(endpoint, method = "GET", data = null, isFormData = false) {
  const token = getAuthToken();
  const headers = {};

  if (!isFormData) {
    headers["Content-Type"] = "application/json";
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const config = {
    method,
    headers
  };

  if (data) {
    config.body = isFormData ? data : JSON.stringify(data);
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, config);
    if (response.status === 401) {
      clearAuthSession();
      if (!window.location.pathname.includes("login") && !window.location.pathname.includes("register") && !window.location.pathname.endsWith("index.html") && window.location.pathname !== "/") {
        window.location.href = "/static/html/login.html";
      }
      throw new Error("Session expired. Please log in again.");
    }
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.detail || "Request failed");
    }
    return result;
  } catch (error) {
    showToast(error.message, "danger");
    throw error;
  }
}

// Convenience Methods
const API = {
  get: (endpoint) => apiRequest(endpoint, "GET"),
  post: (endpoint, data) => apiRequest(endpoint, "POST", data),
  put: (endpoint, data) => apiRequest(endpoint, "PUT", data),
  delete: (endpoint) => apiRequest(endpoint, "DELETE"),
  upload: (endpoint, formData) => apiRequest(endpoint, "POST", formData, true),
  getToken: getAuthToken,
  getUser: getCurrentUser,
  setSession: setAuthSession,
  clearSession: clearAuthSession,
  toast: showToast
};
