# SMTP Authentication & Email Pass: Test Report

This report documents the verification and testing of the SMTP email dispatch implementation across the PropVista platform.

---

## 1. SMTP Email Configurations

PropVista supports environment-variable-based configuration for both Gmail and Outlook SMTP relays, with a graceful console/log mockup fallback if SMTP settings are not configured or fail to connect.

### Supported Configuration Keys

* **`EMAIL_BACKEND`**: Defaults to Django's standard SMTP backend.
* **`EMAIL_HOST`**: SMTP host server (e.g. `smtp.gmail.com` or `smtp-mail.outlook.com`).
* **`EMAIL_PORT`**: Typically `587` for TLS or `465` for SSL.
* **`EMAIL_USE_TLS`**: Enabled (`True`) for encrypted communication.
* **`EMAIL_HOST_USER`**: Sender credential / username.
* **`EMAIL_HOST_PASSWORD`**: App-specific password or account passcode.
* **`DEFAULT_FROM_EMAIL`**: Display name and sender address (e.g., `PropVista <noreply@propvista.com>`).

---

## 2. Integrated Email Flow Event Coverage

The email manager module located in [mail.py](file:///E:/PropVista_Final/propvista/mail.py) constructs and sends responsive plaintext templated emails.

### Flow Events & Handlers

1. **Registration Welcome Email**:
   * **Trigger**: Triggered immediately upon new user registration inside the signup views.
   * **Handler**: `send_welcome_email(user)` in [mail.py](file:///E:/PropVista_Final/propvista/mail.py#L47-L56).

2. **Email Verification Link**:
   * **Trigger**: Registration & when email changes in profile.
   * **Handler**: `send_verification_email(request, user)` in [mail.py](file:///E:/PropVista_Final/propvista/mail.py#L58-L73).
   * **Verification Link**: Encodes user metadata using Django's cryptographically signed dump token: `signing.dumps({"user_id": user.pk, "email": user.email})`.

3. **Login Security Alert**:
   * **Trigger**: User signs into a session.
   * **Handler**: `send_login_alert(user, ip)` in [mail.py](file:///E:/PropVista_Final/propvista/mail.py#L75-L84).

4. **Password Reset Email**:
   * **Trigger**: Triggered via Django's default password reset pipeline.
   * **Template Override**: Configured to send custom instructions with cryptographic reset tokens.

5. **Password Changed Confirmation**:
   * **Trigger**: Password changes successfully via the profile page form.
   * **Handler**: `send_password_changed_email(user)` in [mail.py](file:///E:/PropVista_Final/propvista/mail.py#L86-L94).

6. **Marketplace Inquiry Received**:
   * **Trigger**: A buyer submits an inquiry on a listing.
   * **Handler**: `send_inquiry_received_email(inquiry)` in [mail.py](file:///E:/PropVista_Final/propvista/mail.py#L121-L138). Sends details to the seller.

7. **Property Approval/Rejection Notifications**:
   * **Trigger**: An Admin approves/rejects a listing.
   * **Handlers**: `send_property_approved_email(property)` and `send_property_rejected_email(property, reason)` in [mail.py](file:///E:/PropVista_Final/propvista/mail.py#L102-L119). Sends updates to the property owner.

---

## 3. Automated Test Summary

Verification tests have been implemented to ensure that the Django mail system intercepts, constructs, and routes messages correctly to `mail.outbox`.

| Test Class / Name | Target Flow | Expected Interceptions | Result |
| :--- | :--- | :---: | :---: |
| `test_registration_sends_emails` | Registration Signup | Welcome & Verification emails | **PASS** |
| `test_password_reset_views_and_emails` | Forgot Password form | Reset link token email | **PASS** |
| `test_email_change_triggers_verification` | Profile Email update | Re-verification token email | **PASS** |
| `test_verify_email_flow` | Verification URL | User is_verified -> `True` | **PASS** |

*All verification tests have run and passed successfully in the main pytest runner suite.*

---
*Report compiled on 2026-06-10.*
