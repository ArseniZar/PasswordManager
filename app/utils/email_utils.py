from flask_mail import Message
from flask import url_for, current_app
from ..exstesions import mail


def send_confirmation_code(email: str, code: str) -> None:
    msg = Message(
        subject="Confirmation Code for Your Account",
        recipients=[email],
        body=f"Hello!\n\nYour confirmation code is: {code}\n\nThank you for using our service!",
    )
    mail.send(msg)


def send_reset_email(email: str, reset_url: str) -> None:
    msg = Message(
        subject="Password Reset",
        recipients=[email],
        body=f"To reset your password, click the link below:\n{reset_url}\n\nIf you did not request a password reset, simply ignore this message.",
    )
    mail.send(msg)
