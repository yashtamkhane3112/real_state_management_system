# PropVista Landing Page V1 Backup Documentation

This file documents the backups created and the original landing page structure before initiating the Landing Page V2 Redesign.

## Backed Up Files

The following files have been copied in their original state for safety:
1. **Homepage Template:**
   * Original: `templates/home.html`
   * Backup: `templates/home_backup.html`
2. **Application CSS Stylesheet:**
   * Original: `static/css/app.css`
   * Backup: `static/css/app_backup.css`
3. **Navbar Stylesheet:**
   * Original: `static/css/navbar.css`
   * Backup: `static/css/navbar_backup.css`
4. **Application Script:**
   * Original: `static/js/app.js`
   * Backup: `static/js/app_backup.js`

---

## Original Hero Structure

* **Container:** `<section class="pv-hero pm-hero">`
* **Background Asset:** Video tag `<video class="pv-hero-canvas">` looping `static/property.mp4`.
* **Content Wrapper:** `<div class="container pv-hero-content pm-hero-content">` inside which a `.pm-hero-copy` layout is used.
* **Header & Eyebrow:**
  * Eyebrow: `INTELLIGENT PROPERTY PLATFORM` with building icon.
  * H1: `Real Estate Operations Unified.`
  * Paragraph: `Discover, manage, and close premium property opportunities from one intelligent platform.`
* **Feature Chips:** Row containing:
  * `AI Recommendations` (bi-cpu)
  * `Lifecycle Tracking` (bi-arrow-repeat)
  * `Advanced Analytics` (bi-graph-up-arrow)
* **Search Form:** `<form class="pm-command-search pv-glass">` containing input fields for Location, Asset Type, and Budget.
* **Filter Quick Links:** Popular quick links chip set below the search bar.

---

## Original Landing Page Sections

The V1 landing page consists of the following sections:

1. **Cinematic Hero (`.pm-hero`):** Contains the background video loop, title text, operations chips, search widget, and quick filter links.
2. **Operations Overview (`.pv-section`):** Dashboard card displaying real-time counters (Properties, Inquiry Pipeline, Site Visits, Pending Approvals, Revenue Pipeline), recent activity timeline, and quick links to create properties, approve listings, and view pipelines.
3. **Operations Band (`.pm-ops-band`):** List, Approve, Convert, and Report operations cards outlining the system lifecycle.
4. **Featured Properties (`.pm-featured-section`):** A carousel slider (using Swiper.js) presenting cards for premium properties.
5. **Stakeholder Workspaces & Analytics (`.pv-section-sm`):** Double-column grid. Left column has a Portfolio Command View displaying analytics charts and logs. Right column showcases role-based dashboard shortcuts (Buyer, Seller, Admin).
6. **City Intelligence (`.pm-city-section`):** Grid showing cities covered by PropVista along with active listing counts.
7. **Final CTA (`.pm-final-cta`):** Call-to-action module prompting users to "Deploy the workspace" with "Create account" and "View properties" options.
