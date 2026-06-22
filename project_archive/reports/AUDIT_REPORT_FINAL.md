# PropVista — AUDIT REPORT FINAL
**Audit Date:** 2026-06-22
**Auditor:** Antigravity AI
**Scope:** Full project - Frontend, Backend, Templates, Forms, Views, URLs, Models, Context Processors, Static Assets, JavaScript, CSS, Notifications, Favorites, Visits, Inquiries, AI features, Dashboards, Property Management, Authentication, Role Permissions

---

## CRITICAL

| # | Location | Issue |
|---|----------|-------|
| C1 | `templates/properties/detail.html` L174-183 | Gallery carousel controls use Bootstrap default chevrons with no text labels. Phase 3 fix required. |
| C2 | `static/` root | `videoplayback.mp4` (64.9 MB) loose in `static/` root - orphaned, not referenced by any template. Wasted disk space. |
| C3 | `templates/home.html` L198 | Featured properties use `{{ property.area }}` but model field is `area_sqft`. Results in empty sqft in featured cards. |

---

## HIGH

| # | Location | Issue |
|---|----------|-------|
| H1 | `static/css/` | 13 backup files (*.v7backup, *.v8backup, *.v11backup, *.v12backup, *.qabackup, *_backup.*) polluting static folder. |
| H2 | `static/js/` | 7 backup JS files same issue. Must be moved to archive/. |
| H3 | `templates/` | 7 backup template files (home.html.*backup, home_backup.html) in templates root. Must be archived. |
| H4 | `templates/properties/` | `list.html.qabackup` orphan backup. |
| H5 | `properties/` | `models.py.qabackup` orphan backup. |
| H6 | `scratch/` | 49 temporary Python scripts, screenshots, JS test files. Should be moved to archive/. |
| H7 | Root dir | 4 large PNG screenshots + 6 automation JS files in project root. Should be archived. |

---

## MEDIUM

| # | Location | Issue |
|---|----------|-------|
| M1 | `templates/properties/detail.html` L745-763 | `scrollToInquiry()` uses `block: 'center'` which on mobile can scroll past the form header. Should use `block: 'start'` for better mobile UX. |
| M2 | `templates/partials/property_card.html` | Image height only controlled via CSS class with no aspect-ratio lock. On mobile some cards may render with inconsistent heights if images load at different sizes. |
| M3 | `static/images/` | 8 loose `prop-frame-*.jpg` in static/images root (leftover frame extraction artifacts). Should be archived. |
| M4 | `static/images/story-frames.videoreplacementbackup/` | Backup directory inside static. Should be archived. |
| M5 | `templates/inquiries/` | No `list.html` visible in directory listing - need to verify it exists. View renders `inquiries/list.html`. |

---

## LOW

| # | Location | Issue |
|---|----------|-------|
| L1 | `templates/base.html` | No `<meta name="robots">` or structured SEO meta. |
| L2 | `templates/partials/navbar.html` | `{% endwith %}` at line 38 is technically inside nav element but outside pv-nav-actions - `url_name` unavailable for right-side action active states. Pre-existing, no visible bug. |
| L3 | Root `.md` files | 30+ report files in project root. Only essential docs should remain. |
| L4 | `templates/properties/detail.html` L47-65 | Analytics context (`analytics.views` etc.) - if view doesn't pass `analytics` context, template silently renders 0. |
| L5 | `propvista/manage.py` | Duplicate manage.py inside propvista/ subdirectory alongside root manage.py. Harmless but confusing. |
| L6 | Root `*.v7backup` etc. | Some .md backup docs in root (FULL_BACKUP_REPORT.md etc.) - these are documentation not code, keep in place. |

---

## PHASE 2 - INQUIRY SCROLL STATUS

**WORKING** - scrollToInquiry() correctly implemented in detail.html:
- Target: `#inquiry-form-card` (the actual sidebar inquiry form)
- Has highlight animation + focus on first input
- MINOR FIX NEEDED: `block: 'center'` -> `block: 'start'` for better mobile behavior

Inquiry form contains: Name, Email, Phone, Message, Send inquiry btn, Generate Professional Inquiry btn.
All confirmed present at lines 568-609.

---

## PHASE 3 - GALLERY UX STATUS

**FIX REQUIRED** - Bootstrap default carousel chevrons need to be replaced with labeled navigation controls per specification.

Current: Default `carousel-control-prev-icon` / `carousel-control-next-icon` glyphs
Required: Text-labeled buttons like "← Previous Photo" / "Next Photo →" with photo counter

---

## PHASE 4 - IMAGE QUALITY STATUS

- All property images use `object-fit: cover` - consistent
- Gallery uses Bootstrap carousel with `h-100` - consistent height within container
- Similar properties section uses `height: 180px` inline - consistent
- Featured cards: `property.area` field reference likely wrong (should be `area_sqft`)
- Fallback images: house-01.jpg through house-08.jpg exist

---

## PHASE 5 - FRONTEND POLISH STATUS

- Property grid layout: consistent via CSS class
- Empty whitespace in home.html lines 154-157: harmless
- Inline styles scattered in detail.html: acceptable, no major alignment issues found
- Toast messages: correctly implemented in base.html

---

## PHASE 6 - FUNCTIONAL TEST RESULTS (CODE REVIEW)

| Feature | Status |
|---------|--------|
| Anonymous -> Login redirect | PASS |
| Buyer -> Buyer Dashboard | PASS |
| Seller -> Seller Dashboard | PASS |
| Admin -> Admin Dashboard | PASS |
| Send Inquiry button scroll | PASS (minor mobile improvement needed) |
| Inquiry form submit | PASS |
| Generate Professional Inquiry (AI) | PASS |
| Favorites toggle | PASS |
| Gallery navigation | PASS (UX improvement needed) |
| Notifications mark read | PASS |
| Landing page hero media | PASS (VIDEO_HERO mode active) |

---

## PHASE 7 - CLEANUP PLAN

### Files to archive (DO NOT DELETE):
- static/css/*.v7backup, *.v8backup, *.v11backup, *.v12backup, *.qabackup, *.videoreplacementbackup, *_backup.*
- static/js/*.v7backup, *.v8backup, *.v11backup, *.v12backup, *.qabackup, *.videoreplacementbackup, *_backup.*
- templates/home.html.*, templates/home_backup.html
- templates/properties/list.html.qabackup
- properties/models.py.qabackup
- favorites/views.py.qabackup
- scratch/* (all 49 files)
- Root: run_*.js, visual_validation.js, final-*.png
- static/images/prop-frame-*.jpg (8 files)
- static/images/story-frames.videoreplacementbackup/

### DO NOT MOVE:
- manage.py, requirements.txt, .env, templates/, static/, accounts/, properties/, favorites/, notifications/, visits/, reports/, propvista/

---

## FINAL SCORE (PRE-FIX)

| Category | Score |
|----------|-------|
| Auth & Permissions | 9/10 |
| Property Management | 8/10 |
| Inquiry System | 9/10 |
| Favorites | 9/10 |
| Notifications | 9/10 |
| AI Features | 8/10 |
| Landing Page | 8/10 |
| Gallery UX | 5/10 |
| Image Consistency | 7/10 |
| Dashboards | 8/10 |
| Code Cleanliness | 4/10 |
| **Overall** | **7.6/10** |
