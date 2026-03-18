#include <bits/stdc++.h>
using namespace std;

class solution {
public:
    int minimumTimeToReachDestination(vector<vector<int>>& signal) {
        int n = signal.size();
        int m = signal[0].size();
        
        // Min-heap priority queue to store {time, row, col}
        // Orders elements so the smallest time is processed first
        priority_queue<vector<int>, vector<vector<int>>, greater<vector<int>>> pq;
        
        // Distance matrix to store the minimum time to reach each cell
        // Initialize with a large value (infinity)
        vector<vector<int>> minTime(n, vector<int>(m, INT_MAX));
        
        // Starting point (0, 0) at time t = 0
        minTime[0][0] = 0;
        pq.push({0, 0, 0});
        
        // Direction arrays for moving Up, Down, Left, Right
        int dx[] = {-1, 1, 0, 0};
        int dy[] = {0, 0, -1, 1};
        
        while (!pq.empty()) {
            vector<int> current = pq.top();
            pq.pop();
            
            int t = current[0];
            int r = current[1];
            int c = current[2];
            
            // If we reached the destination (bottom-right cell)
            if (r == n - 1 && c == m - 1) {
                return t;
            }
            
            // Optimization: If we found a path to this cell that is slower than 
            // one already processed, skip it.
            if (t > minTime[r][c]) {
                continue;
            }
            
            // Explore all 4 adjacent neighbors
            for (int i = 0; i < 4; i++) {
                int nr = r + dx[i];
                int nc = c + dy[i];
                
                // Check if the neighbor is within grid boundaries
                if (nr >= 0 && nr < n && nc >= 0 && nc < m) {
                    int neighborSignal = signal[nr][nc];
                    
                    // Calculate the earliest time we can arrive at the neighbor.
                    // We arrive at 'departure_time + 1'.
                    // We must satisfy: (departure_time + 1) > neighborSignal
                    // This means: departure_time >= neighborSignal
                    // We also can't leave before 't' (current time).
                    // So, departure_time = max(t, neighborSignal).
                    


int arrivalTime = max(t, neighborSignal) + 1;

// If this path is faster than the previous best for this cell
if (arrivalTime < minTime[nr][nc]) {
minTime[nr][nc] = arrivalTime;
pq.push({arrivalTime, nr, nc});
}
}
}
}
return -1; // Should not be reached given the problem constraints
}
};