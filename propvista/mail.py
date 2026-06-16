import logging
from django.core.mail import send_mail
from django.conf import settings
from django.core import signing
from django.urls import reverse

logger = logging.getLogger(__name__)

def send_templated_email(subject, message, recipient_list):
    """
    Sends an email safely using the configured Django email backend.
    """
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "PropVista <noreply@propvista.com>")
    
    # Clean and filter out empty recipients to prevent empty recipient errors
    recipient_list = [r for r in recipient_list if r and str(r).strip()]
    if not recipient_list:
        logger.warning(f"Aborted sending email '{subject}': No valid recipients.")
        return False
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {e}")
        print(f"\n--- SMTP SEND FAILURE: {e} ---")
        print(f"Attempted email to {recipient_list}: [Subject: {subject}]")
        print(f"Body:\n{message}")
        print("---------------------------------\n")
        return False

def send_welcome_email(user):
    subject = "Welcome to PropVista!"
    message = (
        f"Hi {user.first_name or user.username},\n\n"
        "Welcome to PropVista! Your account has been successfully created.\n"
        f"Your username is: {user.username}\n"
        f"Your role is: {user.get_role_display() if hasattr(user, 'get_role_display') else user.role}\n\n"
        "Thank you for choosing PropVista."
    )
    return send_templated_email(subject, message, [user.email])

def send_verification_email(request, user):
    token = signing.dumps({"user_id": user.pk, "email": user.email})
    scheme = "https" if request.is_secure() else "http"
    host = request.get_host()
    verify_url = reverse("accounts:verify_email", args=[token])
    full_url = f"{scheme}://{host}{verify_url}"
    
    subject = "Verify Your Email Address — PropVista"
    message = (
        f"Hi {user.first_name or user.username},\n\n"
        "Please verify your email address by clicking on the link below:\n"
        f"{full_url}\n\n"
        "This link will expire in 24 hours.\n\n"
        "If you did not request this, please ignore this email."
    )
    return send_templated_email(subject, message, [user.email])

def send_login_alert(user, ip=None):
    subject = "Security Alert: New Login to PropVista"
    message = (
        f"Hi {user.first_name or user.username},\n\n"
        "This is a quick notification to let you know that a new login was detected on your account.\n"
        f"Username: {user.username}\n"
        f"IP Address: {ip or 'Unknown'}\n\n"
        "If this was you, no action is needed. If you suspect unauthorized access, please reset your password immediately."
    )
    return send_templated_email(subject, message, [user.email])

def send_password_changed_email(user):
    subject = "Your PropVista Password Has Been Changed"
    message = (
        f"Hi {user.first_name or user.username},\n\n"
        "This confirms that the password for your PropVista account was changed successfully.\n\n"
        "If you performed this change, you can safely ignore this email. "
        "If you did not change your password, please contact our security team immediately."
    )
    return send_templated_email(subject, message, [user.email])

def send_security_alert(user, description):
    subject = "PropVista Account Security Alert"
    message = (
        f"Hi {user.first_name or user.username},\n\n"
        "We detected security events on your account:\n"
        f"{description}\n\n"
        "If you did not authorize this, please secure your account."
    )
    return send_templated_email(subject, message, [user.email])

def send_inquiry_received_email(inquiry):
    seller = inquiry.property.created_by
    if not seller or not seller.email:
        return False
    subject = f"New Inquiry Received for {inquiry.property.title}"
    message = (
        f"Hi {seller.first_name or seller.username},\n\n"
        f"You have received a new inquiry on your listing: '{inquiry.property.title}'\n\n"
        f"Buyer Name: {inquiry.name}\n"
        f"Buyer Email: {inquiry.email}\n"
        f"Buyer Phone: {inquiry.phone}\n"
        f"Message:\n{inquiry.message}\n\n"
        "Manage your inquiries in the Inquiry Pipeline dashboard."
    )
    return send_templated_email(subject, message, [seller.email])

def send_property_approved_email(property):
    seller = property.created_by
    if not seller or not seller.email:
        return False
    subject = f"Listing Approved: {property.title}"
    message = (
        f"Hi {seller.first_name or seller.username},\n\n"
        f"Congratulations! Your listing '{property.title}' has been reviewed and approved by the administrator.\n"
        "It is now live on the PropVista marketplace.\n"
    )
    return send_templated_email(subject, message, [seller.email])

def send_property_rejected_email(property):
    seller = property.created_by
    if not seller or not seller.email:
        return False
    subject = f"Listing Needs Revision: {property.title}"
    message = (
        f"Hi {seller.first_name or seller.username},\n\n"
        f"Your listing '{property.title}' has been reviewed and requires changes before it can be approved.\n"
        f"Rejection Reason: {property.rejection_reason or 'No reason provided.'}\n\n"
        "Please edit and resubmit your listing for review."
    )
    return send_templated_email(subject, message, [seller.email])

def send_property_favorited_email(favorite):
    seller = favorite.property.created_by
    if not seller or not seller.email:
        return False
    subject = f"New Shortlist Alert: {favorite.property.title}"
    message = (
        f"Hi {seller.first_name or seller.username},\n\n"
        f"A buyer has added your listing '{favorite.property.title}' to their wishlist!\n"
        f"Buyer: {favorite.user.username}\n"
    )
    return send_templated_email(subject, message, [seller.email])
