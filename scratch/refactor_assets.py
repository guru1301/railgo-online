import os
import re

def main():
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    
    # 1. Write common.js
    common_js_content = """// Common JS for Theme and Sidebar
const themeToggle = document.getElementById("theme-toggle");
const themeText = document.getElementById("theme-text");

function setTheme(theme) {
  document.body.classList.toggle("dark-mode", theme === "dark");
  document.body.classList.toggle("light-mode", theme === "light");
  if (themeToggle) {
    themeToggle.checked = theme === "dark";
  }
  if (themeText) {
    themeText.textContent = theme === "dark" ? "☀️" : "🌙";
  }
  
  const themeTextElements = document.querySelectorAll('.theme-text');
  if (themeTextElements.length > 0) {
    themeTextElements.forEach(el => {
      el.style.color = theme === "dark" ? "#fff" : "#000";
    });
  }
  
  const train = document.querySelector('.train');
  if (train) {
    train.style.backgroundColor = theme === "dark" ? "#333" : "#030000";
  }
  
  localStorage.setItem("theme", theme);
}

if (themeToggle) {
  themeToggle.addEventListener("change", () => {
    setTheme(themeToggle.checked ? "dark" : "light");
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem("theme") || "light";
  setTheme(savedTheme);
});

// Sidebar Functionality
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
"""
    with open(os.path.join(base_dir, 'common.js'), 'w', encoding='utf-8') as f:
        f.write(common_js_content)

    # 2. Process HTML files to link common.js
    # We will use simple string replacement to remove the duplicated JS blocks
    # and insert the script tag.
    
    target_files = [
        'index.html', 'book.html', 'bookings.html', 'confirmation.html',
        'login.html', 'pnr.html', 'signup.html',
        'track-train.html', 'trains.html'
    ]
    
    # Regex to match the theme toggle block
    theme_pattern = re.compile(r'// Theme Toggle Functionality.*?localStorage\.setItem\("theme", theme\);\s*}\s*themeToggle\.addEventListener\("change", \(\) => {\s*setTheme\(themeToggle\.checked \? "dark" : "light"\);\s*}\);\s*(?:// Check local storage for theme\s*const savedTheme = localStorage\.getItem\("theme"\) \|\| "light";\s*setTheme\(savedTheme\);)?', re.DOTALL)
    
    # Regex to match the sidebar block
    sidebar_pattern = re.compile(r'// Sidebar Functionality.*?if \(overlay\) overlay\.addEventListener\(\'click\', closeSidebar\);', re.DOTALL)
    
    for filename in target_files:
        file_path = os.path.join(base_dir, filename)
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Remove theme and sidebar logic
        content = theme_pattern.sub('', content)
        content = sidebar_pattern.sub('', content)
        
        # Inject <script src="common.js"></script> before </body>
        if 'src="common.js"' not in content:
            content = content.replace('</body>', '<script src="common.js"></script>\n</body>')
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    print("JS sync complete.")

if __name__ == "__main__":
    main()
