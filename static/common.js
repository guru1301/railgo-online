
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
        <div style="text-align:right; margin-top:-8px; margin-bottom:16px;">
          <a href="#" onclick="_authShowForgotPassword(); return false;" style="font-size:0.82rem; color:#6c63ff; font-weight:600; text-decoration:none;">Forgot password?</a>
        </div>
        <button class="auth-btn" onclick="_authSubmitLogin()">LOGIN</button>
        <p class="auth-note" style="margin-top:20px; font-size:0.85rem;">Don't have an account? <a href="#" onclick="_authShowRegister(); return false;" style="color:#6c63ff; font-weight:600; text-decoration:none;">Sign Up</a></p>
      </div>`;
    const inp = document.getElementById('auth-password');
    if (inp) { inp.addEventListener('keydown', e => e.key==='Enter' && _authSubmitLogin()); }
}

// ── Forgot Password flow ─────────────────────────────────────────────────────
let _fpEmail = '';

function _authShowForgotPassword() {
    document.getElementById('auth-body').innerHTML = `
      <div class="auth-step">
        <div class="auth-title">Reset Password</div>
        <div class="auth-subtitle">Enter your registered email and we'll send you a reset code</div>
        <div class="auth-error" id="auth-error"></div>
        <div class="auth-input-wrap">
          <i class="bi bi-envelope"></i>
          <input id="auth-fp-email" class="auth-input" type="email" placeholder="you@example.com" autocomplete="email"/>
        </div>
        <button class="auth-btn" onclick="_authSubmitForgotPassword()">SEND RESET CODE</button>
        <p class="auth-note" style="margin-top:20px; font-size:0.85rem;"><a href="#" onclick="_authShowLogin(); return false;" style="color:#64748b; font-weight:600; text-decoration:none;"><i class="bi bi-arrow-left"></i> Back to Login</a></p>
      </div>`;
    document.getElementById('auth-fp-email')?.addEventListener('keydown', e => e.key === 'Enter' && _authSubmitForgotPassword());
}

async function _authSubmitForgotPassword() {
    const email = (document.getElementById('auth-fp-email')?.value || '').trim();
    if (!email) return _authShowError('Please enter your email address.');

    const btn = document.querySelector('.auth-btn');
    if (btn) { btn.disabled = true; btn.textContent = 'Sending...'; }

    try {
        await fetch('/api/auth/forgot-password', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        // Always proceed to OTP step (prevents email enumeration)
        _fpEmail = email;
        _authShowResetPassword();
    } catch {
        _authShowError('Network error. Please try again.');
        if (btn) { btn.disabled = false; btn.textContent = 'SEND RESET CODE'; }
    }
}

function _authShowResetPassword() {
    document.getElementById('auth-body').innerHTML = `
      <div class="auth-step">
        <div class="auth-title">Enter Reset Code</div>
        <div class="auth-subtitle">If <strong style="color:#6c63ff;">${_fpEmail}</strong> is registered, a 6-digit code was sent to it.</div>
        <div class="auth-error" id="auth-error"></div>
        <div class="auth-input-wrap" style="margin-top:20px;">
          <i class="bi bi-key"></i>
          <input id="auth-fp-otp" class="auth-input" type="text" placeholder="6-digit code" maxlength="6" autocomplete="one-time-code"/>
        </div>
        <div class="auth-input-wrap">
          <i class="bi bi-lock"></i>
          <input id="auth-fp-newpw" class="auth-input" type="password" placeholder="New password (min 6 chars)" autocomplete="new-password"/>
        </div>
        <div class="auth-input-wrap">
          <i class="bi bi-lock-fill"></i>
          <input id="auth-fp-confirmpw" class="auth-input" type="password" placeholder="Confirm new password" autocomplete="new-password"/>
        </div>
        <button class="auth-btn" onclick="_authSubmitResetPassword()">RESET PASSWORD</button>
        <p class="auth-note" style="margin-top:16px; font-size:0.85rem;"><a href="#" onclick="_authShowForgotPassword(); return false;" style="color:#64748b; font-weight:600; text-decoration:none;"><i class="bi bi-arrow-left"></i> Re-send code</a></p>
      </div>`;
}

async function _authSubmitResetPassword() {
    const otp       = (document.getElementById('auth-fp-otp')?.value || '').trim();
    const newPw     = document.getElementById('auth-fp-newpw')?.value || '';
    const confirmPw = document.getElementById('auth-fp-confirmpw')?.value || '';

    if (!otp || otp.length !== 6)    return _authShowError('Please enter the 6-digit reset code.');
    if (newPw.length < 6)            return _authShowError('Password must be at least 6 characters.');
    if (newPw !== confirmPw)         return _authShowError('Passwords do not match.');

    const btn = document.querySelector('.auth-btn');
    if (btn) { btn.disabled = true; btn.textContent = 'Resetting...'; }

    try {
        const res = await fetch('/api/auth/reset-password', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: _fpEmail, otp, new_password: newPw })
        });
        const data = await res.json();
        if (!res.ok) {
            _authShowError(data.detail || 'Reset failed.');
            if (btn) { btn.disabled = false; btn.textContent = 'RESET PASSWORD'; }
            return;
        }
        // Success — redirect user to login
        document.getElementById('auth-body').innerHTML = `
          <div class="auth-step" style="text-align:center; padding: 20px 0;">
            <div style="font-size:3rem; margin-bottom:16px;">✅</div>
            <div class="auth-title" style="color:#10b981;">Password Reset!</div>
            <div class="auth-subtitle">Your password has been updated. You can now log in with your new password.</div>
            <button class="auth-btn" style="margin-top:24px;" onclick="_authShowLogin()">GO TO LOGIN</button>
          </div>`;
    } catch {
        _authShowError('Network error. Please try again.');
        if (btn) { btn.disabled = false; btn.textContent = 'RESET PASSWORD'; }
    }
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
        const pbd = document.getElementById('profile-backdrop');
        if (pbd) pbd.classList.add('active');

        // Reset to profile tab
        switchProfileTab('profile');

        // Populate fields
        const nameInp  = document.getElementById('profile-name-input');
        const emailInp = document.getElementById('profile-email-input');
        const dispName = document.getElementById('profile-display-name');
        const dispEmail= document.getElementById('profile-display-email');
        if (nameInp  && user?.name)  { nameInp.value  = user.name; }
        if (emailInp && user?.email) { emailInp.value = user.email; }
        if (dispName  && user?.name)  dispName.textContent  = user.name;
        if (dispEmail && user?.email) dispEmail.textContent = user.email;

        // Load profile pic if saved
        const pic = document.getElementById('profile-pic-container');
        if (pic && user?.profile_pic) {
            pic.innerHTML = `<img src="/${user.profile_pic}" style="width:100%;height:100%;object-fit:cover;" alt="Profile">`;
        }

        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('overlay');
        if (sidebar) sidebar.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
    });
}

function switchProfileTab(tab) {
    const profilePane   = document.getElementById('profile-tab-pane');
    const securityPane  = document.getElementById('security-tab-pane');
    const profileBtn    = document.getElementById('tab-btn-profile');
    const securityBtn   = document.getElementById('tab-btn-security');
    if (!profilePane || !securityPane) return;
    if (tab === 'profile') {
        profilePane.style.display  = 'block';
        securityPane.style.display = 'none';
        if (profileBtn)  { profileBtn.style.color  = '#6c63ff'; profileBtn.style.borderBottomColor  = '#6c63ff'; }
        if (securityBtn) { securityBtn.style.color = '#94a3b8'; securityBtn.style.borderBottomColor = 'transparent'; }
    } else {
        profilePane.style.display  = 'none';
        securityPane.style.display = 'block';
        if (securityBtn) { securityBtn.style.color = '#6c63ff'; securityBtn.style.borderBottomColor = '#6c63ff'; }
        if (profileBtn)  { profileBtn.style.color  = '#94a3b8'; profileBtn.style.borderBottomColor  = 'transparent'; }
        // Clear security fields on tab open
        ['pw-current','pw-new','pw-confirm'].forEach(id => {
            const el = document.getElementById(id); if (el) el.value = '';
        });
        ['pw-error','pw-success'].forEach(id => {
            const el = document.getElementById(id); if (el) el.style.display = 'none';
        });
    }
}




function closeProfileModal() {
    const pbd = document.getElementById('profile-backdrop');
    if (pbd) pbd.classList.remove('active');
}

async function savePasswordChange() {
    const current = document.getElementById('pw-current')?.value || '';
    const newPw   = document.getElementById('pw-new')?.value    || '';
    const confirm = document.getElementById('pw-confirm')?.value || '';
    const errEl   = document.getElementById('pw-error');
    const sucEl   = document.getElementById('pw-success');
    const btn     = document.getElementById('change-pw-btn');

    // Reset state
    errEl.style.display = 'none';
    sucEl.style.display = 'none';

    if (!current)          { errEl.style.display='block'; errEl.textContent='Please enter your current password.'; return; }
    if (newPw.length < 6)  { errEl.style.display='block'; errEl.textContent='New password must be at least 6 characters.'; return; }
    if (newPw !== confirm)  { errEl.style.display='block'; errEl.textContent='Passwords do not match.'; return; }
    if (current === newPw)  { errEl.style.display='block'; errEl.textContent='New password must be different from current password.'; return; }

    btn.disabled = true;
    btn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Updating...';

    try {
        const res = await fetch('/api/auth/change-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${RailGoAuth.getToken()}` },
            body: JSON.stringify({ current_password: current, new_password: newPw })
        });
        const data = await res.json();
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-key-fill me-1"></i>Update Password';
        if (res.ok) {
            // Clear fields on success
            document.getElementById('pw-current').value = '';
            document.getElementById('pw-new').value     = '';
            document.getElementById('pw-confirm').value = '';
            sucEl.style.display = 'block';
            sucEl.innerHTML = '<i class="bi bi-check-circle me-1"></i>Password updated successfully!';
            setTimeout(() => { sucEl.style.display = 'none'; }, 4000);
        } else {
            errEl.style.display = 'block';
            errEl.textContent = data.detail || 'Failed to update password.';
        }
    } catch {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-key-fill me-1"></i>Update Password';
        errEl.style.display = 'block';
        errEl.textContent = 'Network error. Please try again.';
    }
}


// ══════════════════════════════════════════════════════════
//  MY BOOKINGS MODAL
// ══════════════════════════════════════════════════════════
function closeMyBookingsModal() {
    const mbd = document.getElementById('my-bookings-backdrop');
    if (mbd) mbd.classList.remove('active');
}

// ══════════════════════════════════════════════════════
//  LIVE TRAIN STATUS MODAL (Sidebar popup)
// ══════════════════════════════════════════════════════
function openLiveStatusModal() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    if (sidebar) sidebar.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    const bd = document.getElementById('live-status-modal-backdrop');
    if (bd) bd.classList.add('active');
    // Clear previous input
    const inp = document.getElementById('ls-modal-train-no');
    if (inp) { inp.value = ''; setTimeout(() => inp.focus(), 200); }
    const errEl = document.getElementById('ls-modal-error');
    if (errEl) errEl.style.display = 'none';
}

function closeLiveStatusModal() {
    const bd = document.getElementById('live-status-modal-backdrop');
    if (bd) bd.classList.remove('active');
}

function _goLiveStatus() {
    const trainNo  = (document.getElementById('ls-modal-train-no')?.value || '').trim();
    const errEl    = document.getElementById('ls-modal-error');
    const errMsg   = document.getElementById('ls-modal-err-msg');
    if (!trainNo || trainNo.length < 4) {
        errEl.style.display  = 'block';
        errMsg.textContent   = 'Please enter a valid 4-5 digit train number.';
        document.getElementById('ls-modal-train-no').focus();
        return;
    }
    const startDay = document.querySelector('input[name="ls-day"]:checked')?.value || '0';
    closeLiveStatusModal();
    window.location.href = `live-status.html?trainNo=${encodeURIComponent(trainNo)}&startDay=${startDay}`;
}


// ══════════════════════════════════════════════════════
//  MASTER PASSENGER LIST MODAL
// ══════════════════════════════════════════════════════
function openMasterListModal() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    if (sidebar) sidebar.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    requireAuth(() => {
        const mbd = document.getElementById('master-list-backdrop');
        if (mbd) mbd.classList.add('active');
        fetchMasterList();
    });
}

function closeMasterListModal() {
    const mbd = document.getElementById('master-list-backdrop');
    if (mbd) mbd.classList.remove('active');
}

async function fetchMasterList() {
    const body = document.getElementById('master-list-body');
    body.innerHTML = '<div class="text-center my-4"><div class="spinner-border" style="color:#6c63ff;width:28px;height:28px;border-width:3px;"></div><div class="mt-3 text-muted fw-bold" style="font-size:.9rem;">Loading...</div></div>';
    try {
        const passengers = await apiRequest('/api/passengers');
        _renderMasterList(passengers);
    } catch {
        body.innerHTML = '<div class="alert alert-danger mx-3 mt-3">Failed to load. Please try again.</div>';
    }
}

function _renderMasterList(passengers) {
    const body = document.getElementById('master-list-body');
    const isDark = document.body.classList.contains('dark-mode');
    const cardBg = isDark ? 'rgba(11,15,30,0.85)' : 'rgba(255,255,255,0.7)';
    const cardBorder = isDark ? 'rgba(255,255,255,0.09)' : 'rgba(0,0,0,0.08)';
    const textColor = isDark ? '#f1f5f9' : '#1e293b';

    let html = `
    <div style="padding:4px 20px 20px;">
      <div style="background:rgba(108,99,255,.07);border:1.5px dashed rgba(108,99,255,.3);border-radius:14px;padding:18px;margin-bottom:20px;">
        <div style="font-size:.88rem;font-weight:700;color:#6c63ff;margin-bottom:14px;"><i class="bi bi-person-plus-fill me-2"></i>Add New Passenger</div>
        <div style="display:grid;grid-template-columns:1fr 80px 110px;gap:10px;align-items:end;">
          <div>
            <div style="font-size:.7rem;font-weight:700;color:#64748b;margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px;">Full Name</div>
            <input id="ml-new-name" type="text" placeholder="Enter full name" style="width:100%;padding:9px 12px;border-radius:9px;border:1.5px solid rgba(0,0,0,.12);font-size:.9rem;background:rgba(255,255,255,.97);outline:none;color:#1e293b;">
          </div>
          <div>
            <div style="font-size:.7rem;font-weight:700;color:#64748b;margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px;">Age</div>
            <input id="ml-new-age" type="number" placeholder="Age" min="1" max="120" style="width:100%;padding:9px 10px;border-radius:9px;border:1.5px solid rgba(0,0,0,.12);font-size:.9rem;background:rgba(255,255,255,.97);outline:none;color:#1e293b;">
          </div>
          <div>
            <div style="font-size:.7rem;font-weight:700;color:#64748b;margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px;">Gender</div>
            <select id="ml-new-gender" style="width:100%;padding:9px 10px;border-radius:9px;border:1.5px solid rgba(0,0,0,.12);font-size:.9rem;background:rgba(255,255,255,.97);outline:none;cursor:pointer;color:#1e293b;">
              <option value="">Select</option><option value="Male">Male</option><option value="Female">Female</option><option value="Other">Other</option>
            </select>
          </div>
        </div>
        <button onclick="_mlAddPassenger()" style="margin-top:12px;background:linear-gradient(135deg,#6c63ff,#3b82f6);color:#fff;border:none;border-radius:9px;padding:9px 20px;font-weight:700;font-size:.85rem;cursor:pointer;transition:all .2s;">
          <i class="bi bi-plus-circle me-1"></i>Save Passenger
        </button>
        <div id="ml-add-error" style="display:none;color:#ef4444;font-size:.82rem;margin-top:8px;"></div>
      </div>`;

    if (passengers.length === 0) {
        html += `<div style="text-align:center;padding:28px 20px;color:#94a3b8;"><i class="bi bi-people" style="font-size:2.8rem;display:block;margin-bottom:12px;"></i><div style="font-weight:600;font-size:.95rem;">No passengers saved yet</div><div style="font-size:.82rem;margin-top:4px;">Add frequent travellers above to reuse them during booking</div></div>`;
    } else {
        html += `<div style="font-size:.75rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px;">${passengers.length} Saved Traveller${passengers.length !== 1 ? 's' : ''}</div>`;
        passengers.forEach(p => {
            const initials = p.name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
            const gIcon = p.gender === 'Female' ? 'bi-gender-female' : p.gender === 'Male' ? 'bi-gender-male' : 'bi-gender-ambiguous';
            const gColor = p.gender === 'Female' ? '#f472b6' : p.gender === 'Male' ? '#3b82f6' : '#94a3b8';
            html += `
      <div id="ml-card-${p.id}" style="background:${cardBg};border:1px solid ${cardBorder};border-radius:12px;padding:14px 16px;margin-bottom:10px;display:flex;align-items:center;gap:14px;">
        <div style="width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#6c63ff,#f472b6);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:.95rem;flex-shrink:0;">${initials}</div>
        <div style="flex:1;">
          <div style="font-weight:700;font-size:.95rem;color:${textColor};">${p.name}</div>
          <div style="font-size:.78rem;color:#64748b;margin-top:2px;"><i class="bi ${gIcon}" style="color:${gColor};margin-right:4px;"></i>${p.gender} &middot; ${p.age} yrs</div>
        </div>
        <button onclick="_mlDeletePassenger(${p.id})" title="Remove" style="background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.25);color:#ef4444;border-radius:8px;padding:6px 11px;font-size:.85rem;cursor:pointer;transition:all .2s;">
          <i class="bi bi-trash"></i>
        </button>
      </div>`;
        });
    }
    html += '</div>';
    body.innerHTML = html;
}

async function _mlAddPassenger() {
    const name   = (document.getElementById('ml-new-name')?.value || '').trim();
    const age    = parseInt(document.getElementById('ml-new-age')?.value);
    const gender = document.getElementById('ml-new-gender')?.value;
    const errEl  = document.getElementById('ml-add-error');
    if (!name)                        { errEl.style.display='block'; errEl.textContent='Please enter a full name.'; return; }
    if (!age || age < 1 || age > 120) { errEl.style.display='block'; errEl.textContent='Please enter a valid age (1-120).'; return; }
    if (!gender)                      { errEl.style.display='block'; errEl.textContent='Please select a gender.'; return; }
    errEl.style.display = 'none';
    try {
        await apiRequest('/api/passengers', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ name, age, gender })
        });
        document.getElementById('ml-new-name').value   = '';
        document.getElementById('ml-new-age').value    = '';
        document.getElementById('ml-new-gender').value = '';
        fetchMasterList();
    } catch (err) {
        errEl.style.display = 'block';
        errEl.textContent = err.message || 'Failed to save passenger.';
    }
}

async function _mlDeletePassenger(id) {
    if (!confirm('Remove this passenger from your master list?')) return;
    try {
        await apiRequest(`/api/passengers/${id}`, { method: 'DELETE' });
        fetchMasterList();
    } catch {
        alert('Failed to delete. Please try again.');
    }
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
            <li><a href="#" onclick="openMasterListModal(); return false;"><i class="bi bi-people-fill"></i><span>Passenger Master List</span></a></li>
            <li><a href="#" onclick="openLiveStatusModal(); return false;"><i class="bi bi-geo-alt-fill"></i><span>Live Train Status</span></a></li>
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
            <!-- Tab Bar -->
            <div style="display:flex;border-bottom:1.5px solid rgba(0,0,0,.08);margin:-16px -24px 0;padding:0 24px;">
              <button id="tab-btn-profile" onclick="switchProfileTab('profile')" style="flex:1;padding:14px 0;border:none;background:transparent;font-weight:700;font-size:.82rem;color:#6c63ff;border-bottom:2.5px solid #6c63ff;cursor:pointer;transition:all .2s;letter-spacing:.4px;">
                <i class="bi bi-person-fill me-1"></i>PROFILE
              </button>
              <button id="tab-btn-security" onclick="switchProfileTab('security')" style="flex:1;padding:14px 0;border:none;background:transparent;font-weight:700;font-size:.82rem;color:#94a3b8;border-bottom:2.5px solid transparent;cursor:pointer;transition:all .2s;letter-spacing:.4px;">
                <i class="bi bi-shield-lock-fill me-1"></i>SECURITY
              </button>
            </div>

            <!-- ── PROFILE TAB ── -->
            <div id="profile-tab-pane" style="padding-top:8px;">
              <div class="auth-error" id="profile-error"></div>
              <div class="auth-error" id="profile-success" style="display:none;background:rgba(16,185,129,.1);border-color:rgba(16,185,129,.25);color:#10b981;"></div>

              <!-- Avatar hero -->
              <div style="text-align:center;padding:22px 0 18px;">
                <div style="position:relative;width:92px;height:92px;margin:0 auto;cursor:pointer;" onclick="document.getElementById('profile-pic-upload').click()">
                  <div id="profile-pic-container" style="width:92px;height:92px;border-radius:50%;background:linear-gradient(135deg,#6c63ff22,#f472b622);display:flex;align-items:center;justify-content:center;overflow:hidden;box-shadow:0 0 0 3px #fff,0 0 0 5.5px #6c63ff,0 0 0 8px rgba(108,99,255,.15);">
                    <i class="bi bi-person" style="font-size:2.8rem;color:#6c63ff;"></i>
                  </div>
                  <div style="position:absolute;bottom:0px;right:0px;background:linear-gradient(135deg,#6c63ff,#3b82f6);color:#fff;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(108,99,255,.5);border:2.5px solid #fff;">
                    <i class="bi bi-camera-fill" style="font-size:.75rem;"></i>
                  </div>
                </div>
                <input type="file" id="profile-pic-upload" accept="image/*" style="display:none;" onchange="_handleProfilePicUpload(this)">
                <div id="profile-pic-status" style="font-size:.75rem;margin-top:8px;color:#6b7280;display:none;">Uploading...</div>
                <div id="profile-display-name" style="font-size:1.05rem;font-weight:800;color:#1e293b;margin-top:14px;letter-spacing:-.2px;"></div>
                <div id="profile-display-email" style="font-size:.8rem;color:#94a3b8;margin-top:3px;"></div>
              </div>

              <div style="font-size:.72rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.7px;margin-bottom:5px;"><i class="bi bi-person me-1"></i>Display Name</div>
              <div class="auth-input-wrap">
                <i class="bi bi-person"></i>
                <input id="profile-name-input" class="auth-input" type="text" placeholder="Your Name" oninput="document.getElementById('profile-display-name').textContent=this.value"/>
              </div>
              <div style="font-size:.72rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.7px;margin-bottom:5px;margin-top:14px;"><i class="bi bi-envelope me-1"></i>Email Address</div>
              <div class="auth-input-wrap">
                <i class="bi bi-envelope"></i>
                <input id="profile-email-input" class="auth-input" type="email" disabled style="opacity:0.55;cursor:not-allowed;"/>
              </div>
              <button class="auth-btn" id="save-profile-btn" style="margin-top:18px;" onclick="saveProfileModal()"><i class="bi bi-check2-circle me-1"></i>Save Changes</button>
            </div>

            <!-- ── SECURITY TAB ── -->
            <div id="security-tab-pane" style="display:none;padding-top:8px;">
              <!-- Shield hero -->
              <div style="text-align:center;padding:22px 0 18px;">
                <div style="width:72px;height:72px;border-radius:50%;background:linear-gradient(135deg,#6c63ff,#3b82f6);display:flex;align-items:center;justify-content:center;margin:0 auto;box-shadow:0 8px 24px rgba(108,99,255,.35),0 0 0 8px rgba(108,99,255,.1);">
                  <i class="bi bi-shield-lock-fill" style="font-size:1.9rem;color:#fff;"></i>
                </div>
                <div style="font-size:1rem;font-weight:800;color:#1e293b;margin-top:14px;">Change Password</div>
                <div style="font-size:.8rem;color:#94a3b8;margin-top:3px;">Keep your account secure with a strong password</div>
              </div>

              <div class="auth-error" id="pw-error" style="display:none;"></div>
              <div class="auth-error" id="pw-success" style="display:none;background:rgba(16,185,129,.1);border-color:rgba(16,185,129,.25);color:#10b981;"></div>

              <div style="font-size:.72rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.7px;margin-bottom:5px;"><i class="bi bi-lock me-1"></i>Current Password</div>
              <div class="auth-input-wrap" style="margin-bottom:12px;">
                <i class="bi bi-lock"></i>
                <input id="pw-current" class="auth-input" type="password" placeholder="Enter current password" autocomplete="current-password"/>
              </div>
              <div style="font-size:.72rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.7px;margin-bottom:5px;"><i class="bi bi-lock-fill me-1"></i>New Password</div>
              <div class="auth-input-wrap" style="margin-bottom:12px;">
                <i class="bi bi-lock-fill"></i>
                <input id="pw-new" class="auth-input" type="password" placeholder="At least 6 characters" autocomplete="new-password"/>
              </div>
              <div style="font-size:.72rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.7px;margin-bottom:5px;"><i class="bi bi-lock-fill me-1"></i>Confirm New Password</div>
              <div class="auth-input-wrap">
                <i class="bi bi-lock-fill"></i>
                <input id="pw-confirm" class="auth-input" type="password" placeholder="Re-enter new password" autocomplete="new-password"/>
              </div>
              <button class="auth-btn" id="change-pw-btn" style="margin-top:18px;" onclick="savePasswordChange()"><i class="bi bi-key-fill me-1"></i>Update Password</button>
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

    <!-- LIVE STATUS MODAL -->
    <div class="auth-backdrop" id="live-status-modal-backdrop">
      <div class="auth-modal" role="dialog" aria-modal="true" style="width: min(440px, 94vw);">
        <button class="auth-close" onclick="closeLiveStatusModal()" aria-label="Close">&times;</button>
        <div class="auth-header">
          <div class="auth-header-logo"><i class="bi bi-broadcast"></i> Live Train Status</div>
        </div>
        <div class="auth-body" style="padding:24px 28px 28px;">
          <div class="auth-perks" style="margin-bottom:20px;">
            <div class="auth-perk"><i class="bi bi-geo-alt-fill"></i>Real-time Location</div>
            <div class="auth-perk"><i class="bi bi-clock-fill"></i>Arrival Updates</div>
            <div class="auth-perk"><i class="bi bi-exclamation-triangle-fill"></i>Delay Alerts</div>
          </div>
          <div style="font-size:.78rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;"><i class="bi bi-hash me-1"></i>Train Number</div>
          <div style="position:relative;margin-bottom:14px;">
            <i class="bi bi-train-front-fill" style="position:absolute;left:14px;top:50%;transform:translateY(-50%);color:#6c63ff;font-size:1.1rem;"></i>
            <input id="ls-modal-train-no" type="text" maxlength="5" inputmode="numeric" placeholder="e.g. 12625" autocomplete="off"
              style="width:100%;padding:13px 14px 13px 44px;border-radius:12px;border:1.5px solid rgba(108,99,255,.3);font-size:1rem;font-weight:600;color:#1e293b;background:rgba(255,255,255,.95);outline:none;transition:border-color .2s,box-shadow .2s;"
              onfocus="this.style.borderColor='#6c63ff';this.style.boxShadow='0 0 0 3px rgba(108,99,255,.15)'"
              onblur="this.style.borderColor='rgba(108,99,255,.3)';this.style.boxShadow='none'"
              onkeydown="if(event.key==='Enter') _goLiveStatus()">
          </div>
          <div style="font-size:.78rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;"><i class="bi bi-calendar3 me-1"></i>Journey Started</div>
          <div style="display:flex;gap:10px;margin-bottom:20px;">
            <label style="flex:1;display:flex;align-items:center;gap:10px;background:rgba(108,99,255,.07);border:1.5px solid rgba(108,99,255,.2);border-radius:10px;padding:10px 14px;cursor:pointer;transition:all .2s;">
              <input type="radio" name="ls-day" value="0" checked style="accent-color:#6c63ff;"> <span style="font-size:.9rem;font-weight:600;color:#1e293b;">Today</span>
            </label>
            <label style="flex:1;display:flex;align-items:center;gap:10px;background:rgba(108,99,255,.07);border:1.5px solid rgba(108,99,255,.2);border-radius:10px;padding:10px 14px;cursor:pointer;transition:all .2s;">
              <input type="radio" name="ls-day" value="1" style="accent-color:#6c63ff;"> <span style="font-size:.9rem;font-weight:600;color:#1e293b;">Yesterday</span>
            </label>
          </div>
          <div id="ls-modal-error" style="display:none;color:#ef4444;font-size:.83rem;margin-bottom:12px;"><i class="bi bi-exclamation-circle me-1"></i><span id="ls-modal-err-msg"></span></div>
          <button onclick="_goLiveStatus()" style="width:100%;background:linear-gradient(135deg,#007BFF,#FF69B4);color:#fff;border:none;border-radius:12px;padding:14px;font-weight:700;font-size:1rem;cursor:pointer;transition:all .25s;box-shadow:0 6px 18px rgba(108,99,255,.3);display:flex;align-items:center;justify-content:center;gap:10px;">
            <i class="bi bi-broadcast"></i> Check Live Status
          </button>
        </div>
      </div>
    </div>
    <!-- MASTER LIST MODAL -->
    <div class="auth-backdrop" id="master-list-backdrop">
      <div class="auth-modal" role="dialog" aria-modal="true" style="width: min(600px, 94vw); max-height: 90vh; overflow-y: auto;">
        <button class="auth-close" onclick="closeMasterListModal()" aria-label="Close">&times;</button>
        <div class="auth-header">
          <div class="auth-header-logo"><i class="bi bi-people-fill"></i> Passenger Master List</div>
        </div>
        <div class="auth-body" id="master-list-body" style="padding-top: 10px;">
          <div class="text-center my-4"><div class="spinner-border" style="color:#6c63ff;"></div></div>
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

    // Close master list modal on backdrop click
    const mlbd = document.getElementById('master-list-backdrop');
    mlbd?.addEventListener('click', e => { if (e.target === mlbd) closeMasterListModal(); });

    // Close live status modal on backdrop click
    const lsbd = document.getElementById('live-status-modal-backdrop');
    lsbd?.addEventListener('click', e => { if (e.target === lsbd) closeLiveStatusModal(); });

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
