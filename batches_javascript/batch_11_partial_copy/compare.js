const fs = require('fs');

function main() {
    const lines = fs.readFileSync('input.txt', 'utf8').split('\n').filter(l => l.trim().length > 5).map(l => l.trim());
    fs.writeFileSync('output.txt', lines.join('\n'));
    console.log(lines.length);
}

main();
