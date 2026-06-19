import os
import shutil

src_dir = "C:/Users/lenovo/Downloads/property_000"
dst_dir = "E:/PropVista_Final/static/images/story-frames"

os.makedirs(dst_dir, exist_ok=True)

selected_indices = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99]

for idx in selected_indices:
    filename = f"property_{idx:03d}.jpg"
    src_file = os.path.join(src_dir, filename)
    dst_file = os.path.join(dst_dir, filename)
    
    if os.path.exists(src_file):
        shutil.copy2(src_file, dst_file)
        print(f"Copied: {filename} -> static/images/story-frames/")
    else:
        print(f"Source file not found: {filename}")
