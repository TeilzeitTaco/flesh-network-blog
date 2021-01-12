from flask import Flask
from flask_assets import Environment, Bundle


BLOG_NAME = "Flesh-Network"


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static")
    app.config.from_json("config.json")

    if app.config["BEHIND_PROXY"]:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

    # These functions are available in Jinja templates.
    app.jinja_env.globals.update(
        format_title=lambda title: f"{title} | {BLOG_NAME}",
    )

    # Manage asset packaging
    assets = Environment(app)

    js_base = Bundle("scripts/base.js", filters="jsmin", output="gen/js_base.js")
    assets.register("js_base", js_base)

    css_base = Bundle("css/base.css", filters="cssmin", output="gen/css_base.css")
    assets.register("css_base", css_base)

    from blueprints.home import bp as home_bp
    app.register_blueprint(home_bp)

    return app
