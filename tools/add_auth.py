import os
import re

base_path = r"C:\Work\sw\SG200_HMI_FW_ESP32\ESP32_AT\esp-at\web_preview\admin_one"

# Pages that need authentication (not login.html)
html_files = ['index.html', 'forms.html', 'profile.html', 'tables.html', 'about.html']

for filename in html_files:
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Check if auth.js is already included
    if 'js/auth.js' in content:
        print(f"Already has auth: {filename}")
        continue
    
    # Add auth.js script right after <head> tag - it should be first to check auth immediately
    # Add it in the <head> section for early execution
    content = content.replace(
        '<link rel="stylesheet" href="css/main.min.css">',
        '<script src="js/auth.js"></script>\n  <link rel="stylesheet" href="css/main.min.css">'
    )
    
    # Update logout button to call logout() function
    content = content.replace(
        '<a title="Log out" class="navbar-item is-desktop-icon-only">',
        '<a title="Log out" class="navbar-item is-desktop-icon-only" onclick="logout(); return false;" href="#">'
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filename}")
    else:
        print(f"No changes: {filename}")

print("\nDone!")
