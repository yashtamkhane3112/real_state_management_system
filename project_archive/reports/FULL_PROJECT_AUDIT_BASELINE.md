# PropVista — Full Project Audit Baseline
**Generated:** 2026-06-19  
**Purpose:** Pre-audit safety snapshot documenting the state of the project before any changes.

---

## Git Branch & Status

- **Current Branch:** `main`
- **Available Branches:** `main` (active), `master`, `ui-fix-phase-2`
- **Status:** Clean — `nothing to commit, working tree clean`
- **Remote:** Up to date with `origin/main`

### Recent Commits (last 10)
| Hash | Message |
|------|---------|
| 3071d93 | Add backup and scratch files to gitignore |
| 8f04db6 | PropVista V9 landing page improvements |
| 12f8a6d | Landing page improvements, property image fallback system, dashboard routing fixes |
| cf7e38e | Landing page V2 cinematic experience and UI refinements |
| 9e7dbac | Production readiness pass: UI consistency, navbar audit, workspace standardization, homepage scale rebalance, QA validation |
| 04bca3d | Production readiness pass |
| 8250e7e | UI polish, AI insights, homepage refinements |
| d0929f9 | Fix static tag loading for homepage video |
| 9c33d1e | Replace homepage hero illustration with property.mp4 background video |
| 951c277 | Fix security audit findings, backend constraints, and test cases |

---

## Existing Backups (46 total)

### Archive ZIPs
| File | Size |
|------|------|
| `PropVista_FULL_BACKUP_BEFORE_V9.zip` | 215,655 KB (~211 MB) |
| `FULL_PROJECT_AUDIT_BACKUP.zip` *(created this session)* | ~91,986 KB (~89.8 MB) |
| `Estate.zip` | 61 KB |

### Markdown Backup Records
- `LANDING_IMAGE_STORY_BACKUP.md`
- `LANDING_PAGE_V1_BACKUP.md`
- `LANDING_VIDEO_HERO_BACKUP.md`
- `FULL_BACKUP_REPORT.md`

### Versioned File Backups (inline, in-repo)

**CSS:**
- `static/css/app.css.qabackup` (136 KB)
- `static/css/app.css.v11backup` (136 KB)
- `static/css/app.css.v12backup` (136 KB)
- `static/css/app.css.v7backup` (134 KB)
- `static/css/app.css.v8backup` (134 KB)
- `static/css/app.css.videoreplacementbackup` (134 KB)
- `static/css/app_backup.css` (101 KB)
- `static/css/navbar.css.v11backup` (18 KB) × 4 versions
- `static/css/navbar_backup.css` (15 KB)

**JS:**
- `static/js/app.js.qabackup` (49 KB)
- `static/js/app.js.v11backup` (49 KB) × 3 versions
- `static/js/app.js.v7backup` (46 KB)
- `static/js/app.js.v8backup` (43 KB)
- `static/js/app.js.videoreplacementbackup` (44 KB)
- `static/js/app_backup.js` (36 KB)

**Templates:**
- `templates/home.html.qabackup` (27 KB)
- `templates/home.html.v11backup` (27 KB) × 3 versions
- `templates/home.html.v7backup` (22 KB)
- `templates/home.html.v8backup` (22 KB)
- `templates/home.html.videoreplacementbackup` (22 KB)
- `templates/home_backup.html` (19 KB)
- `templates/properties/list.html.qabackup` (6 KB)

**Python:**
- `properties/models.py.qabackup` (12 KB)
- `favorites/views.py.qabackup` (1 KB)
- `leads/views.py.qabackup` (2 KB)
- `reports/views.py.qabackup` (4 KB)

**`landing_backups/` directory:**
- `app.css` (134 KB)
- `app.js` (41 KB)
- `home.html` (23 KB)
- `navbar.css` (18 KB)

---

## Existing Landing Page Modes (3 modes)

| Mode | Directory | Status |
|------|-----------|--------|
| `video-hero` | `static/media/landing/video-hero/` | ✅ Active (default: `LANDING_MEDIA_MODE=VIDEO_HERO`) |
| `image-story` | `static/media/landing/image-story/` | ✅ 10 story images present |
| `video-scrub` | `static/media/landing/video-scrub/` | ⚠️ Directory empty (no scrub frames present) |

### Mode switching configured via:
- `.env`: `LANDING_MEDIA_MODE=VIDEO_HERO`
- `settings.py`: `LANDING_MEDIA_MODE = env("LANDING_MEDIA_MODE", default="VIDEO_HERO")`
- `context.py`: Passed to all templates via context processor
- `home.html`: Conditional rendering via `{% if LANDING_MEDIA_MODE == "VIDEO_HERO" %}`

---

## Existing Videos

| File | Size | Location |
|------|------|----------|
| `videoplayback.mp4` | 61.9 MB | `static/videoplayback.mp4` (root static — duplicate) |
| `videoplayback.mp4` | 61.9 MB | `static/media/landing/video-hero/videoplayback.mp4` (canonical) |

**Note:** Two copies of the same video exist. The root `static/videoplayback.mp4` is a duplicate of the video-hero version.

---

## Existing Image Libraries

**Total images found: 1,119**

### Categorised image assets:
| Category | Location | Count |
|----------|----------|-------|
| Property fallback frames | `static/images/properties/fallbacks/` | ~20 JPG frames |
| Property gallery images | `static/images/properties/` | 9 house JPGs + fallbacks |
| Image story frames | `static/media/landing/image-story/` | 10 story JPGs |
| Film/story frames | `static/images/story-frames/` | Multiple frames |
| Film frames legacy | `static/images/film-frames/` | Multiple frames |
| Prop frame assets | `static/images/prop-frame-*.jpg` | 8 scattered images |
| Scratch screenshots | `scratch/*.png` | 5 large PNG files |

---

## Existing Reports (root level + reports/ directory)

### Root-level MD reports (41 files):
- `FINAL_ACCEPTANCE_REPORT.md`
- `FINAL_PLATFORM_STATUS.md`
- `FINAL_POLISH_REPORT.md`
- `FINAL_PRODUCT_QUALITY_REPORT.md`
- `FINAL_REGRESSION_REPORT.md`
- `FINAL_UX_VALIDATION_REPORT.md`
- `FUNCTIONAL_AUDIT_REPORT.md`
- `HOMEPAGE_SCALE_REBALANCE_REPORT.md`
- `HOW_TO_SWITCH_LANDING_MODE.md`
- `IMAGE_VIEWER_REPORT.md`
- `INSTALLATION_GUIDE.md`
- `LANDING_IMPLEMENTATIONS.md`
- `LANDING_PAGE_V2_REPORT.md`
- `LANDING_VIDEO_HERO_REPORT.md`
- `NAVBAR_FINAL_AUDIT.md`
- `NAVBAR_REDESIGN_REPORT.md`
- `NAVBAR_VISIBILITY_FIX_REPORT.md`
- `NAVIGATION_AUDIT_REPORT.md`
- `PRODUCTION_READINESS_PROGRESS.md`
- `PRODUCTION_READINESS_REPORT.md`
- `PROJECT_CONTEXT_FOR_AI.md`
- `PROJECT_STRUCTURE.md`
- `PROPERTY_LIFECYCLE_REPORT.md`
- `ROUTE_LAYOUT_REPORT.md`
- `SECURITY_AUDIT_REPORT.md`
- `SMTP_TEST_REPORT.md`
- `UI_POLISH_REPORT.md`
- `UI_REFINEMENT_REPORT.md`
- `VALIDATION_REPORT.md`
- `VIDEO_QUALITY_AUDIT.md`
- `WORKSPACE_UI_CONSISTENCY_REPORT.md`
- `README.md`
- `DEMO_CREDENTIALS.md`
- `EMAIL_SETUP_GUIDE.md`
- ... and more

### reports/ directory:
- `MERGE_REPORT.md`
- `PHASE2_5_AUDIT_REPORT.md`
- Plus sub-dirs: `ai_features/`, `artifacts/`, `unused_templates/`

---

## Backup ZIP Created This Session

**File:** `FULL_PROJECT_AUDIT_BACKUP.zip`  
**Size:** ~89.8 MB  
**Files zipped:** 1,742 files  
**Exclusions:** `venv/`, `node_modules/`, `.git/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `staticfiles/`, `PropVista_FULL_BACKUP_BEFORE_V9.zip`, `Estate.zip`, `db.sqlite3`, `videoplayback.mp4` (duplicate at root static)

**Recovery:** Extract `FULL_PROJECT_AUDIT_BACKUP.zip` at `E:\PropVista_Final\` to restore all source files.
