#include "pathfinder.hpp"
#include <queue>
#include <stack>
#include <unordered_map>
#include <cmath>
#include <chrono>
#include <algorithm>
#include <limits>

using namespace std;
using Clock = chrono::high_resolution_clock;

bool Pathfinder::in_bounds(int r, int c, int rows, int cols) {
    return r >= 0 && r < rows && c >= 0 && c < cols;
}

double Pathfinder::heuristic(Cell a, Cell b) {
    return abs(a.row - b.row) + abs(a.col - b.col); // Manhattan
}

vector<Cell> Pathfinder::reconstruct(const vector<vector<Cell>>& parent, Cell start, Cell end) {
    vector<Cell> path;
    Cell cur = end;
    while (!(cur == start)) {
        path.push_back(cur);
        cur = parent[cur.row][cur.col];
    }
    path.push_back(start);
    reverse(path.begin(), path.end());
    return path;
}

// ─── BFS ─────────────────────────────────────────────────────────────────────
Result Pathfinder::bfs(const vector<vector<int>>& grid, Cell start, Cell end) {
    auto t0 = Clock::now();
    int rows = grid.size(), cols = grid[0].size();
    vector<vector<bool>> visited(rows, vector<bool>(cols, false));
    vector<vector<Cell>> parent(rows, vector<Cell>(cols, {-1, -1}));
    vector<Cell> visit_order;

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};

    queue<Cell> q;
    q.push(start);
    visited[start.row][start.col] = true;

    bool found = false;
    while (!q.empty()) {
        Cell cur = q.front(); q.pop();
        visit_order.push_back(cur);
        if (cur == end) { found = true; break; }
        for (int d = 0; d < 4; d++) {
            int nr = cur.row + dr[d], nc = cur.col + dc[d];
            if (in_bounds(nr, nc, rows, cols) && !visited[nr][nc] && grid[nr][nc] == 0) {
                visited[nr][nc] = true;
                parent[nr][nc] = cur;
                q.push({nr, nc});
            }
        }
    }
    auto t1 = Clock::now();
    double ms = chrono::duration<double, milli>(t1 - t0).count();

    Result res;
    res.algorithm = "BFS";
    res.visited = visit_order;
    res.nodes_explored = (int)visit_order.size();
    res.time_ms = ms;
    res.found = found;
    if (found) res.path = reconstruct(parent, start, end);
    return res;
}

// ─── DFS ─────────────────────────────────────────────────────────────────────
Result Pathfinder::dfs(const vector<vector<int>>& grid, Cell start, Cell end) {
    auto t0 = Clock::now();
    int rows = grid.size(), cols = grid[0].size();
    vector<vector<bool>> visited(rows, vector<bool>(cols, false));
    vector<vector<Cell>> parent(rows, vector<Cell>(cols, {-1, -1}));
    vector<Cell> visit_order;

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};

    stack<Cell> st;
    st.push(start);

    bool found = false;
    while (!st.empty()) {
        Cell cur = st.top(); st.pop();
        if (visited[cur.row][cur.col]) continue;
        visited[cur.row][cur.col] = true;
        visit_order.push_back(cur);
        if (cur == end) { found = true; break; }
        for (int d = 0; d < 4; d++) {
            int nr = cur.row + dr[d], nc = cur.col + dc[d];
            if (in_bounds(nr, nc, rows, cols) && !visited[nr][nc] && grid[nr][nc] == 0) {
                parent[nr][nc] = cur;
                st.push({nr, nc});
            }
        }
    }
    auto t1 = Clock::now();
    double ms = chrono::duration<double, milli>(t1 - t0).count();

    Result res;
    res.algorithm = "DFS";
    res.visited = visit_order;
    res.nodes_explored = (int)visit_order.size();
    res.time_ms = ms;
    res.found = found;
    if (found) res.path = reconstruct(parent, start, end);
    return res;
}

// ─── Dijkstra ────────────────────────────────────────────────────────────────
Result Pathfinder::dijkstra(const vector<vector<int>>& grid, Cell start, Cell end) {
    auto t0 = Clock::now();
    int rows = grid.size(), cols = grid[0].size();
    vector<vector<double>> dist(rows, vector<double>(cols, numeric_limits<double>::infinity()));
    vector<vector<Cell>> parent(rows, vector<Cell>(cols, {-1, -1}));
    vector<Cell> visit_order;

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};

    using PQItem = pair<double, Cell>;
    priority_queue<PQItem, vector<PQItem>, greater<PQItem>> pq;
    dist[start.row][start.col] = 0;
    pq.push({0, start});

    bool found = false;
    while (!pq.empty()) {
        auto [d, cur] = pq.top(); pq.pop();
        if (d > dist[cur.row][cur.col]) continue;
        visit_order.push_back(cur);
        if (cur == end) { found = true; break; }
        for (int dir = 0; dir < 4; dir++) {
            int nr = cur.row + dr[dir], nc = cur.col + dc[dir];
            if (in_bounds(nr, nc, rows, cols) && grid[nr][nc] == 0) {
                double nd = dist[cur.row][cur.col] + 1.0;
                if (nd < dist[nr][nc]) {
                    dist[nr][nc] = nd;
                    parent[nr][nc] = cur;
                    pq.push({nd, {nr, nc}});
                }
            }
        }
    }
    auto t1 = Clock::now();
    double ms = chrono::duration<double, milli>(t1 - t0).count();

    Result res;
    res.algorithm = "Dijkstra";
    res.visited = visit_order;
    res.nodes_explored = (int)visit_order.size();
    res.time_ms = ms;
    res.found = found;
    if (found) res.path = reconstruct(parent, start, end);
    return res;
}

// ─── A* ──────────────────────────────────────────────────────────────────────
Result Pathfinder::astar(const vector<vector<int>>& grid, Cell start, Cell end) {
    auto t0 = Clock::now();
    int rows = grid.size(), cols = grid[0].size();
    vector<vector<double>> g(rows, vector<double>(cols, numeric_limits<double>::infinity()));
    vector<vector<Cell>> parent(rows, vector<Cell>(cols, {-1, -1}));
    vector<Cell> visit_order;

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};

    using PQItem = pair<double, Cell>;
    priority_queue<PQItem, vector<PQItem>, greater<PQItem>> pq;
    g[start.row][start.col] = 0;
    pq.push({heuristic(start, end), start});

    bool found = false;
    while (!pq.empty()) {
        auto [f, cur] = pq.top(); pq.pop();
        if (g[cur.row][cur.col] + heuristic(cur, end) < f - 1e-9) continue;
        visit_order.push_back(cur);
        if (cur == end) { found = true; break; }
        for (int dir = 0; dir < 4; dir++) {
            int nr = cur.row + dr[dir], nc = cur.col + dc[dir];
            if (in_bounds(nr, nc, rows, cols) && grid[nr][nc] == 0) {
                double ng = g[cur.row][cur.col] + 1.0;
                if (ng < g[nr][nc]) {
                    g[nr][nc] = ng;
                    parent[nr][nc] = cur;
                    pq.push({ng + heuristic({nr, nc}, end), {nr, nc}});
                }
            }
        }
    }
    auto t1 = Clock::now();
    double ms = chrono::duration<double, milli>(t1 - t0).count();

    Result res;
    res.algorithm = "A*";
    res.visited = visit_order;
    res.nodes_explored = (int)visit_order.size();
    res.time_ms = ms;
    res.found = found;
    if (found) res.path = reconstruct(parent, start, end);
    return res;
}
