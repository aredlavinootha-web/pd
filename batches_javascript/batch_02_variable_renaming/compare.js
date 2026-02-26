function computeQuadraticSum(elements) {
    let accumulator = 0;
    for (const value of elements) {
        accumulator += value * value;
    }
    return accumulator;
}

function handleInput(collection) {
    return computeQuadraticSum(collection);
}

const inputData = [1, 2, 3, 4, 5];
console.log(handleInput(inputData));
