#!/bin/bash
# build.sh — Compile le core C++ en shared library
set -e
mkdir -p build
echo "Compilation de pathfinder + wrapper..."
g++ -O2 -std=c++17 -shared -fPIC \
    -o build/libpathfinder.so \
    src/pathfinder.cpp src/wrapper.cpp
echo "✓ build/libpathfinder.so généré"
echo ""
echo "Lancer le visualiseur : python3 pathfinding_viz.py"
