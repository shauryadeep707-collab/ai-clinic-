/**
 * AI Health Clinic — Authentication & Profile Session Management
 * Dynamically synchronizes user identity, role, avatar, and greetings across all portals.
 */

document.addEventListener("DOMContentLoaded", () => {
  initUserProfile();
  initLogoutButtons();
});

/**
 * Update UI headers, greetings, and forms with active user data
 */
function initUserProfile() {
  const user = API.getUser();
  if (!user) return;

  // 1. Header Name Display
  const nameElements = document.querySelectorAll("#header-user-name, .user-name");
  nameElements.forEach(el => {
    // Only update if it belongs to a header/profile widget
    if (el.closest(".user-profile-badge") || el.id === "header-user-name") {
      el.innerText = user.full_name;
    }
  });

  // 2. Header Role Display
  const roleElements = document.querySelectorAll("#header-user-role, .user-role");
  roleElements.forEach(el => {
    if (el.closest(".user-profile-badge") || el.id === "header-user-role") {
      if (user.role === "doctor") {
        el.innerText = "Verified Doctor";
      } else if (user.role === "admin") {
        el.innerText = "System Admin";
      } else {
        el.innerText = "Patient";
      }
    }
  });

  // 3. Avatar Initials
  const avatarElements = document.querySelectorAll("#header-user-avatar, .user-avatar");
  avatarElements.forEach(el => {
    if (el.closest(".user-profile-badge") || el.id === "header-user-avatar") {
      el.innerText = getInitials(user.full_name);
      if (user.role === "doctor") {
        el.style.background = "#DEF7EC";
        el.style.color = "#03543F";
      } else if (user.role === "admin") {
        el.style.background = "#FEF3C7";
        el.style.color = "#92400E";
      } else {
        el.style.background = "#CCFBF1";
        el.style.color = "#0F766E";
      }
    }
  });

  // 4. Welcome Greeting Header (Patient, Doctor, Admin)
  const welcomeHeading = document.getElementById("welcome-heading");
  if (welcomeHeading) {
    if (user.role === "doctor") {
      const docName = user.full_name.startsWith("Dr") ? user.full_name : `Dr. ${user.full_name}`;
      welcomeHeading.innerText = `Welcome, ${docName}`;
    } else if (user.role === "admin") {
      welcomeHeading.innerText = `Welcome, ${user.full_name}`;
    } else {
      const hour = new Date().getHours();
      let timeGreeting = "Good Morning";
      if (hour >= 12 && hour < 17) {
        timeGreeting = "Good Afternoon";
      } else if (hour >= 17) {
        timeGreeting = "Good Evening";
      }
      const firstName = user.full_name.split(" ")[0] || "Patient";
      welcomeHeading.innerText = `${timeGreeting}, ${firstName}`;
    }
  }

  // 5. Settings / Profile Page Input Prefill
  const profNameInput = document.getElementById("prof-name");
  if (profNameInput && user.full_name) {
    profNameInput.value = user.full_name;
  }
}

/**
 * Computes 2-letter uppercase initials for names, stripping "Dr." prefixes for doctors
 */
function getInitials(name) {
  if (!name) return "US";
  const cleanName = name.replace(/^Dr\.?\s+/i, "").trim();
  const parts = cleanName.split(/\s+/).filter(Boolean);
  if (parts.length === 1) {
    return parts[0].slice(0, 2).toUpperCase();
  }
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/**
 * Handle user logout cleanly across all portal pages
 */
function initLogoutButtons() {
  const logoutBtns = document.querySelectorAll(".btn-logout");
  logoutBtns.forEach(btn => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      try {
        await API.post("/api/auth/logout");
      } catch (err) {
        // Continue clearing client session regardless of network response
      }
      API.clearSession();
      API.toast("Signed out successfully.", "info");
      setTimeout(() => {
        window.location.href = "/static/html/login.html";
      }, 300);
    });
  });
}

/**
 * Handle Login Form Submission
 */
async function handleLogin(event) {
  event.preventDefault();
  const emailInput = document.getElementById("login-email");
  const passwordInput = document.getElementById("login-password");
  const submitBtn = document.getElementById("btn-login-submit");

  const email = emailInput ? emailInput.value.trim() : "";
  const password = passwordInput ? passwordInput.value : "";

  if (!email || !password) {
    API.toast("Please enter both email and password.", "error");
    return;
  }

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Signing In...';
  }

  try {
    const data = await API.post("/api/auth/login", { email, password });
    
    API.setSession(data.access_token, {
      user_id: data.user_id,
      role: data.role,
      full_name: data.full_name,
      email: data.email
    });

    API.toast(`Welcome back, ${data.full_name}! Redirecting...`, "success");

    setTimeout(() => {
      if (data.role === "doctor") {
        window.location.href = "/static/html/doctor-dashboard.html";
      } else if (data.role === "admin") {
        window.location.href = "/static/html/admin-dashboard.html";
      } else {
        window.location.href = "/static/html/patient-dashboard.html";
      }
    }, 500);

  } catch (err) {
    console.error("Login failed:", err);
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="fa-solid fa-right-to-bracket"></i> Sign In to Portal';
    }
  }
}

/**
 * Handle Patient Registration
 */
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

    API.toast(`Account created! Welcome, ${data.full_name}.`, "success");

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
