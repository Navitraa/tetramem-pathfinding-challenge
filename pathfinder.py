from collections import deque
from typing import Tuple, Union

from PIL import Image
from PIL import ImageDraw
import os
from typing import List, Optional


def _to_binary(image: Image.Image, threshold: int = 128):
    gray = image.convert("L")
    w, h = gray.size
    pix = gray.load()
    grid = [[False] * h for _ in range(w)]
    for x in range(w):
        for y in range(h):
            grid[x][y] = pix[x, y] < threshold
    return grid, w, h


def path_exists(
    image: Union[str, Image.Image],
    start: Tuple[int, int],
    end: Tuple[int, int],
    connectivity: int = 4,
    threshold: int = 128,
) -> bool:
    """Return True if there's a path of black pixels between start and end.

    - `image` may be a PIL Image or a filesystem path.
    - `start` and `end` are (x, y) tuples.
    - `connectivity` may be 4 or 8 (defaults to 4).
    - `threshold` is the grayscale cutoff for black.
    """
    if isinstance(image, str):
        img = Image.open(image)
    else:
        img = image

    grid, w, h = _to_binary(img, threshold=threshold)

    sx, sy = start
    ex, ey = end
    if not (0 <= sx < w and 0 <= sy < h and 0 <= ex < w and 0 <= ey < h):
        return False

    if not grid[sx][sy] or not grid[ex][ey]:
        return False

    if (sx, sy) == (ex, ey):
        return True

    if connectivity == 8:
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    else:
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    q = deque()
    q.append((sx, sy))
    seen = [[False] * h for _ in range(w)]
    seen[sx][sy] = True

    while q:
        x, y = q.popleft()
        for dx, dy in neighbors:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[nx][ny] and grid[nx][ny]:
                if (nx, ny) == (ex, ey):
                    return True
                seen[nx][ny] = True
                q.append((nx, ny))

    return False


def find_path(
    image: Union[str, Image.Image],
    start: Tuple[int, int],
    end: Tuple[int, int],
    connectivity: int = 4,
    threshold: int = 128,
) -> Optional[List[Tuple[int, int]]]:
    """Return a list of (x,y) pixels forming a path of black pixels, or None.

    Uses BFS to find a shortest path under the given connectivity.
    """
    if isinstance(image, str):
        img = Image.open(image)
    else:
        img = image

    grid, w, h = _to_binary(img, threshold=threshold)

    sx, sy = start
    ex, ey = end
    if not (0 <= sx < w and 0 <= sy < h and 0 <= ex < w and 0 <= ey < h):
        return None
    if not grid[sx][sy] or not grid[ex][ey]:
        return None
    if (sx, sy) == (ex, ey):
        return [(sx, sy)]

    if connectivity == 8:
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    else:
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    q = deque()
    q.append((sx, sy))
    parent = { (sx, sy): None }

    while q:
        x, y = q.popleft()
        for dx, dy in neighbors:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in parent and grid[nx][ny]:
                parent[(nx, ny)] = (x, y)
                if (nx, ny) == (ex, ey):
                    # reconstruct path
                    path = [(ex, ey)]
                    cur = (x, y)
                    while cur is not None:
                        path.append(cur)
                        cur = parent[cur]
                    path.reverse()
                    return path
                q.append((nx, ny))

    return None


def visualize_path(
    image: Union[str, Image.Image],
    path: List[Tuple[int, int]],
    out_path: Optional[str] = None,
    path_color: Tuple[int, int, int] = (255, 0, 0),
    endpoint_color: Tuple[int, int, int] = (0, 255, 0),
) -> None:
    """Write a copy of the image with the `path` drawn on it and save to `out_path`.

    `path` is a list of (x,y) tuples. Colors are RGB tuples.
    """
    if isinstance(image, str):
        img = Image.open(image).convert("RGB")
    else:
        img = image.convert("RGB")

    draw = ImageDraw.Draw(img)
    for x, y in path:
        draw.point((x, y), fill=path_color)
    # highlight endpoints
    if path:
        draw.point(path[0], fill=endpoint_color)
        draw.point(path[-1], fill=endpoint_color)

    # default output directory
    if out_path is None:
        out_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(out_dir, exist_ok=True)
        # create a filename based on endpoints
        if path:
            fname = f"path_{path[0][0]}_{path[0][1]}_to_{path[-1][0]}_{path[-1][1]}.png"
        else:
            fname = "path.png"
        out_path = os.path.join(out_dir, fname)
    else:
        # ensure parent directory exists if specified
        parent = os.path.dirname(out_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

    img.save(out_path)
    # user-friendly confirmation
    fname = os.path.basename(out_path)
    if os.path.sep + "output" + os.path.sep in out_path or out_path.startswith("output" + os.path.sep) or os.path.dirname(out_path).endswith("output"):
        print(f"Saved output image: {fname} in ./output/")
    else:
        print(f"Saved output image: {out_path}")


def find_two_disjoint_paths(
    image: Union[str, Image.Image],
    start1: Tuple[int, int],
    end1: Tuple[int, int],
    start2: Tuple[int, int],
    end2: Tuple[int, int],
    connectivity: int = 4,
    threshold: int = 128,
) -> Optional[Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]]:
    """Try to find two non-intersecting paths for the two point pairs.

    Strategy: attempt to find a path for the first pair, block its pixels,
    then find a path for the second pair. If that fails, try the other order.
    Returns a tuple (path1, path2) or None.
    """
    # helper to run find_path on an image/grid with some blocked pixels
    def _blocked_image(orig_img, blocked_pixels):
        # create a copy and set blocked pixels to white
        if isinstance(orig_img, str):
            img = Image.open(orig_img).convert("L")
        else:
            img = orig_img.convert("L")
        for x, y in blocked_pixels:
            if 0 <= x < img.width and 0 <= y < img.height:
                img.putpixel((x, y), 255)
        return img

    # attempt order A then B
    p1 = find_path(image, start1, end1, connectivity=connectivity, threshold=threshold)
    if p1 is not None:
        blocked = set(p1)
        img2 = _blocked_image(image, blocked)
        p2 = find_path(img2, start2, end2, connectivity=connectivity, threshold=threshold)
        if p2 is not None:
            return p1, p2

    # attempt order B then A
    p2 = find_path(image, start2, end2, connectivity=connectivity, threshold=threshold)
    if p2 is not None:
        blocked = set(p2)
        img2 = _blocked_image(image, blocked)
        p1 = find_path(img2, start1, end1, connectivity=connectivity, threshold=threshold)
        if p1 is not None:
            return p1, p2

    return None


if __name__ == "__main__":
    # quick sanity check when run directly
    img = Image.new("L", (5, 5), 255)
    for x in range(5):
        img.putpixel((x, 2), 0)
    print(path_exists(img, (0, 2), (4, 2)))
