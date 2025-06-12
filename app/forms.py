from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, URL


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required"),
            Length(
                min=3, max=25, message="Username must be between 3 and 25 characters"
            ),
        ],
        render_kw={"placeholder": "Example: john_doe"},
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Invalid email address"),
        ],
        render_kw={"placeholder": "Example: john@example.com"},
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required"),
            Length(min=6, max=100, message="Password must be at least 6 characters"),
        ],
        render_kw={"placeholder": "Enter your password"},
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password"),
            EqualTo("password", message="Passwords must match"),
        ],
        render_kw={"placeholder": "Re-enter your password"},
    )
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Example: john@example.com"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter your password"},
    )
    submit = SubmitField("Sign In")


class ConfirmEmailForm(FlaskForm):
    code = StringField(
        "Confirmation Code",
        validators=[Length(min=4, max=8)],
        render_kw={"placeholder": "Example: 123456"},
    )
    submit_send = SubmitField("Send Code")
    submit_confirm = SubmitField("Confirm")


class ForgotPasswordForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Example: john@example.com"},
    )
    submit = SubmitField("Send Reset Link")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=6)],
        render_kw={"placeholder": "Enter new password"},
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password")],
        render_kw={"placeholder": "Re-enter new password"},
    )
    submit = SubmitField("Reset Password")


class CreatePasswordForm(FlaskForm):
    site = StringField(
        "Site",
        validators=[DataRequired(), Length(max=120)],
        render_kw={"placeholder": "Example: Gmail, Amazon, Facebook"},
    )
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(max=120)],
        render_kw={"placeholder": "Example: john.doe123"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=4)],
        render_kw={"placeholder": "Enter a secure password"},
    )
    url = URLField(
        "URL",
        validators=[DataRequired(message="URL is required"), URL(), Length(max=255)],
        render_kw={"placeholder": "Example: https://www.gmail.com"},
    )
    comments = TextAreaField(
        "Comments",
        validators=[Optional(), Length(max=500)],
        render_kw={"placeholder": "Any additional notes..."},
    )
    submit = SubmitField("Save")


class EditPasswordForm(FlaskForm):
    site = StringField("Site", validators=[DataRequired(), Length(min=1, max=100)])
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=1, max=100)]
    )
    password = StringField(
        "Password", validators=[DataRequired(), Length(min=1, max=100)]
    )
    url = StringField("URL", validators=[Optional(), URL(), Length(max=200)])
    comments = TextAreaField("Comments", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Update Password")
