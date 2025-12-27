const { PurgeCSS } = require('purgecss');
const fs = require('fs');
const path = require('path');

async function run() {
    const basePath = 'C:/Work/sw/SG200_HMI_FW_ESP32/ESP32_AT/esp-at/web_preview/admin_one';
    
    const result = await new PurgeCSS().purge({
        content: [
            path.join(basePath, 'index.html'),
            path.join(basePath, 'forms.html'),
            path.join(basePath, 'profile.html'),
            path.join(basePath, 'tables.html')
        ],
        css: [path.join(basePath, 'css/main.min.css')],
        safelist: ['is-active', 'is-expanded', 'has-aside-left', 'has-navbar-fixed-top', 'has-aside-expanded']
    });
    
    const outputDir = path.join(basePath, 'css_optimized');
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const outputFile = path.join(outputDir, 'main.min.css');
    fs.writeFileSync(outputFile, result[0].css);
    
    const originalSize = fs.statSync(path.join(basePath, 'css/main.min.css')).size;
    const newSize = fs.statSync(outputFile).size;
    
    console.log(`Original CSS: ${(originalSize/1024).toFixed(1)} KB`);
    console.log(`Optimized CSS: ${(newSize/1024).toFixed(1)} KB`);
    console.log(`Reduction: ${((1 - newSize/originalSize) * 100).toFixed(1)}%`);
    console.log(`Saved to: ${outputFile}`);
}

run().catch(console.error);
