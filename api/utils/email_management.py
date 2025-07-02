import random
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from ..models import OTP, EmailLink
from decouple import config


def send_otp_email(email):
    otp = str(random.randint(int(config('OTP_MIN_NUM')), int(config('OTP_MAX_NUM'))))
    OTP.objects.create(email=email, otp_code=otp)

    subject = "Your OTP for Auto Docs Account"
    from_email = config('EMAIL_HOST_USER')
    to = email
    context = {
        'otp_code': otp
    }

    html_content = render_to_string('../templates/email/forget_password.html', context)
    msg = EmailMultiAlternatives(subject, '', from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_link_email(email):

    link_obj = EmailLink(email=email)
    link_obj.save()

    subject = "Your Verification Link for Auto Docs Account"
    from_email = config('EMAIL_HOST_USER')
    to = email
    context = {
        'unique_id': link_obj.session_id,
        'user_email': email,
    }

    html_content = render_to_string('../templates/email/email_verification.html', context)
    msg = EmailMultiAlternatives(subject, '', from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()