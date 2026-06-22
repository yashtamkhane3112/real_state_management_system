# PropVista Email Configuration & Setup Guide

This guide provides instructions on how to configure and deploy SMTP-based email services for the PropVista platform. 

---

## 1. Environment Variables Configuration

PropVista uses environment variables for secure, production-ready SMTP credentials. Add the following variables to your local `.env` file:

```env
# Email SMTP Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=PropVista <your-email@example.com>
```

---

## 2. SMTP Provider Settings

### A. Gmail SMTP Configuration
To use Google's Gmail servers to send notifications:

1. **SMTP Server:** `smtp.gmail.com`
2. **Port:** `587`
3. **TLS:** Required (`EMAIL_USE_TLS=True`)
4. **App Password Setup:**
   * Go to your [Google Account settings](https://myaccount.google.com/).
   * Enable **2-Step Verification** if you haven't already.
   * Under Security, search for and select **App passwords**.
   * Generate a new app password for "Mail" (choose a custom name like "PropVista").
   * Copy the 16-character code and paste it as `EMAIL_HOST_PASSWORD` in your `.env`.

### B. Outlook / Office 365 SMTP Configuration
To use Microsoft Office 365 or Outlook:

1. **SMTP Server:** `smtp.office365.com` (or `smtp-mail.outlook.com`)
2. **Port:** `587`
3. **TLS:** Required (`EMAIL_USE_TLS=True`)
4. **Setup App Password:**
   * Go to your Microsoft Security Basics page and choose **More security options**.
   * Under **App passwords**, select **Create a new app password**.
   * Use this app password as the `EMAIL_HOST_PASSWORD` in your `.env`.

---

## 3. Graceful Fallback (Offline Mode)

If SMTP variables (`EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`) are left blank, PropVista will **not** fail or crash.
* The system automatically switches to **Mock Mail Mode**.
* Outgoing email notifications are safely logged to the application console and logs.
* Core flows (such as registration, inquiry pipeline updates, and properties creation) continue to function normally.
