import os
import re

def main():
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    
    # Write common.css
    common_css_content = """/* Common UI Elements */
.light-mode {
  color: #000;
}

.dark-mode {
  color: #fff;
}

.theme-text {
  transition: color 0.3s ease-in-out;
}

.light-mode .theme-text {
  color: #000 !important;
}

.dark-mode .theme-text {
  color: #fff !important;
}
"""
    with open(os.path.join(base_dir, 'common.css'), 'w', encoding='utf-8') as f:
        f.write(common_css_content)

    target_files = [
        'index.html', 'book.html', 'bookings.html', 'confirmation.html',
        'login.html', 'pnr.html', 'signup.html',
        'track-train.html', 'trains.html'
    ]
    
    for filename in target_files:
        file_path = os.path.join(base_dir, filename)
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Inject <link rel="stylesheet" href="common.css"> before </head>
        if 'href="common.css"' not in content:
            content = content.replace('</head>', '  <link rel="stylesheet" href="common.css">\n</head>')
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    print("CSS sync complete.")

if __name__ == "__main__":
    main()
