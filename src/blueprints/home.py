import random
from urllib.parse import urlparse

import sqlalchemy
from flask import render_template, request, send_from_directory, current_app, Response
from flask.blueprints import Blueprint
from werkzeug.exceptions import abort

from forms import CommentForm
from main import cache
from misc import FileCache, static_vars, IPTracker
from sitemap import generate_sitemap
from sqlbase import db, BlogPost, Author, Tag, Friend, ReferrerHostname


bp = Blueprint("home", __name__, static_folder="../static")


@bp.before_request
def register_referrer():
    # Save only the hostname (more could be dangerous privacy-wise) of the referrer url.
    if raw_hostname := urlparse(request.referrer).hostname:
        try:
            db.add(ReferrerHostname(raw_hostname))
            db.commit()
        except sqlalchemy.exc.IntegrityError:
            db.rollback()  # Duplicate hostname.


@bp.route("/backlinks")
@cache.cached()
def route_backlinks() -> Response:
    hostnames = db.query(ReferrerHostname).all()
    return render_template("backlinks.html", title="Backlinks", hostnames=hostnames)


@bp.route("/robots.txt")
@bp.route("/favicon.ico")
def static_from_root() -> Response:
    return send_from_directory(current_app.static_folder, request.path[1:])


@bp.route("/sitemap.xml")
@cache.cached()
def sitemap_route() -> Response:
    return Response(generate_sitemap(), mimetype="application/xml")


@bp.route("/")
@cache.cached()
@static_vars(quotes=[
    # Caching these doesn't matter, its okay if these only change occasionally.
    "Because we are all connected.",
    "What are you afraid of?",
    "Please be nice.",
    "Enter, Exit.",
])
def route_root() -> any:
    quote = random.choice(route_root.quotes)
    blog_posts = db.query(BlogPost).order_by(BlogPost.timestamp.desc())
    friends = db.query(Friend).all()
    return render_template("home.html", title="Root", blog_posts=blog_posts,
                           friends=friends, quote=quote)


@bp.route("/posts/<int:blog_post_id>/", methods=["GET", "POST"])
@bp.route("/posts/<int:blog_post_id>/<string:name>/", methods=["GET", "POST"])
@static_vars(file_cache=FileCache(), ip_tracker=IPTracker())
def route_blog_post(blog_post_id: int, name: str = "") -> any:
    if (blog_post := db.query(BlogPost).get(blog_post_id)) is None:
        abort(404)

    if (form := CommentForm()).validate_on_submit():
        comment = form.to_database_object()
        blog_post.comments.append(comment)
        db.commit()

    # The cache object is a function-static (like in C) variable
    blog_post_content = route_blog_post.file_cache.get_contents(blog_post.html_path)

    # Flush the ip tracker, and then, check if we should count this request as a true hit.
    route_blog_post.ip_tracker.remove_expired()
    if route_blog_post.ip_tracker.should_count_request(request.remote_addr, blog_post_id):
        blog_post.hits += 1
        db.commit()

    return render_template("blog_post.html", title=blog_post.name, form=CommentForm(),
                           blog_post=blog_post, blog_post_content=blog_post_content)


@bp.route("/authors/<int:author_id>/")
@bp.route("/authors/<int:author_id>/<string:name>/")
@cache.cached()
def route_author(author_id: int, name: str = "") -> any:
    if (author := db.query(Author).get(author_id)) is None:
        abort(404)

    return render_template("author.html", title=f"Author: \"{author.name}\"",
                           author=author)


@bp.route("/tags/<int:tag_id>/")
@bp.route("/tags/<int:tag_id>/<string:name>/")
@cache.cached()
def route_tag(tag_id: int, name: str = "") -> any:
    if (tag := db.query(Tag).get(tag_id)) is None:
        abort(404)

    return render_template("tag.html", title=f"Blog Posts with Tag: \"{tag.name}\"",
                           tag=tag)
