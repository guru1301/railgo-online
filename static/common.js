
// ══════════════════════════════════════════════════════════
//  THEME
// ══════════════════════════════════════════════════════════
function setTheme(themeName) {
    localStorage.setItem('theme', themeName);
    document.body.classList.remove('light-mode', 'dark-mode');
    document.body.classList.add(themeName + '-mode');
    const themeCheckbox = document.getElementById('theme-toggle');
    if (themeCheckbox) themeCheckbox.checked = (themeName === 'dark');
}

function toggleTheme() {
    setTheme(localStorage.getItem('theme') === 'dark' ? 'light' : 'dark');
}

// ══════════════════════════════════════════════════════════
//  AUTH STATE
// ══════════════════════════════════════════════════════════
const RailGoAuth = {
    getToken()  { return localStorage.getItem('railgo_token'); },
    getUser()   {
        try { return JSON.parse(localStorage.getItem('railgo_user')); } catch { return null; }
    },
    isLoggedIn(){ return !!this.getToken(); },
    save(token, user) {
        localStorage.setItem('railgo_token', token);
        localStorage.setItem('railgo_user', JSON.stringify(user));
    },
    clear() {
        localStorage.removeItem('railgo_token');
        localStorage.removeItem('railgo_user');
    }
};

function getCookie(name) {
    const parts = document.cookie.split(';').map(v => v.trim());
    const row = parts.find(v => v.startsWith(name + '='));
    return row ? decodeURIComponent(row.substring(name.length + 1)) : null;
}

const _nativeFetch = window.fetch.bind(window);
window.fetch = (input, init = {}) => {
    const req = { ...init };
    req.credentials = req.credentials || 'include';
    const method = (req.method || 'GET').toUpperCase();
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
        const csrf = getCookie('railgo_csrf');
        if (csrf) {
            req.headers = { ...(req.headers || {}), 'X-CSRF-Token': csrf };
        }
    }
    return _nativeFetch(input, req);
};

function requireFlowState(requiredKeys, redirectUrl) {
    const missing = (requiredKeys || []).some((key) => !sessionStorage.getItem(key));
    if (missing) {
        window.location.replace(redirectUrl || 'index.html');
        return false;
    }
    return true;
}

const FLOW_STORAGE_KEY = 'railgo_flow_v1';
const FLOW_STEPS = ['search', 'selection', 'passengers', 'payment', 'confirmed'];

function _emptyFlowState() {
    return {
        step: 'search',
        search: null,
        selection: null,
        passengers: [],
        contactDetails: null,
        payment: null,
        confirmation: null,
        updatedAt: Date.now(),
    };
}

const FlowState = {
    read() {
        try {
            const raw = sessionStorage.getItem(FLOW_STORAGE_KEY);
            if (!raw) return _emptyFlowState();
            return { ..._emptyFlowState(), ...JSON.parse(raw) };
        } catch {
            return _emptyFlowState();
        }
    },
    write(patch) {
        const next = { ...this.read(), ...patch, updatedAt: Date.now() };
        sessionStorage.setItem(FLOW_STORAGE_KEY, JSON.stringify(next));
        return next;
    },
    clear() {
        sessionStorage.removeItem(FLOW_STORAGE_KEY);
    },
    setStep(step) {
        if (!FLOW_STEPS.includes(step)) return this.read();
        return this.write({ step });
    },
    validate(requiredBlocks) {
        const state = this.read();
        return (requiredBlocks || []).every((key) => {
            const value = state[key];
            if (Array.isArray(value)) return value.length > 0;
            return !!value;
        });
    },
    ensure(requiredBlocks, redirectUrl) {
        if (!this.validate(requiredBlocks)) {
            window.location.replace(redirectUrl || 'index.html');
            return false;
        }
        return true;
    },
};

async function apiRequest(url, options = {}) {
    const requestOptions = { ...options };
    const headers = { ...(requestOptions.headers || {}) };
    if (RailGoAuth.isLoggedIn() && !headers.Authorization) {
        headers.Authorization = `Bearer ${RailGoAuth.getToken()}`;
    }
    requestOptions.headers = headers;
    const res = await fetch(url, requestOptions);
    let data = null;
    try {
        data = await res.json();
    } catch {
        data = null;
    }
    if (!res.ok) {
        const message = (data && data.detail) ? data.detail : `Request failed (${res.status})`;
        throw new Error(message);
    }
    return data;
}

// ══════════════════════════════════════════════════════════
//  AUTH MODAL
// ══════════════════════════════════════════════════════════
let _authCallback = null;

function openAuthModal(onSuccess) {
    _authCallback = onSuccess || null;
    const bd = document.getElementById('auth-backdrop');
    if (!bd) return;
    // Hide the train loading overlay if present so modal is clearly visible
    const trainOverlay = document.getElementById('train-page-overlay');
    if (trainOverlay) trainOverlay.classList.add('tpo-hide');
    _authShowLogin();
    bd.classList.add('active');
}

function closeAuthModal() {
    const bd = document.getElementById('auth-backdrop');
    if (bd) bd.classList.remove('active');
    _authCallback = null;
}

function _authShowError(msg) {
    const el = document.getElementById('auth-error');
    if (!el) return;
    if (typeof msg === 'object') {
        try { msg = msg[0]?.msg || JSON.stringify(msg); } 
        catch { msg = 'An error occurred.'; }
    }
    el.textContent = msg;
    el.style.display = msg ? 'block' : 'none';
}

function _authShowLogin() {
    document.getElementById('auth-body').innerHTML = `
      <div class="auth-step">
        <div class="auth-title">Sign in to continue</div>
        <div class="auth-subtitle">Enter your email and password to get started</div>
        <div class="auth-error" id="auth-error"></div>
        <div class="auth-input-wrap">
          <i class="bi bi-envelope"></i>
          <input id="auth-email" class="auth-input" type="email" placeholder="you@example.com" autocomplete="email"/>
        </div>
        <div class="auth-input-wrap">
          <i class="bi bi-lock"></i>
          <input id="auth-password" class="auth-input" type="password" placeholder="Your password" autocomplete="current-password"/>
        </div>
        <button class="auth-btn" onclick="_authSubmitLogin()">LOGIN</button>
        <p class="auth-note" style="margin-top:20px; font-size:0.85rem;">Don't have an account? <a href="#" onclick="_authShowRegister(); return false;" style="color:#6c63ff; font-weight:600; text-decoration:none;">Sign Up</a></p>
      </div>`;
    const inp = document.getElementById('auth-password');
    if (inp) { inp.addEventListener('keydown', e => e.key==='Enter' && _authSubmitLogin()); }
}

let _tempRegisterData = {};

function _authShowRegister() {
    document.getElementById('auth-body').innerHTML = `
      <div class="auth-step" id="register-step-1">
        <div class="auth-title">Create your account</div>
        <div class="auth-subtitle">Join RailGo today</div>
        <div class="auth-error" id="auth-error"></div>
        <div class="auth-input-wrap">
          <i class="bi bi-person"></i>
          <input id="auth-name" class="auth-input" type="text" placeholder="Your full name" autocomplete="name"/>
        </div>
        <div class="auth-input-wrap">
          <i class="bi bi-envelope"></i>
          <input id="auth-email" class="auth-input" type="email" placeholder="you@example.com" autocomplete="email"/>
        </div>
        <div class="auth-input-wrap">
          <i class="bi bi-lock"></i>
          <input id="auth-password" class="auth-input" type="password" placeholder="Create a password (min 6 chars)" autocomplete="new-password"/>
        </div>
        <button class="auth-btn" onclick="_authSendOtp()">CONTINUE</button>
        <p class="auth-note" style="margin-top:20px; font-size:0.85rem;">Already have an account? <a href="#" onclick="_authShowLogin(); return false;" style="color:#6c63ff; font-weight:600; text-decoration:none;">Login</a></p>
      </div>
      
      <div class="auth-step" id="register-step-2" style="display:none; text-align:center;">
        <div class="auth-title">Verify your email</div>
        <div class="auth-subtitle">We sent a 6-digit code to <br><span id="verify-email-display" style="font-weight:700; color:#6c63ff;"></span></div>
        <div class="auth-error" id="auth-otp-error"></div>
        
        <div class="otp-container" style="margin: 25px 0;">
            <input type="text" id="auth-otp" class="otp-input" maxlength="6" placeholder="------" autocomplete="one-time-code" />
        </div>
        
        <button class="auth-btn" onclick="_authSubmitRegister()">VERIFY & REGISTER</button>
        <p class="auth-note" style="margin-top:20px; font-size:0.85rem;"><a href="#" onclick="_authShowRegister(); return false;" style="color:#64748b; font-weight:600; text-decoration:none;"><i class="bi bi-arrow-left"></i> Back to details</a></p>
      </div>`;
}

async function _authSubmitLogin() {
    const email = (document.getElementById('auth-email')?.value || '').trim();
    const password = document.getElementById('auth-password')?.value || '';
    if (!email) return _authShowError('Please enter your email.');
    if (!password) return _authShowError('Please enter your password.');
    
    const btn = document.querySelector('.auth-btn');
    if (btn) { btn.disabled = true; btn.textContent = 'Logging in...'; }
    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({email, password})
        });
        const data = await res.json();
        if (!res.ok) { _authShowError(data.detail || 'Login failed.'); if (btn) { btn.disabled=false; btn.textContent='LOGIN'; } return; }
        _authSuccess(data.token, data.user);
    } catch { _authShowError('Network error.'); if (btn) { btn.disabled=false; btn.textContent='LOGIN'; } }
}

async function _authSendOtp() {
    const name = (document.getElementById('auth-name')?.value || '').trim();
    const email = (document.getElementById('auth-email')?.value || '').trim();
    const password = document.getElementById('auth-password')?.value || '';
    if (!name) return _authShowError('Please enter your full name.');
    if (!email) return _authShowError('Please enter your email.');
    if (password.length < 6) return _authShowError('Password must be at least 6 characters.');
    
    const btn = document.querySelector('#register-step-1 .auth-btn');
    if (btn) { btn.disabled = true; btn.textContent = 'Sending code...'; }
    
    try {
        const res = await fetch('/api/auth/send-otp', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({email})
        });
        const data = await res.json();
        if (!res.ok) { _authShowError(data.detail || 'Failed to send OTP.'); if (btn) { btn.disabled=false; btn.textContent='CONTINUE'; } return; }
        
        // Save temp data
        _tempRegisterData = { name, email, password };
        
        // Transition UI
        document.getElementById('register-step-1').style.display = 'none';
        document.getElementById('register-step-2').style.display = 'block';
        document.getElementById('verify-email-display').textContent = email;
        setTimeout(() => document.getElementById('auth-otp')?.focus(), 100);
        
    } catch { _authShowError('Network error.'); if (btn) { btn.disabled=false; btn.textContent='CONTINUE'; } }
}

async function _authSubmitRegister() {
    const otp = (document.getElementById('auth-otp')?.value || '').trim();
    const errEl = document.getElementById('auth-otp-error');
    if (!otp || otp.length !== 6) {
        if(errEl) { errEl.textContent = 'Please enter the 6-digit code.'; errEl.style.display = 'block'; }
        return;
    }
    
    const btn = document.querySelector('#register-step-2 .auth-btn');
    if (btn) { btn.disabled = true; btn.textContent = 'Verifying...'; }
    try {
        const payload = {
            name: _tempRegisterData.name,
            email: _tempRegisterData.email,
            password: _tempRegisterData.password,
            otp: otp
        };
        const res = await fetch('/api/auth/register', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) { 
            let errorMsg = data.detail || 'Registration failed.';
            if (typeof errorMsg === 'object') {
                try { errorMsg = errorMsg[0]?.msg || JSON.stringify(errorMsg); } 
                catch { errorMsg = 'An error occurred.'; }
            }
            if(errEl) { errEl.textContent = errorMsg; errEl.style.display = 'block'; }
            if (btn) { btn.disabled=false; btn.textContent='VERIFY & REGISTER'; } 
            return; 
        }
        _authSuccess(data.token, data.user);
    } catch { 
        if(errEl) { errEl.textContent = 'Network error.'; errEl.style.display = 'block'; }
        if (btn) { btn.disabled=false; btn.textContent='VERIFY & REGISTER'; } 
    }
}

function _authSuccess(token, user) {
    RailGoAuth.save(token, user);
    closeAuthModal();
    _updateHeaderForUser(user);
    if (typeof _authCallback === 'function') { const cb = _authCallback; _authCallback = null; cb(); }
}

function authLogout() {
    fetch('/api/auth/logout', { method: 'POST' }).catch(() => {});
    RailGoAuth.clear();
    FlowState.clear();
    window.location.href = 'index.html';
}

// ══════════════════════════════════════════════════════════
//  PROFILE MODAL
// ══════════════════════════════════════════════════════════
function openProfileModal() {
    requireAuth(() => {
        const user = RailGoAuth.getUser();
        if (user) {
            const pbd = document.getElementById('profile-backdrop');
            if (pbd) {
                document.getElementById('profile-name-input').value = user.name || '';
                document.getElementById('profile-email-input').value = user.email || '';
                document.getElementById('profile-error').style.display = 'none';
                document.getElementById('profile-success').style.display = 'none';
                const picContainer = document.getElementById('profile-pic-container');
                if (picContainer) {
                    if (user.profile_pic) {
                        picContainer.innerHTML = `<img src="${user.profile_pic}" style="width:100%; height:100%; object-fit:cover;">`;
                    } else {
                        picContainer.innerHTML = `<i class="bi bi-person text-secondary" style="font-size:2.5rem;"></i>`;
                    }
                }
                pbd.classList.add('active');
                
                // close sidebar if open
                const sidebar = document.getElementById('sidebar');
                const overlay = document.getElementById('overlay');
                if (sidebar) sidebar.classList.remove('active');
                if (overlay) overlay.classList.remove('active');
            }
        }
    });
}


function closeProfileModal() {
    const pbd = document.getElementById('profile-backdrop');
    if (pbd) pbd.classList.remove('active');
}

// ══════════════════════════════════════════════════════════
//  MY BOOKINGS MODAL
// ══════════════════════════════════════════════════════════
function closeMyBookingsModal() {
    const mbd = document.getElementById('my-bookings-backdrop');
    if (mbd) mbd.classList.remove('active');
}

function openMyBookingsModal() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    if (sidebar) sidebar.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    
    requireAuth(() => {
        const mbd = document.getElementById('my-bookings-backdrop');
        if (mbd) mbd.classList.add('active');
        fetchMyBookings();
    });
}

async function fetchMyBookings() {
    const body = document.getElementById('my-bookings-body');
    body.innerHTML = '<div class="text-center my-4"><div class="spinner-border text-primary" style="border-color:#6c63ff; border-right-color:transparent;"></div><div class="mt-3 text-muted fw-bold">Loading your journeys...</div></div>';
    
    try {
        const res = await fetch('/api/bookings/user/my-bookings', {
            headers: { 'Authorization': `Bearer ${RailGoAuth.getToken()}` }
        });
        if (!res.ok) throw new Error('Failed to fetch bookings');
        const bookings = await res.json();
        
        if (bookings.length === 0) {
            body.innerHTML = `
                <div class="text-center my-5">
                    <i class="bi bi-ticket-perforated" style="font-size: 3rem; color: #cbd5e1;"></i>
                    <h5 class="mt-3 text-muted">No Bookings Found</h5>
                    <p class="text-muted" style="font-size:0.9rem;">Looks like you haven't booked any trains yet.</p>
                    <button class="btn btn-primary mt-2" onclick="closeMyBookingsModal(); window.location.href='index.html'" style="border-radius:12px; font-weight:600;">Book Now</button>
                </div>
            `;
            return;
        }

        let html = '';
        const isDark = document.body.classList.contains('dark-mode');
        const cardBg = isDark ? 'rgba(11, 15, 30, 0.8)' : 'rgba(255,255,255,0.6)';
        const cardBorder = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)';
        const titleColor = isDark ? '#f1f5f9' : '#1e293b';

        bookings.forEach(b => {
            const dateStr = new Date(b.train_instance.journey_date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
            const isPaid = b.payment_status === 'PAID';
            const statusUpper = (b.status || 'Confirmed').toUpperCase();
            const isCancelled = statusUpper === 'CANCELLED';
            const badgeClass = isCancelled ? 'bg-danger text-danger border-danger' : 'bg-success text-success border-success';

            html += '<div style="background:' + cardBg + ';border:1px solid ' + cardBorder + ';border-radius:12px;padding:12px 14px;margin-bottom:10px;box-shadow:0 2px 6px rgba(0,0,0,.04); opacity:' + (isCancelled ? '0.8' : '1') + ';">' +
                '<div class="d-flex justify-content-between align-items-center mb-2">' +
                '<div><span class="badge ' + badgeClass + ' bg-opacity-25 border border-opacity-25 align-middle" style="border-radius:12px;padding:3px 8px;font-size:.65rem;margin-right:8px;">' + statusUpper + '</span>' +
                '<span style="font-size:.85rem;font-weight:700;color:' + titleColor + ';" class="align-middle">' + b.train_instance.train.name + ' <span class="text-muted" style="font-size:.75rem;font-weight:500;">(' + b.train_instance.train.train_number + ')</span></span></div>' +
                '<span class="fw-bold" style="color:#6c63ff;font-size:.75rem;">PNR: ' + b.pnr + '</span></div>' +
                
                '<div class="d-flex justify-content-between align-items-center mb-2 pb-2 border-bottom" style="font-size:.75rem;">' +
                '<div class="text-muted"><i class="bi bi-calendar3 me-1"></i>' + dateStr + ' &middot; ' + b.train_class.class_master.code + ' Class</div>' +
                '<div class="d-flex align-items-center gap-2">' +
                '<span class="fw-bold" style="color:' + titleColor + ';">' + b.train_instance.train.source_station.code + '</span>' +
                '<i class="bi bi-arrow-right text-muted" style="font-size:.7rem;"></i>' +
                '<span class="fw-bold" style="color:' + titleColor + ';">' + b.train_instance.train.destination_station.code + '</span>' +
                '</div></div>' +
                
                '<div class="d-flex justify-content-between align-items-center mt-1">' +
                '<div class="d-flex align-items-center gap-2"><div class="fw-bold" style="font-size:.9rem;background:linear-gradient(135deg,#6c63ff,#f472b6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">&#8377;' + (b.total_amount ? b.total_amount.toFixed(0) : '0') + '</div>' +
                '<div style="font-size:.65rem;font-weight:700;' + (isPaid ? 'color:#10b981' : 'color:#f59e0b') + ';"><i class="bi ' + (isPaid ? 'bi-shield-check-fill' : 'bi-clock') + ' me-1"></i>' + (isPaid ? 'PAID' : (b.payment_status || 'PENDING')) + '</div></div>' +
                '<button onclick="closeMyBookingsModal();window.location.href=\'booking-details.html?pnr=' + b.pnr + '\'" style="background:rgba(108,99,255,.12);border:1px solid rgba(108,99,255,.3);color:#6c63ff;border-radius:8px;padding:4px 14px;font-weight:600;font-size:.75rem;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background=\'rgba(108,99,255,.22)\'" onmouseout="this.style.background=\'rgba(108,99,255,.12)\'">View Ticket</button>' +
                '</div></div>';
        });
        
        body.innerHTML = html;
        
    } catch (err) {
        console.error(err);
        body.innerHTML = '<div class="alert alert-danger mx-3 mt-3">Failed to load bookings. Please try again later.</div>';
    }
}


async function saveProfileModal() {
    const name = document.getElementById('profile-name-input').value.trim();
    const errEl = document.getElementById('profile-error');
    const sucEl = document.getElementById('profile-success');
    errEl.style.display = 'none';
    sucEl.style.display = 'none';
    
    if (!name) {
        errEl.style.display = 'block';
        errEl.innerHTML = '<i class="bi bi-exclamation-circle me-1"></i> Name cannot be empty.';
        return;
    }
    
    const token = RailGoAuth.getToken();
    const btn = document.getElementById('save-profile-btn');
    btn.disabled = true;
    btn.innerHTML = 'Saving...';
    
    try {
        const res = await fetch('/api/auth/profile', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ name })
        });
        
        const data = await res.json();
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-check2-circle me-1"></i>Save Changes';
        
        if (res.ok) {
            RailGoAuth.save(data.token, data.user);
            sucEl.style.display = 'block';
            sucEl.innerHTML = '<i class="bi bi-check-circle me-1"></i> Profile updated successfully!';
            _updateHeaderForUser(data.user);
            setTimeout(() => { closeProfileModal(); }, 1500);
        } else {
            errEl.style.display = 'block';
            errEl.innerHTML = `<i class="bi bi-exclamation-circle me-1"></i> ${data.detail || 'Failed to update.'}`;
        }
    } catch (e) {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-check2-circle me-1"></i>Save Changes';
        errEl.style.display = 'block';
        errEl.innerHTML = '<i class="bi bi-wifi-off me-1"></i> Network error.';
    }
}

async function _handleProfilePicUpload(input) {
    if (!input.files || !input.files[0]) return;
    const file = input.files[0];
    const statusEl = document.getElementById('profile-pic-status');
    const errEl = document.getElementById('profile-error');
    if (statusEl) statusEl.style.display = 'block';
    if (errEl) errEl.style.display = 'none';

    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const token = RailGoAuth.getToken();
        const res = await fetch('/api/auth/profile/picture', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });
        const data = await res.json();
        if (statusEl) statusEl.style.display = 'none';
        
        if (res.ok && data.profile_pic) {
            const user = RailGoAuth.getUser();
            user.profile_pic = data.profile_pic;
            RailGoAuth.save(token, user);
            _updateHeaderForUser(user);
            
            const picContainer = document.getElementById('profile-pic-container');
            if (picContainer) {
                picContainer.innerHTML = `<img src="${user.profile_pic}" style="width:100%; height:100%; object-fit:cover;">`;
            }
        } else {
            if (errEl) { errEl.style.display = 'block'; errEl.innerHTML = `<i class="bi bi-exclamation-circle me-1"></i> Upload failed.`; }
        }
    } catch (e) {
        if (statusEl) statusEl.style.display = 'none';
        if (errEl) { errEl.style.display = 'block'; errEl.innerHTML = `<i class="bi bi-wifi-off me-1"></i> Network error during upload.`; }
    }
    input.value = '';
}

// ══════════════════════════════════════════════════════════
//  HEADER CHIP
// ══════════════════════════════════════════════════════════
function _updateHeaderForUser(user) {
    if (!user) return;
    const navLinks = document.querySelector('.nav-links');
    if (!navLinks) return;
    const navSignupLink = document.getElementById('nav-signup-link');
    if (navSignupLink) navSignupLink.style.display = 'none';

    // Show logout in sidebar
    const logoutLink = document.querySelector('.logout-link');
    if (logoutLink) logoutLink.style.display = 'block';

    // Build initials
    const initials = user.name.split(' ').map(w=>w[0]).join('').substring(0,2).toUpperCase();
    
    // Update menu toggle (left side)
    const menuToggle = document.getElementById('menu-toggle');
    if (menuToggle) {
        if (user.profile_pic) {
            menuToggle.innerHTML = `<img src="${user.profile_pic}" style="width:36px; height:36px; border-radius:50%; object-fit:cover; border:2px solid #6c63ff;">`;
        } else {
            menuToggle.innerHTML = `<div class="user-avatar" style="width:36px; height:36px; font-size:0.9rem;">${initials}</div>`;
        }
    }

    const sidebarHeader = document.getElementById('sidebar-header');
    if (sidebarHeader) {
        sidebarHeader.innerHTML = `
            <div style="display:flex; align-items:center; gap:12px;">
                ${user.profile_pic ? `<img src="${user.profile_pic}" style="width:44px; height:44px; border-radius:50%; object-fit:cover; border:2px solid #6c63ff;">` : `<div class="user-avatar" style="width:44px; height:44px; font-size:1.15rem;">${initials}</div>`}
                <div style="overflow:hidden;">
                    <div style="font-weight:700; font-size:1.05rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${user.name}</div>
                    <div style="font-size:0.75rem; color:rgba(255,255,255,0.8); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${user.email}</div>
                </div>
            </div>`;
    }
}

// ══════════════════════════════════════════════════════════
//  requireAuth — call before protected actions
// ══════════════════════════════════════════════════════════
function requireAuth(callback) {
    if (RailGoAuth.isLoggedIn()) { callback(); return; }
    openAuthModal(callback);
}

// ══════════════════════════════════════════════════════════
//  HEADER + SIDEBAR INJECTION
// ══════════════════════════════════════════════════════════
function injectHeaderAndSidebar() {
    const headerHTML = `
    <header class="header">
        <div class="logo-container">
            <div class="menu-toggle" id="menu-toggle"><i class="bi bi-list"></i></div>
            <div class="logo" onclick="window.location.href='index.html'">
                <i class="bi bi-train-front-fill"></i> RailGo
            </div>
        </div>
        <nav class="nav-links">
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
            <a href="#">Contact</a>
            <a href="#" id="nav-signup-link">Login / Sign Up</a>
            <div class="theme-toggle-container">
                <i class="bi bi-sun-fill text-warning"></i>
                <label class="theme-switch">
                    <input type="checkbox" id="theme-toggle">
                    <span class="slider"></span>
                </label>
                <i class="bi bi-moon-fill text-info"></i>
            </div>
        </nav>
    </header>
    <div class="sidebar" id="sidebar">
        <button class="sidebar-close" id="sidebar-close"><i class="bi bi-x-lg"></i></button>
        <div class="sidebar-header" id="sidebar-header"><h3>RailGo Menu</h3></div>
        <ul class="sidebar-menu">
            <li><a href="#" onclick="openMyBookingsModal(); return false;"><i class="bi bi-ticket-perforated-fill"></i><span>My Bookings</span></a></li>
            <li><a href="live-status.html"><i class="bi bi-geo-alt-fill"></i><span>Live Train Status</span></a></li>
            <li><a href="#" onclick="openProfileModal(); return false;"><i class="bi bi-person"></i><span>My Profile</span></a></li>
            <li><a href="#"><i class="bi bi-question-circle"></i><span>Help &amp; Support</span></a></li>
            <li class="logout-link" style="display:none;"><a href="#" onclick="authLogout(); return false;" style="color:#ef4444;"><i class="bi bi-box-arrow-right" style="color:#ef4444;"></i><span>Logout</span></a></li>
        </ul>
    </div>
    <div class="overlay" id="overlay"></div>

    <!-- AUTH MODAL -->
    <div class="auth-backdrop" id="auth-backdrop">
      <div class="auth-modal" role="dialog" aria-modal="true">
        <button class="auth-close" onclick="closeAuthModal()" aria-label="Close">&times;</button>
        <div class="auth-header">
          <div class="auth-header-logo"><i class="bi bi-train-front-fill"></i>RailGo</div>
        </div>
        <div class="auth-perks">
          <div class="auth-perk"><i class="bi bi-shield-check-fill"></i>Secure Booking</div>
          <div class="auth-perk"><i class="bi bi-lightning-charge-fill"></i>Instant Confirm</div>
          <div class="auth-perk"><i class="bi bi-geo-alt-fill"></i>Track Journey</div>
          <div class="auth-perk"><i class="bi bi-headset"></i>24/7 Support</div>
        </div>
        <div class="auth-body" id="auth-body"></div>
      </div>
    </div>

    <!-- PROFILE MODAL -->
    <div class="auth-backdrop" id="profile-backdrop">
      <div class="auth-modal" role="dialog" aria-modal="true" style="width: min(500px, 94vw);">
        <button class="auth-close" onclick="closeProfileModal()" aria-label="Close">&times;</button>
        <div class="auth-header">
          <div class="auth-header-logo"><i class="bi bi-person-circle"></i> My Profile</div>
        </div>
        <div class="auth-body" id="profile-body">
            <div class="auth-step">
                <div class="auth-error" id="profile-error"></div>
                <div class="auth-error status-success" id="profile-success" style="background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.25); color: #10b981;"></div>
                
                <div style="text-align:center; margin-bottom: 24px; position:relative;">
                    <div style="position:relative; width:80px; height:80px; margin:0 auto; cursor:pointer;" onclick="document.getElementById('profile-pic-upload').click()">
                        <div id="profile-pic-container" style="width:80px; height:80px; border-radius:50%; background:#f3f4f6; display:flex; align-items:center; justify-content:center; border:3px solid #6c63ff; overflow:hidden;">
                            <i class="bi bi-person text-secondary" style="font-size:2.5rem;"></i>
                        </div>
                        <div style="position:absolute; bottom:-4px; right:-4px; background:#6c63ff; color:#fff; border-radius:50%; width:28px; height:28px; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 5px rgba(0,0,0,0.2);"><i class="bi bi-camera-fill" style="font-size:0.85rem;"></i></div>
                    </div>
                    <input type="file" id="profile-pic-upload" accept="image/*" style="display:none;" onchange="_handleProfilePicUpload(this)">
                    <div id="profile-pic-status" style="font-size:0.75rem; margin-top:8px; color:#6b7280; display:none;">Uploading...</div>
                </div>
                
                <div style="font-size:0.78rem; font-weight:700; color:#64748b; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.8px;"><i class="bi bi-person me-1"></i>Full Name</div>
                <div class="auth-input-wrap">
                  <i class="bi bi-person"></i>
                  <input id="profile-name-input" class="auth-input" type="text" placeholder="Your Name"/>
                </div>

                <div style="font-size:0.78rem; font-weight:700; color:#64748b; margin-bottom:6px; margin-top: 14px; text-transform:uppercase; letter-spacing:0.8px;"><i class="bi bi-envelope me-1"></i>Email Address</div>
                <div class="auth-input-wrap">
                  <i class="bi bi-envelope"></i>
                  <input id="profile-email-input" class="auth-input" type="email" disabled style="opacity:0.6; cursor:not-allowed;"/>
                </div>

                <button class="btn btn-primary mt-4 w-100" id="save-profile-btn" style="border-radius:12px; font-weight:600; padding:12px;" onclick="saveProfileModal()">Save Changes</button>
                <button class="btn btn-outline-secondary mt-2 w-100" style="border-radius:12px; font-weight:600; padding:12px;" onclick="closeProfileModal()">Close</button>
            </div>
        </div>
      </div>
    </div>

    <!-- MY BOOKINGS MODAL -->
    <div class="auth-backdrop" id="my-bookings-backdrop">
      <div class="auth-modal" role="dialog" aria-modal="true" style="width: min(700px, 94vw); max-height: 90vh; overflow-y: auto;">
        <button class="auth-close" onclick="closeMyBookingsModal()" aria-label="Close">&times;</button>
        <div class="auth-header">
          <div class="auth-header-logo"><i class="bi bi-ticket-detailed-fill"></i> My Bookings</div>
        </div>
        <div class="auth-body" id="my-bookings-body" style="padding-top: 15px;">
           <div class="text-center my-4"><div class="spinner-border text-primary"></div><div class="mt-2 text-muted">Loading bookings...</div></div>
        </div>
      </div>
    </div>
    `;

    const placeholder = document.getElementById('universal-header');
    if (placeholder) placeholder.innerHTML = headerHTML;

    // Sidebar
    const menuToggle   = document.getElementById('menu-toggle');
    const sidebar      = document.getElementById('sidebar');
    const overlay      = document.getElementById('overlay');
    const sidebarClose = document.getElementById('sidebar-close');
    const openSidebar  = () => { sidebar?.classList.add('active'); overlay?.classList.add('active'); };
    const closeSidebar = () => { sidebar?.classList.remove('active'); overlay?.classList.remove('active'); };
    menuToggle?.addEventListener('click', openSidebar);
    sidebarClose?.addEventListener('click', closeSidebar);
    overlay?.addEventListener('click', closeSidebar);

    // Theme toggle
    const themeCheckbox = document.getElementById('theme-toggle');
    if (themeCheckbox) themeCheckbox.addEventListener('change', toggleTheme);

    // Close auth modal on backdrop click
    const bd = document.getElementById('auth-backdrop');
    bd?.addEventListener('click', e => { if (e.target === bd) closeAuthModal(); });

    // Close profile modal on backdrop click
    const pbd = document.getElementById('profile-backdrop');
    pbd?.addEventListener('click', e => { if (e.target === pbd) closeProfileModal(); });

    // "Sign Up" nav link → open auth modal instead of separate page
    const signupLink = document.getElementById('nav-signup-link');
    if (signupLink) {
        signupLink.addEventListener('click', e => {
            e.preventDefault();
            openAuthModal(null);
        });
    }

    // If already logged in, show user chip
    const user = RailGoAuth.getUser();
    if (user) _updateHeaderForUser(user);
}

// ══════════════════════════════════════════════════════════
//  INIT
// ══════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
    setTheme(localStorage.getItem('theme') || 'light');
    injectHeaderAndSidebar();
});
