import os
import random
from typing import Any, Optional, Union

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
)

from ..exstesions import bcrypt, db, cache ,SESSION_TOKEN_KEY_PATTERN
from ..forms import (
    ConfirmEmailForm,
    ForgotPasswordForm,
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
)
from ..models.user import User
from ..utils.email_utils import send_confirmation_code, send_reset_email
from ..utils.token_utils import (
    create_token_from_password,
    generate_reset_token_from_forgot_password,
    verify_reset_token_from_forgot_password,
)


auth: Blueprint = Blueprint("auth", __name__)



@auth.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    form: RegistrationForm = RegistrationForm()
    if form.validate_on_submit():
        email: str = form.email.data.strip()
        username: str = form.username.data.strip()
        password: str = form.password.data.strip()
        
        current_app.logger.info(f"[register] Form submitted with email={email}, username={username}")
        existing_user: Optional[User] = __get_user_by_field__('email', email)
        if existing_user:
            current_app.logger.warning(f"[register] Attempt to register with existing email: {email}")
            flash("A user with this email already exists.", "error")
            return render_template("auth/register/register.html", form=form)

        try:
            hashed_password: str = bcrypt.generate_password_hash(password).decode("utf-8")
            current_app.logger.debug(f"[register] Password hashed for email={email}")
        except Exception as e:
            current_app.logger.exception(f"[register] Error hashing password for email={email}: {e}")
            flash("Internal error while processing password. Try again.", "error")
            return render_template("auth/register/register.html", form=form)
        
        try:
            encryption_salt: bytes = os.urandom(16)
            current_app.logger.debug(f"[register] Generated encryption salt for email={email}")
        except Exception as e:
            current_app.logger.exception(f"[register] Error generating encryption salt for email={email}: {e}")
            flash("Internal error while preparing account. Try again.", "error")
            return render_template("auth/register/register.html", form=form)
        
        
        user: User = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            is_confirmed=False,
            encryption_salt=encryption_salt,
        )

        try:
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(f"User registered successfully: id={user.id}, email={user.email}")
            flash("User successfully created! Please confirm your email.", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error during registration: {e}")
            flash("Registration error. Please try again later.", "error")
            return render_template("auth/register/register.html", form=form)
        
        return redirect(url_for("auth.login"))

    return render_template("auth/register/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    form: LoginForm = LoginForm()
    current_app.logger.debug("[login] Login form instantiated")

    if form.validate_on_submit():
        email: str = form.email.data.strip()
        password: str = form.password.data.strip()
        current_app.logger.info(f"[login] Form submitted with email={email}")

        user: Optional[User] = __get_user_by_field__('email', email)
        if not user:
            current_app.logger.warning(f"[login] No user found with email={email}")
            flash("There was a problem. Please try again later.", "error")
            return render_template("auth/login/login.html", form=form)

        try:
            valid: bool = bcrypt.check_password_hash(user.password_hash, password)
            current_app.logger.debug(f"[login] Password hash checked for user_id={user.id}, valid={valid}")
        except UnicodeEncodeError as e:
            current_app.logger.error(f"[login] Encoding error in password check for user_id={user.id}: {e}")
            flash("Password format error. Please try again.", "error")
            valid = False

        if valid:
            if not user.is_confirmed:
                current_app.logger.warning(f"[login] User not confirmed: user_id={user.id}")
                flash("Please confirm your account before logging in.", "warning")
                return redirect(url_for("auth.confirm_account", user_id=user.id))

            try:
                token: Optional[str] = create_token_from_password(password, user.encryption_salt)
                if not token:
                    current_app.logger.error(f"[login] Token generation failed or empty for user_id={user.id}")
                    return redirect(url_for("auth.login"))

                session[SESSION_TOKEN_KEY_PATTERN.format(user.id)] = token
                current_app.logger.info(f"[login] Token stored in session for user_id={user.id}")

                login_user(user)
                current_app.logger.info(f"[login] User logged in successfully: user_id={user.id}")
                flash("You have successfully logged in!", "success")
                return redirect(url_for("home.index"))

            except Exception as e:
                current_app.logger.exception(f"[login] Exception during token generation for user_id={user.id}: {e}")
                flash("An unexpected error occurred during login. Please try again.", "error")
                return redirect(url_for("auth.login"))
        else:
            current_app.logger.warning(f"[login] Invalid credentials for email={email}")
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth.login"))
    else:
        if request.method == "POST":
            current_app.logger.debug("[login] Form validation failed on POST")
        else:
            current_app.logger.debug("[login] GET request - rendering login form")

    return render_template("auth/login/login.html", form=form)




# @auth.route("/forgot_password", methods=["GET", "POST"])
# def forgot_password() -> str:
#     form: ForgotPasswordForm = ForgotPasswordForm()
#     if form.validate_on_submit():
#         email: str = form.email.data.strip()
#         user: Optional[User] = __get_user_by_field__("email", email)

#         if user:
#                 try:
#                     token: str = generate_reset_token_from_forgot_password(user.id)
#                     reset_url: str = url_for("auth.reset_password", token=token, _external=True)
#                     send_reset_email(user.email, reset_url)
#                     current_app.logger.info(f"Password reset email sent to {user.email}")
#                     flash("A reset link has been sent.", "info")
#                 except Exception as e:
#                     current_app.logger.error(f"Error sending reset email to {user.email}: {e}")
#                     flash("Failed to send reset email. Please try again later.", "error")
#                     return redirect(url_for("auth.forgot_password"))
#         else:
#             flash("Email is not registered.", "info")

#         return redirect(url_for("auth.login"))

#     return render_template("auth/forgot_password/forgot_password.html", form=form)


# @auth.route("/reset_password/<token>", methods=["GET", "POST"])
# def reset_password(token: str) -> str:
#     user_id: Optional[int] = verify_reset_token_from_forgot_password(token)
#     if not user_id:
#             current_app.logger.warning(f"Invalid or expired reset token attempted: {token}")
#             flash("The reset link is invalid or has expired.", "error")
#             return redirect(url_for("auth.forgot_password"))
#     user: Optional[User] = __get_user__(user_id)
#     if not user:
#         current_app.logger.error(f"User not found for reset token user_id={user_id}")
#         flash("User not found.", "error")
#         return redirect(url_for("auth.forgot_password"))

#     form: ResetPasswordForm = ResetPasswordForm()
#     if form.validate_on_submit():
#         user.password_hash = bcrypt.generate_password_hash(
#             form.password.data.strip()
#         ).decode("utf-8")
#         db.session.commit()
#         flash("Your password has been successfully changed!", "success")
#         return redirect(url_for("auth.login"))
#     return render_template("auth/reset_password/reset_password.html", form=form)




@auth.route("/confirm/<int:user_id>", methods=["GET", "POST"])
def confirm_account(user_id: int) -> str:
    SESSION_CONFIRM_CODE_PATTERN: str = "confirm_code_{}"
    form: ConfirmEmailForm = ConfirmEmailForm()
    code_sent: bool = False

    current_app.logger.debug(f"[confirm_account] Request received for user_id={user_id} with method={request.method}")

    user: Optional[User] = __get_user_by_id__(user_id)
    if not user:
        current_app.logger.warning(f"[confirm_account] User not found: id={user_id}")
        flash("User not found.", "error")
        return redirect(url_for("auth.login"))

    if user.is_confirmed:
        flash("Your account is already confirmed.", "info")
        current_app.logger.info(f"[confirm_account] User already confirmed: id={user.id}")
        return redirect(url_for("auth.login"))

    if (
        getattr(form, "submit_send", None)
        and form.submit_send.data
        and request.method == "POST"
    ):
        code: str = str(random.randint(100000, 999999))
        session_key = SESSION_CONFIRM_CODE_PATTERN.format(user_id)
        session[session_key] = code
        current_app.logger.debug(f"[confirm_account] Generated confirmation code {code} stored in session under key {session_key}")

        try:
            send_confirmation_code(user.email, code)
            current_app.logger.info(f"[confirm_account] Confirmation code sent to email {user.email} (user_id={user.id})")
            flash("A confirmation code has been sent to your email.", "info")
            code_sent = True
        except Exception as e:
            current_app.logger.error(f"[confirm_account] Failed to send confirmation code email to {user.email}: {e}")
            flash("Failed to send confirmation code. Please try again later.", "error")

    elif (
        getattr(form, "submit_confirm", None)
        and form.submit_confirm.data
        and form.validate_on_submit()
    ):
        session_key = SESSION_CONFIRM_CODE_PATTERN.format(user_id)
        code_in_session: Optional[str] = session.get(session_key)
        code_entered: str = form.code.data.strip()
        current_app.logger.debug(
            f"[confirm_account] Confirmation attempt for user_id={user.id}: entered_code={code_entered}, session_code={code_in_session}"
        )

        if not code_in_session:
            current_app.logger.warning(f"[confirm_account] No confirmation code found in session for user_id={user.id}")

        if code_in_session and code_entered == code_in_session:
            user.is_confirmed = True
            try:
                db.session.commit()
                session.pop(session_key, None)
                current_app.logger.info(f"[confirm_account] User email confirmed successfully: user_id={user.id}")
                flash("Email successfully confirmed!", "success")
                return redirect(url_for("auth.login"))
            except SQLAlchemyError as e:
                error_message = (
                    str(e.__dict__.get("orig")) if hasattr(e, "__dict__") else str(e)
                )
                current_app.logger.error(
                    f"[confirm_account] DB commit failed during confirmation for user_id={user.id}: {error_message}"
                )
                flash(f"An error occurred while confirming your email: {error_message}", "error")
        else:
            flash("Invalid confirmation code.", "error")
            current_app.logger.warning(
                f"[confirm_account] Invalid confirmation code entered for user_id={user.id}: entered={code_entered}, expected={code_in_session}"
            )
            code_sent = True

    else:
        current_app.logger.debug(f"[confirm_account] Rendering confirmation page for user_id={user.id}")

    return render_template(
        "auth/confirm/confirm.html",
        user=user,
        form=form,
        code_sent=code_sent,
    )



@auth.route("/logout")
@login_required
def logout():
    user_id: User = current_user.id
    session.pop(SESSION_TOKEN_KEY_PATTERN.format(user_id), None)
    cache.delete(f"decrypted_passwords_{user_id}")
    logout_user()
    flash("You have been logged out.", "info")
    current_app.logger.info(f"User with id={user_id} has logged out.")
    return redirect(url_for("auth.login"))






def __get_user_by_field__(field_name: str, value: Any) -> Optional[User]:
    try:
        user: User = User.query.filter_by(**{field_name: value}).first()
        return user
    except OperationalError as e:
        current_app.logger.error(f"Database operational error: {e}")
    except IntegrityError as e:
        current_app.logger.error(f"Database integrity error: {e}")
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error: {e}")
    return None




def __get_user_by_id__(user_id: Any) -> Optional[User]:
    try:
        user = User.query.get(user_id)
        return user
    except OperationalError as e:
        current_app.logger.error(f"Database operational error: {e}")
    except IntegrityError as e:
        current_app.logger.error(f"Database integrity error: {e}")
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error: {e}")
    return None
