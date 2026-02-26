function sumOfSquares(numbers) {
    let total = 0;
    for (const num of numbers) {
        total += num * num;
    }
    return total;
}

function processList(data) {
    return sumOfSquares(data);
}

const myList = [1, 2, 3, 4, 5];
console.log(processList(myList));
