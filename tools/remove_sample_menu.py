import os
import re

base_path = r"C:\Work\sw\SG200_HMI_FW_ESP32\ESP32_AT\esp-at\web_preview\admin_one"

html_files = ['index.html', 'forms.html', 'profile.html', 'tables.html']

for filename in html_files:
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Remove any div containing Sample Menu - match pattern with any icon structure
    # Match from <div class="navbar-item has-dropdown has-dropdown-with-icons has-divider is-hoverable">
    # until its closing </div> where it contains Sample Menu
    pattern = r'<div class="navbar-item has-dropdown has-dropdown-with-icons has-divider is-hoverable">\s*<a[^>]*>\s*(?:<span[^>]*>\s*)?(?:<i[^>]*></i>\s*)?(?:</span>\s*)?(?:<span[^>]*>\s*)?(?:<i[^>]*></i>\s*)?(?:</span>\s*)?<span>Sample Menu</span>.*?</div>\s*</div>\s*'
    
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filename}")
    else:
        print(f"No changes: {filename}")

print("\nDone!")
