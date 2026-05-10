import re

def main():
    with open('static/trains.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open('static/index.html', 'r', encoding='utf-8') as f:
        index_content = f.read()

    # --- 1. CSS Background Replacements ---
    # Find trains.html body CSS and replace it
    trains_body_regex = re.compile(r'body\s*\{[^}]*\}', re.MULTILINE)
    index_body_regex = re.compile(r'body\s*\{[^}]*\}', re.MULTILINE)
    
    index_body_match = index_body_regex.search(index_content)
    if index_body_match:
        index_body_css = index_body_match.group(0)
        content = trains_body_regex.sub(index_body_css, content)

    # Extract pseudo elements body::before from index and add it to trains
    index_body_before = re.search(r'body::before\s*\{[^}]*\}', index_content).group(0)
    trains_body_before = re.search(r'body::before\s*\{[^}]*\}', content).group(0)
    content = content.replace(trains_body_before, index_body_before)
    
    # Also grab .bg-pattern and .stars from index.html if possible to be consistent
    # They might not exist in trains.html but are nice to have. Let's just append sidebar CSS first.
    
    # --- 2. Sidebar CSS ---
    # Extract sidebar CSS from index.html
    sidebar_css_start = index_content.find("/* Sidebar */")
    sidebar_css_end = index_content.find("/* Main Content */")
    sidebar_css = index_content[sidebar_css_start:sidebar_css_end]
    
    # Inject sidebar CSS into trains.html before </style>
    if "/* Sidebar */" not in content:
        content = content.replace("</style>", sidebar_css + "\n</style>")

    # Add smooth scroll to date slider
    smooth_scroll_css = """
    .date-slider {
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
    }
    """
    content = content.replace(".date-slider {", smooth_scroll_css + "\n    .date-slider {")

    # --- 3. Sidebar HTML ---
    # Extract sidebar HTML from index.html
    sidebar_html_start = index_content.find("<!-- Sidebar -->")
    sidebar_html_end = index_content.find("<div class=\"main-content\">")
    sidebar_html = index_content[sidebar_html_start:sidebar_html_end]

    # Inject sidebar HTML into trains.html after </header>
    if "<!-- Sidebar -->" not in content:
        content = content.replace("</header>", "</header>\n" + sidebar_html)

    # --- 4. JS Date Slider Fix (AJAX instead of reload) ---
    old_change_date = """function changeDate(newDate) {
        const params = new URLSearchParams(window.location.search);
        params.set('date', newDate);
        window.location.search = params.toString();
    }"""
    
    new_change_date = """function changeDate(newDate) {
        // Update URL silently
        const url = new URL(window.location);
        url.searchParams.set('date', newDate);
        window.history.pushState({}, '', url);
        
        // Fetch new data asynchronously
        fetchTrains();
        
        // Scroll slightly to make sure active element is visible
        setTimeout(() => {
            const activeEl = document.querySelector('.date-item.active');
            if (activeEl) activeEl.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        }, 100);
    }"""
    
    content = content.replace(old_change_date, new_change_date)
    
    # Also ensure getUrlParams parses correctly without reading from cache state
    # Actually getUrlParams reads from window.location.search which is correct since pushState updates it.

    with open('static/trains.html', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("trains.html successfully optimized and fixed.")

if __name__ == '__main__':
    main()
