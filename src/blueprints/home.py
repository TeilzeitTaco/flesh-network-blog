from flask.blueprints import Blueprint
from flask import render_template

from main import cache
from sqlbase import db, BlogPost, Author, Tag

bp = Blueprint("home", __name__, static_folder="../static")


@bp.route("/")
@cache.cached()
def route_root():
    blog_posts = db.query(BlogPost)
    return render_template("home.html", title="Root", blog_posts=blog_posts)


@bp.route("/posts/<int:blog_post_id>/")
@bp.route("/posts/<int:blog_post_id>/<string:title>/")
@cache.cached()
def route_blog_post(blog_post_id: int, title: str = ""):
    blog_post = db.query(BlogPost).get(blog_post_id)
    if blog_post is None:
        return "error"

    with open(blog_post.html_path, "r") as f:
        blog_post_content = f.read()

    return render_template("blog_post.html", title=blog_post.title,
                           blog_post=blog_post, blog_post_content=blog_post_content)


@bp.route("/authors/<int:author_id>/")
@bp.route("/authors/<int:author_id>/<string:name>/")
@cache.cached()
def route_author(author_id: int, name: str = ""):
    author = db.query(Author).get(author_id)
    if author is None:
        return "error"

    return render_template("author.html", title=f"Author: \"{author.name}\"",
                           author=author)


@bp.route("/tag/<int:tag_id>/")
@bp.route("/tag/<int:tag_id>/<string:name>/")
@cache.cached()
def route_tag(tag_id: int, name: str = ""):
    tag = db.query(Tag).get(tag_id)
    if tag is None:
        return "error"

    return render_template("tag.html", title=f"Blog Posts with Tag: \"{tag.name}\"",
                           tag=tag)

