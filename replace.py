import os

static_dir = os.path.join(os.path.dirname(__file__), 'static')

for file in os.listdir(static_dir):
    if file.endswith('.html'):
        file_path = os.path.join(static_dir, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace placeholder background images
        content = content.replace('/api/placeholder/1920/1080', '/bg.png')
        content = content.replace('/api/placeholder/60/60', '/favicon.png')
        
        # Replace old Spring Boot port with FastAPI port
        content = content.replace('http://localhost:1301', 'http://localhost:8000')
        
        # Add favicon meta tag if it doesn't exist
        if '<head>' in content and 'favicon' not in content.lower():
            content = content.replace('<head>', '<head>\n    <link rel="icon" type="image/x-icon" href="/favicon.ico">')
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

print("Replacement complete.")
