import shutil
import os

files_to_backup = [
    ("E:/PropVista_Final/templates/home.html", "E:/PropVista_Final/templates/home.html.v7backup"),
    ("E:/PropVista_Final/static/css/app.css", "E:/PropVista_Final/static/css/app.css.v7backup"),
    ("E:/PropVista_Final/static/js/app.js", "E:/PropVista_Final/static/js/app.js.v7backup"),
    ("E:/PropVista_Final/static/css/navbar.css", "E:/PropVista_Final/static/css/navbar.css.v7backup")
]

for src, dst in files_to_backup:
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Backed up: {src} -> {dst}")
    else:
        print(f"File not found: {src}")
