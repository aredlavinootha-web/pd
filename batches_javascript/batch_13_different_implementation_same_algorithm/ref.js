function binarySearch(arr, target) {
    let left = 0, right = arr.length - 1;
    while (left <= right) {
        const center = left + Math.floor((right - left) / 2);
        const val = arr[center];
        if (val === target) return center;
        if (val < target) left = center + 1;
        else right = center - 1;
    }
    return -1;
}

const a = [1, 3, 5, 7, 9];
console.log(binarySearch(a, 5));
console.log(binarySearch(a, 4));
