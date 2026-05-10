import os
import re

HEADER_HTML = """
<header class="header-glass">
    <div class="logo-container">
        <div class="menu-toggle" id="menu-toggle">
            <i class="bi bi-list"></i>
        </div>
        <div class="logo" onclick="window.location.href='index.html'" style="cursor:pointer;">
            <i class="bi bi-train-front-fill me-2"></i> RAILGO
        </div>
    </div>
    <nav class="nav-links">
        <a href="index.html">Home</a>
        <a href="#">About</a>
        <a href="trains.html">Trains</a>
        <a href="track-train.html">Tracking</a>
        <a href="signup.html" class="nav-btn">Sign Up</a>
    </nav>
</header>
<!-- Sidebar -->
<div class="sidebar-glass" id="sidebar">
    <button class="sidebar-close" id="sidebar-close">
        <i class="bi bi-x-lg"></i>
    </button>
    <div class="sidebar-header">
        <h3>Menu</h3>
    </div>
    <ul class="sidebar-menu">
        <li><a href="index.html"><i class="bi bi-house-door"></i> <span>Home</span></a></li>
        <li><a href="bookings.html"><i class="bi bi-ticket-perforated-fill"></i> <span>My Bookings</span></a></li>
        <li><a href="pnr.html"><i class="bi bi-search"></i> <span>PNR Enquiry</span></a></li>
        <li><a href="track-train.html"><i class="bi bi-geo-alt"></i> <span>Track Train</span></a></li>
        <li><a href="signup.html"><i class="bi bi-person"></i> <span>Profile</span></a></li>
    </ul>
</div>
<div class="overlay" id="overlay"></div>
"""

COMMON_JS_INJECTION = """
// Inject Header and Sidebar
function injectHeaderAndSidebar() {
    const headerPlaceholder = document.getElementById('universal-header');
    if (headerPlaceholder) {
        headerPlaceholder.innerHTML = `%s`;
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
}

document.addEventListener('DOMContentLoaded', injectHeaderAndSidebar);
""" % (HEADER_HTML.replace('\n', ' ').replace('"', '\\"'))

COMMON_CSS_INJECTION = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

body.app-bg {
    font-family: 'Inter', sans-serif !important;
    background: linear-gradient(rgba(10, 15, 30, 0.7), rgba(10, 15, 30, 0.8)), url('https://images.unsplash.com/photo-1541427468627-a89a96e5ca1d?auto=format&fit=crop&q=80&w=2000') no-repeat center center/cover !important;
    background-attachment: fixed !important;
    color: #fff;
    min-height: 100vh;
    margin: 0;
}

/* Premium Header Glass */
.header-glass {
    position: fixed;
    top: 0; left: 0; width: 100%;
    height: 70px;
    background: rgba(15, 20, 35, 0.6);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 40px;
    z-index: 1000;
}

.header-glass .logo-container {
    display: flex;
    align-items: center;
    gap: 20px;
}

.header-glass .menu-toggle {
    font-size: 1.5rem;
    color: #fff;
    cursor: pointer;
    transition: color 0.3s;
}

.header-glass .menu-toggle:hover {
    color: #0d6efd;
}

.header-glass .logo {
    font-size: 1.5rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: 1px;
}

.header-glass .nav-links {
    display: flex;
    gap: 30px;
    align-items: center;
}

.header-glass .nav-links a {
    color: #ddd;
    text-decoration: none;
    font-size: 0.95rem;
    font-weight: 500;
    transition: color 0.3s;
}

.header-glass .nav-links a:hover {
    color: #fff;
}

.header-glass .nav-btn {
    background: #0d6efd;
    color: #fff !important;
    padding: 8px 20px;
    border-radius: 5px;
    font-weight: 600;
}

.header-glass .nav-btn:hover {
    background: #0b5ed7;
}

/* Premium Sidebar Glass */
.sidebar-glass {
    position: fixed;
    top: 0; left: -320px;
    width: 320px; height: 100vh;
    background: rgba(15, 20, 35, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    z-index: 1001;
    transition: left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    padding-top: 80px;
}

.sidebar-glass.active { left: 0; }

.sidebar-glass .sidebar-header {
    padding: 0 30px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 20px;
}

.sidebar-glass h3 {
    color: #fff;
    font-weight: 600;
    margin: 0;
}

.sidebar-glass .sidebar-close {
    position: absolute;
    top: 20px; right: 20px;
    background: none; border: none;
    color: #fff; font-size: 1.5rem;
    cursor: pointer;
}

.sidebar-glass .sidebar-menu {
    list-style: none; padding: 0; margin: 0;
}

.sidebar-glass .sidebar-menu a {
    display: flex; align-items: center;
    padding: 15px 30px;
    color: #ddd; text-decoration: none;
    font-size: 1rem; transition: 0.3s;
}

.sidebar-glass .sidebar-menu a:hover {
    background: rgba(255,255,255,0.05);
    color: #fff;
    padding-left: 35px;
}

.sidebar-glass .sidebar-menu i {
    font-size: 1.2rem; width: 35px; color: #0d6efd;
}

.overlay {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.6);
    z-index: 1000; opacity: 0; pointer-events: none;
    transition: opacity 0.4s;
    backdrop-filter: blur(3px);
}
.overlay.active { opacity: 1; pointer-events: all; }

/* Booking Engine Form (Horizontal) */
.glass-panel {
    background: rgba(25, 30, 45, 0.7);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
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
    color: #aaa;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 5px;
}

.horizontal-form .form-control {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    color: #fff;
    padding: 12px 15px;
    border-radius: 8px;
}

.horizontal-form .form-control:focus {
    background: rgba(255,255,255,0.1);
    border-color: #0d6efd;
    box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
    color: #fff;
}

.horizontal-form .form-control::placeholder {
    color: #666;
}

.horizontal-form select.form-control {
    appearance: none;
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23fff' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right 15px center;
    background-size: 12px 12px;
}

.horizontal-form select.form-control option {
    background: #191e2d;
    color: #fff;
}

.search-btn-premium {
    background: #0d6efd;
    color: #fff;
    border: none;
    padding: 12px 30px;
    border-radius: 8px;
    font-weight: 600;
    transition: 0.3s;
    height: 49.6px; /* Match input height roughly */
}

.search-btn-premium:hover {
    background: #0b5ed7;
    transform: translateY(-2px);
}
"""

def strip_old_header(content):
    # Try to strip <header>...</header>
    content = re.sub(r'<header[^>]*>.*?</header>', '', content, flags=re.DOTALL)
    # Try to strip <!-- Sidebar --> ... </div> \n <div class="overlay"></div>
    content = re.sub(r'<!-- Sidebar -->.*?(<div class="overlay"[^>]*></div>)', '', content, flags=re.DOTALL)
    content = re.sub(r'<div class="sidebar".*?(<div class="overlay"[^>]*></div>)', '', content, flags=re.DOTALL)
    return content

def process_file(filename):
    path = os.path.join('static', filename)
    if not os.path.exists(path): return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add common.js script tag if missing
    if 'common.js' not in content:
        content = content.replace('</body>', '<script src="common.js"></script>\n</body>')
    
    # 2. Add common.css link if missing
    if 'common.css' not in content:
        content = content.replace('</head>', '<link rel="stylesheet" href="common.css">\n</head>')

    # 3. Strip old headers/sidebars
    content = strip_old_header(content)

    # 4. Inject universal header placeholder
    if '<div id="universal-header"></div>' not in content:
        content = content.replace('<body', '<body') # Find body tag
        # Replace the first opening body tag properly
        body_match = re.search(r'<body[^>]*>', content)
        if body_match:
            body_tag = body_match.group(0)
            if 'app-bg' not in body_tag:
                new_body_tag = body_tag.replace('class="', 'class="app-bg ')
                if new_body_tag == body_tag: # no class attribute
                    new_body_tag = body_tag.replace('>', ' class="app-bg">')
                content = content.replace(body_tag, new_body_tag + '\n    <div id="universal-header"></div>')

    # Specific index.html fixes
    if filename == 'index.html':
        # Remove old styles inside index.html that clash
        content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
        
        # Remove gimmicky HTML
        content = re.sub(r'<div class="bg-pattern"></div>', '', content)
        content = re.sub(r'<div class="stars">.*?</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'<div class="moving-train">.*?</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'<div class="train-icon">.*?</div>', '', content, flags=re.DOTALL)
        
        # Redesign the form wrapper
        old_form_wrapper = re.search(r'<div class="booking-container">.*?</form>', content, flags=re.DOTALL)
        if old_form_wrapper:
            new_form_html = """
            <div class="glass-panel" style="margin-top: 15vh; width: 100%; max-width: 1000px; margin-left: auto; margin-right: auto;">
                <h1 class="mb-4 fw-bold text-white text-center">Where will your next journey take you?</h1>
                <form id="search-form" class="horizontal-form">
                    <div class="form-group">
                        <label class="form-label">From</label>
                        <input type="text" class="form-control" id="source" placeholder="Source Station (e.g., MAS)">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">To</label>
                        <input type="text" class="form-control" id="destination" placeholder="Destination (e.g., NDLS)">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Date</label>
                        <input type="date" class="form-control" id="date">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Class</label>
                        <select class="form-control" id="classType">
                            <option value="">Any</option>
                            <option value="SL">Sleeper (SL)</option>
                            <option value="3A">AC 3 Tier (3A)</option>
                            <option value="2A">AC 2 Tier (2A)</option>
                            <option value="1A">First Class (1A)</option>
                            <option value="CC">Chair Car (CC)</option>
                            <option value="2S">Second Seating (2S)</option>
                        </select>
                    </div>
                    
                    <div class="form-group" style="flex: 0 0 auto;">
                        <button type="button" id="search-button" class="search-btn-premium">Search Trains</button>
                    </div>
                </form>
            </div>
            """
            content = content.replace(old_form_wrapper.group(0), new_form_html)
            
            # Re-inject the JS logic for the search button!
            js_logic = """
            <script>
            document.addEventListener('DOMContentLoaded', () => {
                const searchButton = document.getElementById("search-button");
                if (searchButton) {
                    searchButton.addEventListener("click", () => {
                        const source = document.getElementById("source").value.trim();
                        const destination = document.getElementById("destination").value.trim();
                        
                        if (!source || !destination) {
                            alert("Please enter both source and destination stations.");
                            return;
                        }
                        
                        let date = document.getElementById("date").value;
                        if (!date) {
                            date = new Date().toISOString().split('T')[0];
                        }
                        
                        let classType = document.getElementById("classType").value;
                        let url = `trains.html?source=${encodeURIComponent(source)}&destination=${encodeURIComponent(destination)}&date=${encodeURIComponent(date)}`;
                        if (classType) url += `&classType=${encodeURIComponent(classType)}`;
                        
                        window.location.href = url;
                    });
                }
            });
            </script>
            """
            # Clean up old script tags
            content = re.sub(r'<script>.*?</script>', '', content, flags=re.DOTALL)
            content = content.replace('</body>', js_logic + '\n<script src="common.js"></script>\n</body>')
    
    elif filename == 'trains.html':
        # Clean up trains.html padding for the new header
        content = content.replace('margin-top: 100px;', 'margin-top: 100px;') # Ensure margin
        content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL) # let common.css handle it
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    # 1. Update common.js
    with open('static/common.js', 'a', encoding='utf-8') as f:
        f.write("\n" + COMMON_JS_INJECTION)
        
    # 2. Update common.css
    with open('static/common.css', 'w', encoding='utf-8') as f:
        f.write(COMMON_CSS_INJECTION)
        
    # 3. Process HTML files
    for file in ['index.html', 'trains.html', 'signup.html', 'login.html']:
        process_file(file)

    print("Complete Redesign applied successfully.")

if __name__ == '__main__':
    main()
