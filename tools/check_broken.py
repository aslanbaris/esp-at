import os
import re

base_path = r"C:\Work\sw\SG200_HMI_FW_ESP32\ESP32_AT\esp-at\web_preview\admin_one"

# Correct navbar structure (from about.html which is working)
correct_navbar = '''    <div class="navbar-menu fadeIn animated faster" id="navbar-menu">
      <div class="navbar-end">
        <div class="navbar-item">
          <span>John Doe</span>
        </div>
        <a title="Log out" class="navbar-item is-desktop-icon-only">
          <span class="icon"><i class="mdi mdi-logout"></i></span>
          <span>Log out</span>
        </a>
      </div>
    </div>
  </nav>'''

html_files = ['index.html', 'forms.html', 'profile.html', 'tables.html']

for filename in html_files:
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Find where the broken navbar ends and fix it
    # Pattern: broken navbar that ends abruptly without </nav> and missing aside
    broken_pattern = r'<div class="navbar-menu fadeIn animated faster" id="navbar-menu">\s*<div class="navbar-end">\s*<div class="navbar-item">\s*<span>John Doe</span>\s*</div>\s*</div>\s*</section>'
    
    if re.search(broken_pattern, content, re.DOTALL):
        # Need to restore the structure - find the section that should come after nav
        # Look for hero-bar section
        match = re.search(r'(<section class="hero is-hero-bar">)', content)
        if match:
            # We need to insert the closing nav and the entire aside + title-bar section
            print(f"File {filename} needs complex repair...")
    
    # Simpler approach: Just fix the navbar closing and add logout
    # Find: <div class="navbar-item">\n          <span>John Doe</span>\n        </div>\n    </div>\n  </section>
    # Replace with proper closing + aside
    
    # This is too complex - let's just use the backup approach
    print(f"Checking: {filename}")

print("\nNeed to manually repair files or restore from backup")
