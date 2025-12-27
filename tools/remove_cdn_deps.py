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
    
    # 1. Remove Chart.js CDN script
    content = re.sub(r'<script[^>]*src="https://cdnjs\.cloudflare\.com/ajax/libs/Chart\.js[^"]*"[^>]*></script>\s*', '', content)
    
    # 2. Remove chart.sample.min.js
    content = re.sub(r'<script[^>]*src="js/chart\.sample\.min\.js"[^>]*></script>\s*', '', content)
    
    # 3. Remove the entire chart card (Performance card with canvas)
    # Match from <div class="card"> containing Performance chart to its closing </div>
    content = re.sub(
        r'<div class="card">\s*<header class="card-header">\s*<p class="card-header-title">\s*<span class="icon"><i class="mdi mdi-finance"></i></span>\s*Performance\s*</p>.*?</div>\s*</div>\s*</div>\s*(?=<div class="card has-table)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 4. Replace avatar images with CSS initials circle
    # Pattern: <img src="https://avatars.dicebear.com/v2/initials/NAME.svg" class="is-rounded">
    def replace_avatar(match):
        return '<span class="avatar-initials" style="display:inline-flex;width:32px;height:32px;border-radius:50%;background:#00d1b2;color:white;font-size:14px;font-weight:bold;align-items:center;justify-content:center;">--</span>'
    
    content = re.sub(
        r'<img src="https://avatars\.dicebear\.com/[^"]*"[^>]*>',
        replace_avatar,
        content
    )
    
    # 5. Remove John Doe avatar in navbar
    content = re.sub(
        r'<img src="https://avatars\.dicebear\.com/[^"]*" alt="[^"]*">',
        '<span style="display:inline-flex;width:32px;height:32px;border-radius:50%;background:#00d1b2;color:white;font-size:12px;font-weight:bold;align-items:center;justify-content:center;">JD</span>',
        content
    )
    
    # 6. Remove footer external images (shields.io badge)
    content = re.sub(r'<a[^>]*href="https://github\.com/vikdiesel[^"]*"[^>]*>\s*<img src="https://img\.shields\.io/[^"]*"[^>]*>\s*</a>', '', content)
    
    # 7. Remove JustBoil.me logo reference  
    content = re.sub(r'<a[^>]*href="https://justboil\.me"[^>]*>.*?</a>', '', content, flags=re.DOTALL)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filename}")
    else:
        print(f"No changes: {filename}")

print("\nDone!")
