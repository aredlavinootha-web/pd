function normalize(s) {
    return s.toLowerCase().replace(/ /g, '');
}

function charsMatch(s, left, right) {
    return s[left] === s[right];
}

function isPalindrome(s) {
    s = normalize(s);
    let left = 0, right = s.length - 1;
    while (left < right) {
        if (!charsMatch(s, left, right)) return false;
        left++; right--;
    }
    return true;
}

console.log(isPalindrome("A man a plan a canal Panama"));
console.log(isPalindrome("hello"));
