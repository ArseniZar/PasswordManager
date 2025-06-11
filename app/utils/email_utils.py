from flask_mail import Message
from flask import url_for, current_app
from ..exstesions import mail


def send_confirmation_code(email: str, code: str) -> None:
    print("good")
    msg = Message(
        subject="Код подтверждения для вашего аккаунта",
        recipients=[email],
        body=f"Здравствуйте!\n\nВаш код подтверждения: {code}\n\nСпасибо, что используете наш сервис!",
    )
    mail.send(msg)


def send_reset_email(email, reset_url):
    msg = Message(
        subject="Сброс пароля",
        recipients=[email],
        body=f"Для сброса пароля перейдите по ссылке:\n{reset_url}\n\nЕсли вы не запрашивали сброс, просто проигнорируйте это письмо.",
    )
    mail.send(msg)
