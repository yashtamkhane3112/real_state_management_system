import os
from PIL import Image

dir_path = "C:/Users/lenovo/Downloads/property_000"
image_files = sorted([f for f in os.listdir(dir_path) if f.endswith(".jpg")])

print(f"Total files found: {len(image_files)}")

# Check properties of first file
first_path = os.path.join(dir_path, image_files[0])
with Image.open(first_path) as img:
    print(f"Resolution: {img.size[0]}x{img.size[1]} ({img.format})")

# Let's inspect the files size and choose 10 spaced-out frames (e.g., index 0, 11, 22, 33, 44, 55, 66, 77, 88, 99)
# to see if they form a smooth cinematic walkthrough sequence.
selected_indices = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99]
print("\nCurating sequence of spaced-out frames:")
for idx in selected_indices:
    filename = image_files[idx]
    filepath = os.path.join(dir_path, filename)
    file_size = os.path.getsize(filepath)
    with Image.open(filepath) as img:
        print(f"Frame {idx:02d}: {filename} | Size: {file_size/1024:.1f} KB | Resolution: {img.size[0]}x{img.size[1]}")
