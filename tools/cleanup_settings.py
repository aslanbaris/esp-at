import os
import re

settings_file = r"C:\Work\sw\SG200_HMI_FW_ESP32\ESP32_AT\esp-at\web_preview\admin_one\settings.html"

with open(settings_file, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

# Regex to match the section.is-main-section and its contents
# We will reconstruct the section with only the desired card
main_section_start = content.find('<section class="section is-main-section">')
if main_section_start != -1:
    main_section_end = content.find('</section>', main_section_start) + 10
    
    # Extract the clients table card
    # Find the card that contains "Clients"
    clients_card_match = re.search(r'<div class="card has-table">.*?<p class="card-header-title">.*?Clients.*?</p>.*?</div>\s*</div>\s*</div>', content, re.DOTALL)
    
    if clients_card_match:
        # We need to be careful to capture the full card. The regex above might end too early or late depending on nested divs.
        # Let's try to locate the "Clients" card block more reliably.
        
        # Strategy:
        # 1. Start after "is-main-section"
        # 2. Skip the first notification (Responsive table)
        # 3. Capture the Clients card
        # 4. Ignore everything else until </section>
        
        # Find start of Clients card
        clients_start_idx = content.find('<div class="card has-table">', main_section_start)
        
        # We know the Clients card ends before the "Tightly wrapped" notification
        tightly_wrapped_idx = content.find('Tightly wrapped', clients_start_idx)
        
        if (tightly_wrapped_idx != -1):
             # Find the notification div before "Tightly wrapped"
            notification_start = content.rfind('<div class="notification is-info">', clients_start_idx, tightly_wrapped_idx)
            
            # The Clients card ends before this notification
            clients_end_idx = notification_start
            
            # Extract just the Clients card part
            clients_card_html = content[clients_start_idx:clients_end_idx].strip()
            
            # Create the new section content
            new_section_content = f'''    <section class="section is-main-section">
      {clients_card_html}
    </section>'''
            
            # Replace the old section
            content = content[:main_section_start] + new_section_content + content[main_section_end:]
            
            print("Layout updated successfully.")
        else:
             print("Could not find 'Tightly wrapped' marker.")
    else:
        print("Could not find Clients card.")

else:
    print("Could not find is-main-section.")

if len(content) != original_len:
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("File saved.")
else:
    print("No changes made.")
