import os
import re

base_path = r"C:\Work\sw\SG200_HMI_FW_ESP32\ESP32_AT\esp-at\web_preview\admin_one"

html_files = ['index.html', 'forms.html', 'profile.html', 'tables.html', 'about.html']

for filename in html_files:
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Remove the About link from top navbar (the help-circle-outline icon)
    # Pattern: <a href="about.html" title="About" class="navbar-item has-divider is-desktop-icon-only">...</a>
    content = re.sub(
        r'<a href="about\.html" title="About" class="navbar-item has-divider is-desktop-icon-only">.*?</a>\s*',
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
