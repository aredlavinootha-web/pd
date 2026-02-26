const fs = require('fs');
const path = require('path');

function transform(data) {
    return data.toUpperCase();
}

function main(inputPath, outputPath) {
    const data = fs.readFileSync(inputPath, 'utf8');
    const result = transform(data);
    fs.writeFileSync(outputPath, result);
}

const [,, inputArg, outputArg] = process.argv;
if (!inputArg || !outputArg) {
    console.error('Usage: node prog.js input output');
    process.exit(1);
}
main(inputArg, outputArg);
