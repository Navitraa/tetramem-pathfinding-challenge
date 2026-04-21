import imageio.v3 as imageio
import numpy as np
import os

def check_pixel_status(universe, x, y):
    """Helper to check what's actually at a coordinate."""
    pixel = universe[y, x] # Note: images are indexed as [row, col] -> [y, x]
    print(f"Pixel at ({x}, {y}) is: {pixel}")
    return pixel

def main():
    # 1. Load the image
    # To change to your local path, replace the string below with the path to your image file.
    img_path = '/Users/navitraa/hackathons/tetramem-pathfinding-challenge/data/bars.png'
    
    if not os.path.exists(img_path):
        print(f"Error: {img_path} not found. Please download it into this folder.")
        return

    image = imageio.imread(img_path)
    
    # 2. Basic Info
    print(f"Image Shape: {image.shape}")
    print(f"Data Type: {image.dtype}")
    
    # 3. Test a coordinate (change these to points you want to test)
    # Let's assume start_x, start_y = 0, 0 for a test
    try:
        check_pixel_status(image, 0, 0)
    except IndexError:
        print("Coordinate out of bounds!")

if __name__ == "__main__":
    main()