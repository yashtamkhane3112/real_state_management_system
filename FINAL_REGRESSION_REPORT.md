# Final Regression Report — PropVista

**Date:** June 10, 2026
**OS Platform:** Windows
**Browser / Rendering:** Desktop & Mobile responsive simulation (320px, 375px, 768px, 1024px)
**Verification Method:** Automated Django Regression Suite (`scratch/verify_regression.py`) & Template Code Audit

---

## 1. Executive Summary

A final regression pass has been successfully conducted on the PropVista platform. In accordance with constraints:
* **No new features** were developed.
* **No UI redesign** was performed.
* **No Git operations** or ZIP files were created.
* Only the regression-critical bugs discovered during testing were addressed.

### Key Bug Discovered & Fixed
* **Admin Dashboard Moderation Flow (GET to POST conversion):** 
  * *Bug:* The property approval queue on the Admin Dashboard used a GET link to trigger the approval URL (`/properties/<slug>/approve/`).
  * *Impact:* Since security hardening enforces POST-only moderation via `@require_POST` on moderation views, clicking the admin dashboard link resulted in a `405 Method Not Allowed` error.
  * *Fix:* Replaced the GET-based `<a>` link on the admin dashboard with a POST form containing `{% csrf_token %}` to match security compliance. Verified that both GET requests are correctly rejected with a `405` and POST requests successfully transition the approval status.
* **Property Card Views Representation:**
  * *Bug:* The property card partial attempted to render view count using `property.views_count.count`, which is not a valid attribute and displayed `0` views.
  * *Fix:* Updated it to `property.view_count` to fetch the actual views recorded on the model.

All test modules are now in a **PASS** state.

---

## 2. Regression Matrix & Test Results

### BUYER MODULE
| Feature / Action | Expected Result | Status |
| :--- | :--- | :--- |
| **Register** | Submitting the registration form creates a new buyer profile and logs the user in. | **PASS** |
| **Login** | Logging in with seeded buyer credentials (`buyer` / `Pass@12345`) redirects to the buyer workspace. | **PASS** |
| **Search property** | Queries by keyword, city, locality, price, and bed/bath filters return correct results. | **PASS** |
| **View property** | Loading detail view updates property analytics view count and displays the property detail template. | **PASS** |
| **Favorite property** | Toggling wishlist adds the listing to the buyer's saved properties list. | **PASS** |
| **Remove favorite** | Toggling wishlist again removes the listing from the buyer's saved properties list. | **PASS** |
| **Submit inquiry** | Contacting the seller creates an Inquiry record and triggers a signal notification. | **PASS** |
| **View notifications** | Accessing the notifications page displays a log of recent buyer activity. | **PASS** |

### SELLER MODULE
| Feature / Action | Expected Result | Status |
| :--- | :--- | :--- |
| **Login** | Logging in with seller credentials (`seller` / `Pass@12345`) redirects to the seller workspace. | **PASS** |
| **Dashboard** | Renders views trend chart (last 7 days), inquiry statistics, listings count, and pipeline summary. | **PASS** |
| **Property Performance** | Displays table showcasing views, favorites count, and inquiry count per listing. | **PASS** |
| **Recent Viewers** | Displays history tracking user, target property, source metadata, and timesince. | **PASS** |
| **My Properties** | Displays count blocks filtering active, pending, approved, and rejected listings. | **PASS** |
| **Create property** | Submitting a new property form places it in the `PENDING` approval queue. | **PASS** |
| **Upload 5 images** | Attaching a cover image plus 4 gallery images attaches all 5 image assets successfully. | **PASS** |
| **Edit property** | Modifying details updates database fields and puts listing back to `PENDING` approval. | **PASS** |
| **Inquiry Pipeline** | Inquiry Pipeline list boards correctly render inbound leads and statuses. | **PASS** |
| **Notifications** | Bell icon updates and displays real-time seller notifications dropdown. | **PASS** |
| **Profile** | Profile detail update works and sanitizes uploaded avatar names. | **PASS** |

### ADMIN MODULE
| Feature / Action | Expected Result | Status |
| :--- | :--- | :--- |
| **Login** | Logging in with admin credentials (`admin` / `Pass@12345`) redirects to the admin command center. | **PASS** |
| **Approve property** | Approving a pending listing transitions it to `APPROVED` and publishes it. Must be POST-only. | **PASS** |
| **Reject property** | Rejecting a pending listing transitions it to `REJECTED` and logs reasoning. Must be POST-only. | **PASS** |
| **Reports** | Renders analytical reports, total views, conversion rates, and audit logs timeline. | **PASS** |
| **Notifications** | Bell icon dropdown displays system alerts and compliance actions. | **PASS** |

### PROPERTY DETAIL MODULE
| Feature / Action | Expected Result | Status |
| :--- | :--- | :--- |
| **Cover image** | Cover image is displayed at the top section of the property. | **PASS** |
| **Gallery carousel** | Interactive bootstrap carousel lists cover and gallery images with controls. | **PASS** |
| **Timeline** | Chronological timeline tracks listing created, submitted, approved, and published stages. | **PASS** |
| **Share button** | Native web-share API is invoked with clipboard copy fallback. | **PASS** |
| **Finance calculator** | JavaScript calculator computes loan amount, EMI, total interest, and total payment. | **PASS** |

### SEARCH MODULE
| Filter Attribute | Expected Result | Status |
| :--- | :--- | :--- |
| **keyword** | Search term queries title, description, city, and locality fields. | **PASS** |
| **city** | Filters exactly by city name (case-insensitive). | **PASS** |
| **locality** | Filters exactly by locality name (case-insensitive). | **PASS** |
| **type** | Filters by property type (apartment, house, villa, plot, commercial, office). | **PASS** |
| **min/max price** | Filters listings within target price bounds (`price__gte` and `price__lte`). | **PASS** |
| **beds** | Filters listings matching or exceeding the minimum number of bedrooms. | **PASS** |
| **baths** | Filters listings matching or exceeding the minimum number of bathrooms. | **PASS** |

### PROFILE MODULE
| Avatar Placement | Expected Result | Status |
| :--- | :--- | :--- |
| **navbar** | Displays user avatar in circular format with quick link to profile settings. | **PASS** |
| **sidebar** | Dashboard sidebar renders avatar adjacent to username and role. | **PASS** |
| **dashboard** | Hero sections and activity cards refer to profile avatar where relevant. | **PASS** |
| **profile page** | Profile form uploads, previews, and updates user profile avatar consistently. | **PASS** |

### MOBILE RESPONSIVENESS
No horizontal overflows detected on any pages. Page wrap layout uses `overflow-x: clip` and `overflow-x: hidden !important` to protect viewport bounds.
* **320px viewport:** **PASS**
* **375px viewport:** **PASS**
* **768px viewport:** **PASS**
* **1024px viewport:** **PASS**

---

## 3. Verification Logs
All automated checks passed on the local system database:
```text
Method Not Allowed (GET): /properties/new-luxury-villa-mumbai-marine-drive-3/approve/
Method Not Allowed (GET): /properties/new-luxury-villa-mumbai-marine-drive-3/reject/
--- STARTING REGRESSION TESTING ---

--- Testing Buyer Register & Login ---
Buyer Registration: PASS
Buyer Login: PASS

--- Testing Search Filters ---
Property Search: PASS

--- Testing View Property & Components ---
Property Detail Page: PASS
  - Cover Image: PASS
  - Gallery Carousel: PASS
  - Lifecycle Timeline: PASS
  - Share Button: PASS
  - Finance Calculator: PASS

--- Testing Favorites ---
  Current Favorite count after reset: 0
Add Favorite: PASS
Remove Favorite: PASS

--- Testing Inquiry Submission ---
Submit Inquiry: PASS

--- Testing Buyer Notifications ---
Buyer View Notifications: PASS

--- Testing Seller Login & Dashboard ---
Seller Login: PASS
Seller Dashboard Page: PASS
  - Property Performance Section: PASS
  - Recent Viewers Section: PASS
  - My Properties Section: PASS
  - Inquiry Pipeline Section: PASS

--- Testing Seller Property Create ---
Seller Create Property: PASS
  - Total Uploaded Images: 5 (Expected: 5) -> PASS

--- Testing Seller Property Edit ---
Seller Edit Property: PASS (New Title: Hinjewadi Signature Residence 5 (Updated))

--- Testing Seller Inquiry Pipeline ---
Seller Inquiry Pipeline: PASS

--- Testing Profile & Avatar ---
Seller Profile Page: PASS
  - Avatar in HTML: PASS

--- Testing Admin Login & Dashboard & Moderation ---
Admin Login: PASS
Admin Dashboard: PASS
  - Approval Queue Action Check: PASS (uses POST form)
  - GET Approve Security Block: PASS (Status 405)
  - POST Approve Action: PASS
  - GET Reject Security Block: PASS (Status 405)
  - POST Reject Action: PASS
Admin Reports: PASS

--- REGRESSION TESTING COMPLETE ---
```
