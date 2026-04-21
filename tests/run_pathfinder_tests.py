import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PIL import Image
from pathfinder import path_exists


def test_straight_line():
    img = Image.new("L", (10, 10), 255)
    for x in range(10):
        img.putpixel((x, 5), 0)
    assert path_exists(img, (0, 5), (9, 5)) is True


def test_blocked():
    img = Image.new("L", (10, 10), 255)
    for x in range(10):
        img.putpixel((x, 5), 0)
    img.putpixel((5, 5), 255)  # break the line
    assert path_exists(img, (0, 5), (9, 5)) is False


def test_diagonal_connectivity():
    img = Image.new("L", (3, 3), 255)
    img.putpixel((0, 0), 0)
    img.putpixel((1, 1), 0)
    img.putpixel((2, 2), 0)
    assert path_exists(img, (0, 0), (2, 2), connectivity=4) is False
    assert path_exists(img, (0, 0), (2, 2), connectivity=8) is True


if __name__ == "__main__":
    test_straight_line()
    test_blocked()
    test_diagonal_connectivity()
    print("All tests passed.")
