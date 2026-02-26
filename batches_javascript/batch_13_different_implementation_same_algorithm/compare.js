function binarySearchRec(arr, lo, hi, target) {
    if (lo > hi) return -1;
    const mid = lo + Math.floor((hi - lo) / 2);
    if (arr[mid] === target) return mid;
    if (arr[mid] < target) return binarySearchRec(arr, mid + 1, hi, target);
    return binarySearchRec(arr, lo, mid - 1, target);
}

function binarySearch(arr, target) {
    return binarySearchRec(arr, 0, arr.length - 1, target);
}

const a = [1, 3, 5, 7, 9];
console.log(binarySearch(a, 5));
console.log(binarySearch(a, 4));
