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
    
    # 1. Remove GitHub menu item from sidebar
    # <li><a href="https://github.com/..." class="has-icon">...<span class="menu-item-label">GitHub</span></a></li>
    content = re.sub(
        r'<li>\s*<a[^>]*href="https://github\.com/vikdiesel[^"]*"[^>]*class="has-icon"[^>]*>.*?GitHub.*?</a>\s*</li>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 2. Remove GitHub button from top-right (in title bar section)
    # <a href="https://github.com/..." class="button is-primary">...<span>GitHub</span></a>
    content = re.sub(
        r'<a[^>]*href="https://github\.com/vikdiesel[^"]*"[^>]*class="button is-primary"[^>]*>.*?</a>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 3. Change "Admin One HTML" to "SG200 FPC"
    content = content.replace('<b>Admin</b> One HTML', '<b>SG200</b> FPC')
    content = content.replace('Admin One HTML', 'SG200 FPC')
    
    # 4. Update page title
    content = re.sub(r'<title>.*?</title>', '<title>SG200 FPC Dashboard</title>', content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filename}")
    else:
        print(f"No changes: {filename}")

# Update CSS for sidebar background color
css_path = os.path.join(base_path, 'css', 'main.min.css')
if os.path.exists(css_path):
    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()
    
    # The sidebar uses .aside class - change its background
    # Original color is usually #1e1e2d or similar dark color
    # Add custom override at the end
    
    custom_css = """
/* Custom SG200 FPC Branding */
.aside { background-color: #474C80 !important; }
.aside-tools { background-color: #3a3f6a !important; }
"""
    
    if '/* Custom SG200 FPC Branding */' not in css:
        css += custom_css
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css)
        print("Updated: main.min.css (sidebar color)")

print("\nDone!")
