# PropVista Full Project Backup Report (Pre-V9)

This document confirms the creation of a full project backup before introducing the **V9 Premium Scroll-Controlled Video Story** implementation.

---

## 🗄️ Backup Details
* **Backup File Name**: `PropVista_FULL_BACKUP_BEFORE_V9.zip`
* **Location**: Root directory of the project ([PropVista_FULL_BACKUP_BEFORE_V9.zip](file:///E:/PropVista_Final/PropVista_FULL_BACKUP_BEFORE_V9.zip))
* **Excluded Directories**: `.git`, `node_modules`, `venv`, `.pytest_cache`, `.ruff_cache`, `landing_backups` (to keep backup size optimized and avoid binary bloat)

---

## 📺 Current Landing Implementation State
* **Interchangeable Media Modes Switch**: Implemented using a setting/environment switch `LANDING_MEDIA_MODE` supporting:
  * `VIDEO_HERO` (Autoplaying loop video with overlay search panel and chips)
  * `VIDEO_SCRUB` (Video scroll scrub)
  * `IMAGE_STORY` (Twilights cross-fading image sequence)
* **Configuration Context**: Controlled dynamically via environment variables (`.env`) loaded in Django's custom context processor `propvista/context.py`.
* **Refined Final CTA Section**: Optimized background image pointing to `static/images/properties/cta-bg.jpg` (highly premium wide sunset exterior shot), with decreased overlay intensity, subtle image zoom transition on hover, premium spacing, and a glassmorphic content backplate.

---

## 🖼️ Current Assets Used
* **Hero Loop Video**: `static/media/landing/video-hero/videoplayback.mp4` (~61.9 MB, 49.87s duration).
* **Scrub Video**: `static/media/landing/video-scrub/property.mp4` (~4.25 MB, 10.00s duration).
* **Story Frames**: `static/media/landing/image-story/property_000.jpg` to `property_099.jpg` (11 high-detail frames, ~2.3 MB).
* **CTA Background Image**: `static/images/properties/cta-bg.jpg` (twilight villa exterior shot, copy of `property_099.jpg`, ~217 KB).

---

## ⏪ Rollback Steps
To restore files back to the exact pre-V9 state:
1. Extract files from `PropVista_FULL_BACKUP_BEFORE_V9.zip` into the project root directory, overwriting modifications.
2. Alternatively, restore individual modified project files from the `landing_backups/` archive:
   * Copy `landing_backups/home.html` to `templates/home.html`
   * Copy `landing_backups/app.css` to `static/css/app.css`
   * Copy `landing_backups/navbar.css` to `static/css/navbar.css`
   * Copy `landing_backups/app.js` to `static/js/app.js`

---

## 📁 Git Status Output
```text
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
	modified:   accounts/decorators.py
	modified:   accounts/views.py
	modified:   propvista/context.py
	modified:   propvista/settings.py
	modified:   static/css/app.css
	modified:   static/js/app.js
	modified:   templates/home.html
	modified:   tests/test_new_features.py

Untracked files:
	HOW_TO_SWITCH_LANDING_MODE.md
	LANDING_IMPLEMENTATIONS.md
	PropVista_FULL_BACKUP_BEFORE_V9.zip
	landing_backups/
	scratch/...
```
