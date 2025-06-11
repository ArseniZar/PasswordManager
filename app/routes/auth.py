import random
import os
from typing import Optional
from flask import (
    Blueprint,
    session,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError
from ..forms import (
    RegistrationForm,
    LoginForm,
    ConfirmEmailForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from ..exstesions import bcrypt, db, cache
from ..models.user import User
from ..utils.token_utils import (
    generate_reset_token,
    verify_reset_token,
    create_token_from_password,
)
from ..utils.email_utils import send_confirmation_code, send_reset_email

auth: Blueprint = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register() -> str:
    """Handle user registration."""
    form: RegistrationForm = RegistrationForm()
    if form.validate_on_submit():
        existing_user: Optional[User] = User.query.filter_by(
            email=form.email.data.strip()
        ).first()
        if existing_user:
            flash("A user with this email already exists.", "error")
            return render_template("auth/register/register.html", form=form)

        hash_password: str = bcrypt.generate_password_hash(
            form.password.data.strip()
        ).decode("utf-8")
        encryption_salt: bytes = os.urandom(16)

        user: User = User(
            username=form.username.data.strip(),
            email=form.email.data.strip(),
            password_hash=hash_password,
            is_confirmed=False,
            encryption_salt=encryption_salt,
        )
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("auth.login"))
        except SQLAlchemyError as e:
            current_app.logger.error(str(e))
            flash("Registration error. Please try again later.", "error")

    return render_template("auth/register/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login() -> str:
    form: LoginForm = LoginForm()
    if form.validate_on_submit():
        user: Optional[User] = User.query.filter_by(
            email=form.email.data.strip()
        ).first()
        if user and bcrypt.check_password_hash(
            user.password_hash, form.password.data.strip()
        ):
            if not user.is_confirmed:
                flash("Please confirm your account before logging in", "warning")
                return redirect(url_for("auth.confirm_account", user_id=user.id))
            login_user(user)
            flash("You have successfully logged in!", "success")
            session[f"token_from_password_{user.id}"] = create_token_from_password(
                form.password.data.strip(), user.encryption_salt
            )
            return redirect(url_for("home.index"))
        else:
            flash("Invalid email or password", "error")
    return render_template("auth/login/login.html", form=form)


@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password() -> str:
    """Handle password reset requests."""
    form: ForgotPasswordForm = ForgotPasswordForm()
    if form.validate_on_submit():
        user: Optional[User] = User.query.filter_by(
            email=form.email.data.strip()
        ).first()
        if user:
            token: str = generate_reset_token(user.id)
            reset_url: str = url_for("auth.reset_password", token=token, _external=True)
            send_reset_email(user.email, reset_url)
        flash("If this email exists, a reset link has been sent.", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/forgot_password/forgot_password.html", form=form)


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token: str) -> str:
    user_id: Optional[int] = verify_reset_token(token)
    if not user_id:
        flash("The reset link is invalid or has expired.", "error")
        return redirect(url_for("auth.forgot_password"))
    user: Optional[User] = User.query.get(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("auth.forgot_password"))
    form: ResetPasswordForm = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = bcrypt.generate_password_hash(
            form.password.data.strip()
        ).decode("utf-8")
        db.session.commit()
        flash("Your password has been successfully changed!", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password/reset_password.html", form=form)


@auth.route("/confirm/<int:user_id>", methods=["GET", "POST"])
def confirm_account(user_id: int) -> str:
    """Handle email confirmation for a user."""
    user: User = User.query.get_or_404(user_id)
    if user.is_confirmed:
        flash("Your account is already confirmed.", "info")
        return redirect(url_for("auth.login"))
    form: ConfirmEmailForm = ConfirmEmailForm()
    code_sent: bool = False

    if (
        getattr(form, "submit_send", None)
        and form.submit_send.data
        and request.method == "POST"
    ):
        code: str = str(random.randint(100000, 999999))
        session[f"confirm_code_{user_id}"] = code
        send_confirmation_code(user.email, code)
        flash("A confirmation code has been sent to your email.", "info")
        code_sent = True

    elif (
        getattr(form, "submit_confirm", None)
        and form.submit_confirm.data
        and form.validate_on_submit()
    ):
        code_in_session: Optional[str] = session.get(f"confirm_code_{user_id}")
        if code_in_session and form.code.data.strip() == code_in_session:
            user.is_confirmed = True
            db.session.commit()
            session.pop(f"confirm_code_{user_id}", None)
            flash("Email successfully confirmed!", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("Invalid confirmation code.", "error")
            code_sent = True

    return render_template(
        "auth/confirm/confirm.html", user=user, form=form, code_sent=code_sent
    )


@auth.route("/logout")
@login_required
def logout():
    user_id = current_user.id
    session.pop(f"token_from_password_{user_id}", None)
    cache.delete(f"decrypted_passwords_{user_id}")
    logout_user()
    return redirect(url_for("auth.login"))
