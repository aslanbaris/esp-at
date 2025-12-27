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
    
    # Replace external About link in sidebar
    content = re.sub(
        r'<a href="https://justboil\.me/[^"]*" class="has-icon">',
        '<a href="about.html" class="has-icon">',
        content
    )
    
    # Replace external About link in navbar
    content = re.sub(
        r'<a href="https://justboil\.me/[^"]*" title="About"',
        '<a href="about.html" title="About"',
        content
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filename}")
    else:
        print(f"No changes: {filename}")

print("\nDone!")
