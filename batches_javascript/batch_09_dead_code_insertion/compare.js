function countEven(nums) {
    let count = 0;
    for (const n of nums) { if (n % 2 === 0) count++; }
    return count;
}

console.log(countEven([1, 2, 3, 4, 5, 6]));
