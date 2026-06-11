# Input Validation & Quality Report — PropVista

**Date:** June 10, 2026
**OS Platform:** Windows
**Status:** PASS (All backend validations, frontend triggers, and verification scripts are fully functional)

---

## 1. Summary of Validation Rules

To ensure clean database records, high-quality inquiries, and premium user interaction, robust validation rules are applied at all layers of the PropVista platform:
* **Frontend:** Real-time sanitization, HTML5 constraint validations, and browser validation blocks (`reportValidity`).
* **Backend Forms:** ModelForm standard validation, field overrides, and custom field cleaning.
* **Backend API:** Django Rest Framework serializer validations.

---

## 2. Phone Number Validation

### Requirements
* Only digits allowed.
* Length must be exactly 10 digits.
* No letters, special characters, spaces, or symbols.
* Inline feedback displayed to users.
* Submissions blocked for invalid inputs.

### Core Implementation Locations

1. **Frontend Sanitization & Feedback:**
   * **Location:** [static/js/app.js](file:///E:/PropVista_Final/static/js/app.js#L662-L706)
   * **Action:** Matches all phone fields dynamically, strips out non-digits (`\D`) as the user types, sets `maxlength="10"` and `pattern="\d{10}"`. Attaches form submit event hooks to prevent default behavior and show inline `.phone-error-msg` elements if length is not exactly 10 digits.

2. **Backend Form Validations (`clean_phone`):**
   * **User Registration:** [accounts/forms.py:RegisterForm](file:///E:/PropVista_Final/accounts/forms.py#L21-L27)
   * **User Profile Page:** [accounts/forms.py:UserForm](file:///E:/PropVista_Final/accounts/forms.py#L57-L63)
   * **Inquiry Submission:** [inquiries/forms.py:InquiryForm](file:///E:/PropVista_Final/inquiries/forms.py#L12-L18)
   * **Lead Pipeline Forms:** [leads/forms.py:LeadForm](file:///E:/PropVista_Final/leads/forms.py#L23-L29)

3. **Backend Serializers Validation:**
   * **Accounts API:** [accounts/serializers.py](file:///E:/PropVista_Final/accounts/serializers.py#L18-L23)
   * **Inquiries API:** [inquiries/serializers.py](file:///E:/PropVista_Final/inquiries/serializers.py#L12-L17)
   * **Leads API:** [leads/api_views.py](file:///E:/PropVista_Final/leads/api_views.py#L35-L40)

---

## 3. Data Validation & Input Quality

In addition to phone numbers, other core parameters are subject to the following input quality rules:

| Field | Rule | Error Message | Frontend / HTML5 Constraints | Backend Form / Serializer |
| :--- | :--- | :--- | :--- | :--- |
| **Email** | Valid RFC-5322 structure | *Browser default* | `type="email"` | Django `EmailField` / `EmailValidator` |
| **Price** | Must be greater than 0 | "Price must be greater than 0." | `min="0.01"` `step="any"` | `clean_price()` / `validate_price()` |
| **Bedrooms** | Cannot be negative | "Bedrooms cannot be negative." | `min="0"` | `error_messages["min_value"]` / `validate_bedrooms()` |
| **Bathrooms** | Cannot be negative | "Bathrooms cannot be negative." | `min="0"` | `error_messages["min_value"]` / `validate_bathrooms()` |
| **Area (Sqft)**| Must be greater than 0 | "Area must be greater than 0." | `min="1"` | `clean_area_sqft()` / `validate_area_sqft()` |

---

## 4. Verification & Testing

### 1. Automated Regression Suite (Pytest)
All 31 existing tests in the suite compile and pass:
```bash
venv\Scripts\pytest
```
**Output:**
```
collected 31 items
properties/tests.py ........                                             [ 25%]
tests/test_core.py ....                                                  [ 38%]
tests/test_new_features.py ...................                           [100%]
============================= 31 passed in 24.92s =============================
```

### 2. Manual/Integration Validation Verification Script
The validation verification script simulates client requests with invalid inputs to ensure they are blocked at the Django Form level:
```bash
venv\Scripts\python.exe scratch/verify_validation.py
```
**Output:**
```
--- STARTING VALIDATION TESTS ---

[Phone Validation Checks]
  Register with phone '123': REJECTED (PASS)
  Register with phone 'abcd123456': REJECTED (PASS)
  Register with phone '98765': REJECTED (PASS)
  Register with phone '987654321012': REJECTED (PASS)
  Register with phone '98-7654-3210': REJECTED (PASS)
  Register with phone '98765 43210': REJECTED (PASS)

[Property Field Validation Checks]
  Price = 0: REJECTED (PASS)
  Bedrooms = -1: REJECTED (PASS)
  Bathrooms = -2: REJECTED (PASS)
  Area = 0: REJECTED (PASS)

--- VALIDATION TESTS COMPLETE ---
```

---

## 5. Image Size Policy Compliance

In accordance with the directive **"DO NOT LIMIT IMAGE SIZE"**, all previous file-size limitation checks on cover images and gallery photo uploads have been removed from backend validator forms.
* **Frontend Handling:** Uploaded images of all file sizes are permitted and auto-fitted dynamically to cards and detail carousels utilizing modern responsive aspect ratios (`object-fit: cover` and `object-fit: contain` classes) to prevent stretching, distortion, or overflow.
* **Form Validation:** Form verification processes images of any size without blocking.
