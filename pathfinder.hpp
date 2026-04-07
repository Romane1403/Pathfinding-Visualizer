#pragma once
#include <vector>
#include <tuple>
#include <string>

struct Cell {
    int row, col;
    bool operator==(const Cell& o) const { return row == o.row && col == o.col; }
    bool operator<(const Cell& o)  const { return row < o.row || (row == o.row && col < o.col); }
};

struct Result {
    std::vector<Cell> path;
    std::vector<Cell> visited;
    int nodes_explored;
    double time_ms;
    bool found;
    std::string algorithm;
};

class Pathfinder {
public:
    // grid: 0=free, 1=wall
    static Result bfs(const std::vector<std::vector<int>>& grid, Cell start, Cell end);
    static Result dfs(const std::vector<std::vector<int>>& grid, Cell start, Cell end);
    static Result dijkstra(const std::vector<std::vector<int>>& grid, Cell start, Cell end);
    static Result astar(const std::vector<std::vector<int>>& grid, Cell start, Cell end);

private:
    static bool in_bounds(int r, int c, int rows, int cols);
    static std::vector<Cell> reconstruct(const std::vector<std::vector<Cell>>& parent, Cell start, Cell end);
    static double heuristic(Cell a, Cell b); // Manhattan distance
};
