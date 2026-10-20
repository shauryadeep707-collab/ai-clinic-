/**
 * Authentication and Session Management
 */

document.addEventListener("DOMContentLoaded", () => {
  // Update header profile display if present
  const user = API.getUser();
  const userNameElem = document.getElementById("header-user-name");
  const userRoleElem = document.getElementById("header-user-role");
  const userAvatarElem = document.getElementById("header-user-avatar");

  if (user) {
    if (userNameElem) userNameElem.innerText = user.full_name;
    if (userRoleElem) userRoleElem.innerText = user.role.charAt(0).toUpperCase() + user.role.slice(1);
    if (userAvatarElem) {
      const initials = user.full_name.split(" ").map(n => n[0]).join("").toUpperCase();
      userAvatarElem.innerText = initials.slice(0, 2);
    }
  }

  // Logout button binding
  const logoutBtns = document.querySelectorAll(".btn-logout");
  logoutBtns.forEach(btn => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      try {
        await API.post("/api/auth/logout");
      } catch (err) {}
      API.clearSession();
      window.location.href = "/static/html/login.html";
    });
  });
});

async function handleLogin(event) {
  event.preventDefault();
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;

  try {
    const data = await API.post("/api/auth/login", { email, password });
    API.setSession(data.access_token, {
      user_id: data.user_id,
      role: data.role,
      full_name: data.full_name,
      email: data.email
    });
    API.toast("Login successful! Redirecting...", "success");
    setTimeout(() => {
      if (data.role === "doctor") {
        window.location.href = "/static/html/doctor-dashboard.html";
      } else if (data.role === "admin") {
        window.location.href = "/static/html/admin-dashboard.html";
      } else {
        window.location.href = "/static/html/patient-dashboard.html";
      }
    }, 600);
  } catch (err) {
    console.error("Login failed", err);
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const fullName = document.getElementById("reg-name").value.trim();
  const email = document.getElementById("reg-email").value.trim();
  const password = document.getElementById("reg-password").value;
  const role = document.getElementById("reg-role") ? document.getElementById("reg-role").value : "patient";
  const phone = document.getElementById("reg-phone") ? document.getElementById("reg-phone").value.trim() : "";

  try {
    const data = await API.post("/api/auth/register", {
      full_name: fullName,
      email,
      password,
      role,
      phone
    });
    API.setSession(data.access_token, {
      user_id: data.user_id,
      role: data.role,
      full_name: data.full_name,
      email: data.email
    });
    API.toast("Registration complete! Redirecting...", "success");
    setTimeout(() => {
      if (role === "doctor") {
        window.location.href = "/static/html/doctor-register.html";
      } else {
        window.location.href = "/static/html/patient-dashboard.html";
      }
    }, 600);
  } catch (err) {
    console.error("Registration failed", err);
  }
}
