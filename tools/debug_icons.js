const https = require('https');

https.get('https://raw.githubusercontent.com/Templarian/MaterialDesign/master/meta.json', (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
        const meta = JSON.parse(data);
        // Show first 10 icon names
        console.log('Sample icon names from database:');
        meta.slice(0, 20).forEach(i => console.log(`  - ${i.name}`));

        // Search for 'account'
        const accountIcons = meta.filter(i => i.name.includes('account')).slice(0, 10);
        console.log('\nIcons containing "account":');
        accountIcons.forEach(i => console.log(`  - ${i.name}`));

        // Search for 'menu'
        const menuIcons = meta.filter(i => i.name.includes('menu')).slice(0, 10);
        console.log('\nIcons containing "menu":');
        menuIcons.forEach(i => console.log(`  - ${i.name}`));
    });
});
