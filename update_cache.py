import os
import glob

for filepath in glob.glob('static/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace("common.js?v=3", "common.js?v=4")
    content = content.replace("common.js?v=2", "common.js?v=4")
    content = content.replace("common.js?v=1", "common.js?v=4")
    content = content.replace('"common.js"', '"common.js?v=4"')
    content = content.replace("'common.js'", "'common.js?v=4'")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
print("Done updating common.js version.")
