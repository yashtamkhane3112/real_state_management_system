import os
import shutil

src_dir = "C:/Users/lenovo/Downloads/videoplayback (1)"
dst_dir = "E:/PropVista_Final/static/images/properties/fallbacks"

os.makedirs(dst_dir, exist_ok=True)

# Copy files 0001.jpg to 0020.jpg
for i in range(1, 21):
    filename = f"{i:04d}.jpg"
    src_file = os.path.join(src_dir, filename)
    dst_file = os.path.join(dst_dir, filename)
    
    if os.path.exists(src_file):
        shutil.copy2(src_file, dst_file)
        print(f"Copied fallback image: {filename} -> static/images/properties/fallbacks/")
    else:
        print(f"Source image not found: {src_file}")
