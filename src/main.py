from flask import Flask
from flask_assets import Environment, Bundle


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static")
    assets = Environment(app)

    js_home = Bundle("scripts/base.js", filters="jsmin", output="gen/js_home.js")
    assets.register("js_home", js_home)

    from blueprints.home import bp as home_bp
    app.register_blueprint(home_bp)

    return app
