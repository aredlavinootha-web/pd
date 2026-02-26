function isPalindrome(s) {
    s = s.toLowerCase().replace(/ /g, '');
    let left = 0, right = s.length - 1;
    while (left < right) {
        if (s[left] !== s[right]) return false;
        left++; right--;
    }
    return true;
}

console.log(isPalindrome("A man a plan a canal Panama"));
console.log(isPalindrome("hello"));
