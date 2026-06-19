import os
import shutil

src = "C:/Users/lenovo/Downloads/property.mp4"
dst = "E:/PropVista_Final/static/property.mp4"

if os.path.exists(src):
    src_size = os.path.getsize(src)
    dst_size = os.path.getsize(dst) if os.path.exists(dst) else 0
    print(f"Source video size: {src_size} bytes")
    print(f"Destination video size: {dst_size} bytes")
    shutil.copy2(src, dst)
    print("Video copied successfully!")
else:
    print(f"Source video not found at: {src}")
