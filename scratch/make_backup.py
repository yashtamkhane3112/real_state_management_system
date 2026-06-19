import os
import zipfile

def zip_project():
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    zip_path = os.path.join(project_dir, "PropVista_FULL_BACKUP_BEFORE_V9.zip")
    
    print(f"Creating backup zip at: {zip_path}")
    print(f"Project directory: {project_dir}")
    
    ignored_dirs = {"node_modules", "venv", ".git", ".pytest_cache", ".ruff_cache", "landing_backups"}
    ignored_files = {"PropVista_FULL_BACKUP_BEFORE_V9.zip"}
    
    count = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            # Modify dirs in-place to prevent walking ignored directories
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            
            for file in files:
                if file in ignored_files:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_dir)
                
                # Check file size to avoid zipping massive binary files if any (e.g. video files > 100MB, but let's zip what's there)
                # Let's zip the files. We can skip the zip file itself.
                zipf.write(file_path, arcname)
                count += 1
                if count % 200 == 0:
                    print(f"Zipped {count} files...")
                    
    print(f"Backup created successfully! Total files zipped: {count}")

if __name__ == "__main__":
    zip_project()
