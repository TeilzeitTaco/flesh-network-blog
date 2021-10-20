import os
import random
from datetime import datetime
from typing import Callable
from urllib.parse import urlparse

from flask import current_app
from flask import render_template, request, send_from_directory, Response, url_for
from flask.blueprints import Blueprint
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import abort
from werkzeug.utils import redirect, secure_filename

from forms import CommentForm
from main import cache
from misc import FileCache, static_vars, IPTracker, in_res_path, hash_string
from readable_queries import get_all_visible_blog_posts
from sitemap import generate_sitemap
from sqlbase import db, BlogPost, Author, Tag, Friend, ReferrerHostname

bp = Blueprint("home", __name__, static_folder="../static")


def try_with_integrity_protection(statement: Callable) -> None:
    try:
        statement()
        db.commit()
    except IntegrityError:
        db.rollback()  # Duplicate.


@bp.before_request
def register_referrer() -> None:
    # Save only the hostname (more could be dangerous privacy-wise) of the referrer url.
    if raw_hostname := urlparse(request.referrer).hostname:
        try_with_integrity_protection(lambda: db.add(ReferrerHostname(raw_hostname)))


@bp.route("/backlinks")
@cache.cached()
def route_backlinks() -> Response:
    return render_template("backlinks.html", title="Backlinks", return_to_root=True,
                           hostnames=db.query(ReferrerHostname).all())


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
    "Hauptseite für den pyrotechnischen Klassizismus.",
    "Ich sehe die Morgenröte eines schönen Tages.",
    "Increasingly decreasing in all things.",
    "Increasingly afraid it's gonna rain",
    "Abgedroschene Gesellschaftskritik",
    "Watch the turtle cross the road.",
    "The flesh suffers just the same",
    "Total Inexcusable Obscurantism.",
    "Because we are all connected.",
    "You'll be walking on air~",
    "What are you afraid of?",
    "Do bats eat cats?",
    "Online Doom Cult.",
    "Antimon Antinomy",
    "Please be nice.",
    "Enter, Exit.",
    "Silly HQ",
])
def route_root() -> any:
    quote = random.choice(route_root.quotes)

    friends = db.query(Friend).all()
    category_tags = [tag for tag in db.query(Tag).filter_by(main_section=True) if tag.blog_posts]
    blog_posts = get_all_visible_blog_posts().order_by(BlogPost.timestamp.desc()).limit(5).all()

    return render_template("home.html", title="Root", header="Welcome to the Flesh-Network.", sub_header=quote,
                           blog_posts=blog_posts, friends=friends, category_tags=category_tags,
                           quote=quote)


@bp.route("/blogposts/")
def route_posts() -> any:
    blog_posts = get_all_visible_blog_posts().order_by(BlogPost.timestamp.desc()).all()
    return render_template("posts.html", title="All Writings", return_to_root=True,
                           blog_posts=blog_posts)


@bp.route("/blogposts/<int:blog_post_id>/survey", methods=["POST"])
def route_survey_submit(blog_post_id: int) -> any:
    if (blog_post := db.query(BlogPost).get(blog_post_id)) is None:
        abort(404)

    if not blog_post.allow_file_upload:
        abort(403)

    # check if the post request has the file part
    if "file" not in request.files:
        abort(422)

    file = request.files["file"]
    if file.filename == "":
        abort(422)

    hashed_ip = hash_string(current_app.config["SECRET_KEY"] + request.remote_addr, 8)
    file_name = f"{hashed_ip}-{datetime.now().timestamp()}-{secure_filename(file.filename)}"
    file_path = os.path.join(blog_post.uploaded_files_path, file_name)
    file.save(file_path)

    return render_template("survey_thanks.html", return_to_root=True,
                           title=f"Content Submission for \"{blog_post.name}\"",
                           blog_post=blog_post, hashed_ip=hashed_ip)


@bp.route("/blogposts/<int:blog_post_id>/", methods=["GET", "POST"])
@bp.route("/blogposts/<int:blog_post_id>/<string:_name>/", methods=["GET", "POST"])
@static_vars(file_cache=FileCache(), ip_tracker=IPTracker())
def route_blog_post(blog_post_id: int, _name: str = "") -> any:
    if (blog_post := db.query(BlogPost).get(blog_post_id)) is None:
        abort(404)

    # Comment posting
    if (form := CommentForm()).validate_on_submit() and blog_post.allow_comments:
        comment = form.to_database_object()
        try_with_integrity_protection(lambda: blog_post.comments.append(comment))
        return redirect(url_for("home.route_blog_post", blog_post_id=blog_post_id, _name=_name))

    # The cache object is a function-static (like in C) variable
    blog_post_content = route_blog_post.file_cache.get_contents(blog_post.html_path)

    # Flush the ip tracker, and then, check if we should count this request as a true hit.
    route_blog_post.ip_tracker.remove_expired()
    if route_blog_post.ip_tracker.should_count_request(request.remote_addr, blog_post_id):
        blog_post.hits += 1
        db.commit()

    # Select a random image to be served for opengraph embeds.
    image_resources = [fr for fr in blog_post.file_resources if fr.is_thumbnail]
    open_graph_image = in_res_path(random.choice(image_resources).name) if image_resources else None

    return render_template("blog_post.html", title=blog_post.name, return_to_root=True,
                           blog_post=blog_post, blog_post_content=blog_post_content,
                           form=CommentForm(), open_graph_image=open_graph_image)


@bp.route("/authors/<int:author_id>/")
@bp.route("/authors/<int:author_id>/<string:_name>/")
@cache.cached()
def route_author(author_id: int, _name: str = "") -> any:
    if (author := db.query(Author).get(author_id)) is None:
        abort(404)

    return render_template("author.html", title=f"Author: \"{author.name}\"", return_to_root=True,
                           author=author)


@bp.route("/tags/<int:tag_id>/")
@bp.route("/tags/<int:tag_id>/<string:_name>/")
@cache.cached()
def route_tag(tag_id: int, _name: str = "") -> any:
    # The "name" parameter is called "_name" to avoid unused variable
    # warnings in PyCharm. It is not beautiful but better than someone
    # removing them just by following suggestions.
    if (tag := db.query(Tag).get(tag_id)) is None:
        abort(404)

    title = f"Posts in category \"{tag.name}\":" if tag.main_section else f"Posts with tag \"{tag.name}\":"
    return render_template("tag.html", title=title, return_to_root=True,
                           tag=tag)


@bp.route("/files")
@cache.cached()
def route_files() -> any:
    blog_posts = get_all_visible_blog_posts().order_by(BlogPost.timestamp.desc()).all()
    file_count = sum(len(blog_post.file_resources) for blog_post in blog_posts)
    return render_template("files.html", title="File Index", return_to_root=True,
                           blog_posts=blog_posts, file_count=file_count)
