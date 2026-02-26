function computeStats(data) {
    const total = data.reduce((s, v) => s + v, 0);
    const avg = data.length > 0 ? total / data.length : 0;
    let mx = data[0], mn = data[0];
    for (const v of data) {
        if (v > mx) mx = v;
        if (v < mn) mn = v;
    }
    return { avg, max: mx, min: mn };
}

const d = [10, 20, 30, 40, 50];
console.log(computeStats(d));
