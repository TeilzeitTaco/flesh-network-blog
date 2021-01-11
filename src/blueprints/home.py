from flask.blueprints import Blueprint
from flask import render_template


bp = Blueprint("home", __name__, static_folder="../static")


@bp.route("/")
def route_root():
    return render_template("home.html", title="TEST")
