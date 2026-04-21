# tetramem-pathfinding-challenge

Lightweight utilities to find and visualize pixel-wise paths that travel only on black pixels in raster images.

Contents
- `pathfinder.py` — implementations: `path_exists`, `find_path`, `visualize_path`, `find_two_disjoint_paths`.
- `data/` — example input images.
- `tests/` — unit tests.

Requirements
- Python 3.10+ (this project used a 3.13 venv during development)
- See `requirements.txt` for runtime dependencies (Pillow, numpy, etc.).

Quick setup
1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```
2. Install dependencies:
```bash
python -m pip install -r requirements.txt
```

API & Usage

1) Check path existence
- Function: `path_exists(image, start, end, connectivity=4, threshold=128) -> bool`
- Example:
```bash
python - <<'PY'
from PIL import Image
from pathfinder import path_exists
img = Image.open('data/bars.png')
print(path_exists(img, (0,0), (10,0)))
PY
```

2) Find and visualize a valid path
- Functions: `find_path(image, start, end, ...) -> list[(x,y)]` and
  `visualize_path(image, path, out_path=None, path_color=(255,0,0), endpoint_color=(0,255,0))`.
- `visualize_path` defaults to saving into `./output/` when `out_path` is omitted.
- Example (saves image to `output/`):
```bash
python - <<'PY'
from PIL import Image
from pathfinder import find_path, visualize_path
img = Image.open('data/bars.png')
p = find_path(img, (0,0), (10,0))
if p:
    visualize_path(img, p)  # -> ./output/path_0_0_to_10_0.png
else:
    print('No path found')
PY
```

3) Two disjoint paths
- Function: `find_two_disjoint_paths(image, start1, end1, start2, end2, ...) -> (path1, path2) | None`.
- The current implementation uses a greedy approach: find one path, block it, then find the other; it tries both orders. This is simple and fast but not guaranteed to find a solution when one exists.
- Example:
```bash
python - <<'PY'
from PIL import Image
from pathfinder import find_two_disjoint_paths, visualize_path
img = Image.open('data/polygons.png')
res = find_two_disjoint_paths(img, (0,1), (10,1), (0,4), (10,4))
if res:
    p1, p2 = res
    visualize_path(img, p1, 'output/path1.png')
    visualize_path(img, p2, 'output/path2.png')
else:
    print('No disjoint paths found (greedy strategy)')
PY
```

Outputs
- Default output directory: `./output/` (created automatically by `visualize_path`).
- To view on macOS:
```bash
ls -l output
open output/<file>.png
```

Testing
- Run the lightweight smoke script:
```bash
python tests/run_pathfinder_tests.py
```
- Recommended: use unittest discovery (works in CI):
```bash
python -m unittest discover -v
```

Development notes
- Pixel indexing in the code uses `(x, y)` coordinates (width, height). `grid[x][y]` is width-major.
- `threshold` controls what is considered "black" (pixels with grayscale < threshold).
- For large images or heavy workloads, consider converting the grayscale image to a NumPy mask for faster operations.



