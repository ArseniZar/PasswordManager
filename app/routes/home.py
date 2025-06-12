from typing import Any, Dict, List, Optional
from faker import Faker
from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_required, current_user
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
)
from ..models.user import User
from ..models.passwords import Passwords
from ..exstesions import db, cache, SESSION_TOKEN_KEY_PATTERN
from ..utils.cpypto_utils import encrypt_data, decrypt_data
from ..utils.search_utils import search_passwords
from ..utils.csv_utils import export_passwords_to_csv , parse_csv, merge_passwords
from ..forms import (
    CreatePasswordForm,
    EditPasswordForm
)

DECRYPTED_PASSWORDS_CACHE_KEY = "decrypted_passwords_{}"
home = Blueprint("home", __name__)



@home.route("/home", methods=["GET", "POST"])
@login_required
def index() -> str | Response:
    user_id: int = current_user.id
    current_app.logger.debug(f"[home.index] Request by user_id={user_id}")

    token: Optional[str] = session.get(SESSION_TOKEN_KEY_PATTERN.format(user_id))

    if not token:
        current_app.logger.warning(f"[home.index] Session token missing or invalid for user_id={user_id}")
        return redirect(url_for("auth.login"))

    try:
        passwords: List[Dict[str, Any]] = __get_cached_decrypted_passwords__(current_user, token)
        current_app.logger.debug(f"[home.index] Retrieved {len(passwords)} passwords for user_id={user_id}")
    except Exception as e:
        current_app.logger.error(f"[home.index] Error retrieving passwords for user_id={user_id}: {e}")
        flash("An error occurred while loading your passwords.", "error")
        passwords = []

    return render_template("home/home.html",passwords=passwords, )


@home.route("/create_password", methods=["GET", "POST"])
@login_required
def create_password() -> str:
    user_id: int = current_user.id
    form: CreatePasswordForm = CreatePasswordForm()
    if form.validate_on_submit():
        token: Optional[str] = session.get(SESSION_TOKEN_KEY_PATTERN.format(user_id))
        if not token:
            current_app.logger.warning(f"[home.create_password] Session token missing for user_id={user_id}")
            return redirect(url_for("auth.login"))

        try:
            encrypted_login: str = encrypt_data(form.username.data, token)
            encrypted_password: str = encrypt_data(form.password.data, token)
        except Exception as e:
            current_app.logger.error(f"[home.create_password] Encryption failed for user_id={user_id}: {e}")
            flash("An error occurred while encrypting your data. Please try again.", "error", )
            return render_template("home/create_password/create_password.html", form=form)

        url: str = form.url.data.strip()
        description: str = form.comments.data.strip() if form.comments.data else ""
        site: str = form.site.data.strip()

        new_password: Passwords = Passwords(
            url=url,
            login=encrypted_login,
            password=encrypted_password,
            description=description,
            user_id=user_id,
            site=site,
        )

        try:
            db.session.add(new_password)
            db.session.commit()
            current_app.logger.info(f"[home.create_password] Password successfully added for user_id={user_id}, password_id={new_password.id}")
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error( f"[home.create_password] Database error while adding password for user_id={user_id}: {e}")
            flash("An error occurred while adding the password. Please try again later.","error",)
            return render_template("home/create_password/create_password.html", form=form)

        cache.delete(f"decrypted_passwords_{user_id}")
        flash("Password was added successfully!", "success")
        return redirect(url_for("home.index"))
    return render_template("home/create_password/create_password.html", form=form)


@home.route("/search", methods=["POST"])
@login_required
def search() -> 'Response':
    query: str = request.json.get("q", "")
    user_id: int = current_user.id
    token_key: str = SESSION_TOKEN_KEY_PATTERN.format(user_id)
    token: Optional[str] = session.get(token_key)
    results:  List[Dict[str, Any]] = []
    
    current_app.logger.debug(f"[home.search] Received search query from user_id={user_id}: '{query}'")
    
    if not token:
        current_app.logger.warning(f"[home.search] Session token missing for user_id={user_id}")
    else:
        try:
            decrypted_passwords:  List[Dict[str, Any]] = __get_cached_decrypted_passwords__(current_user, token)
            results = search_passwords(decrypted_passwords, query)
            current_app.logger.debug(f"[home.search] Found {len(results)} matching entries for user_id={user_id}")
        except Exception as e:
            current_app.logger.error(f"[home.search] Error during search for user_id={user_id}: {e}")
            results = []
            
    html: str = render_template("home/password_items_list.html", passwords=results)
    return jsonify({"html": html}) , 200


@home.route("/delete-passwords", methods=["POST"])
@login_required
def delete_passwords():
    user_id: int = current_user.id
    current_app.logger.debug(f"[home.delete_passwords] Deletion request received for user_id={user_id}")
    ids: list[int] = request.json.get("ids", [])
    token: str | None = session.get(SESSION_TOKEN_KEY_PATTERN.format(user_id))

    if not token:
        current_app.logger.warning(f"[home.delete_passwords] Missing token for user_id={user_id}")
        return jsonify({"html": ""}), 401

    if not ids:
        current_app.logger.warning(f"[home.delete_passwords] No IDs provided for deletion by user_id={user_id}")
        return jsonify({"html": ""}), 400
    
    current_app.logger.info(f"[home.delete_passwords] Attempting to delete {len(ids)} passwords for user_id={user_id}")
    
    try:
        Passwords.query.filter(
            Passwords.user_id == user_id,
            Passwords.id.in_(ids)
        ).delete(synchronize_session=False)
        db.session.commit()
        current_app.logger.info(f"[home.delete_passwords] Successfully deleted {len(ids)} password(s) for user_id={user_id}")
        flash(f"Deleted {len(ids)} record(s).", "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"[home.delete_passwords] Database error for user_id={user_id}: {e}")
        flash("An error occurred while deleting passwords.", "danger")
        return jsonify({"html": ""}), 500

    cache.delete(DECRYPTED_PASSWORDS_CACHE_KEY.format(user_id))
    current_app.logger.debug(f"[home.delete_passwords] Cache invalidated for user_id={user_id}")

    passwords: List[Dict[str, Any]] = __get_cached_decrypted_passwords__(current_user, token)
    html: str = render_template("home/password_items_list.html", passwords=passwords)

    return jsonify({"html": html}), 200




@home.route("/profile")
@login_required
def profile():
    user_id: int = current_user.id
    current_app.logger.debug(f"[home.profile] Profile requested by user_id={user_id}")
    password_count: int = Passwords.query.filter_by(user_id=user_id).count()
    return render_template("profile/profile.html", password_count=password_count)


@home.route("/profile/export_csv")
@login_required
def export_csv():
    user_id: int = current_user.id
    token: Optional[str] = session.get(SESSION_TOKEN_KEY_PATTERN.format(user_id))
    if not token:
        current_app.logger.warning(f"[export_csv] No token found in session for user_id={user_id}")
        return redirect(url_for("auth.login"))
    try:
        cache_key = DECRYPTED_PASSWORDS_CACHE_KEY.format(user_id)
        current_app.logger.debug(f"[export_csv] Deleting cache for user_id={user_id}, key={cache_key}")
        cache.delete(cache_key)

        current_app.logger.debug(f"[export_csv] Fetching decrypted passwords for user_id={user_id}")
        passwords:  List[Dict[str, Any]] = __get_cached_decrypted_passwords__(current_user, token)
        response: Response = export_passwords_to_csv(passwords)
        flash("File exported successfully.", "success")
        return response
    except Exception as e:
        current_app.logger.error(f"[export_csv] Error during export for user_id={user_id}: {e}")
        flash("File exported error.", "error")
        return redirect(url_for("home.profile"))


@home.route("/profile/import_csv", methods=["POST"])
@login_required
def import_csv():
    user_id: int = current_user.id
    current_app.logger.debug(f"[home.import_csv] Import request received for user_id={user_id}")

    token: Optional[str] = session.get(SESSION_TOKEN_KEY_PATTERN.format(user_id))
    if not token:
        current_app.logger.warning(f"[home.import_csv] Session token missing for user_id={user_id}")
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("auth.login"))

    if 'file' not in request.files:
        current_app.logger.warning(f"[home.import_csv] No file provided for user_id={user_id}")
        flash("No file provided.", "error")
        return redirect(url_for("home.profile"))

    file = request.files['file']
    if file.filename == '':
        current_app.logger.warning(f"[home.import_csv] No file selected for user_id={user_id}")
        flash("No file selected.", "error")
        return redirect(url_for("home.profile"))

    if not file.filename.lower().endswith('.csv'):
        current_app.logger.warning(f"[home.import_csv] Invalid file format for user_id={user_id}")
        flash("Invalid file format. Please upload a CSV file.", "error")
        return redirect(url_for("home.profile"))

    try:
        imported_passwords: List[Dict[str, str]] = parse_csv(file)
        if not imported_passwords:
            current_app.logger.info(f"[home.import_csv] No valid password records found in CSV for user_id={user_id}")
            flash("No valid password records found in the CSV.", "warning")
            return redirect(url_for("home.profile"))

        existing_passwords: List[Dict[str, Any]] = __get_cached_decrypted_passwords__(current_user, token)
        merged_passwords: List[Dict[str, str]] = merge_passwords(
            existing_passwords,
            imported_passwords,
            replace_existing=True
        )

        try:
            Passwords.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            for password in merged_passwords:
                encrypted_login: str = encrypt_data(password.get("login", ""), token)
                encrypted_password: str = encrypt_data(password.get("password", ""), token)
                new_password: Passwords = Passwords(
                    url=password.get("url", "").strip(),
                    login=encrypted_login,
                    password=encrypted_password,
                    description=password.get("description", "").strip(),
                    site=password.get("site", "").strip(),
                    user_id=user_id,
                )
                db.session.add(new_password)
            db.session.commit()
            cache.delete(DECRYPTED_PASSWORDS_CACHE_KEY.format(user_id))
            current_app.logger.info(f"[home.import_csv] Successfully imported {len(imported_passwords)} password records for user_id={user_id}")
            flash(f"Successfully imported {len(imported_passwords)} password records.", "success")
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"[home.import_csv] Database error for user_id={user_id}: {e}")
            flash("An error occurred while saving passwords to the database.", "error")
            return redirect(url_for("home.profile"))

    except ValueError as e:
        current_app.logger.error(f"[home.import_csv] Error processing CSV for user_id={user_id}: {e}")
        flash(f"Error processing CSV file: {str(e)}", "error")
    except Exception as e:
        current_app.logger.error(f"[home.import_csv] Unexpected error for user_id={user_id}: {e}")
        flash(f"An unexpected error occurred: {str(e)}", "error")

    return redirect(url_for("home.profile"))






@home.route("/profile/password_test")
@login_required
def password_test():
    flash("Password test not implemented yet.", "info")
    return redirect(url_for("home.profile"))







@home.route("/edit_password/<int:password_id>", methods=["GET", "POST"])
@login_required
def edit_password(password_id: int) -> str | Response:
    user_id: int = current_user.id
    current_app.logger.debug(f"[home.edit_password] Edit request for password_id={password_id} by user_id={user_id}")
    
    password_entry: Optional[Passwords] = __get_password_by_field__(password_id,user_id)
    if not password_entry:
        current_app.logger.warning(f"[home.edit_password] Password_id={password_id} not found for user_id={user_id}")
        flash("Password entry not found.", "error")
        return redirect(url_for("home.index"))

    token: Optional[str] = session.get(SESSION_TOKEN_KEY_PATTERN.format(user_id))
    if not token:
        current_app.logger.warning(f"[home.edit_password] Session token missing for user_id={user_id}")
        return redirect(url_for("auth.login"))

    form: EditPasswordForm = EditPasswordForm()

    if form.validate_on_submit():
        try:
            encrypted_login: str = encrypt_data(form.username.data, token)
            encrypted_password: str = encrypt_data(form.password.data, token)
        except Exception as e:
            current_app.logger.error(f"[home.edit_password] Encryption failed for user_id={user_id}, password_id={password_id}: {e}")
            flash("An error occurred while encrypting your data. Please try again.", "error")
            return render_template("home/edit_password/edit_password.html", form=form)

        password_entry.site = form.site.data.strip()
        password_entry.url = form.url.data.strip()
        password_entry.login = encrypted_login
        password_entry.password = encrypted_password
        password_entry.description = form.comments.data.strip() if form.comments.data else ""

        try:
            db.session.commit()
            current_app.logger.info(f"[home.edit_password] Password successfully updated for user_id={user_id}, password_id={password_id}")
            cache.delete(DECRYPTED_PASSWORDS_CACHE_KEY.format(user_id))
            flash("Password was updated successfully!", "success")
            return redirect(url_for("home.index"))
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"[home.edit_password] Database error while updating password_id={password_id} for user_id={user_id}: {e}")
            flash("An error occurred while updating the password. Please try again later.", "error")

    if request.method == "GET":
        try:
            form.site.data = password_entry.site
            form.username.data = decrypt_data(password_entry.login, token)
            form.password.data = decrypt_data(password_entry.password, token)
            form.url.data = password_entry.url
            form.comments.data = password_entry.description
        except Exception as e:
            current_app.logger.error(f"[home.edit_password] Decryption failed for password_id={password_id}: {e}")
            flash("An error occurred while loading the password data.", "error")
            return redirect(url_for("home.index"))

    return render_template("home/edit_password/edit_password.html", form=form)



def __get_password_by_field__(password_id: str, user_id: Any) -> Optional[User]:
    try:
        password: Optional[Passwords] = Passwords.query.filter_by(id=password_id, user_id=user_id).first()
        return password
    except OperationalError as e:
        current_app.logger.error(f"Database operational error: {e}")
    except IntegrityError as e:
        current_app.logger.error(f"Database integrity error: {e}")
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error: {e}")
    return None



def __get_cached_decrypted_passwords__(
    user: User, token: str, timeout: int = 300
) -> List[Dict[str, Any]]:
    passwords = cache.get(DECRYPTED_PASSWORDS_CACHE_KEY.format(user.id))
    if passwords is None:
        db_passwords = user.passwords
        passwords = []
        for p in db_passwords:
            try:
                decrypted_login = decrypt_data(p.login, token)
                decrypted_password = decrypt_data(p.password, token)
            except Exception as e:
                current_app.logger.error(
                    f"[__get_cached_decrypted_passwords__] Decryption error for password_id={p.id}: {e}"
                )
                decrypted_login = ""
                decrypted_password = ""
            passwords.append(
                {
                    "id": p.id,
                    "url": p.url,
                    "site": p.site,
                    "login": decrypted_login,
                    "password": decrypted_password,
                    "description": p.description,
                }
            )
        cache.set(
            DECRYPTED_PASSWORDS_CACHE_KEY.format(user.id), passwords, timeout=timeout
        )
    return passwords
