/**
 * Microstash Authentication & Session Management Controller
 * Handles JWT token storage, automatic Bearer header injection,
 * Sign In / Sign Up modals, and session state.
 */

// 1. Transparent Auth Header Fetch Interceptor
(function() {
  const originalFetch = window.fetch;
  window.fetch = function(url, options = {}) {
    options = options || {};
    const token = localStorage.getItem('microstash_token');
    if (token && typeof url === 'string' && (url.startsWith('/api/') || url.includes('/api/'))) {
      options.headers = options.headers || {};
      if (options.headers instanceof Headers) {
        if (!options.headers.has('Authorization')) {
          options.headers.set('Authorization', `Bearer ${token}`);
        }
      } else if (Array.isArray(options.headers)) {
        if (!options.headers.some(([k]) => k.toLowerCase() === 'authorization')) {
          options.headers.push(['Authorization', `Bearer ${token}`]);
        }
      } else {
        if (!options.headers['Authorization'] && !options.headers['authorization']) {
          options.headers['Authorization'] = `Bearer ${token}`;
        }
      }
    }
    return originalFetch(url, options);
  };
})();

// 2. Global Auth State
window.currentUser = null;

function getAuthToken() {
  return localStorage.getItem('microstash_token');
}

function setAuthToken(token) {
  if (token) {
    localStorage.setItem('microstash_token', token);
  } else {
    localStorage.removeItem('microstash_token');
  }
}

function clearAuthToken() {
  localStorage.removeItem('microstash_token');
  window.currentUser = null;
  updateAuthUI();
}

// 3. UI Helpers
function showAlert(message, type = 'error') {
  const alertEl = document.getElementById('auth-alert');
  if (!alertEl) return;
  alertEl.textContent = message;
  alertEl.className = type === 'error' 
    ? 'p-3 rounded-xl text-xs font-medium border bg-error/15 border-error/30 text-error' 
    : 'p-3 rounded-xl text-xs font-medium border bg-primary/15 border-primary/30 text-primary';
  alertEl.classList.remove('hidden');
}

function clearAlert() {
  const alertEl = document.getElementById('auth-alert');
  if (alertEl) {
    alertEl.textContent = '';
    alertEl.classList.add('hidden');
  }
}

function updateAuthUI() {
  const user = window.currentUser;
  const loginBtn = document.getElementById('btn-header-login');
  const userLabel = document.getElementById('header-user-label');
  const tabsView = document.getElementById('auth-view-tabs');
  const profileView = document.getElementById('auth-view-profile');

  if (user) {
    // Header representation
    if (userLabel) userLabel.textContent = `@${user.username}`;
    if (loginBtn) {
      loginBtn.className = "flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-secondary/20 border border-secondary/40 text-xs font-bold text-secondary hover:bg-secondary/30 transition shadow-sm";
    }

    // Modal profile view
    if (tabsView) tabsView.classList.add('hidden');
    if (profileView) {
      profileView.classList.remove('hidden');
      const initials = (user.full_name || user.username || 'U').substring(0, 2).toUpperCase();
      const initialsEl = document.getElementById('profile-avatar-initials');
      if (initialsEl) initialsEl.textContent = initials;

      const nameEl = document.getElementById('profile-fullname');
      if (nameEl) nameEl.textContent = user.full_name || user.username;

      const usernameEl = document.getElementById('profile-username');
      if (usernameEl) usernameEl.textContent = `@${user.username}`;

      const emailEl = document.getElementById('profile-email');
      if (emailEl) emailEl.textContent = user.email;
    }
  } else {
    // Guest representation
    if (userLabel) userLabel.textContent = 'Sign In';
    if (loginBtn) {
      loginBtn.className = "flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary/20 border border-primary/40 text-xs font-bold text-primary hover:bg-primary/30 transition shadow-sm";
    }

    // Modal tabs view
    if (tabsView) tabsView.classList.remove('hidden');
    if (profileView) profileView.classList.add('hidden');
  }
}

// 4. Modal Open/Close & Tab Switching
function openAuthModal(tab = 'login') {
  const modal = document.getElementById('auth-modal');
  if (!modal) return;
  clearAlert();
  if (!window.currentUser) {
    switchAuthTab(tab);
  }
  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

function closeAuthModal() {
  const modal = document.getElementById('auth-modal');
  if (!modal) return;
  modal.classList.add('hidden');
  modal.classList.remove('flex');
  clearAlert();
}

function switchAuthTab(tab) {
  clearAlert();
  const loginBtn = document.getElementById('auth-tab-login-btn');
  const regBtn = document.getElementById('auth-tab-register-btn');
  const formLogin = document.getElementById('form-auth-login');
  const formReg = document.getElementById('form-auth-register');

  if (tab === 'login') {
    if (loginBtn) {
      loginBtn.className = "flex-1 py-2 text-xs font-headline font-bold rounded-xl transition bg-primary text-surface-container-lowest";
    }
    if (regBtn) {
      regBtn.className = "flex-1 py-2 text-xs font-headline font-bold rounded-xl text-on-surface-variant hover:text-white transition";
    }
    if (formLogin) formLogin.classList.remove('hidden');
    if (formReg) formReg.classList.add('hidden');
  } else {
    if (regBtn) {
      regBtn.className = "flex-1 py-2 text-xs font-headline font-bold rounded-xl transition bg-secondary text-surface-container-lowest";
    }
    if (loginBtn) {
      loginBtn.className = "flex-1 py-2 text-xs font-headline font-bold rounded-xl text-on-surface-variant hover:text-white transition";
    }
    if (formReg) formReg.classList.remove('hidden');
    if (formLogin) formLogin.classList.add('hidden');
  }
}

// 5. Auth Action Handlers
async function handleAuthLogin(e) {
  if (e) e.preventDefault();
  clearAlert();

  const identifier = document.getElementById('login-identifier')?.value?.trim();
  const password = document.getElementById('login-password')?.value;
  const submitBtn = document.getElementById('btn-submit-login');

  if (!identifier || !password) {
    showAlert("Please enter your email/username and password.");
    return;
  }

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span>Signing In...</span>`;
  }

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username_or_email: identifier,
        password: password
      })
    });

    const data = await res.json();
    if (!res.ok) {
      showAlert(data.detail || "Authentication failed. Check your credentials.");
      return;
    }

    setAuthToken(data.access_token);
    window.currentUser = data.user;
    updateAuthUI();
    showAlert(`Welcome back, ${data.user.full_name || data.user.username}!`, 'success');

    // Trigger reload of user stashes and stats if available
    if (typeof loadStats === 'function') loadStats();
    if (typeof loadStashes === 'function') loadStashes();

    setTimeout(() => {
      closeAuthModal();
    }, 800);
  } catch (err) {
    console.error("Login error:", err);
    showAlert("Network or server error during sign in.");
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<span>Sign In to Microstash</span><span class="material-symbols-outlined text-[16px]">arrow_forward</span>`;
    }
  }
}

async function handleAuthRegister(e) {
  if (e) e.preventDefault();
  clearAlert();

  const fullName = document.getElementById('reg-fullname')?.value?.trim();
  const username = document.getElementById('reg-username')?.value?.trim();
  const email = document.getElementById('reg-email')?.value?.trim();
  const password = document.getElementById('reg-password')?.value;
  const submitBtn = document.getElementById('btn-submit-register');

  if (!username || !email || !password) {
    showAlert("Username, email, and password are required.");
    return;
  }

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span>Creating Account...</span>`;
  }

  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email,
        username: username,
        password: password,
        full_name: fullName || null
      })
    });

    const data = await res.json();
    if (!res.ok) {
      showAlert(data.detail || "Registration failed.");
      return;
    }

    setAuthToken(data.access_token);
    window.currentUser = data.user;
    updateAuthUI();
    showAlert(`Account created! Welcome, ${data.user.username}.`, 'success');

    if (typeof loadStats === 'function') loadStats();
    if (typeof loadStashes === 'function') loadStashes();

    setTimeout(() => {
      closeAuthModal();
    }, 800);
  } catch (err) {
    console.error("Registration error:", err);
    showAlert("Network error during registration.");
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<span>Create Free Account</span><span class="material-symbols-outlined text-[16px]">how_to_reg</span>`;
    }
  }
}

async function handleAuthLogout() {
  try {
    await fetch('/api/auth/logout', { method: 'POST' });
  } catch (err) {
    console.warn("Logout endpoint error:", err);
  } finally {
    clearAuthToken();
    closeAuthModal();
    if (typeof loadStats === 'function') loadStats();
    if (typeof loadStashes === 'function') loadStashes();
  }
}

// 6. Bootstrap Auth Verification
async function initAuth() {
  const token = getAuthToken();
  if (!token) {
    updateAuthUI();
    return;
  }

  try {
    const res = await fetch('/api/auth/me');
    if (res.ok) {
      const data = await res.json();
      window.currentUser = data.user;
      updateAuthUI();
    } else {
      clearAuthToken();
    }
  } catch (err) {
    console.warn("Could not verify session token:", err);
  }
}

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  initAuth();
});

// Expose globals for inline event handlers
window.openAuthModal = openAuthModal;
window.closeAuthModal = closeAuthModal;
window.switchAuthTab = switchAuthTab;
window.handleAuthLogin = handleAuthLogin;
window.handleAuthRegister = handleAuthRegister;
window.handleAuthLogout = handleAuthLogout;
window.initAuth = initAuth;
