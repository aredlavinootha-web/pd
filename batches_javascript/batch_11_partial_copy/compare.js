const fs = require('fs');

function fetchLines(path) {
    return fs.readFileSync(path, 'utf8').split('\n');
}

function saveResults(items, path) {
    fs.writeFileSync(path, items.join('\n'));
}

function processData() {
    const data = fetchLines('input.txt');
    const filtered = data.filter(x => x.trim().length > 5).map(x => x.trim());
    saveResults(filtered, 'output.txt');
    return filtered.length;
}

console.log(processData());
