from faker import Faker
from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_required, current_user
from ..models.passwords import Passwords
from ..exstesions import db, cache
from ..utils.cpypto_utils import encrypt_data, decrypt_data
from ..utils.search_utils import search_passwords
from ..utils.csv_utils import export_passwords_to_csv
from ..forms import (
    AddPasswordForm,
    CreatePasswordForm,
    DeletePasswordForm,
)

home = Blueprint("home", __name__)


@home.route("/home", methods=["GET", "POST"])
@login_required
def index():
    add_form = AddPasswordForm()
    delete_form = DeletePasswordForm()
    token = session.get(f"token_from_password_{current_user.id}")

    if add_form.submit_add.data and add_form.validate_on_submit():
        return redirect(url_for("home.create_password"))

    if not token:
        flash("Session token not found. Please log in again.", "error")
        return redirect(url_for("auth.login"))

    passwords = get_cached_decrypted_passwords(current_user, token)

    return render_template(
        "home/home.html",
        add_form=add_form,
        delete_form=delete_form,
        passwords=passwords,
    )


@home.route("/create_password", methods=["GET", "POST"])
@login_required
def create_password():
    form = CreatePasswordForm()
    if form.validate_on_submit():
        token = session.get(f"token_from_password_{current_user.id}")
        if not token:
            flash("Session token not found. Please log in again.", "error")
            return redirect(url_for("auth.login"))

        encrypted_login = encrypt_data(form.username.data, token)
        encrypted_password = encrypt_data(form.password.data, token)

        new_password = Passwords(
            url=form.url.data.strip(),
            login=encrypted_login,
            password=encrypted_password,
            description=form.comments.data,
            user_id=current_user.id,
            site=form.site.data.strip(),
        )
        db.session.add(new_password)
        db.session.commit()

        cache.delete(f"decrypted_passwords_{current_user.id}")

        flash("Password saved successfully!", "success")
        return redirect(url_for("home.index"))
    return render_template("home/create_password/create_password.html", form=form)


@home.route("/search", methods=["POST"])
@login_required
def search():
    q = request.json.get("q", "")
    token = session.get(f"token_from_password_{current_user.id}")
    results = []

    if token:
        decrypted_passwords = get_cached_decrypted_passwords(current_user, token)
        results = search_passwords(decrypted_passwords, q)

    html = render_template("home/password_items_list.html", passwords=results)
    return jsonify({"html": html})


@home.route("/delete-passwords", methods=["POST"])
@login_required
def delete_passwords():
    ids = request.json.get("ids", [])
    token = session.get(f"token_from_password_{current_user.id}")
    if not token or not ids:
        return jsonify({"html": ""}), 400

    # Удаляем только свои пароли
    Passwords.query.filter(
        Passwords.user_id == current_user.id, Passwords.id.in_(ids)
    ).delete(synchronize_session=False)
    db.session.commit()

    cache_key = f"decrypted_passwords_{current_user.id}"
    cache.delete(cache_key)
    passwords = get_cached_decrypted_passwords(current_user, token)
    cache.set(f"decrypted_passwords_{current_user.id}", passwords, timeout=300)

    html = render_template("home/password_items_list.html", passwords=passwords)
    return jsonify({"html": html})


# @home.route("/fill_passwords")
# @login_required
# def fill_passwords():
#     fake = Faker()
#     token = session.get(f"token_from_password_{current_user.id}")
#     if not token:
#         flash("Session token not found. Please log in again.", "error")
#         return redirect(url_for("auth.login"))

#     for _ in range(20):  # Сколько паролей добавить
#         url = fake.url()
#         site = fake.domain_name()
#         login = encrypt_data(fake.user_name(), token)
#         password = encrypt_data(fake.password(length=12), token)
#         description = fake.sentence(nb_words=6)
#         new_password = Passwords(
#             url=url,
#             site=site,
#             login=login,
#             password=password,
#             description=description,
#             user_id=current_user.id,
#         )
#         db.session.add(new_password)
#     db.session.commit()
#     flash("База паролей успешно заполнена тестовыми данными!", "success")
#     return redirect(url_for("home.index"))


@home.route("/profile")
@login_required
def profile():
    password_count = len(current_user.passwords)
    return render_template("profile/profile.html", password_count=password_count)


@home.route("/profile/export_csv")
@login_required
def export_csv():
    # Получаем пароли пользователя из БД
    token = session.get(f"token_from_password_{current_user.id}")
    # Формируем список словарей с расшифрованными данными
    passwords = get_cached_decrypted_passwords(current_user, token)
    
    # Возвращаем CSV как файл через функцию из утилиты
    return export_passwords_to_csv(passwords)



@home.route("/profile/import_csv", methods=["POST"])
@login_required
def import_csv():
    # Здесь ваша логика импорта CSV
    flash("Import not implemented yet.", "info")
    return redirect(url_for("profile.profile_page"))


@home.route("/profile/password_test")
@login_required
def password_test():
    # Здесь ваша логика теста паролей
    flash("Password test not implemented yet.", "info")
    return redirect(url_for("profile.profile_page"))





def get_cached_decrypted_passwords(user, token, timeout=300):
    cache_key = f"decrypted_passwords_{user.id}"
    passwords = cache.get(cache_key)
    if passwords is None:
        db_passwords = user.passwords
        passwords = []
        for p in db_passwords:
            passwords.append(
                {
                    "id": p.id,
                    "url": p.url,
                    "site": p.site,
                    "login": decrypt_data(p.login, token),
                    "password": decrypt_data(p.password, token),
                    "description": p.description,
                }
            )
        cache.set(cache_key, passwords, timeout=timeout)
    return passwords
