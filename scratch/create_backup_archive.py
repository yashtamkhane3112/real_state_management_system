import os
import shutil

backup_dir = "E:/PropVista_Final/landing_backups"
os.makedirs(backup_dir, exist_ok=True)

# Copy current active states
shutil.copy2("E:/PropVista_Final/templates/home.html", os.path.join(backup_dir, "home_active.html"))
shutil.copy2("E:/PropVista_Final/static/css/app.css", os.path.join(backup_dir, "app_active.css"))
shutil.copy2("E:/PropVista_Final/static/css/navbar.css", os.path.join(backup_dir, "navbar_active.css"))
shutil.copy2("E:/PropVista_Final/static/js/app.js", os.path.join(backup_dir, "app_active.js"))

# Copy original hero video states
if os.path.exists("E:/PropVista_Final/templates/home_backup.html"):
    shutil.copy2("E:/PropVista_Final/templates/home_backup.html", os.path.join(backup_dir, "home_original.html"))
if os.path.exists("E:/PropVista_Final/static/css/app_backup.css"):
    shutil.copy2("E:/PropVista_Final/static/css/app_backup.css", os.path.join(backup_dir, "app_original.css"))
if os.path.exists("E:/PropVista_Final/static/css/navbar_backup.css"):
    shutil.copy2("E:/PropVista_Final/static/css/navbar_backup.css", os.path.join(backup_dir, "navbar_original.css"))
if os.path.exists("E:/PropVista_Final/static/js/app_backup.js"):
    shutil.copy2("E:/PropVista_Final/static/js/app_backup.js", os.path.join(backup_dir, "app_original.js"))

# Copy V7 scroll scrub states
if os.path.exists("E:/PropVista_Final/templates/home.html.v8backup"):
    shutil.copy2("E:/PropVista_Final/templates/home.html.v8backup", os.path.join(backup_dir, "home_v7_scrub.html"))
if os.path.exists("E:/PropVista_Final/static/css/app.css.v8backup"):
    shutil.copy2("E:/PropVista_Final/static/css/app.css.v8backup", os.path.join(backup_dir, "app_v7_scrub.css"))
if os.path.exists("E:/PropVista_Final/static/js/app.js.v8backup"):
    shutil.copy2("E:/PropVista_Final/static/js/app.js.v8backup", os.path.join(backup_dir, "app_v7_scrub.js"))

# Copy V8 image story states
if os.path.exists("E:/PropVista_Final/templates/home.html.videoreplacementbackup"):
    shutil.copy2("E:/PropVista_Final/templates/home.html.videoreplacementbackup", os.path.join(backup_dir, "home_v8_story.html"))
if os.path.exists("E:/PropVista_Final/static/css/app.css.videoreplacementbackup"):
    shutil.copy2("E:/PropVista_Final/static/css/app.css.videoreplacementbackup", os.path.join(backup_dir, "app_v8_story.css"))
if os.path.exists("E:/PropVista_Final/static/js/app.js.videoreplacementbackup"):
    shutil.copy2("E:/PropVista_Final/static/js/app.js.videoreplacementbackup", os.path.join(backup_dir, "app_v8_story.js"))

print("Backup archive created successfully under landing_backups/!")
