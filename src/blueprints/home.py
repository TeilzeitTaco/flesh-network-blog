from flask.blueprints import Blueprint
from flask import render_template

from sqlbase import db, BlogPost


bp = Blueprint("home", __name__, static_folder="../static")


@bp.route("/")
def route_root():
    blog_posts = db.query(BlogPost)
    return render_template("home.html", title="Root", blog_posts=blog_posts)


# TODO: title is optional
@bp.route("/<int:blog_post_id>/<string:title>")
def route_blog_post(blog_post_id: int, title: str):
    blog_post = db.query(BlogPost).get(blog_post_id)
    if not blog_post:
        return "error"

    with open(blog_post.html_path, "r") as f:
        blog_post_content = f.read()

    return render_template("blog_post.html", title=blog_post.title,
                           blog_post=blog_post, blog_post_content=blog_post_content)
