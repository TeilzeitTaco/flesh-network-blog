import functools
import logging
import os

from urllib.parse import urlparse

from flask import Flask, render_template, request
from flask_assets import Environment, Bundle
from flask_caching import Cache
from werkzeug.exceptions import HTTPException

from misc import in_res_path

BLOG_NAME = "Flesh-Network"
cache = Cache()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_json("config.json")

    if app.config["DEBUG_LOG_TO_FILE"]:
        logging.basicConfig(filename="blog.log", level=logging.DEBUG)

    if app.config["BEHIND_PROXY"]:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

    # Description for meta tag (SEO and such things)
    with open("description.txt") as f:
        seo_description = f.read().replace("\n", " ").strip()

    # These functions and values are available in Jinja templates.
    app.jinja_env.globals.update(
        root_url=lambda: "{uri.scheme}://{uri.netloc}/".format(uri=urlparse(request.base_url)),
        file_name_to_display_name=lambda fn: fn.replace("-", " ").rsplit(".", 1)[0].title(),
        background_image_files=functools.partial(os.listdir, "static/images/backgrounds/"),
        format_title=lambda title: f"{title} | {BLOG_NAME}",
        this_url=lambda: request.base_url,
        seo_description=seo_description,
        in_res_path=in_res_path,
    )

    # Caches pages to reduce server load.
    cache.init_app(app)

    # Manages asset packaging.
    assets = Environment(app)

    js_base = Bundle("scripts/base.js", filters="jsmin", output="gen/js_base.js")
    assets.register("js_base", js_base)

    css_base = Bundle("css/base.css", filters="cssmin", output="gen/css_base.css")
    assets.register("css_base", css_base)

    from blueprints.home import bp as home_bp
    app.register_blueprint(home_bp)

    @app.errorhandler(HTTPException)
    def handle_error(exception):
        return render_template("error.html", title=f"Error {exception.code}: {exception.name}",
                               exception=exception, return_to_root=True), exception.code

    return app
