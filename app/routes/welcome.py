from flask import Blueprint, render_template




welcome = Blueprint("welcome", __name__)

@welcome.route("/")
def start():
    return render_template("welcome/welcome.html")