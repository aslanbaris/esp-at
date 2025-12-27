const fs = require('fs');
const path = require('path');
const https = require('https');

const htmlIcons = [
    'account', 'account-circle', 'account-multiple', 'ballot', 'ballot-outline',
    'buffer', 'cart-outline', 'check', 'chevron-down', 'desktop-mac',
    'dots-vertical', 'email', 'emoticon-sad', 'eye', 'finance',
    'forwardburger', 'github-circle', 'help-circle', 'help-circle-outline',
    'lock', 'logout', 'mail', 'menu', 'plus', 'reload', 'settings',
    'square-edit-outline', 'table', 'trash-can', 'upload', 'view-list'
];

const iconMap = {
    'github-circle': 'github',
    'settings': 'cog',
    'mail': 'email'
};

const basePath = 'C:/Work/sw/SG200_HMI_FW_ESP32/ESP32_AT/esp-at/web_preview/admin_one';

function downloadSvg(iconName) {
    return new Promise((resolve, reject) => {
        const url = `https://cdn.jsdelivr.net/npm/@mdi/svg@latest/svg/${iconName}.svg`;
        https.get(url, (res) => {
            if (res.statusCode !== 200) {
                resolve(null);
                return;
            }
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        }).on('error', () => resolve(null));
    });
}

async function main() {
    console.log('Downloading icons from CDN...\n');

    let css = `/* Material Design Icons - Inline SVG (Offline) */
.mdi { display: inline-flex; align-items: center; justify-content: center; }
.mdi::before { content: ""; display: inline-block; width: 1em; height: 1em; }
.mdi-24px { font-size: 24px; }
.mdi-48px { font-size: 48px; }
.icon .mdi { margin: auto; }

`;

    let matched = 0;
    let failed = [];

    for (const htmlName of htmlIcons) {
        const mdiName = iconMap[htmlName] || htmlName;
        process.stdout.write(`  ${htmlName} -> ${mdiName}...`);

        const svgContent = await downloadSvg(mdiName);

        if (svgContent) {
            // Extract path from the SVG - look for d="..." in <path> element
            // SVG format: <svg ...><path d="M..." /></svg>
            const pathMatch = svgContent.match(/<path[^>]*\sd="([^"]+)"/);

            if (pathMatch && pathMatch[1]) {
                const svgPath = pathMatch[1];
                console.log(` OK (${svgPath.substring(0, 20)}...)`);
                matched++;

                // Create inline SVG
                const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="${svgPath}"/></svg>`;
                const encoded = Buffer.from(svg).toString('base64');
                css += `.mdi-${htmlName}::before { background: currentColor; -webkit-mask: url("data:image/svg+xml;base64,${encoded}") center/contain no-repeat; mask: url("data:image/svg+xml;base64,${encoded}") center/contain no-repeat; }\n`;
            } else {
                console.log(' PARSE FAILED');
                console.log('   Content:', svgContent.substring(0, 100));
                failed.push(htmlName);
                addPlaceholder(htmlName);
            }
        } else {
            console.log(' NOT FOUND');
            failed.push(htmlName);
            // Add placeholder
            const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8" fill="currentColor"/></svg>`;
            const encoded = Buffer.from(svg).toString('base64');
            css += `.mdi-${htmlName}::before { background: currentColor; -webkit-mask: url("data:image/svg+xml;base64,${encoded}") center/contain no-repeat; mask: url("data:image/svg+xml;base64,${encoded}") center/contain no-repeat; }\n`;
        }
    }

    console.log(`\nMatched: ${matched}/${htmlIcons.length}`);
    if (failed.length > 0) {
        console.log(`Failed: ${failed.join(', ')}`);
    }

    const outputPath = path.join(basePath, 'css', 'icons.css');
    fs.writeFileSync(outputPath, css);
    console.log(`\nSaved ${(css.length / 1024).toFixed(1)} KB to ${outputPath}`);
}

main().catch(console.error);
