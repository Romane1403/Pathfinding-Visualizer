// wrapper.cpp — Expose les algos C++ via une API C pour ctypes Python
#include "pathfinder.hpp"
#include <cstring>
#include <cstdlib>

struct CCell_c { int row, col; };

struct CResult_c {
    CCell_c* path;
    int      path_len;
    CCell_c* visited;
    int      visited_len;
    int      nodes_explored;
    double   time_ms;
    bool     found;
    char     algorithm[32];
};

static CResult_c* convert(const Result& r) {
    auto* out = new CResult_c;
    out->path_len = (int)r.path.size();
    out->path = new CCell_c[out->path_len];
    for (int i = 0; i < out->path_len; i++)
        out->path[i] = {r.path[i].row, r.path[i].col};

    out->visited_len = (int)r.visited.size();
    out->visited = new CCell_c[out->visited_len];
    for (int i = 0; i < out->visited_len; i++)
        out->visited[i] = {r.visited[i].row, r.visited[i].col};

    out->nodes_explored = r.nodes_explored;
    out->time_ms = r.time_ms;
    out->found   = r.found;
    strncpy(out->algorithm, r.algorithm.c_str(), 31);
    out->algorithm[31] = '\0';
    return out;
}

static std::vector<std::vector<int>> make_grid(int* flat, int rows, int cols) {
    std::vector<std::vector<int>> g(rows, std::vector<int>(cols));
    for (int r = 0; r < rows; r++)
        for (int c = 0; c < cols; c++)
            g[r][c] = flat[r * cols + c];
    return g;
}

extern "C" {
    CResult_c* pathfinder_bfs(int* grid, int rows, int cols, int sr, int sc, int er, int ec) {
        return convert(Pathfinder::bfs(make_grid(grid, rows, cols), {sr, sc}, {er, ec}));
    }
    CResult_c* pathfinder_dfs(int* grid, int rows, int cols, int sr, int sc, int er, int ec) {
        return convert(Pathfinder::dfs(make_grid(grid, rows, cols), {sr, sc}, {er, ec}));
    }
    CResult_c* pathfinder_dijkstra(int* grid, int rows, int cols, int sr, int sc, int er, int ec) {
        return convert(Pathfinder::dijkstra(make_grid(grid, rows, cols), {sr, sc}, {er, ec}));
    }
    CResult_c* pathfinder_astar(int* grid, int rows, int cols, int sr, int sc, int er, int ec) {
        return convert(Pathfinder::astar(make_grid(grid, rows, cols), {sr, sc}, {er, ec}));
    }
    void free_result(CResult_c* r) {
        if (!r) return;
        delete[] r->path;
        delete[] r->visited;
        delete r;
    }
}
