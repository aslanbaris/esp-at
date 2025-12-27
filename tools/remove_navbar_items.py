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
    
    # 1. Remove Search control (navbar-item with control and input for search)
    content = re.sub(
        r'<div class="navbar-item has-control">\s*<div class="control">.*?</div>\s*</div>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 2. Remove Sample Menu dropdown
    content = re.sub(
        r'<div class="navbar-item has-dropdown has-dropdown-with-icons has-divider is-hoverable">\s*<a class="navbar-link">\s*<span class="icon"><i class="mdi mdi-menu"></i></span>\s*<span>Sample Menu</span>.*?</div>\s*</div>',
        '',
        content,
        flags=re.DOTALL
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filename}")
    else:
        print(f"No changes: {filename}")

print("\nDone!")
