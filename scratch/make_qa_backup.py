import os
import shutil

files_to_backup = [
    ("templates/properties/list.html", "templates/properties/list.html.qabackup"),
    ("static/css/app.css", "static/css/app.css.qabackup"),
    ("properties/models.py", "properties/models.py.qabackup"),
    ("reports/views.py", "reports/views.py.qabackup"),
    ("favorites/views.py", "favorites/views.py.qabackup"),
    ("leads/views.py", "leads/views.py.qabackup"),
    ("templates/home.html", "templates/home.html.qabackup"),
    ("static/js/app.js", "static/js/app.js.qabackup")
]

for src, dst in files_to_backup:
    src_path = os.path.join("E:/PropVista_Final", src)
    dst_path = os.path.join("E:/PropVista_Final", dst)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        print(f"Backed up: {src} -> {dst}")
    else:
        print(f"Source file not found: {src}")
