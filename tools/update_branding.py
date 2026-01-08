import os
import re

# Configuration
FILES_TO_UPDATE = [
    'web_preview/admin_one/index.html',
    'web_preview/admin_one/settings.html',
    'web_preview/admin_one/about.html',
    'web_preview/admin_one/update.html'
]

BASE_DIR = r'c:\Work\sw\SG200_HMI_FW_ESP32\ESP32_AT\esp-at'

# Content to find and replace
TARGET_DIV = '<div class="aside-tools-label">'
NEW_CONTENT = '<div class="aside-tools-label">\n        <img src="img/tay.svg" alt="Taytech" style="max-height: 24px; margin-right: 0.5rem; vertical-align: middle;">'

def update_file(filepath):
    full_path = os.path.join(BASE_DIR, filepath)
    if not os.path.exists(full_path):
        print(f"Skipping {filepath} (not found)")
        return

    print(f"Updating {filepath}...")
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Simple string replacement as the target is unique and consistent
    if 'img/tay.svg' in content:
        print(f"Logo already present in {filepath}")
        return

    # Using regex to find the specific block to avoid messing up if spacing varies slightly
    # But since I generated these files or they are standard, simple replace might work.
    # Let's use simple replace for the opening tag, assuming standard formatting.
    
    if TARGET_DIV in content:
        new_content = content.replace(TARGET_DIV, NEW_CONTENT)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated branding in {filepath}")
    else:
        print(f"Target div not found in {filepath}")

if __name__ == '__main__':
    for f in FILES_TO_UPDATE:
        update_file(f)
