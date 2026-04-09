# Pathfinding Visualizer

Visualiseur interactif d'algorithmes de pathfinding, développé dans le cadre de ma formation d'ingénieure en systèmes embarqués à l'ESEO.

Le moteur de recherche est écrit en **C++17** (performances maximales), exposé à Python via **ctypes**, et affiché en temps réel avec **Pygame**.

---

## Démonstration

> *Lancer le projet et faire une capture GIF avec [Peek](https://github.com/phw/peek) ou [ScreenToGif](https://www.screentogif.com/), puis glisser le fichier ici.*

---

## Installation

### Prérequis

- `g++` (C++17 minimum) — `sudo apt install g++`
- `Python 3.8+`
- `pygame` — `pip install pygame`

### Compilation & lancement

```bash
git clone https://github.com/Romane1403/pathfinding-visualizer
cd pathfinding-visualizer

# Compiler le core C++
bash build.sh

# Lancer le visualiseur
python3 pathfinding_viz.py
```

---

## Contrôles

| Touche / Action | Effet |
|---|---|
| `Clic gauche` | Placer un mur |
| `Clic droit` | Effacer un mur |
| `S` + clic | Déplacer le point de départ |
| `E` + clic | Déplacer le point d'arrivée |
| `1` | Sélectionner BFS |
| `2` | Sélectionner DFS |
| `3` | Sélectionner Dijkstra |
| `4` | Sélectionner A* |
| `SPACE` | Lancer l'algorithme sélectionné |
| `C` | **Mode comparaison** — affiche les 4 chemins simultanément |
| `R` | Réinitialiser la grille |

---

## Architecture du projet

```
pathfinding-visualizer/
├── src/
│   ├── pathfinder.hpp      # Interface C++ — structures Cell, Result, classe Pathfinder
│   ├── pathfinder.cpp      # Implémentation BFS, DFS, Dijkstra, A*
│   └── wrapper.cpp         # Binding C extern pour ctypes Python
├── build/
│   └── libpathfinder.so    # Shared library générée par build.sh
├── pathfinding_viz.py      # Visualiseur Pygame + wrapper ctypes Python
├── build.sh                # Script de compilation
└── README.md
```

### Choix techniques

**Pourquoi C++ pour le moteur ?**
Les algorithmes de pathfinding sur grille de 30×50 = 1500 cellules sont exécutés en boucle lors de la comparaison. Le C++ garantit des temps de réponse < 1 ms là où Python pur prendrait 15-50 ms. La séparation moteur (C++) / IHM (Python) reflète l'architecture réelle des systèmes embarqués : code critique bas niveau, interface haut niveau.

**Pourquoi ctypes et non pybind11 ?**
Pas de dépendance externe à compiler — ctypes est dans la bibliothèque standard Python. Le wrapper `extern "C"` est minimaliste et pédagogique.

---

## Résultats typiques (grille 30×50, chemin non obstrué)

| Algorithme | Nœuds explorés | Longueur chemin | Temps |
|---|---|---|---|
| BFS | ~900 | optimal | ~0.3 ms |
| DFS | ~1400 | non optimal | ~0.2 ms |
| Dijkstra | ~900 | optimal | ~0.5 ms |
| A* | **~200** | optimal | ~0.1 ms |

---

## Auteure

**Romane ARRIS** — Étudiante ingénieure ESEO (électronique, informatique, systèmes embarqués)

[github.com/Romane1403](https://github.com/Romane1403)
