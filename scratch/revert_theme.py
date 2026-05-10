def main():
    css = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

body.app-bg {
    font-family: 'Poppins', sans-serif !important;
    background: linear-gradient(rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.4)), url('upscalemedia-transformed.png') no-repeat center center/cover !important;
    background-attachment: fixed !important;
    color: #333;
    min-height: 100vh;
    margin: 0;
    transition: background 0.3s ease-in-out, color 0.3s ease-in-out;
}

body.app-bg.dark-mode {
    background: linear-gradient(rgba(8, 25, 55, 0.8), rgba(0, 17, 34, 0.9)), url('upscalemedia-transformed.png') no-repeat center center/cover !important;
    color: #fff;
}

body.app-bg.light-mode {
    background: linear-gradient(rgba(255, 255, 255, 0.5), rgba(240, 244, 255, 0.8)), url('upscalemedia-transformed.png') no-repeat center center/cover !important;
    color: #000;
}

/* Original Header Restored */
.header {
    width: 100%;
    background: linear-gradient(135deg, #081937, #001122);
    padding: 15px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
    color: white;
    box-shadow: 0 2px 15px rgba(0, 0, 0, 0.3);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-container {
    display: flex;
    align-items: center;
    gap: 20px;
}

.menu-toggle {
    cursor: pointer;
    font-size: 1.8rem;
    color: white;
    transition: color 0.3s ease;
}

.menu-toggle:hover {
    color: #FF69B4;
}

.logo {
    font-size: 1.8rem;
    font-weight: bold;
    background: linear-gradient(45deg, #FF69B4, #fff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
}

.logo i {
    font-size: 2rem;
    margin-right: 5px;
    filter: drop-shadow(0 0 2px rgba(255, 105, 180, 0.7));
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 20px;
}

.nav-links a {
    color: white;
    text-decoration: none;
    font-weight: 600;
    margin-left: 20px;
    transition: color 0.3s ease-in-out;
    position: relative;
    padding: 5px 0;
}

.nav-links a::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 0;
    height: 2px;
    background: #FF69B4;
    transition: width 0.3s ease;
}

.nav-links a:hover::after {
    width: 100%;
}

.nav-links a:hover {
    color: #FF69B4;
}

.theme-toggle-container {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 5px 10px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 20px;
}

.theme-switch {
    position: relative;
    display: inline-block;
    width: 40px;
    height: 20px;
}

.theme-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0; left: 0; right: 0; bottom: 0;
    background-color: #ccc;
    transition: 0.4s;
    border-radius: 34px;
}

.slider:before {
    position: absolute;
    content: "";
    height: 14px; width: 14px;
    left: 3px; bottom: 3px;
    background-color: white;
    transition: 0.4s;
    border-radius: 50%;
}

input:checked + .slider {
    background-color: #FF69B4;
}

input:checked + .slider:before {
    transform: translateX(18px);
}

/* Original Sidebar Restored */
.sidebar {
    position: fixed;
    top: 0; left: -300px;
    width: 300px; height: 100vh;
    background: linear-gradient(135deg, #081937, #001122);
    color: white;
    z-index: 1001;
    transition: left 0.3s ease-in-out, background 0.3s ease-in-out;
    padding-top: 80px;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.2);
    overflow-y: auto;
}

.dark-mode .sidebar {
    background: linear-gradient(135deg, #081937, #001122);
    color: white;
}

.light-mode .sidebar {
    background: linear-gradient(135deg, #f0f4ff, #d8e1fb);
    color: #333;
}

.sidebar.active {
    left: 0;
}

.sidebar-header {
    padding: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    text-align: center;
    margin-bottom: 20px;
}

.light-mode .sidebar-header {
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.sidebar-header h3 {
    font-size: 1.5rem;
    background: linear-gradient(45deg, #FF69B4, #fff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sidebar-menu {
    list-style: none; padding: 0; margin: 0;
}

.sidebar-menu li {
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.light-mode .sidebar-menu li {
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.sidebar-menu a {
    color: white;
    text-decoration: none;
    padding: 15px 20px;
    display: flex;
    align-items: center;
    gap: 15px;
    transition: all 0.3s;
}

.light-mode .sidebar-menu a {
    color: #333;
}

.sidebar-menu a:hover {
    background: rgba(255, 105, 180, 0.15);
    color: #FF69B4;
    padding-left: 25px;
}

.light-mode .sidebar-menu a:hover {
    background: rgba(0, 123, 255, 0.15);
    color: #007BFF;
}

.sidebar-menu i {
    font-size: 1.3rem;
    width: 30px;
    text-align: center;
}

.sidebar-close {
    position: absolute;
    top: 20px; right: 20px;
    background: transparent; border: none;
    color: white; font-size: 1.5rem;
    cursor: pointer; transition: color 0.3s;
}

.light-mode .sidebar-close {
    color: #333;
}

.sidebar-close:hover {
    color: #FF69B4;
}

.light-mode .sidebar-close:hover {
    color: #007BFF;
}

.overlay {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.6);
    z-index: 1000; opacity: 0; pointer-events: none;
    transition: opacity 0.4s;
    backdrop-filter: blur(3px);
}
.overlay.active { opacity: 1; pointer-events: all; }

/* Booking Engine Form (Horizontal) with User requested UI colours */
.glass-panel {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 15px 45px rgba(0, 0, 0, 0.25);
    position: relative;
    overflow: hidden;
}
.glass-panel::before {
    content: '';
    position: absolute;
    top: -50px; left: -50px;
    width: 100px; height: 100px;
    background: linear-gradient(45deg, #FF69B4, #007BFF);
    border-radius: 50%; opacity: 0.3; z-index: -1;
    animation: float 8s infinite alternate ease-in-out;
}
.glass-panel::after {
    content: '';
    position: absolute;
    bottom: -50px; right: -50px;
    width: 120px; height: 120px;
    background: linear-gradient(45deg, #007BFF, #FF69B4);
    border-radius: 50%; opacity: 0.3; z-index: -1;
    animation: float 10s infinite alternate-reverse ease-in-out;
}

.dark-mode .glass-panel {
    background: rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes float {
    0% { transform: translate(0, 0); }
    50% { transform: translate(20px, 20px); }
    100% { transform: translate(-20px, 20px); }
}

.horizontal-form {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    align-items: flex-end;
}

.horizontal-form .form-group {
    flex: 1;
    min-width: 150px;
}

.horizontal-form .form-label {
    color: #333;
    font-size: 0.95rem;
    font-weight: 600;
    margin-bottom: 5px;
    text-shadow: 0 1px 2px rgba(255,255,255,0.5);
}

.dark-mode .horizontal-form .form-label {
    color: #fff;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

.horizontal-form .form-control {
    background: rgba(255,255,255,0.9);
    border: 1px solid rgba(204,204,204,0.5);
    color: #333;
    padding: 12px 15px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.dark-mode .horizontal-form .form-control {
    background: rgba(34, 34, 34, 0.9);
    border: 1px solid rgba(85, 85, 85, 0.5);
    color: #fff;
}

.horizontal-form .form-control:focus {
    background: #fff;
    border-color: #007BFF;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.2), 0 5px 15px rgba(0, 0, 0, 0.1);
    color: #333;
}

.dark-mode .horizontal-form .form-control:focus {
    background: #222;
    border-color: #FF69B4;
    box-shadow: 0 0 0 3px rgba(255, 105, 180, 0.2), 0 5px 15px rgba(0, 0, 0, 0.3);
    color: #fff;
}

.horizontal-form select.form-control {
    appearance: none;
    background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%23333' class='bi bi-chevron-down' viewBox='0 0 16 16'%3e%3cpath fill-rule='evenodd' d='M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z'/%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right 15px center;
    background-size: 16px;
}

.dark-mode .horizontal-form select.form-control {
    background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%23fff' class='bi bi-chevron-down' viewBox='0 0 16 16'%3e%3cpath fill-rule='evenodd' d='M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z'/%3e%3c/svg%3e");
}

.search-btn-premium {
    background: linear-gradient(45deg, #007BFF, #FF69B4);
    color: #fff;
    border: none;
    padding: 12px 30px;
    border-radius: 8px;
    font-weight: 600;
    transition: 0.3s;
    height: 49.6px;
    box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
}

.search-btn-premium:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 123, 255, 0.5);
}

/* Specific Trains.html Styles */
.class-card {
    min-width: 140px;
    background-color: rgba(255, 255, 255, 0.7);
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid #ccc;
}
.dark-mode .class-card {
    background-color: rgba(0, 0, 0, 0.3);
    border-color: #555;
}
.class-card:hover {
    border-color: #0d6efd;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(13, 110, 253, 0.2);
}
.class-card.available {
    background-color: rgba(40, 167, 69, 0.1);
    border-color: rgba(40, 167, 69, 0.5);
}
.class-card.unavailable {
    background-color: rgba(220, 53, 69, 0.1);
    border-color: rgba(220, 53, 69, 0.3);
}
.banner-fcf {
    background: linear-gradient(90deg, #0f9b0f, #28a745, #34ce57);
    border-radius: 8px;
}
.date-slider-container {
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(15px);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 0 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}
.dark-mode .date-slider-container {
    background: rgba(0, 0, 0, 0.5);
    border-color: rgba(255,255,255,0.1);
}
.date-slider {
    display: flex;
    overflow-x: auto;
    flex-grow: 1;
    scrollbar-width: none;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
}
.date-slider::-webkit-scrollbar {
    display: none;
}
.date-item {
    min-width: 100px;
    text-align: center;
    padding: 10px 5px;
    cursor: pointer;
    border-bottom: 3px solid transparent;
    color: #555;
    transition: 0.3s;
}
.dark-mode .date-item { color: #ccc; }
.date-item:hover {
    background-color: rgba(255,255,255,0.4);
}
.dark-mode .date-item:hover { background-color: rgba(0,0,0,0.2); }
.date-item.active {
    border-bottom: 3px solid #28a745;
    color: #28a745;
    font-weight: bold;
}
.train-main-card {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(15px);
    border-radius: 15px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    position: relative;
    overflow: hidden;
}
.train-main-card::before {
    content: '';
    position: absolute;
    top: -30px; left: -30px;
    width: 80px; height: 80px;
    background: linear-gradient(45deg, #FF69B4, #007BFF);
    border-radius: 50%; opacity: 0.1; z-index: -1;
}
.dark-mode .train-main-card {
    background: rgba(0, 0, 0, 0.5);
    border-color: rgba(255, 255, 255, 0.1);
}
.train-card-title {
    font-size: 1.2rem;
    font-weight: bold;
    color: #333;
}
.dark-mode .train-card-title { color: #fff; }
.class-cards-container {
    padding-bottom: 10px;
}
.class-cards-container::-webkit-scrollbar {
    height: 6px;
}
.class-cards-container::-webkit-scrollbar-thumb {
    background-color: #555;
    border-radius: 10px;
}
.availability-text {
    font-size: 0.85rem;
}
.theme-text {
    color: #333;
}
.dark-mode .theme-text { color: #fff !important; }

.main-content {
    margin-top: 100px;
    padding: 20px 5%;
}
"""
    js = """
// Original Theme logic and injection
function setTheme(themeName) {
    localStorage.setItem('theme', themeName);
    document.body.classList.remove('light-mode', 'dark-mode');
    document.body.classList.add(themeName + '-mode');
    
    const themeCheckbox = document.getElementById('theme-toggle');
    if (themeCheckbox) {
        themeCheckbox.checked = themeName === 'dark';
    }
}

function toggleTheme() {
    if (localStorage.getItem('theme') === 'dark') {
        setTheme('light');
    } else {
        setTheme('dark');
    }
}

function injectHeaderAndSidebar() {
    const headerHTML = `
    <header class="header">
        <div class="logo-container">
            <div class="menu-toggle" id="menu-toggle">
                <i class="bi bi-list"></i>
            </div>
            <div class="logo" onclick="window.location.href='index.html'">
                <i class="bi bi-train-front-fill"></i> RailGo
            </div>
        </div>
        <nav class="nav-links">
            <a href="index.html">Home</a>
            <a href="#">About</a>
            <a href="#">Contact</a>
            <a href="signup.html">Sign Up</a>
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
        <div class="sidebar-header">
            <h3>RailGo Menu</h3>
        </div>
        <ul class="sidebar-menu">
            <li><a href="#"><i class="bi bi-ticket-perforated-fill"></i><span>My Bookings</span></a></li>
            <li><a href="#"><i class="bi bi-search"></i><span>PNR Enquiry</span></a></li>
            <li><a href="#"><i class="bi bi-clock-history"></i><span>Last Transactions</span></a></li>
            <li><a href="#"><i class="bi bi-calendar-check"></i><span>Upcoming Journey</span></a></li>
            <li><a href="#"><i class="bi bi-x-circle"></i><span>Cancel Ticket</span></a></li>
            <li><a href="track-train.html"><i class="bi bi-geo-alt"></i><span>Track Your Train</span></a></li>
            <li><a href="#"><i class="bi bi-person"></i><span>My Profile</span></a></li>
            <li><a href="#"><i class="bi bi-question-circle"></i><span>Help & Support</span></a></li>
        </ul>
    </div>
    <div class="overlay" id="overlay"></div>
    `;

    const placeholder = document.getElementById('universal-header');
    if (placeholder) {
        placeholder.innerHTML = headerHTML;
    }

    // Attach Sidebar Functionality
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const sidebarClose = document.getElementById('sidebar-close');

    function openSidebar() {
        if (sidebar) sidebar.classList.add('active');
        if (overlay) overlay.classList.add('active');
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
    }

    if (menuToggle) menuToggle.addEventListener('click', openSidebar);
    if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
    if (overlay) overlay.addEventListener('click', closeSidebar);

    // Attach Theme Toggle Logic
    const themeCheckbox = document.getElementById('theme-toggle');
    if (themeCheckbox) {
        themeCheckbox.addEventListener('change', toggleTheme);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Initial Setup
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    injectHeaderAndSidebar();
});
"""
    with open('static/common.css', 'w', encoding='utf-8') as f:
        f.write(css)
    with open('static/common.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Reverted completely to user's desired hybrid state.")

if __name__ == '__main__':
    main()
