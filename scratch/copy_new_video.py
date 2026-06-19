import os
import shutil

src = "C:/Users/lenovo/Downloads/videoplayback.mp4"
dst = "E:/PropVista_Final/static/videoplayback.mp4"

if os.path.exists(src):
    src_size = os.path.getsize(src)
    print(f"New video source size: {src_size} bytes")
    shutil.copy2(src, dst)
    print("New video copied to static directory successfully!")
else:
    print(f"Source video not found at: {src}")
