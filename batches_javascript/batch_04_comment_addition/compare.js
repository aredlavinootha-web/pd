function findMax(arr) {
    if (!arr || arr.length === 0) return null;
    let maxVal = arr[0];
    for (let i = 1; i < arr.length; i++) {
        if (arr[i] > maxVal) maxVal = arr[i];
    }
    return maxVal;
}

const data = [3, 7, 2, 9, 1];
console.log(findMax(data));
