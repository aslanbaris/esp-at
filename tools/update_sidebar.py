import os
import re

base_path = r"C:\Work\sw\SG200_HMI_FW_ESP32\ESP32_AT\esp-at\web_preview\admin_one"

# Files to update sidebar menu
html_files = ['index.html', 'settings.html', 'about.html']

# New simplified sidebar menu structure (without labels, without Forms/Profile)
new_sidebar_menu = '''    <div class="menu is-menu-main">
      <ul class="menu-list">
        <li>
          <a href="index.html" class="DASHBOARD_ACTIVE has-icon">
            <span class="icon"><i class="mdi mdi-desktop-mac"></i></span>
            <span class="menu-item-label">Dashboard</span>
          </a>
        </li>
        <li>
          <a href="settings.html" class="SETTINGS_ACTIVE has-icon">
            <span class="icon"><i class="mdi mdi-cog"></i></span>
            <span class="menu-item-label">Settings</span>
          </a>
        </li>
        <li>
          <a href="about.html" class="ABOUT_ACTIVE has-icon">
            <span class="icon"><i class="mdi mdi-help-circle"></i></span>
            <span class="menu-item-label">About</span>
          </a>
        </li>
      </ul>
    </div>'''

for filename in html_files:
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        print(f"Not found: {filename}")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Determine which page is active
    if filename == 'index.html':
        active_marker = new_sidebar_menu.replace('DASHBOARD_ACTIVE ', 'is-active ').replace('SETTINGS_ACTIVE ', '').replace('ABOUT_ACTIVE ', '')
    elif filename == 'settings.html':
        active_marker = new_sidebar_menu.replace('DASHBOARD_ACTIVE ', '').replace('SETTINGS_ACTIVE ', 'is-active ').replace('ABOUT_ACTIVE ', '')
    elif filename == 'about.html':
        active_marker = new_sidebar_menu.replace('DASHBOARD_ACTIVE ', '').replace('SETTINGS_ACTIVE ', '').replace('ABOUT_ACTIVE ', 'is-active ')
    else:
        active_marker = new_sidebar_menu.replace('DASHBOARD_ACTIVE ', '').replace('SETTINGS_ACTIVE ', '').replace('ABOUT_ACTIVE ', '')
    
    # Replace the entire menu section
    # Pattern to match from <div class="menu is-menu-main"> to </div> (closing of menu)
    pattern = r'<div class="menu is-menu-main">.*?</div>\s*</aside>'
    replacement = active_marker + '\n  </aside>'
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Also update tables.html references to settings.html
    content = content.replace('tables.html', 'settings.html')
    content = content.replace('Tables', 'Settings')
    content = content.replace('Responsive Settings', 'Settings')  # Fix over-replacement
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filename}")
    else:
        print(f"No changes: {filename}")

# Now update settings.html page title
settings_path = os.path.join(base_path, 'settings.html')
if os.path.exists(settings_path):
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the hero title
    content = re.sub(r'<h1 class="title">\s*Responsive Settings\s*</h1>', '<h1 class="title">Settings</h1>', content)
    content = re.sub(r'<h1 class="title">\s*Settings\s*</h1>', '<h1 class="title">Settings</h1>', content)
    
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated settings.html title")

print("\nDone!")
