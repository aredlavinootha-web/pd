function sumList(nums) {
    let total = 0, i = 0;
    while (i < nums.length) { total += nums[i]; i++; }
    return total;
}

console.log(sumList([1, 2, 3, 4, 5]));
