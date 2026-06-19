# Landing Video Hero Backup Documentation (V12)

This backup records the system state prior to replacing the image story landing media with the standard premium autoplay hero video (`C:\Users\lenovo\Downloads\videoplayback.mp4`).

---

## 🗄️ Files Backed Up
* [templates/home.html.v12backup](file:///E:/PropVista_Final/templates/home.html.v12backup)
* [static/css/app.css.v12backup](file:///E:/PropVista_Final/static/css/app.css.v12backup)
* [static/css/navbar.css.v12backup](file:///E:/PropVista_Final/static/css/navbar.css.v12backup)
* [static/js/app.js.v12backup](file:///E:/PropVista_Final/static/js/app.js.v12backup)

---

## 📺 Previous Landing State
* **Active Landing Mode**: `IMAGE_STORY` (displaying 10 mathematically curated, high-resolution visual frames with scroll cross-fading and zoom).
* **Previous Assets**:
  * `static/media/landing/image-story/story_01.jpg` to `story_10.jpg` (curated from `videoplayback (1)`).
* **Final CTA Background**: `static/images/properties/cta-bg.jpg` (twilight villa exterior shot).
* **Featured Properties Spacing & Spacers**: Modified to have refined light background (`linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%)`) with slate title and dark ghost button.

---

## ⏪ Rollback Steps
To restore the Landing Page to its V11 Cinematic Image Story state:
1. Copy the `.v12backup` files back to their active locations:
   ```powershell
   cp templates/home.html.v12backup templates/home.html
   cp static/css/app.css.v12backup static/css/app.css
   cp static/css/navbar.css.v12backup static/css/navbar.css
   cp static/js/app.js.v12backup static/js/app.js
   ```
2. Restart the server if templates or settings are cached.
