from flask.blueprints import Blueprint
from flask import render_template

from sqlbase import db, BlogPost


bp = Blueprint("home", __name__, static_folder="../static")


@bp.route("/")
def route_root():
    blog_posts = db.query(BlogPost)
    return render_template("home.html", title="Root", blog_posts=blog_posts)
