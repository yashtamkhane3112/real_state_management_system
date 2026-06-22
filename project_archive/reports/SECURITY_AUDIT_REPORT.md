# Security Audit Report: Access Control & Authorization Pass

This report documents the security audit and authorization model implementation for PropVista. Every route has been audited to enforce the required role-based access controls and prevent unauthorized actions.

---

## 1. Access Control Model

PropVista implements strict role-based access control (RBAC) across three predefined user roles: **Buyer**, **Seller**, and **Admin**. Additionally, strict limits are placed on **Anonymous Users**.

### Roles & Permission Matrix

| Route/Feature | Anonymous | Buyer | Seller | Admin |
| :--- | :---: | :---: | :---: | :---: |
| **Public Listings** | Allowed | Allowed | Allowed | Allowed |
| **Profile Page** | Blocked (302 Login) | Allowed | Allowed | Allowed |
| **Notifications Page** | Blocked (302 Login) | Allowed | Allowed | Allowed |
| **Properties Search & Detail** | Allowed | Allowed | Allowed | Allowed |
| **Favorites Toggle & View** | Blocked (302 Login) | Allowed | Blocked (403) | Allowed |
| **Seller Dashboard** | Blocked (302 Login) | Blocked (403) | Allowed | Allowed |
| **Inquiry Pipeline / Seller Favs** | Blocked (302 Login) | Blocked (403) | Allowed | Allowed |
| **Admin Dashboard** | Blocked (302 Login) | Blocked (403) | Blocked (403) | Allowed |
| **Reports & Audit Logs** | Blocked (302 Login) | Blocked (403) | Blocked (403) | Allowed |
| **Property Approve / Reject** | Blocked (302 Login) | Blocked (403) | Blocked (403) | Allowed |

---

## 2. Implementation & Enforcement

Security constraints are enforced at the view level using Django's built-in decorators and custom role-verification decorators.

### Custom Role Decorators & Mixins
Role-based constraints are implemented in [decorators.py](file:///E:/PropVista_Final/accounts/decorators.py).
* **`@login_required`**: Enforces that the user is authenticated. Anonymous users are redirected (HTTP 302) to the login view.
* **`@role_required(roles)`**: Verifies that the authenticated user has one of the allowed roles. If the user does not possess the correct role, Django raises a `PermissionDenied` exception, returning an **HTTP 403 Forbidden** status code.

### Route Audits & Decorated Views
The following critical views and URLs were audited and updated:
1. **`/reports/`**: Mapped to `reports_home` in [reports/views.py](file:///E:/PropVista_Final/reports/views.py). Decorated with `@login_required` and `@role_required(['admin'])`.
2. **`/accounts/dashboard/admin/`**: Mapped to `admin_dashboard` in [accounts/views.py](file:///E:/PropVista_Final/accounts/views.py). Decorated with `@login_required` and `@role_required(['admin'])`.
3. **`/properties/<slug>/approve/`**: Mapped to `approve_property` in [properties/views.py](file:///E:/PropVista_Final/properties/views.py). Decorated with `@login_required` and `@role_required(['admin'])`.
4. **`/properties/<slug>/reject/`**: Mapped to `reject_property` in [properties/views.py](file:///E:/PropVista_Final/properties/views.py). Decorated with `@login_required` and `@role_required(['admin'])`.
5. **`/notifications/`**: Mapped to `notification_list` in [notifications/views.py](file:///E:/PropVista_Final/notifications/views.py). Decorated with `@login_required`.
6. **`/accounts/profile/`**: Mapped to `profile` in [accounts/views.py](file:///E:/PropVista_Final/accounts/views.py). Decorated with `@login_required`.

---

## 3. Security Test Validation

Automated regression tests have been added to verify that unauthorized requests fail with HTTP 403 Forbidden.

* **Test Case**: `test_access_control_route_restrictions` inside [test_new_features.py](file:///E:/PropVista_Final/tests/test_new_features.py#L479-L502).
  * Asserts that unauthenticated users attempting to access dashboards, notifications, or profiles are redirected to the login page (HTTP 302).
  * Asserts that a **Buyer** user attempting to access the Admin reports or Admin dashboard receives **HTTP 403 Forbidden**.
  * Asserts that a **Seller** user attempting to access the Admin dashboard receives **HTTP 403 Forbidden**.
* **Status**: **PASSING** (Verified in the full `pytest` regression run).

---
*Report compiled on 2026-06-10.*
