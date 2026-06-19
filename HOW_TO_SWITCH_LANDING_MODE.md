# How to Switch Landing Media Mode

PropVista supports four different immersive homepage layouts out of the box, controlled by a single configuration switch. 

This guide details the procedure to safely switch between modes in under 2 minutes.

---

## ⚙️ Configuration Switch Details

The active mode is determined by the `LANDING_MEDIA_MODE` environment variable in the root `.env` file.

Supported Values:
* `VIDEO_SCROLL_STORY` (Mode D, Default: Premium scroll-controlled video story)
* `VIDEO_HERO` (Mode A: Autoplay video background overlaying search form)
* `VIDEO_SCRUB` (Mode B: Scroll-interactive scrub video of property clip)
* `IMAGE_STORY` (Mode C: Scroll-interactive cinematic cross-fade photo sequence)


---

## 🔄 Switching Procedure (3 Steps)

### Step 1: Change the Configuration in `.env`
Open your root [.env](file:///E:/PropVista_Final/.env) file and locate/edit `LANDING_MEDIA_MODE`.

Example (to switch to `IMAGE_STORY`):
```ini
# Landing page media configuration mode
LANDING_MEDIA_MODE=IMAGE_STORY
```

### Step 2: Restart the Development Server
If you are running the server locally, stop it using `Ctrl+C` and start it again:
```powershell
# In PowerShell:
.\venv\Scripts\python manage.py runserver
```
*(Django reads settings on startup; a restart is required to load environment changes into Django settings memory).*

### Step 3: Verify the Homepage
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your web browser and verify:
1. The correct media block loads.
2. The browser console has no errors.
3. No layout shifts or broken assets exist.

---

## ⏪ Rollback Instructions

If you encounter any layout issues or visual errors:
1. Revert `LANDING_MEDIA_MODE` in [.env](file:///E:/PropVista_Final/.env) to `VIDEO_HERO` (the default verified state).
2. Restart the server.
3. If files need full rollback, copy the respective files from the [landing_backups/](file:///E:/PropVista_Final/landing_backups/) directory back to their destinations:
   * `landing_backups/home.html` -> `templates/home.html`
   * `landing_backups/app.css` -> `static/css/app.css`
   * `landing_backups/navbar.css` -> `static/css/navbar.css`
   * `landing_backups/app.js` -> `static/js/app.js`
