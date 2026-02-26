function computeStats(data) {
    let mx = data[0], mn = data[0], total = 0;
    for (const v of data) {
        if (v > mx) mx = v;
        if (v < mn) mn = v;
        total += v;
    }
    const avg = data.length > 0 ? total / data.length : 0;
    return { avg, max: mx, min: mn };
}

const d = [10, 20, 30, 40, 50];
console.log(computeStats(d));
