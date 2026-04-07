"""
pathfinding_viz.py — Visualiseur interactif pour les algorithmes de pathfinding
Appelle le core C++ via ctypes, affiche l'exploration en temps réel avec Pygame.

Contrôles :
  Clic gauche  → placer un mur
  Clic droit   → effacer un mur
  S            → définir le point de départ
  E            → définir le point d'arrivée
  1            → BFS
  2            → DFS
  3            → Dijkstra
  4            → A*
  C            → comparer tous les algos
  R            → réinitialiser la grille
  SPACE        → lancer l'algorithme sélectionné
"""

import ctypes
import os
import sys
import time
import subprocess
import pygame

# ─── Compilation automatique du .so ─────────────────────────────────────────
def compile_lib():
    src = os.path.join(os.path.dirname(__file__), "src", "pathfinder.cpp")
    out = os.path.join(os.path.dirname(__file__), "build", "libpathfinder.so")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    print("Compilation du core C++...")
    result = subprocess.run(
        ["g++", "-O2", "-std=c++17", "-shared", "-fPIC", "-o", out, src],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Erreur de compilation :\n", result.stderr)
        sys.exit(1)
    print("Compilation réussie !")
    return out

# ─── Structures ctypes miroir du C++ ────────────────────────────────────────
class CCell(ctypes.Structure):
    _fields_ = [("row", ctypes.c_int), ("col", ctypes.c_int)]

class CResult(ctypes.Structure):
    _fields_ = [
        ("path",           ctypes.POINTER(CCell)),
        ("path_len",       ctypes.c_int),
        ("visited",        ctypes.POINTER(CCell)),
        ("visited_len",    ctypes.c_int),
        ("nodes_explored", ctypes.c_int),
        ("time_ms",        ctypes.c_double),
        ("found",          ctypes.c_bool),
        ("algorithm",      ctypes.c_char * 32),
    ]

# ─── Wrapper Python ──────────────────────────────────────────────────────────
class PathfinderLib:
    def __init__(self, lib_path):
        self.lib = ctypes.CDLL(lib_path)
        for name in ["bfs", "dfs", "dijkstra", "astar"]:
            fn = getattr(self.lib, f"pathfinder_{name}")
            fn.restype = ctypes.POINTER(CResult)
            fn.argtypes = [
                ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int,
                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int
            ]
        self.lib.free_result.argtypes = [ctypes.POINTER(CResult)]

    def _run(self, fn_name, grid, start, end):
        rows, cols = len(grid), len(grid[0])
        flat = [grid[r][c] for r in range(rows) for c in range(cols)]
        arr = (ctypes.c_int * len(flat))(*flat)
        fn = getattr(self.lib, f"pathfinder_{fn_name}")
        res_ptr = fn(arr, rows, cols, start[0], start[1], end[0], end[1])
        res = res_ptr.contents
        path    = [(res.path[i].row, res.path[i].col) for i in range(res.path_len)]
        visited = [(res.visited[i].row, res.visited[i].col) for i in range(res.visited_len)]
        out = {
            "path": path, "visited": visited,
            "nodes": res.nodes_explored, "time_ms": res.time_ms,
            "found": res.found, "algo": res.algorithm.decode()
        }
        self.lib.free_result(res_ptr)
        return out

    def bfs(self, grid, start, end):      return self._run("bfs", grid, start, end)
    def dfs(self, grid, start, end):      return self._run("dfs", grid, start, end)
    def dijkstra(self, grid, start, end): return self._run("dijkstra", grid, start, end)
    def astar(self, grid, start, end):    return self._run("astar", grid, start, end)


# ─── Visualiseur Pygame ──────────────────────────────────────────────────────
ROWS, COLS = 30, 50
CELL = 20
WIDTH  = COLS * CELL
HEIGHT = ROWS * CELL + 110   # panneau infos en bas

# Palette
BG       = (18, 18, 24)
GRID_C   = (35, 35, 48)
WALL_C   = (55, 55, 75)
START_C  = (80, 200, 120)
END_C    = (220, 80, 80)
VISIT_C  = (60, 100, 180)
PATH_C   = (255, 200, 50)
TEXT_C   = (200, 200, 210)
PANEL_C  = (25, 25, 35)
ALGO_COLORS = {
    "BFS":      (80,  160, 220),
    "DFS":      (180, 100, 220),
    "Dijkstra": (80,  200, 160),
    "A*":       (255, 160,  60),
}

ALGO_KEYS = {
    pygame.K_1: "BFS",
    pygame.K_2: "DFS",
    pygame.K_3: "Dijkstra",
    pygame.K_4: "A*",
}

class Viz:
    def __init__(self, lib: PathfinderLib):
        self.lib = lib
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pathfinding Visualizer — Romane ARRIS")
        self.font_sm = pygame.font.SysFont("monospace", 13)
        self.font_md = pygame.font.SysFont("monospace", 15, bold=True)
        self.clock  = pygame.time.Clock()
        self.reset()
        self.selected_algo = "A*"
        self.stats = {}
        self.compare_results = []
        self.mode = "idle"   # idle | running | done | compare

    def reset(self):
        self.grid  = [[0]*COLS for _ in range(ROWS)]
        self.start = (5, 5)
        self.end   = (ROWS-6, COLS-6)
        self.visit_anim = []
        self.path_anim  = []
        self.anim_idx   = 0
        self.mode = "idle"
        self.stats = {}
        self.compare_results = []

    def cell_at(self, mx, my):
        if my >= ROWS * CELL: return None
        return my // CELL, mx // CELL

    def draw_grid(self):
        for r in range(ROWS):
            for c in range(COLS):
                x, y = c * CELL, r * CELL
                color = BG
                cell = (r, c)
                if self.grid[r][c] == 1:
                    color = WALL_C
                elif cell == self.start:
                    color = START_C
                elif cell == self.end:
                    color = END_C
                pygame.draw.rect(self.screen, color, (x, y, CELL-1, CELL-1))

    def draw_anim(self):
        for i, (r, c) in enumerate(self.visit_anim[:self.anim_idx]):
            if (r, c) in (self.start, self.end): continue
            alpha = max(80, 220 - (self.anim_idx - i) * 3)
            col = ALGO_COLORS.get(self.selected_algo, VISIT_C)
            s = pygame.Surface((CELL-1, CELL-1), pygame.SRCALPHA)
            s.fill((*col, alpha))
            self.screen.blit(s, (c*CELL, r*CELL))
        if self.anim_idx >= len(self.visit_anim):
            for r, c in self.path_anim:
                if (r, c) in (self.start, self.end): continue
                pygame.draw.rect(self.screen, PATH_C, (c*CELL+2, r*CELL+2, CELL-5, CELL-5))

    def draw_compare(self):
        for res in self.compare_results:
            col = ALGO_COLORS.get(res["algo"], VISIT_C)
            for r, c in res["path"]:
                if (r, c) in (self.start, self.end): continue
                s = pygame.Surface((CELL-1, CELL-1), pygame.SRCALPHA)
                s.fill((*col, 180))
                self.screen.blit(s, (c*CELL, r*CELL))

    def draw_panel(self):
        panel_y = ROWS * CELL
        pygame.draw.rect(self.screen, PANEL_C, (0, panel_y, WIDTH, 110))

        # Ligne 1 : algo sélectionné + touches
        hints = "[1]BFS [2]DFS [3]Dijkstra [4]A*  [SPACE]Lancer  [C]Comparer  [R]Reset  [S/E]Départ/Arrivée"
        self.screen.blit(self.font_sm.render(hints, True, (120, 120, 140)), (8, panel_y + 6))

        # Ligne 2 : algo courant
        algo_surf = self.font_md.render(f"Algo : {self.selected_algo}", True,
                                        ALGO_COLORS.get(self.selected_algo, TEXT_C))
        self.screen.blit(algo_surf, (8, panel_y + 26))

        # Ligne 3 : stats
        if self.stats:
            s = self.stats
            info = (f"Noeuds explorés : {s.get('nodes', '?')}   "
                    f"Longueur chemin : {len(s.get('path', []))}   "
                    f"Temps : {s.get('time_ms', 0):.3f} ms   "
                    f"{'✓ Chemin trouvé' if s.get('found') else '✗ Aucun chemin'}")
            self.screen.blit(self.font_sm.render(info, True, TEXT_C), (8, panel_y + 50))

        # Ligne 4 : comparaison
        if self.compare_results:
            x = 8
            for res in self.compare_results:
                col = ALGO_COLORS.get(res["algo"], TEXT_C)
                txt = f"{res['algo']}: {res['nodes']}n  {len(res['path'])}p  {res['time_ms']:.2f}ms"
                surf = self.font_sm.render(txt, True, col)
                self.screen.blit(surf, (x, panel_y + 72))
                x += surf.get_width() + 20

        # Légende start/end
        pygame.draw.rect(self.screen, START_C, (8,  panel_y + 90, 12, 12))
        pygame.draw.rect(self.screen, END_C,   (80, panel_y + 90, 12, 12))
        self.screen.blit(self.font_sm.render("Départ", True, TEXT_C), (24, panel_y + 90))
        self.screen.blit(self.font_sm.render("Arrivée", True, TEXT_C), (96, panel_y + 90))

    def run_algo(self, algo=None):
        algo = algo or self.selected_algo
        fn = {"BFS": self.lib.bfs, "DFS": self.lib.dfs,
              "Dijkstra": self.lib.dijkstra, "A*": self.lib.astar}[algo]
        res = fn(self.grid, self.start, self.end)
        return res

    def start_animation(self):
        res = self.run_algo()
        self.visit_anim = res["visited"]
        self.path_anim  = res["path"]
        self.stats = res
        self.anim_idx = 0
        self.mode = "running"

    def run_compare(self):
        self.compare_results = []
        for algo in ["BFS", "DFS", "Dijkstra", "A*"]:
            res = self.run_algo(algo)
            res["algo"] = algo
            self.compare_results.append(res)
        self.mode = "compare"
        self.stats = {}

    def run(self):
        placing_walls = False
        erasing = False
        set_mode = None   # "start" | "end" | None

        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); return

                if event.type == pygame.KEYDOWN:
                    if event.key in ALGO_KEYS:
                        self.selected_algo = ALGO_KEYS[event.key]
                        self.mode = "idle"
                    elif event.key == pygame.K_SPACE:
                        self.visit_anim = []; self.path_anim = []
                        self.compare_results = []
                        self.start_animation()
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_c:
                        self.visit_anim = []; self.path_anim = []
                        self.run_compare()
                    elif event.key == pygame.K_s:
                        set_mode = "start"
                    elif event.key == pygame.K_e:
                        set_mode = "end"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    cell = self.cell_at(*event.pos)
                    if cell:
                        if set_mode == "start":
                            self.start = cell; set_mode = None
                        elif set_mode == "end":
                            self.end = cell; set_mode = None
                        elif event.button == 1:
                            placing_walls = True
                            if cell not in (self.start, self.end):
                                self.grid[cell[0]][cell[1]] = 1
                        elif event.button == 3:
                            erasing = True
                            self.grid[cell[0]][cell[1]] = 0

                if event.type == pygame.MOUSEBUTTONUP:
                    placing_walls = False; erasing = False

                if event.type == pygame.MOUSEMOTION:
                    cell = self.cell_at(*event.pos)
                    if cell and cell not in (self.start, self.end):
                        if placing_walls: self.grid[cell[0]][cell[1]] = 1
                        if erasing:       self.grid[cell[0]][cell[1]] = 0

            # Animation
            if self.mode == "running":
                step = max(1, len(self.visit_anim) // 80)
                self.anim_idx = min(self.anim_idx + step, len(self.visit_anim))
                if self.anim_idx >= len(self.visit_anim):
                    self.mode = "done"

            # Dessin
            self.screen.fill(BG)
            self.draw_grid()
            if self.mode in ("running", "done"):
                self.draw_anim()
            elif self.mode == "compare":
                self.draw_compare()
            self.draw_panel()

            # Indicateur set_mode
            if set_mode:
                msg = f"Cliquez pour placer le {'DÉPART' if set_mode == 'start' else 'ARRIVÉE'}"
                surf = self.font_md.render(msg, True, START_C if set_mode == "start" else END_C)
                self.screen.blit(surf, (WIDTH//2 - surf.get_width()//2, 4))

            pygame.display.flip()


# ─── Entrypoint ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    lib_path = os.path.join(os.path.dirname(__file__), "build", "libpathfinder.so")
    if not os.path.exists(lib_path):
        lib_path = compile_lib()
    lib = PathfinderLib(lib_path)
    viz = Viz(lib)
    viz.run()
