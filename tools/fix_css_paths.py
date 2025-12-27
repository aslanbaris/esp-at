import os

base_path = r"C:\Work\sw\SG200_HMI_FW_ESP32\ESP32_AT\esp-at\web_preview\admin_one"
html_files = [f for f in os.listdir(base_path) if f.endswith('.html')]

for filename in html_files:
    filepath = os.path.join(base_path, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    # Replace css/ paths with root paths
    # main.min.css was renamed to main.css
    content = content.replace('href="css/main.min.css"', 'href="main.css"')
    content = content.replace('href="css/icons.css"', 'href="icons.css"')
    
    # Also handle main.css if it was referenced that way
    content = content.replace('href="css/main.css"', 'href="main.css"')

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filename}")
    else:
        print(f"No changes in {filename}")
