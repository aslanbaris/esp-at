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

# New Sidebar Template (with placeholder for active class)
SIDEBAR_TEMPLATE = """<div class="menu is-menu-main">
      <ul class="menu-list">
        <li>
          <a href="index.html" class="{index_active}has-icon">
            <span class="icon"><i class="mdi mdi-desktop-mac"></i></span>
            <span class="menu-item-label">Dashboard</span>
          </a>
        </li>
        <li>
          <a href="settings.html" class="{settings_active}has-icon">
            <span class="icon"><i class="mdi mdi-settings"></i></span>
            <span class="menu-item-label">Settings</span>
          </a>
        </li>
        <li>
          <a href="update.html" class="{update_active}has-icon">
            <span class="icon"><i class="mdi mdi-upload"></i></span>
            <span class="menu-item-label">Update</span>
          </a>
        </li>
        <li>
          <a href="about.html" class="{about_active}has-icon">
            <span class="icon"><i class="mdi mdi-help-circle"></i></span>
            <span class="menu-item-label">About</span>
          </a>
        </li>
      </ul>
    </div>"""

def update_file(filepath):
    full_path = os.path.join(BASE_DIR, filepath)
    if not os.path.exists(full_path):
        print(f"Skipping {filepath} (not found)")
        return

    print(f"Updating {filepath}...")
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Determine active page
    filename = os.path.basename(filepath)
    context = {
        'index_active': 'is-active ' if filename == 'index.html' else '',
        'settings_active': 'is-active ' if filename == 'settings.html' else '',
        'update_active': 'is-active ' if filename == 'update.html' else '',
        'about_active': 'is-active ' if filename == 'about.html' else '',
    }

    new_sidebar = SIDEBAR_TEMPLATE.format(**context)

    # Regex to replace the menu div
    # Matches <div class="menu is-menu-main"> ... </div> (non-greedy)
    # We use DOTALL to match newlines
    pattern = re.compile(r'<div class="menu is-menu-main">.*?</div>', re.DOTALL)
    
    if pattern.search(content):
        new_content = pattern.sub(new_sidebar, content)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated sidebar in {filepath}")
    else:
        print(f"Sidebar container not found in {filepath}")

if __name__ == '__main__':
    for f in FILES_TO_UPDATE:
        update_file(f)
