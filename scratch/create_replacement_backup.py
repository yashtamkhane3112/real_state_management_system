import shutil
import os

files_to_backup = [
    ("E:/PropVista_Final/templates/home.html", "E:/PropVista_Final/templates/home.html.videoreplacementbackup"),
    ("E:/PropVista_Final/static/css/app.css", "E:/PropVista_Final/static/css/app.css.videoreplacementbackup"),
    ("E:/PropVista_Final/static/css/navbar.css", "E:/PropVista_Final/static/css/navbar.css.videoreplacementbackup"),
    ("E:/PropVista_Final/static/js/app.js", "E:/PropVista_Final/static/js/app.js.videoreplacementbackup")
]

for src, dst in files_to_backup:
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Backed up: {src} -> {dst}")
    else:
        print(f"File not found: {src}")

# Backup story frames directory
story_src = "E:/PropVista_Final/static/images/story-frames"
story_dst = "E:/PropVista_Final/static/images/story-frames.videoreplacementbackup"
if os.path.exists(story_src):
    if os.path.exists(story_dst):
        shutil.rmtree(story_dst)
    shutil.copytree(story_src, story_dst)
    print(f"Backed up story frames directory to: {story_dst}")
