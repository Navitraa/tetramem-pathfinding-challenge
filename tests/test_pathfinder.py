import os
import tempfile
import unittest
from PIL import Image

from pathfinder import find_path, visualize_path, find_two_disjoint_paths


class PathfinderTests(unittest.TestCase):
    def test_find_path_straight_line(self):
        img = Image.new("L", (10, 10), 255)
        for x in range(10):
            img.putpixel((x, 5), 0)

        path = find_path(img, (0, 5), (9, 5))
        self.assertIsNotNone(path)
        self.assertEqual(path[0], (0, 5))
        self.assertEqual(path[-1], (9, 5))
        self.assertEqual(len(path), 10)
        # consecutive pixels are adjacent
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            self.assertTrue(abs(x1 - x2) + abs(y1 - y2) <= 1)

    def test_visualize_path_writes_file(self):
        img = Image.new("L", (5, 5), 255)
        path = [(0, 0), (1, 0), (2, 0)]
        fd, fname = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        try:
            visualize_path(img, path, fname)
            self.assertTrue(os.path.exists(fname))
            self.assertGreater(os.path.getsize(fname), 0)
        finally:
            os.remove(fname)

    def test_find_two_disjoint_paths(self):
        # two parallel horizontal lines so disjoint paths should exist
        img = Image.new("L", (7, 5), 255)
        for x in range(7):
            img.putpixel((x, 1), 0)
            img.putpixel((x, 3), 0)

        res = find_two_disjoint_paths(img, (0, 1), (6, 1), (0, 3), (6, 3))
        self.assertIsNotNone(res)
        p1, p2 = res
        set1, set2 = set(p1), set(p2)
        self.assertTrue(set1.isdisjoint(set2))
        # endpoints correct
        self.assertIn((0, 1), set1)
        self.assertIn((6, 1), set1)
        self.assertIn((0, 3), set2)
        self.assertIn((6, 3), set2)


if __name__ == "__main__":
    unittest.main()
