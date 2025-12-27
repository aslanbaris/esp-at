import subprocess
import os

# Paths
base_path = r"C:\Work\sw\SG200_HMI_FW_ESP32\ESP32_AT\esp-at\web_preview\admin_one"
css_file = os.path.join(base_path, "css", "main.min.css")
output_dir = os.path.join(base_path, "css_optimized")

# Get all HTML files
html_files = [os.path.join(base_path, f) for f in os.listdir(base_path) if f.endswith(".html")]

# Create output dir
os.makedirs(output_dir, exist_ok=True)

# Build content string
content_str = ",".join(html_files)

print(f"CSS file: {css_file}")
print(f"HTML files: {html_files}")
print(f"Output dir: {output_dir}")

# Run PurgeCSS
cmd = [
    "purgecss",
    "--css", css_file,
    "--content", *html_files,
    "--output", output_dir
]

print(f"Running: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, text=True)
print(f"stdout: {result.stdout}")
print(f"stderr: {result.stderr}")
print(f"Return code: {result.returncode}")

# Check result
if result.returncode == 0:
    output_file = os.path.join(output_dir, "main.min.css")
    if os.path.exists(output_file):
        size = os.path.getsize(output_file)
        print(f"\nSuccess! Optimized CSS size: {size:,} bytes ({size/1024:.1f} KB)")
        
        # Compare with original
        original_size = os.path.getsize(css_file)
        print(f"Original CSS size: {original_size:,} bytes ({original_size/1024:.1f} KB)")
        print(f"Reduction: {(1 - size/original_size)*100:.1f}%")
