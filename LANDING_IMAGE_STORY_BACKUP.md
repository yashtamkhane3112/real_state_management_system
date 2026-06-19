# Landing Image Story Backup (V11)

This backup records the system state prior to replacing the landing page media with the new image story experience using frames extracted from `C:\Users\lenovo\Downloads\videoplayback (1)`.

---

## 🗄️ Files Backed Up
* [templates/home.html.v11backup](file:///E:/PropVista_Final/templates/home.html.v11backup) (copy of `templates/home.html`)
* [static/css/app.css.v11backup](file:///E:/PropVista_Final/static/css/app.css.v11backup) (copy of `static/css/app.css`)
* [static/css/navbar.css.v11backup](file:///E:/PropVista_Final/static/css/navbar.css.v11backup) (copy of `static/css/navbar.css`)
* [static/js/app.js.v11backup](file:///E:/PropVista_Final/static/js/app.js.v11backup) (copy of `static/js/app.js`)

---

## 📺 Previous Landing State
* **Active Mode**: `VIDEO_SCROLL_STORY` (Mode D, utilizing linear interpolation on scroll over `600vh` to update `videoplayback.mp4` currentTime at 60 FPS).
* **Other Supported Modes**:
  * `VIDEO_HERO` (Autoplaying background video)
  * `VIDEO_SCRUB` (10-second scroll scrub video)
  * `IMAGE_STORY` (11-image cross-fade scroll sequence)

---

## ⏪ Rollback Instructions
To restore the previous landing page state:
1. Copy the `.v11backup` files back to their active locations:
   * Copy `templates/home.html.v11backup` to `templates/home.html`
   * Copy `static/css/app.css.v11backup` to `static/css/app.css`
   * Copy `static/css/navbar.css.v11backup` to `static/css/navbar.css`
   * Copy `static/js/app.js.v11backup` to `static/js/app.js`
2. Restart the Django development server to reload template contexts.
