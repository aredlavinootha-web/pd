// Find maximum value in array
function findMax(arr) {
    // Handle empty array
    if (!arr || arr.length === 0) return null;
    // Start with first element
    let maxVal = arr[0];
    // Iterate through rest
    for (let i = 1; i < arr.length; i++) {
        // Update if larger found
        if (arr[i] > maxVal) maxVal = arr[i];
    }
    return maxVal;
}

// Main block
const data = [3, 7, 2, 9, 1];
console.log(findMax(data));
